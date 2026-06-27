"""
questionnaire_adapter.py — Dentists' Tax & Business Architecture System™
=========================================================================
Maps your personal + financial questionnaire dicts directly to Q_ signals.
Enhanced version with full support for entity returns (1120S, 1120, 1065).

No MongoDB. No ODM. Just plain Python dicts in, enriched signals dict out.

USAGE
-----
    from questionnaire_adapter import build_signals_from_questionnaire

    # personal_q and financial_q are plain dicts matching your schema
    signals = SignalEngine().derive(ret)
    signals = build_signals_from_questionnaire(signals, personal_q, financial_q)
    strategies = StrategyScorer().score_all(signals, config)

SCHEMA FIELDS USED
------------------
From personalQuestionnaire:
    dateOfBirth, spouseName, spouseDateOfBirth, spouseAnnualCompensation,
    noOfChildren, children[{age, dateOfBirth, inCollege}],
    businessStructure, employeesCount, businessOwnershipPercentage,
    secondaryBusinessOwnership, thirdBusinessOwnership,
    monthlyMedicalInsurance, premiumPayer,
    ownsPracticeBuilding, ownsSecondaryHome, secondaryHomeCount,
    ownsBoatOrYacht, hasRentalProperties, rentalPropertyCount,
    spouseWorksInPractice, planningRetirement, retirementAge,
    clientAnnualCompensation, householdIncome, longTermFinancialGoals,
    buildingPurchasePrice,        ← exact office building cost basis
    buildingPlacedInServiceYear,  ← determines bonus depreciation rate
    plannedEquipmentPurchase,     ← Section 179 opportunity amount
    managementCompanyRevenue,     ← actual non-SSTB income for QBI
    
    # Entity return fields (NEW)
    has1120S, has1120, has1065,   ← which entity types exist
    sCorpOfficerComp,             ← current officer compensation
    sCorpDistributions,           ← current distributions
    cCorpRetainedEarningsActual,  ← actual C-Corp retained earnings
    partnershipGuaranteedPayments,← guaranteed payments received
    hasForm4797, hasForm6252,     ← attached forms present
    installmentSaleProceeds,      ← from Form 6252
    section1231Gain,              ← from Form 4797
    nolCarryoverAmount,           ← NOL carryforward amount
    realEstateProfessionalHours,  ← hours in real estate activities
    otherWorkHours,               ← hours in other work
    practiceSalePlanned,          ← planning to sell practice
    isoSpreadAmount,              ← ISO/stock option spread
    annualEquipmentLeasePayments, ← equipment lease payments

From financialQuestionnaire:
    dob (fallback DOB), retirementPlan, retirementAge,
    annualPremium, hasLifeInsurance, insurancePolicyType,
    totalCashValue, cashOnHand, realEstateValues,
    commercialProperty, workersCompPremiumOver40k, selfInsured,
    estimatedNetWorthRange, currentSecuritiesInvestments,
    newEmployeesPerYear,
    cCorpRetainedEarnings         ← exact C-Corp retained earnings
"""

from datetime import date, datetime
from typing import Any, Dict, Optional, List


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _to_date(val) -> Optional[date]:
    """Accepts date, datetime, or ISO string. Returns date or None."""
    if val is None:
        return None
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, str):
        try:
            return datetime.fromisoformat(val.replace("Z", "")).date()
        except Exception:
            return None
    return None


def _age_from_dob(dob) -> Optional[int]:
    d = _to_date(dob)
    if d is None:
        return None
    return (date.today() - d).days // 365


def _to_float(val, default=0.0) -> float:
    if val is None:
        return default
    try:
        return float(str(val).replace(",", "").replace("$", ""))
    except Exception:
        return default


def _to_int(val, default=0) -> int:
    try:
        return int(val)
    except Exception:
        return default


def _to_bool(val, default=False) -> bool:
    if val is None:
        return default
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in ("true", "yes", "1")
    return bool(val)


# ═══════════════════════════════════════════════════════════════════════════════
#  CASH BALANCE ACTUARIAL TABLE
# ═══════════════════════════════════════════════════════════════════════════════

_CB_LIMITS_BY_AGE = {
    35: 85_000,  40: 105_000, 45: 140_000,
    50: 185_000, 55: 235_000, 60: 280_000, 65: 310_000,
}

def _cash_balance_limit_from_dob(dob) -> float:
    """
    Returns approximate maximum annual cash balance contribution.
    Interpolates between IRS § 415 age brackets.
    Real plans require an actuary — this is the best estimate from Phase 1 data.
    """
    age = _age_from_dob(dob)
    if age is None:
        return 140_000.0  # conservative fallback if DOB missing
    age = max(35, min(65, age))
    ages = sorted(_CB_LIMITS_BY_AGE.keys())
    for i, a in enumerate(ages):
        if age <= a:
            if i == 0:
                return float(_CB_LIMITS_BY_AGE[a])
            a_lo, a_hi = ages[i - 1], ages[i]
            frac = (age - a_lo) / (a_hi - a_lo)
            return _CB_LIMITS_BY_AGE[a_lo] + frac * (_CB_LIMITS_BY_AGE[a_hi] - _CB_LIMITS_BY_AGE[a_lo])
    return float(_CB_LIMITS_BY_AGE[65])


# ═══════════════════════════════════════════════════════════════════════════════
#  BUSINESS STRUCTURE → FICA EXEMPTION
# ═══════════════════════════════════════════════════════════════════════════════

def _fica_exempt_for_children(business_structure: str) -> Optional[bool]:
    """
    IRC §3121(b)(3)(A): children under 18 are FICA-exempt when employed by
    a parent's sole proprietorship or parent-only partnership.
    S-Corp and C-Corp do NOT get this exemption.
    Returns True / False / None (unknown).
    """
    s = (business_structure or "").strip()
    if s in ("Sole proprietorship", "Partnership", "LLC", "1099_Associate"):
        return True
    if s in ("S Corporation", "C Corporation", "W2_Associate"):
        return False
    return None  # "Other" or missing


# ═══════════════════════════════════════════════════════════════════════════════
#  CHILDREN UNDER 18 COUNT
# ═══════════════════════════════════════════════════════════════════════════════

def _count_children_under_18(children: list, fallback_count: int) -> int:
    """
    Counts children under 18 from the children[] array.
    Each child may have: age (Number) or dateOfBirth (Date/String).
    Falls back to fallback_count (noOfChildren) if array is empty.
    """
    if not children:
        return fallback_count  # conservative: assume all are under 18 if no DOBs

    count = 0
    for child in children:
        age = child.get("age")
        if age is not None:
            if _to_int(age) < 18:
                count += 1
        else:
            child_age = _age_from_dob(child.get("dateOfBirth"))
            if child_age is not None and child_age < 18:
                count += 1
    return count


# ═══════════════════════════════════════════════════════════════════════════════
#  STATE LOOKUP TABLES
# ═══════════════════════════════════════════════════════════════════════════════

_PTET_STATES = {
    "CA","NY","NJ","IL","CT","MA","OR","MN","CO","WI","MD","GA","VA","AZ",
    "NC","SC","OH","PA","MI","ID","KS","NE","NM","HI","ME","NH","VT","RI",
    "DE","ND","SD","MT","WY","AK","IN","MS","OK","AR","MO","AL","LA","UT",
}

_COMMUNITY_PROPERTY_STATES = {"AZ","CA","ID","LA","NV","NM","TX","WA","WI"}

_STATE_MARGINAL_RATES = {
    "CA":0.133,"NY":0.109,"NJ":0.1075,"OR":0.099,"MN":0.0985,"VT":0.0875,
    "DC":0.1075,"HI":0.11,"ME":0.0715,"WI":0.0765,"SC":0.07,"CT":0.069,
    "ID":0.058,"MT":0.059,"NE":0.0684,"MA":0.09,"RI":0.0599,"ND":0.029,
    "MO":0.048,"MD":0.0575,"GA":0.055,"KY":0.045,"VA":0.0575,"NC":0.0475,
    "AL":0.05,"OH":0.0399,"LA":0.06,"MI":0.0425,"AR":0.0475,"IL":0.0495,
    "CO":0.044,"AZ":0.025,"IN":0.03,"PA":0.0307,"MS":0.05,"KS":0.057,
    "OK":0.0475,"NM":0.059,"UT":0.0485,"WV":0.065,"DE":0.066,
    "FL":0.0,"TX":0.0,"NV":0.0,"WA":0.0,"WY":0.0,"SD":0.0,"AK":0.0,
    "NH":0.0,"TN":0.0,
}


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN ADAPTER
# ═══════════════════════════════════════════════════════════════════════════════

def build_signals_from_questionnaire(
    signals: dict,
    personal: Dict[str, Any],
    financial: Dict[str, Any],
) -> dict:
    """
    Injects Q_ signals from questionnaire dicts into the signals dict.
    Enhanced with full entity return support.

    Parameters
    ----------
    signals   : dict produced by SignalEngine.derive(ret)
    personal  : dict matching personalQuestionnaireSchema
    financial : dict matching financialQuestionnaireSchema

    Returns
    -------
    Enriched signals dict — all Q_ keys populated.
    """
    # Defensive copy — support cases where signals is None or missing keys
    s   = (signals or {}).copy()
    p   = personal  or {}
    f   = financial or {}

    # Guard against malformed or missing primary_state values
    raw_primary_state = s.get("_primary_state", "")
    if not isinstance(raw_primary_state, str):
        raw_primary_state = ""
    primary_state = raw_primary_state.upper()

    marginal_rate = s.get("_fed_marginal_rate", 0.37)
    agi           = s.get("_agi", 0)
    obi           = s.get("_obi", 0)
    existing_ret  = s.get("_retirement", 0)
    state_tax     = s.get("_state_tax", 0)

    # ─────────────────────────────────────────────────────────────────────────
    # 1. REAL ESTATE / COST SEGREGATION
    #    ownsPracticeBuilding        → owns vs. rents (eliminates false positives)
    #    buildingPurchasePrice       → exact cost basis
    #    buildingPlacedInServiceYear → correct bonus dep rate by year
    #    realEstateValues            → fallback basis proxy if above not provided
    #    commercialProperty          → secondary ownership confirmation
    # ─────────────────────────────────────────────────────────────────────────
    owns_building       = _to_bool(p.get("ownsPracticeBuilding"))
    building_purchase   = _to_float(p.get("buildingPurchasePrice"))
    building_year       = _to_int(p.get("buildingPlacedInServiceYear"))
    re_value            = _to_float(f.get("realEstateValues"))
    commercial          = _to_bool(f.get("commercialProperty"))

    # Infer building ownership from purchase price if explicit boolean not set
    if not owns_building and building_purchase > 0:
        owns_building = True
    s["Q_OWNS_BUILDING"]              = owns_building
    s["Q_BUILDING_PURCHASE_PRICE"]    = building_purchase
    s["Q_BUILDING_SERVICE_YEAR"]      = building_year

    if owns_building or commercial:
        # Priority: use exact purchase price if provided, else fall back to proxy
        if building_purchase > 0:
            building_basis = building_purchase
        elif re_value > 0:
            # Fallback: 50% of total RE value (mixes home + building)
            building_basis = re_value * 0.50
        else:
            building_basis = 800_000   # last-resort conservative default

        # Bonus depreciation rate by placed-in-service year (IRC §168(k) phase-down)
        current_year = date.today().year
        service_year = building_year if building_year and building_year > 2000 else current_year
        if service_year <= 2022:
            bonus_rate = 1.00   # 100% bonus
        elif service_year == 2023:
            bonus_rate = 0.80   # 80%
        elif service_year == 2024:
            bonus_rate = 0.60   # 60%
        elif service_year == 2025:
            bonus_rate = 0.40   # 40%
        else:
            bonus_rate = 0.20   # 20% (2026+)

        reclassifiable = building_basis * 0.27          # 27% avg reclassification
        five_yr_share  = reclassifiable * 0.60          # 60% of reclassified → 5/15-yr
        bonus_yr1      = five_yr_share * bonus_rate     # exact bonus rate for this building
        str_line_yr1   = (five_yr_share * (1 - bonus_rate)) / 5  # remainder over 5 yrs
        baseline_39yr  = reclassifiable / 39            # what straight-line 39-yr gives
        incremental    = bonus_yr1 + str_line_yr1 - baseline_39yr

        s["Q_COST_SEG_INCREMENTAL_DEDUCTION"] = max(0.0, incremental)
        s["Q_BUILDING_BASIS"]                 = building_basis
        s["Q_BONUS_DEP_RATE"]                 = bonus_rate
    else:
        # Renter → cost seg savings = exactly $0
        s["Q_COST_SEG_INCREMENTAL_DEDUCTION"] = 0.0
        s["Q_BUILDING_BASIS"]                 = 0.0
        s["Q_BONUS_DEP_RATE"]                 = 0.0

    # ─────────────────────────────────────────────────────────────────────────
    # 2. SECTION 179 / EQUIPMENT PURCHASES
    #    plannedEquipmentPurchase → equipment client plans to buy
    #    Formula: §179 full deduction vs 5-yr MACRS year-1 = 80% incremental
    # ─────────────────────────────────────────────────────────────────────────
    planned_equip = _to_float(p.get("plannedEquipmentPurchase"))
    s["Q_179_BASE_AMOUNT"]           = planned_equip
    s["Q_179_INCREMENTAL_DEDUCTION"] = planned_equip * 0.80
    # 0.80 = (1 - 1/5): §179 gives 100% deduction yr-1 vs MACRS yr-1 = 20%
    # Incremental benefit = 80% of cost × marginal rate

    # ─────────────────────────────────────────────────────────────────────────
    # 3. HEALTH INSURANCE PREMIUM
    #    monthlyMedicalInsurance × 12 = annual premium
    #    premiumPayer → who pays (determines if already deducted)
    # ─────────────────────────────────────────────────────────────────────────
    monthly_med   = _to_float(p.get("monthlyMedicalInsurance"))
    annual_premium_health = monthly_med * 12
    premium_payer = str(p.get("premiumPayer", "") or "").lower()

    # If practice/business pays → likely already deducted through entity
    practice_pays = any(kw in premium_payer for kw in
                        ["practice", "business", "employer", "company", "corp"])
    s["Q_HEALTH_PREMIUM"]               = annual_premium_health
    s["Q_HEALTH_DEDUCTION_AVAILABLE"]   = 0.0 if practice_pays else annual_premium_health

    # ─────────────────────────────────────────────────────────────────────────
    # 4. HIRING CHILDREN
    #    children[] with age/dateOfBirth → real count under 18
    #    noOfChildren → fallback count
    #    businessStructure → FICA exemption determination
    # ─────────────────────────────────────────────────────────────────────────
    children_list     = p.get("children") or []
    no_of_children    = _to_int(p.get("noOfChildren"))
    num_kids_under_18 = _count_children_under_18(children_list, no_of_children)
    std_deduction     = 14_600  # 2024 standard deduction

    biz_structure = str(p.get("businessStructure", "") or "")
    fica_exempt   = _fica_exempt_for_children(biz_structure)

    s["Q_NUM_CHILDREN"]          = num_kids_under_18
    s["Q_HIRING_CHILDREN_WAGES"] = num_kids_under_18 * std_deduction
    s["Q_FICA_EXEMPT_CHILDREN"]  = fica_exempt
    s["Q_FICA_SAVINGS_CHILDREN"] = (
        num_kids_under_18 * std_deduction * 0.153 * 0.9235
        if fica_exempt is True else 0.0
    )

    # If questionnaire confirms children exist, override SIG_DEPENDENTS_PRESENT.
    # The PDF extraction often misses dependents (empty section on 1040) even when
    # the owner has children who are legitimate hire-children candidates.
    if num_kids_under_18 > 0:
        s["SIG_DEPENDENTS_PRESENT"] = True

    # ─────────────────────────────────────────────────────────────────────────
    # 5. CASH BALANCE PLAN (age-based actuarial estimate)
    #    dateOfBirth (personal) or dob (financial) → owner age → CB limit
    #    retirementPlan (financial string) → detect existing plan type
    # ─────────────────────────────────────────────────────────────────────────
    dob = p.get("dateOfBirth") or f.get("dob")
    cb_limit = _cash_balance_limit_from_dob(dob)

    ret_plan_str = str(f.get("retirementPlan", "") or "").lower()
    has_db_plan  = any(kw in ret_plan_str for kw in
                       ["defined benefit", "cash balance", "db plan", "pension"])

    s["Q_CASH_BALANCE_LIMIT"]       = cb_limit
    s["Q_HAS_DEFINED_BENEFIT_PLAN"] = has_db_plan
    s["Q_CASH_BALANCE_INCREMENTAL"] = 0.0 if has_db_plan else max(0.0, cb_limit - existing_ret)

    # ─────────────────────────────────────────────────────────────────────────
    # 6. QBI / ENTITY RESTRUCTURE
    #    managementCompanyRevenue → actual non-SSTB income
    #    secondaryBusinessOwnership / thirdBusinessOwnership → existence signal
    #    If real revenue provided → exact 20% QBI deduction calculation
    #    If not provided → conservative 8% of OBI proxy
    # ─────────────────────────────────────────────────────────────────────────
    secondary_biz           = _to_float(p.get("secondaryBusinessOwnership"))
    third_biz               = _to_float(p.get("thirdBusinessOwnership"))
    mgmt_co_revenue         = _to_float(p.get("managementCompanyRevenue"))
    has_multi_entity        = (secondary_biz > 0 or third_biz > 0 or mgmt_co_revenue > 0)

    if mgmt_co_revenue > 0:
        # Exact: client told us the actual management company revenue
        non_sstb = mgmt_co_revenue
    elif has_multi_entity:
        # Entity exists but revenue unknown → 12% of OBI conservative proxy
        non_sstb = obi * 0.12
    else:
        # No restructuring yet → 8% very conservative proxy
        non_sstb = obi * 0.08

    s["Q_MGMT_CO_REVENUE"]           = mgmt_co_revenue
    s["Q_NON_SSTB_INCOME"]           = non_sstb
    s["Q_QBI_RESTRUCTURE_DEDUCTION"] = non_sstb * 0.20

    # ─────────────────────────────────────────────────────────────────────────
    # 7. PTET / SALT (ENHANCED FOR MULTIPLE ENTITIES)
    #    Auto-derive from primary state + entity presence
    #    PTET requires a pass-through entity AND state offering PTET
    #    AND not already elected (SIG_PTET_DETECTED from return)
    # ─────────────────────────────────────────────────────────────────────────
    # Check for passthrough entities from both return data and questionnaire
    has_passthrough_return = s.get("SIG_HAS_S_CORP", False) or s.get("SIG_HAS_PARTNERSHIP", False)
    has_passthrough_q = _to_bool(p.get("has1120S")) or _to_bool(p.get("has1065"))
    has_passthrough = has_passthrough_return or has_passthrough_q
    
    # Count passthrough entities for multi-entity PTET opportunities
    passthrough_count = sum([
        bool(s.get("SIG_HAS_S_CORP")),
        bool(s.get("SIG_HAS_PARTNERSHIP")),
        bool(p.get("has1120S")),
        bool(p.get("has1065")),
    ])

    already_elected = s.get("SIG_PTET_DETECTED", False)
    state_offers_ptet = primary_state in _PTET_STATES

    s["Q_PTET_CONFIRMED"] = (
        state_offers_ptet and has_passthrough and not already_elected
    )

    # Multiple entities = multiple PTET elections possible
    if passthrough_count > 1 and state_offers_ptet and not already_elected:
        s["Q_MULTI_ENTITY_PTET_OPPORTUNITY"] = True
        s["Q_PTET_CONFIRMED"] = True  # Still eligible

    s["Q_STATE_MARGINAL_RATE"] = _STATE_MARGINAL_RATES.get(primary_state, 0.0)

    # ─────────────────────────────────────────────────────────────────────────
    # 8. LIFE INSURANCE / EXECUTIVE BONUS PLAN
    #    annualPremium       → existing or desired premium
    #    hasLifeInsurance    → existing policy
    #    insurancePolicyType → Permanent Whole Life vs Term Life
    #    totalCashValue      → existing cash value
    # ─────────────────────────────────────────────────────────────────────────
    annual_prem_ins = _to_float(f.get("annualPremium"))
    has_life_ins    = _to_bool(f.get("hasLifeInsurance"))
    policy_type     = str(f.get("insurancePolicyType", "") or "")
    is_whole_life   = any(kw in policy_type for kw in ("Whole", "Permanent"))
    cash_value      = _to_float(f.get("totalCashValue"))

    # Gross-up calculation: total deduction = premium + tax gross-up
    gross_up = (annual_prem_ins / (1 - marginal_rate) - annual_prem_ins
                if marginal_rate < 1 and annual_prem_ins > 0 else 0.0)

    s["Q_EXISTING_LIFE_INSURANCE"]    = has_life_ins
    s["Q_INSURANCE_IS_WHOLE_LIFE"]    = is_whole_life
    s["Q_POLICY_CASH_VALUE"]          = cash_value
    s["Q_EXEC_BONUS_TOTAL_DEDUCTION"] = annual_prem_ins + gross_up

    # ─────────────────────────────────────────────────────────────────────────
    # 9. C-CORP RETAINED EARNINGS
    #    cCorpRetainedEarnings → exact retained earnings from Form 1120
    #    cashOnHand → no longer used as proxy (completely different figure)
    # ─────────────────────────────────────────────────────────────────────────
    has_c_corp_return = s.get("SIG_HAS_C_CORP", False)
    has_c_corp_q = _to_bool(p.get("has1120"))
    has_c_corp = has_c_corp_return or has_c_corp_q
    
    c_corp_retained_fin = _to_float(f.get("cCorpRetainedEarnings"))
    c_corp_retained_pers = _to_float(p.get("cCorpRetainedEarningsActual"))
    c_corp_retained = c_corp_retained_fin or c_corp_retained_pers
    
    s["Q_C_CORP_RETAINED_EARNINGS"] = c_corp_retained if has_c_corp else 0.0

    # ─────────────────────────────────────────────────────────────────────────
    # 10. ISO / STOCK OPTIONS
    # ─────────────────────────────────────────────────────────────────────────
    s["Q_ISO_SPREAD"] = _to_float(p.get("isoSpreadAmount", 0))

    # ─────────────────────────────────────────────────────────────────────────
    # 11. COMMUNITY PROPERTY
    #     spouseName presence → married indicator
    #     spouseAnnualCompensation / spouseWorksInPractice → spouse has income
    # ─────────────────────────────────────────────────────────────────────────
    spouse_name       = str(p.get("spouseName", "") or "").strip()
    is_married        = len(spouse_name) > 0
    spouse_comp       = _to_float(p.get("spouseAnnualCompensation"))
    spouse_in_biz     = _to_bool(p.get("spouseWorksInPractice"))
    spouse_has_income = spouse_comp > 0 or spouse_in_biz
    in_cp_state       = primary_state in _COMMUNITY_PROPERTY_STATES

    applicable = is_married and spouse_has_income and in_cp_state
    s["Q_COMMUNITY_PROPERTY_APPLICABLE"] = applicable
    s["Q_COMMUNITY_PROPERTY_PROBABILITY"] = 1.0 if applicable else 0.0

    # ─────────────────────────────────────────────────────────────────────────
    # 12. EDUCATIONAL ASSISTANCE §127
    #     employeesCount → number of W-2 employees eligible for the plan
    #     newEmployeesPerYear → growth signal
    # ─────────────────────────────────────────────────────────────────────────
    emp_count     = _to_int(p.get("employeesCount")) or _to_int(f.get("newEmployeesPerYear"))
    s["Q_EDUCATIONAL_ASSISTANCE_DEDUCTION"] = emp_count * 5_250 if emp_count > 0 else 0.0

    # ─────────────────────────────────────────────────────────────────────────
    # 13. EQUIPMENT LEASING
    # ─────────────────────────────────────────────────────────────────────────
    s["Q_ANNUAL_LEASE_PAYMENTS"] = _to_float(p.get("annualEquipmentLeasePayments", 0))

    # ─────────────────────────────────────────────────────────────────────────
    # 14. RENTAL PROPERTIES
    #     hasRentalProperties + rentalPropertyCount → override return signals
    # ─────────────────────────────────────────────────────────────────────────
    has_rentals  = _to_bool(p.get("hasRentalProperties"))
    rental_count = _to_int(p.get("rentalPropertyCount"))
    # Infer from count if boolean not explicitly set
    if not has_rentals and rental_count > 0:
        has_rentals = True
    s["Q_HAS_RENTAL_PROPERTIES"] = has_rentals
    s["Q_RENTAL_PROPERTY_COUNT"]  = rental_count
    # Strengthen the signal if confirmed by questionnaire
    if has_rentals:
        s["SIG_REAL_ESTATE_ACTIVITY"] = True
        s["SIG_SCHEDULE_E_PRESENT"]   = True

    # ─────────────────────────────────────────────────────────────────────────
    # 15. PRIMARY HOME / SECONDARY HOME / BOAT
    #     ownsHome / ownsPrimaryHome → Augusta Rule on primary residence
    #     ownsSecondaryHome          → Augusta Rule / short-term rental opportunity
    #     ownsBoatOrYacht            → depreciation / charter deduction potential
    # ─────────────────────────────────────────────────────────────────────────
    s["Q_OWNS_PRIMARY_HOME"]   = _to_bool(p.get("ownsHome") or p.get("ownsPrimaryHome"))
    s["Q_OWNS_SECONDARY_HOME"] = _to_bool(p.get("ownsSecondaryHome"))
    s["Q_SECONDARY_HOME_COUNT"] = _to_int(p.get("secondaryHomeCount"))
    s["Q_OWNS_BOAT_OR_YACHT"]  = _to_bool(p.get("ownsBoatOrYacht"))

    # Override Augusta Rule signal if primary or secondary home confirmed
    if s["Q_OWNS_PRIMARY_HOME"] or s["Q_OWNS_SECONDARY_HOME"]:
        s["SIG_SECOND_HOME_USAGE"] = True
        conf = s.get("_signal_confidence") or {}
        conf["SIG_SECOND_HOME_USAGE"] = "FACT"
        s["_signal_confidence"] = conf
    if s["Q_OWNS_SECONDARY_HOME"]:
        s["SIG_SCHEDULE_E_PRESENT"] = True
    # Short-term rental: from questionnaire if present
    q_str = _to_bool(p.get("hasShortTermRental") or p.get("shortTermRental"))
    if q_str:
        s["Q_SHORT_TERM_RENTAL"] = True
        s["SIG_SHORT_TERM_RENTAL"] = True
        conf = s.get("_signal_confidence") or {}
        conf["SIG_SHORT_TERM_RENTAL"] = "FACT"
        s["_signal_confidence"] = conf

    # ─────────────────────────────────────────────────────────────────────────
    # 16. CAPTIVE INSURANCE
    #     workersCompPremiumOver40k → primary feasibility signal
    #     selfInsured → already self-insuring (may strengthen or overlap)
    # ─────────────────────────────────────────────────────────────────────────
    s["Q_WORKERS_COMP_OVER_40K"] = _to_bool(f.get("workersCompPremiumOver40k"))
    s["Q_SELF_INSURED"]          = _to_bool(f.get("selfInsured"))
    s["Q_CAPTIVE_CANDIDATE"]     = (
        s["Q_WORKERS_COMP_OVER_40K"] and s.get("SIG_HIGH_INCOME", False)
    )

    # ─────────────────────────────────────────────────────────────────────────
    # 17. RETIREMENT URGENCY
    #     planningRetirement + retirementAge + DOB → years to retirement
    # ─────────────────────────────────────────────────────────────────────────
    planning_ret   = _to_bool(p.get("planningRetirement"))
    ret_age_target = _to_int(p.get("retirementAge")) or _to_int(f.get("retirementAge"))
    owner_age      = _age_from_dob(dob)

    if owner_age and ret_age_target > 0:
        years_to_ret = max(0, ret_age_target - owner_age)
    else:
        years_to_ret = 10  # neutral default

    s["Q_PLANNING_RETIREMENT"]     = planning_ret
    s["Q_YEARS_TO_RETIREMENT"]     = years_to_ret
    s["Q_RETIREMENT_URGENCY_HIGH"] = planning_ret and years_to_ret <= 7

    # ─────────────────────────────────────────────────────────────────────────
    # 18. NET WORTH / LEGACY
    #     estimatedNetWorthRange → estate planning strategy eligibility
    #     currentSecuritiesInvestments → investment income signals
    # ─────────────────────────────────────────────────────────────────────────
    nw_range = str(f.get("estimatedNetWorthRange", "") or "")
    s["Q_NET_WORTH_OVER_5M"]       = any(r in nw_range for r in
                                         ["$6,","$11,","$16,","$21,","$26,","$31,","$36,"])
    s["Q_NET_WORTH_OVER_10M"]      = any(r in nw_range for r in
                                         ["$11,","$16,","$21,","$26,","$31,","$36,"])
    s["Q_INVESTMENT_PORTFOLIO"]    = _to_float(f.get("currentSecuritiesInvestments"))
    s["Q_HAS_INVESTMENT_PORTFOLIO"] = s["Q_INVESTMENT_PORTFOLIO"] > 0

    # ─────────────────────────────────────────────────────────────────────────
    # 19. LONG-TERM GOALS SIGNAL
    #     longTermFinancialGoals → retirement / real_estate_acquisition /
    #                              legacy_planning / other
    # ─────────────────────────────────────────────────────────────────────────
    goals = str(p.get("longTermFinancialGoals", "") or "").lower()
    s["Q_GOAL_RETIREMENT"]         = "retirement" in goals
    s["Q_GOAL_REAL_ESTATE"]        = "real_estate" in goals
    s["Q_GOAL_LEGACY"]             = "legacy" in goals

    # ─────────────────────────────────────────────────────────────────────────
    # 20. PRACTICE / PROPERTY SALE SIGNAL
    #     practiceSalePlanned → Boolean from questionnaire
    #     Also inferred from longTermFinancialGoals if "sale" or "exit" mentioned
    # ─────────────────────────────────────────────────────────────────────────
    sale_planned = _to_bool(p.get("practiceSalePlanned"))
    sale_in_goals = any(kw in goals for kw in ["sale", "exit", "sell", "transition"])
    s["Q_PRACTICE_SALE_PLANNED"] = sale_planned or sale_in_goals

    # ─────────────────────────────────────────────────────────────────────────
    # 21. REAL ESTATE PROFESSIONAL (CRITICAL FIX)
    #     Required for REP eligibility — NEVER infer from return
    # ─────────────────────────────────────────────────────────────────────────
    rep_hours = _to_float(p.get("realEstateProfessionalHours"))
    other_work_hours = _to_float(p.get("otherWorkHours"))

    s["Q_REP_HOURS"] = rep_hours
    s["Q_OTHER_WORK_HOURS"] = other_work_hours

    s["Q_REP_QUALIFIES"] = (
        rep_hours >= 750 and rep_hours > other_work_hours
    )

    # ─────────────────────────────────────────────────────────────────────────
    # 22. MULTI-ENTITY CONFIRMATION (QUESTIONNAIRE OVERRIDE)
    # ─────────────────────────────────────────────────────────────────────────
    has_multiple_businesses = (
        _to_float(p.get("secondaryBusinessOwnership")) > 0
        or _to_float(p.get("thirdBusinessOwnership")) > 0
    )

    s["Q_HAS_MULTIPLE_ENTITIES"] = has_multiple_businesses

    # Strengthen system signal if confirmed
    if has_multiple_businesses:
        s["SIG_MULTI_ENTITY"] = True

    # ─────────────────────────────────────────────────────────────────────────
    # 23. INVESTMENT VS ACTIVE BUSINESS CLARITY
    # ─────────────────────────────────────────────────────────────────────────
    investment_portfolio = _to_float(f.get("currentSecuritiesInvestments"))
    s["Q_HAS_PASSIVE_INVESTMENTS"] = investment_portfolio > 0

    # ─────────────────────────────────────────────────────────────────────────
    # 24. ENTITY TYPE CONFIRMATION (QUESTIONNAIRE OVERRIDE)
    #     Allows client to confirm entity types even if returns weren't uploaded
    # ─────────────────────────────────────────────────────────────────────────
    has_1120s_q = _to_bool(p.get("has1120S"))
    has_1120_q = _to_bool(p.get("has1120"))
    has_1065_q = _to_bool(p.get("has1065"))

    # Track entity count for multi-entity detection
    entity_count = 0

    if has_1120s_q:
        s["SIG_HAS_S_CORP"] = True
        s["SIG_HAS_S_CORP_VERIFIED"] = True
        s["SIG_BUSINESS_PRESENT"] = True
        entity_count += 1
        # Questionnaire confirmation = FACT confidence; removes 12% _cmult penalty
        _sig_conf = s.setdefault("_signal_confidence", {})
        _sig_conf["SIG_HAS_S_CORP"] = "FACT"
        _sig_conf["SIG_HAS_S_CORP_VERIFIED"] = "FACT"
        _sig_conf["SIG_BUSINESS_PRESENT"] = "FACT"
        
        # Override OBI if officer comp provided
        officer_comp = _to_float(p.get("sCorpOfficerComp"))
        distributions = _to_float(p.get("sCorpDistributions"))
        if officer_comp > 0 or distributions > 0:
            s["_wages"] = max(s.get("_wages", 0), officer_comp)
            s["_distributions"] = max(s.get("_distributions", 0), distributions)
            s["_obi"] = max(s.get("_obi", 0), officer_comp + distributions)
            
            # Check reasonable compensation ratio
            if officer_comp > 0 and (officer_comp + distributions) > 0:
                wage_ratio = officer_comp / (officer_comp + distributions)
                if wage_ratio < 0.4:
                    s["SIG_LOW_OWNER_WAGES"] = True
                    s["SIG_HIGH_DISTRIBUTIONS_VS_WAGES"] = True

    if has_1120_q:
        s["SIG_HAS_C_CORP"] = True
        s["SIG_BUSINESS_PRESENT"] = True
        entity_count += 1
        
        # Override retained earnings if provided
        retained = _to_float(p.get("cCorpRetainedEarningsActual"))
        if retained > 0:
            s["Q_C_CORP_RETAINED_EARNINGS"] = retained

    if has_1065_q:
        s["SIG_HAS_PARTNERSHIP"] = True
        s["SIG_BUSINESS_PRESENT"] = True
        s["SIG_K1_PRESENT"] = True
        entity_count += 1
        # Questionnaire confirmation = FACT confidence; removes 12% _cmult penalty
        _sig_conf = s.setdefault("_signal_confidence", {})
        _sig_conf["SIG_HAS_PARTNERSHIP"] = "FACT"
        _sig_conf["SIG_K1_PRESENT"] = "FACT"
        _sig_conf["SIG_BUSINESS_PRESENT"] = "FACT"
        
        guaranteed = _to_float(p.get("partnershipGuaranteedPayments"))
        if guaranteed > 0:
            s["_guaranteed_payments"] = guaranteed
            s["_obi"] = max(s.get("_obi", 0), guaranteed)

    # Multi-entity detection
    if entity_count >= 2:
        s["SIG_MULTI_ENTITY"] = True

    # ─────────────────────────────────────────────────────────────────────────
    # 25. ATTACHED FORM SIGNALS
    #     Forms 4797 (asset sales), 6252 (installment sales), etc.
    # ─────────────────────────────────────────────────────────────────────────
    has_4797 = _to_bool(p.get("hasForm4797"))
    has_6252 = _to_bool(p.get("hasForm6252"))
    installment_proceeds = _to_float(p.get("installmentSaleProceeds"))
    section_1231_gain = _to_float(p.get("section1231Gain"))

    if has_4797 or section_1231_gain > 0:
        s["SIG_HAS_ASSET_SALES"] = True
        s["_section_1231_gain"] = section_1231_gain

    if has_6252 or installment_proceeds > 0:
        s["SIG_HAS_INSTALLMENT_SALE"] = True
        s["_installment_proceeds"] = installment_proceeds
        # This will help trigger DTTS-006 (installment sales)

    # ─────────────────────────────────────────────────────────────────────────
    # 26. NOL CARRYOVER (for C-Corps)
    # ─────────────────────────────────────────────────────────────────────────
    nol_amount = _to_float(p.get("nolCarryoverAmount"))
    if nol_amount > 0 and (s.get("SIG_HAS_C_CORP", False) or has_1120_q):
        s["Q_NOL_CARRYOVER"] = nol_amount
        s["SIG_NOL_CARRYOVER"] = True

    # ─────────────────────────────────────────────────────────────────────────
    # 27. S-CORP OFFICER COMPENSATION ANALYSIS
    # ─────────────────────────────────────────────────────────────────────────
    if s.get("SIG_HAS_S_CORP", False) or has_1120s_q:
        # If we have both wages and distributions, analyze ratio
        wages = s.get("_wages", 0)
        dist = s.get("_distributions", 0)
        total = wages + dist
        
        if total > 0:
            wage_ratio = wages / total
            if wage_ratio < 0.4:
                s["SIG_LOW_OWNER_WAGES"] = True
                s["SIG_HIGH_DISTRIBUTIONS_VS_WAGES"] = True
                
                # Calculate potential SE tax savings
                se_savings = (dist * 0.153 * 0.9235) * 0.5  # Conservative estimate
                s["Q_SE_TAX_SAVINGS_ESTIMATE"] = se_savings

    # ─────────────────────────────────────────────────────────────────────────
    # FINAL SIGNAL CORRECTIONS (QUESTIONNAIRE > AI)
    # ─────────────────────────────────────────────────────────────────────────
    # Questionnaire always wins over AI
    if s.get("Q_HAS_RENTAL_PROPERTIES"):
        s["SIG_REAL_ESTATE_ASSET"] = True

    if s.get("Q_HAS_MULTIPLE_ENTITIES"):
        s["SIG_MULTI_ENTITY"] = True

    # If we have entity confirmation, ensure business present is True
    if has_1120s_q or has_1120_q or has_1065_q:
        s["SIG_BUSINESS_PRESENT"] = True

    return s


# ═══════════════════════════════════════════════════════════════════════════════
#  RELATED PARTIES LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

# Which form types each related party adds to the strategy set
_RELATED_PARTY_FORM_SIGNALS = {
    "1120S": {
        "SIG_HAS_S_CORP": True,
        "SIG_BUSINESS_PRESENT": True,
    },
    "1120": {
        "SIG_HAS_C_CORP": True,
        "SIG_BUSINESS_PRESENT": True,
    },
    "1065": {
        "SIG_HAS_PARTNERSHIP": True,
        "SIG_BUSINESS_PRESENT": True,
    },
    "1040": {},   # personal return — no additional entity signals
}

def apply_related_parties(signals: dict, related_party_forms: list) -> dict:
    """
    When the user selects related party return types alongside their primary 1040,
    this function adds the entity signals for those forms so the scorer surfaces
    strategies that are only available to that entity type.

    Parameters
    ----------
    signals              : dict from SignalEngine.derive(ret) (already enriched)
    related_party_forms  : list of form type strings e.g. ["1120S", "1065"]

    Returns
    -------
    Signals dict with related-party entity signals activated.

    Example
    -------
        # User uploaded 1040 + selected 1120S as related party
        signals = apply_related_parties(signals, ["1120S"])
        # Now SIG_HAS_S_CORP = True, strategies like S-Corp salary optimisation
        # and PTET election are surfaced even if the 1120S wasn't uploaded
    """
    s = signals.copy()
    entity_form_count = 0
    entity_types_activated = set()
    
    for form in (related_party_forms or []):
        form_key = str(form).upper().strip()
        extra = _RELATED_PARTY_FORM_SIGNALS.get(form_key, {})
        if extra:  # non-empty = it's an entity form (not 1040)
            entity_form_count += 1
            entity_types_activated.add(form_key)
        for sig_key, sig_val in extra.items():
            # Only activate — never deactivate a signal that was already True
            if sig_val is True:
                s[sig_key] = True
                
    # Add entity types activated for reference
    s["Q_RELATED_PARTY_ENTITY_TYPES"] = list(entity_types_activated)
    
    # FIX: when a related-party entity form is added alongside the primary return,
    # the taxpayer now has 2+ entities — set SIG_MULTI_ENTITY accordingly.
    # This unlocks holding company, entity-layering, and mgmt-company strategies.
    if entity_form_count >= 1 and (
        s.get("SIG_HAS_S_CORP") or s.get("SIG_HAS_C_CORP") or s.get("SIG_HAS_PARTNERSHIP")
    ):
        # Primary return already has at least one entity + related party adds another
        primary_entity_count = sum([
            bool(signals.get("SIG_HAS_S_CORP")),
            bool(signals.get("SIG_HAS_C_CORP")),
            bool(signals.get("SIG_HAS_PARTNERSHIP")),
        ])
        if primary_entity_count >= 1 or entity_form_count >= 2:
            s["SIG_MULTI_ENTITY"] = True
            
    return s


# ═══════════════════════════════════════════════════════════════════════════════
#  COMPLETENESS REPORT
# ═══════════════════════════════════════════════════════════════════════════════

def completeness_report(personal: dict, financial: dict) -> dict:
    """
    Shows which critical fields are populated and what accuracy impact
    each missing field has on the savings estimates.

    Returns a dict with:
        answered        : list of filled fields
        unanswered      : list of missing fields with impact labels
        completeness_pct: 0-100
        accuracy_label  : "HIGH" / "MODERATE" / "LOW"
        tier1_complete  : bool — are the top-impact fields all answered?
        schema_gaps     : fields recommended to add to the questionnaire
    """
    p = personal  or {}
    f = financial or {}

    def has(d, k):
        v = d.get(k)
        return v is not None and v != "" and v != 0 and v is not False

    checks = [
        # Tier 1 - Highest impact (must-have)
        (p, "dateOfBirth",                  "Cash balance contribution limit",           1),
        (p, "ownsPracticeBuilding",         "Cost segregation applicability",            1),
        (p, "buildingPurchasePrice",        "Cost seg dollar amount (exact basis)",      1),
        (p, "monthlyMedicalInsurance",      "Health deduction amount",                   1),
        (p, "businessStructure",            "FICA exemption for children",               1),
        (p, "noOfChildren",                 "Hiring children opportunity",               1),
        (p, "plannedEquipmentPurchase",     "Section 179 savings amount",                1),
        
        # Tier 2 - Important for accuracy
        (p, "employeesCount",               "Educational assistance §127 amount",        2),
        (p, "spouseName",                   "Community property determination",          2),
        (p, "hasRentalProperties",          "Rental / Schedule E strategies",            2),
        (p, "planningRetirement",           "Retirement urgency calibration",            2),
        (p, "ownsSecondaryHome",            "Augusta Rule / STR strategies",             2),
        (p, "buildingPlacedInServiceYear",  "Cost seg bonus dep rate (year-specific)",   2),
        (p, "managementCompanyRevenue",     "QBI restructure exact dollar amount",       2),
        (p, "has1120S",                     "S-Corp strategy eligibility",               2),
        (p, "has1120",                      "C-Corp strategy eligibility",               2),
        (p, "has1065",                      "Partnership strategy eligibility",          2),
        (p, "sCorpOfficerComp",             "Reasonable compensation analysis",          2),
        (p, "sCorpDistributions",           "Distribution vs wage analysis",             2),
        (f, "annualPremium",                 "Executive bonus plan savings",              2),
        (f, "hasLifeInsurance",              "Life insurance strategy detection",         2),
        (f, "retirementPlan",                 "Existing retirement plan detection",        2),
        (f, "cCorpRetainedEarnings",          "C-Corp dividends planning amount",          2),
        
        # Tier 3 - Niche strategies
        (f, "estimatedNetWorthRange",        "Estate / legacy strategy eligibility",      3),
        (f, "workersCompPremiumOver40k",     "Captive insurance eligibility",             3),
        (f, "currentSecuritiesInvestments",  "Investment income strategies",              3),
        (p, "hasForm4797",                    "Asset sale strategies",                     3),
        (p, "hasForm6252",                    "Installment sale strategies",               3),
        (p, "installmentSaleProceeds",        "Installment sale savings calc",             3),
        (p, "section1231Gain",                "Section 1231 gain strategies",              3),
        (p, "realEstateProfessionalHours",    "Real estate professional status",          3),
        (p, "practiceSalePlanned",            "Exit planning strategies",                  3),
    ]

    answered   = []
    unanswered = []
    for source, key, impact, tier in checks:
        item = {"field": key, "impact": impact, "tier": tier}
        if has(source, key):
            answered.append(item)
        else:
            unanswered.append(item)

    pct = round(len(answered) / len(checks) * 100)
    tier1_done = all(has(src, k) for src, k, _, t in checks if t == 1)

    schema_gaps = [
        {
            "field":   "hasDSOEquity",
            "schema":  "personalQuestionnaire",
            "type":    "Boolean",
            "impact":  "ISO/AMT planning — currently always $0 without this",
            "example": True,
            "note":    "Only relevant for dentists with DSO equity or practice management stock options",
        },
        {
            "field":   "isoSpreadAmount",
            "schema":  "personalQuestionnaire",
            "type":    "Number",
            "impact":  "ISO/AMT planning dollar amount — show only if hasDSOEquity = true",
            "example": 200_000,
            "note":    "FMV minus exercise price times number of shares",
        },
        {
            "field":   "annualEquipmentLeasePayments",
            "schema":  "personalQuestionnaire",
            "type":    "Number",
            "impact":  "Equipment leasing savings — currently always $0 without this",
            "example": 60_000,
            "note":    "Total annual lease payments for dental equipment",
        },
        {
            "field":   "cCorpRetainedEarningsActual",
            "schema":  "personalQuestionnaire",
            "type":    "Number",
            "impact":  "C-Corp dividend planning — exact retained earnings",
            "example": 500_000,
            "note":    "More accurate than financial questionnaire estimate",
        },
        {
            "field":   "partnershipGuaranteedPayments",
            "schema":  "personalQuestionnaire",
            "type":    "Number",
            "impact":  "Partnership income classification",
            "example": 50_000,
            "note":    "Guaranteed payments affect SE tax and QBI",
        },
        {
            "field":   "nolCarryoverAmount",
            "schema":  "personalQuestionnaire",
            "type":    "Number",
            "impact":  "NOL carryforward strategies",
            "example": 100_000,
            "note":    "Critical for C-Corps with prior losses",
        },
    ]

    return {
        "answered":        answered,
        "unanswered":      unanswered,
        "completeness_pct": pct,
        "tier1_complete":  tier1_done,
        "accuracy_label":  (
            "HIGH — real values used"        if pct >= 70 else
            "MODERATE — mixed real/estimated" if pct >= 40 else
            "LOW — mostly estimates"
        ),
        "schema_gaps": schema_gaps,
    }