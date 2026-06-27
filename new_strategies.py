TAX_YEAR_LIMITS = {
    2024: {
        "defined_contribution_limit":    69_000,   # §415(c)
        "elective_deferral_limit":        23_000,   # §402(g)
        "hsa_family_limit":                8_300,   # §223(b)(2)(B)
        "educational_assistance_limit":    5_250,   # §127(a)(2)
        "qbi_sstb_phaseout_mfj":         383_900,  # §199A(b)(3) MFJ
        "llc_phaseout_mfj":              180_000,  # §25A(d)(2) MFJ start
        "salt_cap":                       10_000,   # §164(b)(6) through 2025
        "child_standard_deduction":       14_600,   # §63(c)(5)
        "sep_contribution_pct":               0.25, # §408(k)(6)
        "catch_up_contribution":           7_500,   # §414(v)(2)(B)(i)
        "gift_tax_annual_exclusion":      18_000,   # §2503(b)
    },
    2025: {
        "defined_contribution_limit":    70_000,   # IRS Rev. Proc. 2024-40
        "elective_deferral_limit":        23_500,
        "hsa_family_limit":                8_550,
        "educational_assistance_limit":    5_250,   # unchanged
        "qbi_sstb_phaseout_mfj":         394_600,
        "llc_phaseout_mfj":              180_000,
        "salt_cap":                       10_000,
        "child_standard_deduction":       15_000,   # estimated CPI adj
        "sep_contribution_pct":               0.25,
        "catch_up_contribution":           7_500,
        "gift_tax_annual_exclusion":      19_000,
    },
}
_LIM = TAX_YEAR_LIMITS.get(2024, TAX_YEAR_LIMITS[2024])

STRATEGY_LIBRARY = [

    {
        "id": "DTTS-002-401-h-plan-add-on-to-db-plan",
        "name": "401(h) Plan Add-on to DB Plan",
        "_id": "69bdb3c6e5397a28d4543e82",
        "irc": "IRC §401(h)",
        "category": "Retirement Plans",
        "overlap_group": "Retirement Plan",
        "applicable_forms": ["1120", "1120S"],  # Corporate tax returns
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_RETIREMENT_PLAN", False) and
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HEALTH_INS_EXPENSE", False)
        ),

        "materiality_fn": lambda s: (
            72 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HAS_RETIREMENT_PLAN") else
            60 if s.get("SIG_HIGH_INCOME") and s.get("SIG_HAS_RETIREMENT_PLAN") else
            55 if s.get("SIG_VERY_HIGH_INCOME") else
            40 if s.get("SIG_HIGH_INCOME") else
            25
        ),

        "fed_savings_fn": lambda s: (
            50_000 * s.get("_fed_marginal_rate", 0)
        ),

        "state_savings_fn": lambda s: (
            50_000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
        ),

        "speed_days": 60,
        "complexity": 35,
        "audit_friction": 10,

        "plain_english": (
            "A §401(h) account is a medical benefit sub-account attached to "
            "an existing defined benefit or cash balance plan. Contributions "
            "are tax-deductible to the employer and grow tax-free, funding "
            "post-retirement medical expenses for the owner and spouse. "
            "The §401(h) account can receive up to 25% of the total DB plan "
            "contributions in any year — on top of regular retirement "
            "contributions. Withdrawals used for qualified medical expenses "
            "are completely tax-free. For a dentist already running a cash "
            "balance plan, adding a §401(h) sub-account via plan amendment "
            "converts future medical costs into a fully deductible, "
            "tax-free benefit."
        ),

        "documentation": [
            "DB or cash balance plan amendment adding §401(h) sub-account",
            "Actuarial certification of §401(h) contribution allocation",
            "Annual contribution records (§401(h) ≤ 25% of total DB contributions)",
            "Post-retirement medical expense records for tax-free withdrawals",
        ],

        "cpa_handoff": [
            "§401(h) requires an existing qualified DB or cash balance plan — add via plan amendment",
            "Contribution limit: §401(h) sub-account ≤ 25% of total DB plan contributions for the year",
            "Benefits must be for medical care (§213(d)) — cannot be general purpose",
            "Tax-free withdrawals: must be used for qualified medical expenses of retiree and spouse",
            "Forfeitures in §401(h) cannot revert to employer — must remain for medical benefits",
            "Coordinate with cash balance plan — add §401(h) to existing plan",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],

    },

    {
        "id": "DTTS-003-s-corp-2-shareholder-health-deduction",
        "name": "S-Corp 2% Shareholder Health Deduction",
        "_id": "69bdb3c7e5397a28d4543e8a",
        "irc": "IRC §162(l), §1372; Notice 2008-1",
        "category": "Entity & Structuring",
        "overlap_group": "Health Insurance Deduction",
        "applicable_forms": ["1120S", "1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_S_CORP_VERIFIED", False) and s.get("SIG_HEALTH_INS_EXPENSE", False)
        ),

        "materiality_fn": lambda s: (
            68 if s.get("SIG_HAS_S_CORP_VERIFIED", False) and s.get("SIG_HEALTH_INS_EXPENSE", False) else 45
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_HEALTH_DEDUCTION_AVAILABLE", 0) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("Q_HEALTH_DEDUCTION_AVAILABLE", 0) * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 5,

        "plain_english": (
            "An S-Corp owner who owns more than 2% of the company cannot "
            "receive health insurance as a tax-free employee fringe benefit. "
            "Instead, the S-Corp pays the premium, includes it in the owner's "
            "W-2 wages, and the owner deducts it above-the-line on Schedule 1 "
            "under §162(l). The net result is the same as a self-employed "
            "health insurance deduction — the premium reduces AGI without "
            "requiring itemization — but only if the procedure is followed "
            "exactly. If the premium is not run through payroll and included "
            "in the W-2, the deduction is lost entirely."
        ),

        "documentation": [
            "Health insurance policy in S-Corp or owner's name",
            "W-2 with health premium included in Box 1 (and noted in Box 14)",
            "S-Corp deduction of premium as compensation expense on Form 1120S",
            "Schedule 1 §162(l) deduction on owner's Form 1040",
        ],

        "cpa_handoff": [
            "Premium must be included in owner's W-2 Box 1 — not excluded as fringe benefit",
            "S-Corp deducts premium as compensation; owner claims §162(l) above-the-line",
            "Policy can be in owner's name or S-Corp's name — either works if W-2 inclusion done",
            "§162(l) deduction limited to net S-Corp W-2 wages (earned income limit)",
            "Family members covered under the policy must also be included correctly in W-2",
            "FICA: premium in W-2 Box 1 but NOT subject to FICA per Notice 2008-1",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-004-maximizing-qbi-via-entity-restructure",
        "name": "Maximizing QBI via Entity Restructure",
        "_id": "69bdb3c8e5397a28d4543e92",
        "irc": "IRC §199A, §199A(b)(2), §199A(b)(3), §199A(d)(2), §199A(d)(3), §199A(e)(4)",
        "category": "Entity & Structuring",
        "overlap_group": "QBI Optimization",
        "applicable_forms": ["1040", "1120S", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_S_CORP_VERIFIED", False) and
            s.get("SIG_MULTI_ENTITY", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("Q_MGMT_CO_REVENUE", 0) > 0  # §199A: only if non-SSTB mgmt co income exists

        ),

        "materiality_fn": lambda s: (
            80 if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("SIG_HAS_S_CORP_VERIFIED", False) else 60
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_QBI_RESTRUCTURE_DEDUCTION", s.get("_obi", 0) * 0.04) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    0
),

        "speed_days": 45,
        "complexity": 35,
        "audit_friction": 15,

        "plain_english": (
            "The §199A QBI deduction gives pass-through business owners up to "
            "a 20% deduction on qualified business income — potentially worth "
            "tens of thousands per year. Dental practices are Specified Service "
            "Trades or Businesses (SSTBs), meaning the deduction phases out "
            "completely above $483,900 of taxable income for married filers "
            "in 2024. Entity restructuring — separating the clinical practice "
            "from a non-clinical management company, real estate entity, or "
            "ancillary service line — can carve out non-SSTB income eligible "
            "for the full QBI deduction without phase-out. Maximizing W-2 "
            "wages paid by the S-Corp also unlocks more of the deduction "
            "within the phase-out range through the W-2 wage limitation test."
        ),

        "documentation": [
            "Form 8995-A with SSTB designation and phase-out calculation",
            "Entity structure diagram showing QBI aggregation elections",
            "W-2 wage documentation per entity",
            "UBIA (unadjusted basis of qualified property) schedule",
            "Aggregation election statement attached to return (annual filing required)",
        ],

        "cpa_handoff": [
            "Dentistry = SSTB — §199A deduction phases out $383,900–$483,900 MFJ (2024)",
            "Below phase-out: full 20% QBI deduction — no W-2 wage test applies",
            "Within phase-out: deduction limited by W-2 wages (50%) or W-2 + UBIA (25% + 2.5%)",
            "Restructure: non-clinical management co income may NOT be SSTB — model separately",
            "Aggregation election: combine entities to maximize W-2 wages — file election annually",
            "Coordinate with multi-entity wage allocation for W-2 optimization",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-005-key-person-insurance-deduction",
        "name": "Key-Person Insurance Deduction",
        "_id": "69bdb3c9e5397a28d4543e9a",
        "irc": "IRC §162, §264(a)(1), §101(a), §101(j)",
        "category": "Insurance & Risk",
        "overlap_group": "Life Insurance Planning",
        "applicable_forms": ["1120", "1120S", "1065"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            (s.get("SIG_HAS_S_CORP_VERIFIED", False) or s.get("SIG_HAS_C_CORP", False)) and
            s.get("SIG_HIGH_INCOME", False)
        ),

        "materiality_fn": lambda s: (
            55 if s.get("SIG_HIGH_INCOME", False) and s.get("SIG_HAS_S_CORP_VERIFIED", False) else 35
        ),

        "fed_savings_fn": lambda s: (
            8_000 * s.get("_fed_marginal_rate", 0)
        ),

        "state_savings_fn": lambda s: (
            8_000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
        ),

        "speed_days": 30,
        "complexity": 20,
        "audit_friction": 15,

        "plain_english": (
            "Key-person insurance protects the business if its most critical "
            "person — typically the owner-dentist — dies or becomes disabled. "
            "The tax treatment depends entirely on the type of policy: premiums "
            "on key-person term life insurance are NOT deductible under §264, "
            "and the death benefit is tax-free. Key-person disability insurance "
            "premiums ARE deductible to the business, but any disability benefits "
            "received are then taxable as ordinary income. The owner can choose "
            "to forgo the premium deduction and receive disability benefits "
            "tax-free instead. For C-Corps holding life insurance on employees, "
            "the §101(j) COLI notice and consent must be executed annually."
        ),

        "documentation": [
            "Insurance policy with business as owner and beneficiary",
            "§264 analysis confirming deductibility (disability) vs. non-deductibility (life)",
            "§101(j) COLI notice and consent (if C-Corp life insurance policy)",
            "Premium payment records and Form 1120/1120S deduction support",
        ],

        "cpa_handoff": [
            "Key-person LIFE premiums: NOT deductible §264(a)(1); death benefit tax-free §101(a)",
            "Key-person DISABILITY premiums: deductible §162; benefits taxable when received",
            "Alternative: forgo disability premium deduction → benefits received tax-free",
            "Business must be owner AND beneficiary — personal benefit taints deductibility",
            "C-Corp COLI: §101(j) COLI notice and consent required annually; AMT implications",
            "Distinguish from buy-sell insurance — different ownership/purpose structure",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires policy design, underwriting/actuarial review, and compliance documentation before implementation.",
        ],

    },

    {
        "id": "DTTS-006-installment-sales-to-defer-capital-gains",
        "name": "Installment Sales to Defer Capital Gains",
        "_id": "69bdb3c9e5397a28d4543ea8",
        "irc": "IRC §453, §453(i), §453A, §453B",
        "category": "Exit & Sale",
        "overlap_group": "Practice Sale Exit",
        "applicable_forms": ["1040", "1120", "1120S", "1065"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("Q_PRACTICE_SALE_PLANNED", False) and
            (s.get("SIG_HAS_S_CORP_VERIFIED", False) or s.get("SIG_HAS_C_CORP", False) or
             s.get("SIG_REAL_ESTATE_ASSET", False))
        ),

        "materiality_fn": lambda s: (
            80 if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("SIG_REAL_ESTATE_ASSET", False) else 65
        ),

        "fed_savings_fn": lambda s: (
            38_080 * 3.10
        ),

        "state_savings_fn": lambda s: (
            800_000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0) * 0.20
        ),

        "speed_days": 60,
        "complexity": 25,
        "audit_friction": 15,

        "plain_english": (
            "An installment sale spreads the recognition of capital gains "
            "over multiple years as payments are received — instead of paying "
            "tax on the full gain in the year of sale. For a dental practice "
            "sold for $1 million, spreading gain over 5 years keeps each "
            "year's income lower, potentially avoiding the 3.8% Net Investment "
            "Income Tax and keeping the taxpayer in a lower bracket. Important: "
            "§1245 depreciation recapture is recognized fully in the year of "
            "sale regardless of the installment method — only the capital gain "
            "portion is deferred. The interest on the installment note is also "
            "taxable as ordinary income each year."
        ),

        "documentation": [
            "Installment sale agreement with stated interest rate (≥ AFR)",
            "Form 6252 (Installment Sale Income) filed annually until fully paid",
            "Gross profit percentage calculation and basis documentation",
            "§453A interest charge analysis if deferred gain > $5M",
            "Asset allocation agreement (Form 8594) coordinated with buyer",
        ],

        "cpa_handoff": [
            "Gross profit % = (selling price − adjusted basis) / selling price",
            "Each payment: gross profit % × principal received = gain recognized that year",
            "§1245 recapture: recognized in FULL in year of sale — not deferred",
            "Interest on note: must be ≥ AFR — taxable as ordinary income each year",
            "§453A: interest charge applies on deferred gain > $5M — model for DSO deals",
            "Coordinate with asset allocation — installment + allocation strategy combined",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-007-c-corp-dividends-planning",
        "name": "C-Corp Dividends Planning",
        "_id": "69bdb3cae5397a28d4543ebf",
        "irc": "IRC §§301–316, §1(h)(11), §11, §531",
        "category": "Entity & Structuring",
        "overlap_group": "C-Corp Planning",
        "applicable_forms": ["1120", "1040"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_C_CORP", False) and
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False)
        ),

        "materiality_fn": lambda s: (
            65 if s.get("SIG_HAS_C_CORP", False) and s.get("SIG_VERY_HIGH_INCOME", False) else 40
        ),

        "fed_savings_fn": lambda s: (
            200_000 * max(0, s.get("_fed_marginal_rate", 0) - 0.21) * 0.30
        ),

        "state_savings_fn": lambda s: (
            200_000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0) * 0.20
        ),

        "speed_days": 45,
        "complexity": 30,
        "audit_friction": 15,

        "plain_english": (
            "A C-Corporation pays a flat 21% federal income tax rate on its "
            "earnings. When those earnings are distributed to shareholders "
            "as qualified dividends, they are taxed at the preferential 20% "
            "capital gains rate — plus 3.8% NIIT for high earners. The "
            "combined effective rate is often comparable to S-Corp pass-through "
            "rates at top brackets. The real advantage is the C-Corp's ability "
            "to retain earnings at 21% and redeploy them inside the entity — "
            "buying equipment, funding benefits, or accumulating for a future "
            "sale — before any shareholder-level tax is triggered. This "
            "deferral creates compounding value over time. Excessive "
            "accumulation beyond reasonable business needs risks the §531 "
            "accumulated earnings tax at 20%."
        ),

        "documentation": [
            "C-Corp board resolution declaring dividend",
            "Form 1099-DIV issued to shareholders",
            "Earnings and profits (E&P) calculation and tracking",
            "Qualified dividend holding period confirmation (>60 days)",
            "§531 accumulated earnings tax analysis if retained earnings exceed reasonable needs",
        ],

        "cpa_handoff": [
            "Qualified dividend rate: 0% / 15% / 20% based on shareholder taxable income",
            "Combined effective rate: 21% corp + 23.8% QDI (with NIIT) ≈ 40.8% — model vs. S-Corp",
            "C-Corp value: retain earnings at 21%, deploy fringe benefits before distribution",
            "§531 accumulated earnings tax: 20% penalty if retained beyond reasonable business needs",
            "E&P tracking: distributions from E&P first (dividend), then return of capital (§301)",
            "Coordinate with management company for C-Corp fringe benefit deployment",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-008-ic-disc-export-income-deduction",
        "name": "IC-DISC Export Income Deduction",
        "_id": "69bdb3cbe5397a28d4543ed0",
        "irc": "IRC §§991–997",
        "category": "General Planning",
        "overlap_group": None,
        "applicable_forms": ["1120", "1040"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and s.get("SIG_HAS_C_CORP", False)
        ),

        "materiality_fn": lambda s: (
            20
        ),

        "fed_savings_fn": lambda s: (
            0
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 90,
        "complexity": 50,
        "audit_friction": 25,

        "plain_english": (
            "An IC-DISC converts ordinary business income from export sales "
            "into qualified dividend income taxed at the preferential 20% rate. "
            "The operating company pays a commission to the IC-DISC — deductible "
            "at ordinary rates — and the IC-DISC distributes it as a qualified "
            "dividend to the shareholder at 20%. The rate arbitrage between "
            "37% ordinary income and 20% qualified dividends is the savings. "
            "For dental practices, this strategy requires meaningful export "
            "revenue — dental products, training, or intellectual property "
            "licensed internationally. Most dental practices will not qualify. "
            "Flag for questionnaire confirmation before recommending."
        ),

        "documentation": [
            "IC-DISC incorporation documents (separate C-Corp required)",
            "Form 1120-IC-DISC filed annually",
            "Export revenue documentation (qualified export receipts)",
            "Commission agreement between operating company and IC-DISC",
            "Shareholder interest charge calculation on deemed distributions",
        ],

        "cpa_handoff": [
            "⚠️ Dental practices rarely have export revenue — confirm before recommending",
            "IC-DISC must be a separately incorporated C-Corp with at least $2,500 capital",
            "Commission: lesser of 4% of qualified export receipts or 50% of export net income",
            "IC-DISC distributes to shareholder as qualified dividend — taxed at 20%",
            "Interest charge: shareholder pays annual interest on deemed IC-DISC distributions",
            "No export revenue = no IC-DISC benefit — low priority for typical dental practice",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires qualified export receipts — dental product sales, IP licensing, or training internationally.",
        ],

    },

    {
        "id": "DTTS-009-100-meals-deduction-for-company-parties",
        "name": "100% Meals Deduction for Company Parties",
        "_id": "69bdb3cce5397a28d4543ed8",
        "irc": "IRC §162, §274(e)(4), §274(n)(2)(B)",
        "category": "General Planning",
        "overlap_group": None,
        "applicable_forms": ["1040", "1120", "1120S", "1065"],
        "phase_1_eligible": True,
        "estimate_confidence": "MODERATE",

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            (s.get("SIG_HAS_S_CORP_VERIFIED", False) or s.get("SIG_HAS_C_CORP", False) or
             s.get("SIG_SCHEDULE_C_PRESENT", False))
        ),

        "materiality_fn": lambda s: (
        60 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        45 if s.get("SIG_HIGH_INCOME") else
        30
    ),

        "fed_savings_fn": lambda s: (
    s.get("_obi", 0) * 0.005 * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("_obi", 0) * 0.005 * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 7,
        "complexity": 5,
        "audit_friction": 5,

        "plain_english": (
            "Most business meals are only 50% deductible after the 2018 tax "
            "law changes. But there is an important exception: recreational "
            "and social activities primarily for the benefit of all employees — "
            "like a holiday party, summer picnic, or team lunch open to every "
            "staff member — are 100% deductible. The key requirements are "
            "that the event must be open to all employees (not just the owner "
            "or executives) and must be a social/recreational event rather "
            "than a working business meal. A dental office holiday party with "
            "food, beverages, and entertainment for the entire team qualifies "
            "for the full deduction."
        ),

        "documentation": [
            "Event receipts (caterer, venue, food and beverage invoices)",
            "Guest list confirming all employees invited and attended",
            "Business purpose notation confirming social/recreational nature",
            "Distinction from client entertainment (which is fully disallowed)",
        ],

        "cpa_handoff": [
            "§274(e)(4): company party 100% deductible if open to ALL employees — not just executives",
            "§274(n)(2)(B): de minimis meals 100% deductible — coffee, occasional snacks for office",
            "Client entertainment: fully disallowed post-TCJA §274(a) — do not mix with employee events",
            "Holiday party: document guest list proving all employees invited",
            "Working meals with business purpose: 50% deductible — separate from company parties",
            "State conformity: most states conform to federal meal deduction rules",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-010-buy-sell-stock-redemption-with-life-insurance",
        "name": "Buy-Sell Stock Redemption with Life Insurance",
        "_id": "69bdb3cce5397a28d4543ee0",
        "irc": "IRC §101(a), §302, §302(b)(3), §303, §264(a)(1)",
        "category": "Insurance & Risk",
        "overlap_group": "Life Insurance Planning",
        "applicable_forms": ["1120", "1120S"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            (s.get("SIG_HAS_S_CORP_VERIFIED", False) or s.get("SIG_HAS_C_CORP", False)) and
            s.get("SIG_HIGH_INCOME", False) and
            (s.get("SIG_MULTI_ENTITY", False) or s.get("SIG_HAS_PARTNERSHIP", False))
        ),

        "materiality_fn": lambda s: (
            60 if s.get("SIG_HAS_S_CORP_VERIFIED", False) and s.get("SIG_HIGH_INCOME", False) else 40
        ),

        "fed_savings_fn": lambda s: (
            100_000 * 0.238 * 0.30  # probability-weighted future capital gain avoided
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 60,
        "complexity": 35,
        "audit_friction": 10,

        "plain_english": (
            "A buy-sell agreement funded with life insurance ensures that if "
            "one owner dies, the remaining owners can buy out the deceased "
            "owner's share at a pre-agreed price — without a fire sale or "
            "forced partnership with the deceased's heirs. In an entity "
            "redemption structure, the business owns and is beneficiary of "
            "the life insurance, receives the tax-free death benefit, and "
            "redeems the deceased's stock. In a cross-purchase structure, "
            "each owner individually owns policies on the other owners — "
            "this gives the surviving owner a stepped-up basis in the "
            "acquired interest, which reduces future capital gain on eventual "
            "sale. Premiums are not deductible in either structure."
        ),

        "documentation": [
            "Buy-sell agreement (entity redemption or cross-purchase)",
            "Life insurance policies with correct ownership and beneficiary designations",
            "Practice valuation supporting insurance coverage amount",
            "§101(j) COLI notice and consent (if C-Corp holds policy on employee-owner)",
            "Annual review of policy values vs. current practice FMV",
        ],

        "cpa_handoff": [
            "Premiums NOT deductible under §264(a)(1) in either redemption or cross-purchase",
            "Death benefit: tax-free to business/surviving owner under §101(a)",
            "Entity redemption: surviving owner's basis NOT stepped up — future gain larger",
            "Cross-purchase: surviving owner gets stepped-up basis in purchased interest",
            "S-Corp with 3+ owners: entity redemption preferred (fewer policies); basis trap applies",
            "C-Corp entity redemption: §101(j) COLI notice required; AMT exposure on cash value",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires policy design, underwriting/actuarial review, and compliance documentation before implementation.",
        ],

    },

    {
        "id": "DTTS-011-double-up-401-k-contributions-for-spouses",
        "name": "Double-Up 401(k) Contributions for Spouses",
        "_id": "69bdb3cde5397a28d4543ee9",
        "irc": "IRC §401(k), §415, §402(g)",
        "category": "Retirement Plans",
        "overlap_group": "Retirement Plan",
        "applicable_forms": ["1120S", "1120", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_RETIREMENT_PLAN", False) and
            (s.get("SIG_HAS_S_CORP_VERIFIED", False) or s.get("SIG_HAS_C_CORP", False)) and
            s.get("SIG_HIGH_INCOME", False)
        ),

        "materiality_fn": lambda s: (
            72 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HAS_RETIREMENT_PLAN") else
            60 if s.get("SIG_HIGH_INCOME") else
            40
        ),

        "fed_savings_fn": lambda s: (
            69_000 * s.get("_fed_marginal_rate", 0)
        ),

        "state_savings_fn": lambda s: (
            69_000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
        ),

        "speed_days": 21,
        "complexity": 20,
        "audit_friction": 15,

        "plain_english": (
            "If your spouse performs real work for the dental practice and "
            "receives a W-2, they can participate in the 401(k) plan as a "
            "regular employee. This means the practice can contribute up to "
            "$69,000 to the spouse's 401(k) account in 2024 — on top of "
            "the owner's own contributions. A couple running a dental practice "
            "together can shelter up to $138,000 per year in combined "
            "retirement contributions. The spouse's role must be genuine "
            "with reasonable compensation for actual services — a paper "
            "arrangement without real work will not withstand IRS scrutiny."
        ),

        "documentation": [
            "Spouse job description and employment agreement",
            "Spouse W-2 reflecting reasonable compensation for actual services",
            "Time records or work documentation for spouse's role",
            "401(k) plan document confirming spouse's eligibility",
            "Contribution records for spouse's deferrals and employer contributions",
        ],

        "cpa_handoff": [
            "Spouse must have bona fide W-2 employment with reasonable compensation",
            "Spouse deferral limit: $23,000 (2024); $30,500 if spouse is age 50+",
            "Total §415 limit per person: $69,000 — applies separately to each participant",
            "Employer profit sharing to spouse: deductible under §404 to the practice",
            "ADP test: spouse participation as NHCE may affect plan nondiscrimination testing",
            "Coordinate with cash balance combo — spouse may also participate in CB plan",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
            "Requires related-party role, compensation, and documentation review before implementation.",
        ],

    },

    {
        "id": "DTTS-012-401k",
        "name": "Solo 401(k) / Traditional 401(k) + Profit Sharing",
        "_id": "69bdb3cee5397a28d4543ef6",
        "irc": "IRC §402(g), §415",
        "category": "Retirement & Benefits",
        "overlap_group": "Retirement Plan",
        "applicable_forms": ["1040", "1120S", "1120"],
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",

        "eligibility_logic": lambda s: (
            s.get("SIG_NO_RETIREMENT_PLAN", False) or s.get("SIG_RETIREMENT_UNDERFUNDED", False)
        ),

        "materiality_fn": lambda s: (
            100 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_NO_RETIREMENT_PLAN") else
            80  if s.get("SIG_HIGH_INCOME") and s.get("SIG_NO_RETIREMENT_PLAN") else
            70  if s.get("SIG_NO_RETIREMENT_PLAN") else
            65  if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_RETIREMENT_UNDERFUNDED") else
            55  if s.get("SIG_HIGH_INCOME") else
            40
        ),

        "fed_savings_fn": lambda s: (
            min(
                min(_LIM["elective_deferral_limit"], s.get("Q_CASH_BALANCE_INCREMENTAL", min(_LIM["elective_deferral_limit"], s.get("_wages", 0) * 0.25 if s.get("_wages", 0) > 0 else 5_000))),
                s.get("_max_retirement_at_current_w2", 69_000)
            ) * s.get("_fed_marginal_rate", 0)
        ),

        "state_savings_fn": lambda s: (
            min(_LIM["defined_contribution_limit"], max(s.get("_obi", 0), s.get("_wages", 0)) * 0.25) *
            (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
        ),

        "speed_days": 30,
        "complexity": 15,
        "audit_friction": 5,

        "plain_english": (
            "A 401(k) with profit sharing allows business owners to make large "
            "tax-deductible retirement contributions."
        ),

        "documentation": [
            "Plan adoption agreement",
            "Contribution calculations",
            "IRS Form 5500-EZ if required"
        ],

        "cpa_handoff": [
            "Establish retirement plan",
            "Calculate maximum deductible contribution"
        ],

        "prerequisites": [],
    },

    {
        "id": "DTTS-013-grantor-retained-income-trust-grit",
        "name": "Grantor Retained Income Trust (GRIT)",
        "_id": "69bdb3cfe5397a28d4543f03",
        "irc": "IRC §2702, §2702(a)(2), §2036, §2501; Treas. Reg. §25.2702-1",
        "category": "Trusts & Estate",
        "overlap_group": "Grantor Trust Planning",
        "applicable_forms": ["1041", "709"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_DEPENDENTS_PRESENT", False) and
            s.get("_agi", 0) > 1_000_000
        ),

        "materiality_fn": lambda s: (
            55 if s.get("_agi", 0) > 1_500_000 else 35
        ),

        "fed_savings_fn": lambda s: (
            1_000_000 * 0.20 * 0.40 * 0.40
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 120,
        "complexity": 65,
        "audit_friction": 15,

        "plain_english": (
            "A Grantor Retained Income Trust (GRIT) allows a grantor to "
            "transfer assets into a trust while retaining the right to income "
            "from the trust for a set number of years. At the end of the term, "
            "the remaining assets pass to the beneficiaries at a reduced "
            "gift tax cost — because the value of the retained income stream "
            "reduces the taxable gift. However, the 1990 tax law changes "
            "largely eliminated the GRIT for transfers to family members — "
            "the retained income interest is valued at zero for gift tax "
            "purposes when family members are the remaindermen. For transfers "
            "to non-family beneficiaries (charities, non-family individuals), "
            "the GRIT still functions as designed. For family transfers, "
            "the modern GRAT (Grantor Retained Annuity Trust) is generally "
            "preferred and more favorable."
        ),

        "documentation": [
            "GRIT trust document (estate planning attorney required)",
            "Asset transfer and funding documentation",
            "Gift tax return (Form 709) reporting taxable gift to remainder beneficiaries",
            "§7520 rate documentation at date of funding",
            "Actuarial calculation of retained income interest value",
        ],

        "cpa_handoff": [
            "§2702: GRIT with FAMILY beneficiaries — retained interest valued at ZERO, full FMV = gift",
            "GRIT with NON-FAMILY beneficiaries: §2702 does not apply; retained interest has value",
            "Modern alternative for family: GRAT (qualified interest under §2702(b))",
            "§2036 risk: if grantor retains too much control, assets pulled back into estate at death",
            "File Form 709 (Gift Tax Return) to report the discounted gift at funding",
            "Estate planning attorney required — do not implement without qualified counsel",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],

    },

    {
        "id": "DTTS-014-in-kind-roth-conversion-of-appreciated-assets",
        "name": "In-Kind Roth Conversion of Appreciated Assets",
        "_id": "69bdb3d0e5397a28d4543f0c",
        "irc": "IRC §402A, §408A, §408A(d)(3), §72",
        "category": "Retirement Plans",
        "overlap_group": "Roth Conversion Strategy",
        "applicable_forms": ["1040"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_RETIREMENT_PLAN", False) and
            s.get("SIG_HIGH_INCOME", False)
        ),

        "materiality_fn": lambda s: (
            68 if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("SIG_HAS_RETIREMENT_PLAN", False) else 50
        ),

        "fed_savings_fn": lambda s: (
            100_000 * 0.07 * s.get("_fed_marginal_rate", 0) * 0.20
        ),

        "state_savings_fn": lambda s: (
            100_000 * 0.07
            * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
            * 0.20
        ),

        "speed_days": 14,
        "complexity": 20,
        "audit_friction": 5,

        "plain_english": (
            "A Roth conversion moves money from a traditional IRA to a Roth "
            "IRA — you pay tax now on the converted amount, but all future "
            "growth is tax-free and there are no required minimum distributions "
            "during your lifetime. An in-kind conversion means transferring "
            "the actual investments rather than selling first — particularly "
            "valuable when assets are temporarily down in value, since you "
            "pay tax on the lower current value and capture all future "
            "recovery tax-free inside the Roth. The best time to convert is "
            "in a low-income year — a practice transition year, a year with "
            "a large depreciation deduction, or before RMDs begin."
        ),

        "documentation": [
            "IRA custodian conversion instructions (in-kind transfer request)",
            "FMV documentation for converted assets on conversion date",
            "Form 1099-R from custodian reporting the conversion",
            "Form 8606 tracking basis in traditional IRA (if any non-deductible contributions)",
            "Income projection confirming current-year tax rate vs. projected future rate",
        ],

        "cpa_handoff": [
            "Taxable amount = FMV of assets on conversion date — same as if sold and converted",
            "In-kind benefit: convert at depressed FMV → lower tax → all recovery grows tax-free",
            "Best timing: low-income year — practice transition, large deduction year, pre-RMD",
            "§72(t): 10% penalty if under age 59½ and funds not in Roth for 5 years",
            "SECURE 2.0: Roth IRA has no RMD during owner's lifetime — powerful for estate planning",
            "Pro-rata rule: if pre-tax IRA exists, conversion is pro-rated — model carefully",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],

    },

    {
        "id": "DTTS-015-pre-ipo-stock-options-amt-planning",
        "name": "Pre-IPO Stock Options & AMT Planning",
        "_id": "69bdb3d0e5397a28d4543f15",
        "irc": "IRC §422, §422(b), §56(b)(3), §55, §53",
        "category": "Exit & Sale",
        "overlap_group": None,
        "applicable_forms": ["1040", "1120"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("SIG_HAS_C_CORP", False)
        ),

        "materiality_fn": lambda s: (
            55 if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("SIG_HAS_C_CORP", False) else 30
        ),

        "fed_savings_fn": lambda s: (
            200_000 * (0.28 - 0.20) * 0.40  # probability-weighted
        ),

        "state_savings_fn": lambda s: (
            200_000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0) * 0.20
        ),

        "speed_days": 30,
        "complexity": 40,
        "audit_friction": 15,

        "plain_english": (
            "Incentive Stock Options (ISOs) receive special tax treatment — "
            "no regular income tax when you exercise them. The catch is the "
            "Alternative Minimum Tax: the difference between the option's "
            "fair market value and your exercise price counts as an AMT "
            "preference item, potentially triggering AMT even though no "
            "regular tax is owed. The planning strategy is to exercise ISOs "
            "in calculated tranches — enough each year to stay below the AMT "
            "trigger point. AMT paid in prior years creates a credit that "
            "reduces future regular tax when you eventually sell the shares "
            "and your tax situation normalizes."
        ),

        "documentation": [
            "ISO grant agreements with exercise price and vesting schedule",
            "FMV documentation at date of exercise (409A valuation or trading price)",
            "Form 3921 (Exercise of Incentive Stock Option)",
            "Form 6251 (AMT calculation) for exercise year",
            "AMT credit carryforward schedule (Form 8801)",
        ],

        "cpa_handoff": [
            "ISO exercise: no regular income tax; BUT spread is AMT preference item (§56(b)(3))",
            "AMT rate: 28% on AMTI above exemption — model vs. regular tax at each exercise level",
            "Exercise in tranches: stay below AMT trigger — model optimal exercise amount annually",
            "Disqualifying disposition: if stock drops post-exercise, DQ disposition limits AMT damage",
            "§53 AMT credit: AMT paid is recoverable in future years when regular tax > TMT",
            "Dental context: relevant for DSO equity, practice management company options",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-016-cost-segregation",
        "name": "Cost Segregation",
        "_id": "69bdb3d1e5397a28d4543f23",
        "irc": "IRC §§167, 168, §168(k); Rev. Proc. 87-56; IRS Cost Segregation ATG",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Depreciation — Cost Segregation",
        "applicable_forms": ["1040", "1120", "1120S", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            (
                s.get("Q_OWNS_BUILDING", False) or s.get("SIG_REAL_ESTATE_ASSET", False)
            ) and
            (s.get("SIG_HAS_DEPRECIATION", False) or s.get("SIG_LOW_DEPRECIATION", False)) and
            s.get("Q_COST_SEG_INCREMENTAL_DEDUCTION", 0) > 0  # §168: must own depreciable property
        ),

        "materiality_fn": lambda s: (
            88 if s.get("SIG_REAL_ESTATE_ASSET", False) and s.get("SIG_LOW_DEPRECIATION", False) else 72
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_COST_SEG_INCREMENTAL_DEDUCTION", 0) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("Q_COST_SEG_INCREMENTAL_DEDUCTION", 0) * s.get("Q_STATE_MARGINAL_RATE", 0.05) * 0.80
),

        "speed_days": 45,
        "complexity": 35,
        "audit_friction": 20,

        "plain_english": (
            "Cost segregation is an engineering study that breaks down a "
            "building into its component parts and reclassifies them from "
            "39-year straight-line depreciation into shorter-lived categories "
            "of 5, 7, or 15 years. A dental office built or purchased for "
            "$1 million might have $300,000 in components — specialized "
            "plumbing, electrical for equipment, dental cabinetry, flooring, "
            "and parking lot — that qualify for accelerated depreciation or "
            "bonus depreciation. Instead of deducting $25,000 per year for "
            "39 years, those components generate hundreds of thousands in "
            "deductions in the first few years. For existing buildings, a "
            "lookback study captures all missed depreciation in a single "
            "catch-up deduction without amending prior returns."
        ),

        "documentation": [
            "Cost segregation study report (qualified engineer or CPA specialist)",
            "Property closing documents and original cost basis",
            "Form 4562 reflecting reclassified depreciation schedules",
            "Form 3115 (Change in Accounting Method) for lookback / catch-up",
            "Bonus depreciation calculation for reclassified 5-yr and 15-yr components",
        ],

        "cpa_handoff": [
            "Cost seg reclassifies 39-yr building components to 5-yr, 7-yr, and 15-yr property",
            "5-yr property: dental-specific fixtures, special-purpose electrical/plumbing, cabinetry",
            "15-yr property: parking lot, sidewalks, landscaping — also eligible for bonus depreciation",
            "Bonus depreciation: 60% in 2024 on reclassified 5-yr and 15-yr components",
            "Lookback: Rev. Proc. 2011-14 + Form 3115 — catch-up all prior years in current year",
            "Passive activity: if rental property, passive loss limitations (§469) may apply",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],

    },

    {
        "id": "DTTS-017-health-savings-account-hsa-optimization",
        "name": "Health Savings Account (HSA) Optimization",
        "_id": "69bdb3d2e5397a28d4543f30",
        "irc": "IRC §223, §223(b), §223(c)(1), §223(f)(1), §223(f)(4), §106(d)",
        "category": "General Planning",
        "overlap_group": "Health Savings Account (HSA)",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HEALTH_INS_EXPENSE", False) and
            (s.get("SIG_HIGH_INCOME", False) or s.get("SIG_VERY_HIGH_INCOME", False))
        ),

        "materiality_fn": lambda s: (
            75 if s.get("SIG_VERY_HIGH_INCOME", False) else 62
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_HEALTH_PREMIUM", 0) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("Q_HEALTH_PREMIUM", 0) * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 5,

        "plain_english": (
            "A Health Savings Account is the only savings vehicle in the tax "
            "code with a triple tax advantage: contributions are deductible, "
            "growth is tax-free, and withdrawals for medical expenses are "
            "tax-free. The optimization strategy is to invest your HSA in "
            "low-cost index funds rather than leaving it in a cash sweep, "
            "pay current medical expenses out-of-pocket, and save every "
            "receipt — there is no deadline to reimburse yourself. Years "
            "later, you can take a completely tax-free distribution by "
            "submitting those old receipts. After age 65, you can withdraw "
            "for any purpose at ordinary income rates, making the HSA "
            "function like a second traditional IRA."
        ),

        "documentation": [
            "HDHP enrollment confirmation (required for HSA eligibility)",
            "HSA contribution records and Form 8889",
            "Investment elections confirming HSA invested (not cash sweep)",
            "Medical expense receipt file — date, amount, provider (no submission deadline)",
            "Employer HSA contribution records (§106(d) exclusion from FICA)",
        ],

        "cpa_handoff": [
            "Confirm HDHP enrollment: min deductible $1,600 self / $3,200 family (2024)",
            "Max contribution: $4,150 self-only / $8,300 family + $1,000 catch-up if 55+",
            "Invest HSA — do not spend on current expenses; accumulate receipts instead",
            "No deadline on reimbursement: receipts from any prior year can be submitted later",
            "CA and NJ: no state HSA conformity — track separately for state tax purposes",
            "Age 65+: non-medical withdrawals taxed as ordinary income (no 20% penalty)",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-018-hiring-spouse-in-the-business",
        "name": "Hiring Spouse in the Business",
        "_id": "69bdb3d3e5397a28d4543f37",
        "irc": "IRC §162, §3121(b)(3), §3306(c)(5), §401(k), §106",
        "category": "General Planning",
        "overlap_group": "Family Employment",
        "applicable_forms": ["1040", "1120S", "1120", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("_filing_status", "S") in ("MFJ", "MARRIED FILING JOINTLY", "MFS", "MARRIED FILING SEPARATELY") and
            (
                s.get("Q_COMMUNITY_PROPERTY_APPLICABLE", False) or  # confirmed married + in business
                (s.get("_wages", 0) > 0 and s.get("SIG_HIGH_INCOME", False))          # has wages, could hire spouse
            )
        ),

        "materiality_fn": lambda s: (
            65 if s.get("SIG_HIGH_INCOME", False) and s.get("SIG_HAS_S_CORP_VERIFIED", False) else 50
        ),

        "fed_savings_fn": lambda s: (
    min(s.get("_wages", 0) * 0.30, 60_000) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    min(s.get("_wages", 0) * 0.30, 60_000) * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 21,
        "complexity": 15,
        "audit_friction": 20,

        "plain_english": (
            "If your spouse performs real work for the dental practice — "
            "managing the schedule, handling billing, running the front desk, "
            "or providing administrative support — they should be on the "
            "payroll as a W-2 employee. This creates multiple tax benefits: "
            "their wages are deductible to the business, they can participate "
            "in the 401(k) and profit sharing plans with their own contribution "
            "limits, and the practice can provide health insurance and other "
            "benefits at full deductibility. The spouse's role must be genuine "
            "with documented services and reasonable compensation — the IRS "
            "scrutinizes spousal employment arrangements carefully."
        ),

        "documentation": [
            "Spouse employment agreement with job description and hourly rate",
            "Time records documenting actual hours and services performed",
            "Spouse W-2 reflecting reasonable compensation",
            "Form 941 confirming payroll tax compliance",
            "401(k) and benefit enrollment records for spouse",
        ],

        "cpa_handoff": [
            "Spouse must perform bona fide services — document role, hours, and duties",
            "Compensation must be reasonable for the work performed — benchmark to market rates",
            "Full payroll required: W-2, Form 941, FICA withholding on spouse wages",
            "FUTA: sole proprietor pays no FUTA on spouse wages; S-Corp/C-Corp DOES pay FUTA",
            "Retirement: spouse participates in 401(k) / profit sharing under own §415 limit",
            "Health insurance: employer contribution to spouse deductible under §106 as employee",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires related-party role, compensation, and documentation review before implementation.",
        ],

    },

    {
        "id": "DTTS-019-deduction-bunching-with-donor-advised-fund",
        "name": "Deduction Bunching with Donor-Advised Fund",
        "_id": "69bdb3d4e5397a28d4543f3f",
        "irc": "IRC §170, §170(b)(1)(A), §170(b)(1)(C), §170(f)(8), §63(c)",
        "category": "General Planning",
        "overlap_group": "Charitable Giving",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HIGH_INCOME", False) or s.get("SIG_VERY_HIGH_INCOME", False)
        ),

        "materiality_fn": lambda s: (
            62 if s.get("SIG_VERY_HIGH_INCOME", False) else 48
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.08 * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.08 * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 7,
        "complexity": 10,
        "audit_friction": 5,

        "plain_english": (
            "The standard deduction ($29,200 for married couples in 2024) "
            "means that smaller annual charitable contributions produce no "
            "additional tax benefit — you take the standard deduction anyway. "
            "The bunching strategy concentrates two or three years of planned "
            "giving into a single year, pushing your itemized deductions well "
            "above the standard deduction threshold. A Donor-Advised Fund "
            "makes this practical: you get the full tax deduction in the "
            "bunching year, but distribute grants to your chosen charities "
            "over time at your own pace. Contributing appreciated stock "
            "instead of cash is even more powerful — you avoid capital gains "
            "tax entirely and still deduct the full fair market value."
        ),

        "documentation": [
            "DAF contribution receipt (written acknowledgment from sponsoring organization)",
            "Form 8283 for noncash contributions ≥ $500 (appreciated stock)",
            "Qualified appraisal for noncash contributions ≥ $5,000",
            "Standard vs. itemized deduction comparison showing bunching benefit",
            "5-year carryforward schedule if AGI limits apply",
        ],

        "cpa_handoff": [
            "Bunching: contribute 2-3 years of giving in one year → itemize; standard deduction in off-years",
            "DAF: full deduction in contribution year; grants to charity distributed over time",
            "Appreciated stock: avoid capital gain; deduct full FMV — 30% AGI limit applies",
            "Cash to DAF: 60% AGI limit; 5-year carryforward for excess",
            "Substantiation: written acknowledgment required for contributions ≥ $250",
            "Form 8283: required for noncash contributions ≥ $500; qualified appraisal ≥ $5,000",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-021-life-insurance-death-benefit-estate-exclusion",
        "name": "Life Insurance Death Benefit Estate Exclusion",
        "_id": "69bdb3d5e5397a28d4543f48",
        "irc": "IRC §101(a), §2042, §2042(2), §2035(a), §2503(b)",
        "category": "Insurance & Risk",
        "overlap_group": "Life Insurance Planning",
        "applicable_forms": ["1041", "706"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and s.get("SIG_DEPENDENTS_PRESENT", False)
        ),

        "materiality_fn": lambda s: (
            65 if s.get("_agi", 0) > 1_000_000 else 45
        ),

        "fed_savings_fn": lambda s: (
            2_000_000 * 0.40 * 0.40
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 60,
        "complexity": 40,
        "audit_friction": 10,

        "plain_english": (
            "Life insurance death benefits are income-tax-free to beneficiaries "
            "under §101(a). However, if you own the policy at death, the entire "
            "death benefit is included in your taxable estate under §2042 — "
            "subject to 40% estate tax. An Irrevocable Life Insurance Trust "
            "(ILIT) solves this: the trust owns the policy, you give up all "
            "incidents of ownership, and the death benefit passes to your "
            "beneficiaries completely outside your estate. You fund the "
            "trust each year with gifts to pay the premiums, using the "
            "$18,000 per-beneficiary annual gift tax exclusion. Crummey "
            "notices must be sent to beneficiaries annually to preserve "
            "the gift tax exclusion."
        ),

        "documentation": [
            "ILIT trust document (irrevocable — estate planning attorney required)",
            "Life insurance policy owned by ILIT (not by insured)",
            "Annual Crummey notices to trust beneficiaries",
            "Annual gift tax exclusion analysis ($18K/beneficiary/year in 2024)",
            "Three-year lookback analysis if transferring existing policy to ILIT",
        ],

        "cpa_handoff": [
            "§2042: decedent's life insurance included in estate if any incidents of ownership retained",
            "ILIT: trust owns policy → no incidents of ownership → death benefit outside estate",
            "Fund via annual exclusion gifts ($18K/beneficiary 2024) + Crummey notices required",
            "Three-year rule §2035: transfer existing policy to ILIT more than 3 years before death",
            "Income tax: death benefit still tax-free to ILIT/beneficiaries under §101(a)",
            "Estate planning attorney required — ILIT is irrevocable once established",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires policy design, underwriting/actuarial review, and compliance documentation before implementation.",
        ],

    },

    {
        "id": "DTTS-022-roth-conversion-ladder",
        "name": "Roth Conversion Ladder",
        "_id": "69bdb3d6e5397a28d4543f51",
        "irc": "IRC §402A, §408A, §408A(d)(3), §408A(d)(3)(F), §401(a)(9)",
        "category": "Retirement Plans",
        "overlap_group": "Roth Conversion Strategy",
        "applicable_forms": ["1040"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_RETIREMENT_PLAN", False) and s.get("SIG_HIGH_INCOME", False)
        ),

        "materiality_fn": lambda s: (
            70 if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("SIG_HAS_RETIREMENT_PLAN", False) else 52
        ),

        "fed_savings_fn": lambda s: (
            50_000 * max(0, s.get("_fed_marginal_rate", 0) - 0.24)
        ),

        "state_savings_fn": lambda s: (
            50_000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0) * 0.30
        ),

        "speed_days": 14,
        "complexity": 20,
        "audit_friction": 5,

        "plain_english": (
            "A Roth conversion ladder converts a portion of your traditional "
            "IRA to Roth every year — systematically, in controlled amounts — "
            "instead of all at once. The goal is to convert while your tax "
            "rate is lower than it will be in retirement when Required Minimum "
            "Distributions force large taxable withdrawals. Each year, you "
            "calculate how much you can convert while staying within a "
            "favorable tax bracket — typically to the top of the 22% or 24% "
            "bracket. Over 10-15 years, this can eliminate the entire "
            "traditional IRA balance at favorable rates, permanently reducing "
            "future RMDs and leaving a tax-free Roth estate for heirs."
        ),

        "documentation": [
            "Annual conversion amount calculation (bracket filling analysis)",
            "IRA custodian conversion confirmation for each tax year",
            "Form 1099-R for each year's conversion",
            "Form 8606 tracking basis and conversion amounts",
            "Five-year rule tracking schedule per annual conversion",
        ],

        "cpa_handoff": [
            "Convert annually to top of 22% or 24% bracket — avoid pushing into 32%+",
            "Each conversion has its own 5-year clock for §72(t) penalty purposes",
            "RMD reduction: each dollar converted reduces future RMD → reduces future ordinary income",
            "IRMAA: Roth conversions increase MAGI in conversion year — may affect Medicare premiums",
            "Pro-rata rule: if pre-tax IRA exists alongside Roth, conversion is pro-rated",
            "Model over 10-15 year horizon: total tax paid over ladder vs. RMD tax scenario",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],

    },

    {
        "id": "DTTS-023-charitable-lead-annuity-trust-clat",
        "name": "Charitable Lead Annuity Trust (CLAT)",
        "_id": "69bdb3d6e5397a28d4543f5a",
        "irc": "IRC §170, §2055(e)(2)(B), §2522(c)(2)(B), §2702(a)(2)(B), §664",
        "category": "Charitable & Foundations",
        "overlap_group": "Charitable Giving",
        "applicable_forms": ["1041", "709"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_DEPENDENTS_PRESENT", False) and
            s.get("_agi", 0) > 1_000_000
        ),

        "materiality_fn": lambda s: (
            68 if s.get("_agi", 0) > 1_500_000 else 45
        ),

        "fed_savings_fn": lambda s: (
            370_000 * 0.40 * 0.40
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 120,
        "complexity": 65,
        "audit_friction": 15,

        "plain_english": (
            "A Charitable Lead Annuity Trust (CLAT) pays a fixed annuity to "
            "charity for a set number of years — then the remaining assets "
            "pass to your children or grandchildren. The key tax advantage: "
            "the gift to your heirs is valued for gift tax purposes by "
            "subtracting the present value of the charity's annuity from "
            "the total assets transferred. If the trust is structured as a "
            "'zeroed-out' CLAT — where the annuity value equals the full "
            "amount transferred at the IRS discount rate — the taxable gift "
            "to heirs is zero. Any investment return above the IRS hurdle "
            "rate passes to heirs completely free of gift and estate tax. "
            "This strategy requires genuine charitable intent and functions "
            "best in a high-interest-rate environment."
        ),

        "documentation": [
            "CLAT trust document (estate planning attorney required)",
            "§7520 rate documentation at date of funding",
            "Annuity calculation — zeroed-out vs. partial gift design",
            "Form 709 (Gift Tax Return) — reporting taxable gift to remainder beneficiaries",
            "Annual trust income tax return (Form 1041 for non-grantor CLAT)",
        ],

        "cpa_handoff": [
            "CLAT: charity gets annuity for term; remainder passes to heirs at reduced gift tax cost",
            "Zeroed-out CLAT: annuity = FMV at §7520 rate → $0 taxable gift; all excess to heirs tax-free",
            "Grantor CLAT: grantor pays trust income tax → treated as additional charitable gift to trust",
            "Non-grantor CLAT: trust files own 1041; no income tax deduction to grantor",
            "Requires genuine charitable intent — trust must actually pay charity annually",
            "File Form 709 in year of funding; annual trust administration required",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],

    },

    {
        "id": "DTTS-024-qbi-deduction-optimization",
        "name": "QBI Deduction Optimization",
        "_id": "69bdb3d7e5397a28d4543f62",
        "irc": "IRC §199A, §199A(b)(2), §199A(b)(3), §199A(d)(3), §199A(e)(4)",
        "category": "General Planning",
        "overlap_group": "QBI Optimization",
        "applicable_forms": ["1040", "1120S", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_S_CORP_VERIFIED", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            not s.get("SIG_SSTB_ABOVE_PHASEOUT", False) and  # dental QBI fully phased out
            s.get("SIG_QBI_MISSING", False)
        ),

        "materiality_fn": lambda s: (
            82 if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("SIG_HAS_S_CORP_VERIFIED", False) else 65
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_QBI_RESTRUCTURE_DEDUCTION", s.get("_obi", 0) * 0.05) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    0
),

        "speed_days": 21,
        "complexity": 25,
        "audit_friction": 10,

        "plain_english": (
            "The §199A QBI deduction allows pass-through business owners "
            "to deduct up to 20% of their qualified business income — but "
            "dental practices are service businesses subject to a phase-out "
            "above $483,900 of taxable income for married filers in 2024. "
            "QBI optimization focuses on maximizing the deduction within "
            "the existing structure: setting the right W-2 salary level "
            "to pass the wage test, ensuring qualified property basis is "
            "fully tracked, and most powerfully — using retirement "
            "contributions to reduce taxable income below the SSTB "
            "phase-out threshold, which can restore tens of thousands "
            "in deductions."
        ),

        "documentation": [
            "Form 8995-A with SSTB phase-out calculation and W-2 wage test",
            "W-2 wage documentation per entity",
            "UBIA (unadjusted basis immediately after acquisition) schedule per entity",
            "Aggregation election statement filed with return (annual)",
            "Taxable income calculation showing position relative to phase-out range",
        ],

        "cpa_handoff": [
            "Phase-out: $383,900–$483,900 MFJ (2024) — dentistry SSTB fully phased out above $483,900",
            "Key lever: retirement contributions (cash balance) reduce taxable income below phase-out",
            "W-2 wage test: owner salary must be ≥40% of S-Corp QBI to satisfy 50% wage test",
            "UBIA: often missed — includes original cost of §1245 property still in service",
            "Aggregation: combine S-Corp + real estate entity annually — file election each year",
            "Coordinate with entity restructure and cash balance for maximum effect",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],


},

    {
        "id": "DTTS-025-employer-provided-life-insurance",
        "name": "Employer-Provided Life Insurance",
        "_id": "69bdb3d8e5397a28d4543f69",
        "irc": "IRC §§79, 105, 106, 125, 132",
        "category": "Insurance & Risk",
        "overlap_group": "Life Insurance Planning",
        "applicable_forms": ["1120", "1120S"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_HIGH_INCOME", False)
        ),

        "materiality_fn": lambda s: (
            45 if s.get("SIG_HAS_S_CORP_VERIFIED", False) else 30
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_EXEC_BONUS_TOTAL_DEDUCTION", 0) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("Q_EXEC_BONUS_TOTAL_DEDUCTION", 0) * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 30,
        "complexity": 20,
        "audit_friction": 10,

        "plain_english": (
            "A dental practice can deduct life insurance premiums as a "
            "business expense when coverage is provided as an employee "
            "fringe benefit. The first $50,000 of group-term life insurance "
            "is excludable from the employee's taxable income under IRC §79. "
            "For S-Corp owner-dentists who own more than 2% of the practice, "
            "premiums are included in W-2 wages but are then deductible on "
            "the personal return — creating a net benefit through proper "
            "payroll structuring. This is a low-complexity strategy that "
            "works best when the practice already runs payroll and wants to "
            "add tax-efficient benefits for the owner and staff."
        ),

        "documentation": [
            "Group-term life insurance policy documents",
            "Payroll records showing premium treatment for >2% S-Corp shareholders",
            "W-2 Box 12 Code C — imputed income for coverage exceeding $50,000",
            "Cafeteria plan document (if §125 election in place)",
            "IRS Table I rates for imputed income calculation on excess coverage",
        ],

        "cpa_handoff": [
            "§79: first $50K group-term coverage excluded from employee gross income",
            "Coverage >$50K: imputed income calculated using IRS Table I rates — report on W-2",
            ">2% S-Corp shareholders: premiums included in W-2 wages; deduct on Form 1040",
            "Key person policies: premiums NOT deductible; death benefit tax-free under §101",
            "Cafeteria plan (§125): allows pre-tax employee elections for premium funding",
            "Coordinate with payroll provider to ensure proper W-2 coding and deduction treatment",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires policy design, underwriting/actuarial review, and compliance documentation before implementation.",
        ],

    },

    {
        "id": "DTTS-026-separate-property-election-in-community-states",
        "name": "Separate Property Election in Community Property States",
        "irc": "IRC §66, §66(a), §66(b), §66(c)",
        "category": "International & State",
        "overlap_group": "Retirement Plan",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_STATE_RETURN_PRESENT", False) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("_primary_state", "") in (
                "AZ", "CA", "ID", "LA", "NV", "NM", "TX", "WA", "WI"
            )
        ),

        "materiality_fn": lambda s: (
            55 if s.get("SIG_SCHEDULE_C_PRESENT", False) or s.get("SIG_HAS_S_CORP_VERIFIED", False) else 35
        ),

        "fed_savings_fn": lambda s: (
    min(s.get("_agi", 0) * 0.15, 21_000) * s.get("Q_COMMUNITY_PROPERTY_PROBABILITY", 0)
),

        "state_savings_fn": lambda s: (
    0
),

        "speed_days": 30,
        "complexity": 30,
        "audit_friction": 20,

        "plain_english": (
            "In the nine community property states — Arizona, California, "
            "Idaho, Louisiana, Nevada, New Mexico, Texas, Washington, and "
            "Wisconsin — income earned during marriage is generally treated "
            "as owned equally by both spouses. For a dentist running a "
            "practice, this can mean the non-practicing spouse is also "
            "subject to self-employment tax on their 50% share of business "
            "income. Depending on the state and filing status, a separate "
            "property election or careful filing strategy can eliminate this "
            "unintended SE tax exposure. This is a state-specific strategy "
            "that requires confirming the exact rules in the taxpayer's "
            "home state before implementation."
        ),

        "documentation": [
            "State community property election or agreement (state-specific form)",
            "Filing status documentation — MFJ vs. MFS analysis",
            "SE income allocation schedule per spouse",
            "State return showing community vs. separate income treatment",
            "Pub. 555 community property worksheet",
        ],

        "cpa_handoff": [
            "Community property states: AZ, CA, ID, LA, NV, NM, TX, WA, WI",
            "SE income of one spouse may be 50% community property — both spouses could owe SE tax",
            "§66(a): if spouses live apart all year and don't file jointly, community income treated as separate",
            "Separate property election (state law): eliminates community income split for business earnings",
            "MFS in community property state: each spouse reports 50% of all community income/deductions",
            "Coordinate with state-licensed CPA — rules vary significantly by state",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],

    },

    {
        "id": "DTTS-027-state-tax-deduction-workaround-salt-cap",
        "name": "State Tax Deduction Workaround (SALT Cap)",
        "_id": "69bdb3d8e5397a28d4543f70",
        "irc": "IRC §164, §164(b)(6), §164(a)(3), §199A",
        "category": "International & State",
        "overlap_group": "SALT PTET Workaround",
        "applicable_forms": ["1120S", "1065", "1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HIGH_SALT", False) and
            s.get("SIG_STATE_RETURN_PRESENT", False) and
            s.get("SIG_PTET_OPPORTUNITY", False) and
            s.get("Q_PTET_CONFIRMED", False) and  # must confirm state has PTET opt-in
            (s.get("SIG_HAS_S_CORP_VERIFIED", False) or s.get("SIG_HAS_PARTNERSHIP", False))
        ),

        "materiality_fn": lambda s: (
            75 if s.get("SIG_HAS_S_CORP_VERIFIED", False) and s.get("SIG_HIGH_INCOME", False) else 50
        ),

        "fed_savings_fn": lambda s: (
    (max(
        s.get("_obi", 0) * s.get("Q_STATE_MARGINAL_RATE", 0.05)
        - _LIM["salt_cap"], 0
    ) * s.get("_fed_marginal_rate", 0))
    if s.get("Q_PTET_CONFIRMED", False) and s.get("_obi", 0) > 0 else 0
),

        "state_savings_fn": lambda s: (
    0
),

        "speed_days": 21,
        "complexity": 20,
        "audit_friction": 10,

        "plain_english": (
            "The Tax Cuts and Jobs Act capped the deduction for state and "
            "local taxes at $10,000 for individuals — a significant hit for "
            "high-income dentists in states like California, New York, or "
            "New Jersey where state income taxes can easily exceed $50,000. "
            "The primary workaround is the Pass-Through Entity Tax (PTET) "
            "election: the dental S-Corp or partnership pays state income "
            "tax at the entity level, where it is fully deductible as a "
            "business expense with no cap. The owner then receives a "
            "dollar-for-dollar credit on their personal state return. "
            "This election is now available in most high-tax states and "
            "can recover tens of thousands in lost federal deductions."
        ),

        "documentation": [
            "PTET election form filed with state (timing varies by state — often by March 15)",
            "Entity-level state tax payment records",
            "Personal return state credit documentation",
            "Form 1040 Schedule A — confirm SALT cap position before and after PTET",
            "State conformity analysis — confirm state allows PTET deduction at entity level",
        ],

        "cpa_handoff": [
            "SALT cap: $10K limit on individual state/local tax deduction — same for MFJ and single",
            "PTET workaround: S-Corp/partnership pays state tax at entity level — no cap as §162 deduction",
            "Owner receives state credit on personal return — net state cost = $0",
            "Federal benefit: excess state tax above $10K now deductible → saves fed tax at marginal rate",
            "Election timing: most states require PTET election by March 15 or estimated payment deadlines",
            "Monitor TCJA sunset after 2025 — SALT cap may expire; reassess annually",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-028-qbi",
        "name": "Qualified Business Income (QBI) Deduction — §199A",
        "irc": "IRC §199A",
        "category": "Deduction & Reimbursement",
        "overlap_group": "QBI Optimization",
        "applicable_forms": ["1040", "1120S", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_QBI_MISSING", False) and
            not s.get("SIG_HAS_C_CORP", False) and  # FIX: §199A QBI deduction not available to C-Corps
            s.get("_obi", 0) > 0 and
            s.get("_agi", 0) < _LIM["qbi_sstb_phaseout_mfj"]
        ),

        "materiality_fn": lambda s: 85 if s.get("SIG_QBI_MISSING", False) else 50,

        "fed_savings_fn": lambda s: (
            max(s.get("_obi", 0), s.get("_wages", 0)) * 0.20 * s.get("_fed_marginal_rate", 0)
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 7,
        "complexity": 15,
        "audit_friction": 10,

        "plain_english": (
            "The §199A deduction allows pass-through business owners to deduct up to "
            "20% of qualified business income. Proper wage and income planning can "
            "maximize this deduction."
        ),

        "documentation": [
            "QBI worksheet (Form 8995 or 8995-A)",
            "Entity income documentation"
        ],

        "cpa_handoff": [
            "Recompute QBI deduction",
            "File amended return if deduction previously missed"
        ],

        "prerequisites": ["Pass-through entity or self-employment income"],
    },

    {
        "id": "DTTS-029-conservation-easement-with-mineral-rights-retained",
        "name": "Conservation Easement with Mineral Rights Retained",
        "_id": "69bdb3d9e5397a28d4543f78",
        "irc": "IRC §170(h), §170(h)(1), §170(h)(4), §170(h)(5), §170(f)(11)",
        "category": "Charitable & Foundations",
        "overlap_group": "Conservation Easement Strategies",
        "applicable_forms": ["1040"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            (s.get("SIG_REAL_ESTATE_ACTIVITY", False) or s.get("SIG_SCHEDULE_E_PRESENT", False))
        ),

        "materiality_fn": lambda s: (
            60 if s.get("_agi", 0) > 750_000 else 40
        ),

        "fed_savings_fn": lambda s: (
            min(166_667, s.get("_agi", 0) * 0.50) * s.get("_fed_marginal_rate", 0) * 0.30
        ),

        "state_savings_fn": lambda s: (
            0
        ),

        "speed_days": 180,
        "complexity": 70,
        "audit_friction": 40,

        "plain_english": (
            "A conservation easement allows a landowner to donate a "
            "permanent restriction on how their land can be developed "
            "to a qualified land trust or government organization — and "
            "take a charitable deduction for the reduction in property "
            "value caused by that restriction. When mineral rights are "
            "retained, the owner keeps the right to extract any oil, gas, "
            "or minerals beneath the surface while still receiving the "
            "deduction for the surface development restriction. The "
            "deduction is based on a qualified appraisal and can be "
            "substantial — but this strategy carries high IRS scrutiny, "
            "particularly for syndicated arrangements. Only legitimate, "
            "owner-driven easements with genuine conservation purpose "
            "and proper appraisals should be considered."
        ),

        "documentation": [
            "Qualified appraisal by IRS-qualified appraiser (required for deductions >$500K)",
            "Form 8283 Section B — noncash charitable contribution reporting",
            "Deed of conservation easement (recorded with county)",
            "Baseline documentation report from land trust",
            "Mineral rights reservation clause in easement deed",
            "15-year carryforward schedule if deduction exceeds 50% AGI limit",
        ],

        "cpa_handoff": [
            "Deduction = FMV before easement − FMV after; requires qualified appraisal",
            "Deduction limit: 50% of AGI/yr with 15-year carryforward (100% for qualified farmers/ranchers)",
            "Mineral rights retained: reduces easement value but owner keeps subsurface extraction rights",
            "HIGH AUDIT RISK: syndicated easements on IRS Dirty Dozen — only recommend owner-driven",
            "Form 8283 Section B required; appraisal must be completed before return filing date",
            "Perpetuity requirement: restriction must be permanent — no time-limited easements",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-030-irrevocable-life-insurance-trust-ilit",
        "name": "Irrevocable Life Insurance Trust (ILIT)",
        "_id": "69bdb3d9e5397a28d4543f81",
        "irc": "IRC §101, §101(a), §2042, §2035, §2503(b), §2503(c), §677",
        "category": "Insurance & Risk",
        "overlap_group": "Life Insurance Planning",
        "applicable_forms": ["1041", "706"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("SIG_DEPENDENTS_PRESENT", False)
        ),

        "materiality_fn": lambda s: (
            60 if s.get("_agi", 0) > 1_000_000 else 40
        ),

        "fed_savings_fn": lambda s: (
            2_000_000 * 0.40 * 0.35
        ),

        "state_savings_fn": lambda s: (
            0
        ),

        "speed_days": 90,
        "complexity": 60,
        "audit_friction": 15,

        "plain_english": (
            "An Irrevocable Life Insurance Trust (ILIT) is a trust that "
            "owns a life insurance policy on the dentist's life — keeping "
            "the death benefit completely outside the taxable estate. "
            "Without an ILIT, life insurance owned by the insured is "
            "included in the taxable estate and can trigger a 40% federal "
            "estate tax on the proceeds. With an ILIT, the trust owns the "
            "policy; the dentist makes annual gifts to the trust to pay "
            "premiums (using the annual gift tax exclusion of $18,000 per "
            "beneficiary); and at death, proceeds pass to heirs free of "
            "both income and estate tax. The ILIT can also lend money to "
            "the estate to cover any estate taxes without increasing the "
            "taxable estate."
        ),

        "documentation": [
            "ILIT trust document (irrevocable — estate planning attorney required)",
            "Crummey notice letters — sent to beneficiaries annually before premium payment",
            "Life insurance policy owned by ILIT (not the insured)",
            "Annual gift tax exclusion documentation ($18,000/beneficiary in 2024)",
            "Form 706 — estate tax return noting ILIT structure and exclusion of proceeds",
            "3-year look-back analysis if transferring existing policy to ILIT (§2035)",
        ],

        "cpa_handoff": [
            "§2042: life insurance included in estate if decedent held incidents of ownership at death",
            "ILIT solution: trust owns policy — decedent holds no incidents of ownership → excluded from estate",
            "§2035 look-back: policy transferred to ILIT within 3 years of death pulled back into estate",
            "Crummey notices: required annually so gifts to trust qualify for $18K annual exclusion",
            "At death: proceeds paid to ILIT → distributed to beneficiaries income- and estate-tax-free",
            "Liquidity: ILIT can loan proceeds to estate or purchase estate assets to fund estate taxes",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
            "Requires policy design, underwriting/actuarial review, and compliance documentation before implementation.",
        ],

    },

    {
        "id": "DTTS-031-section-280a-g-the-augusta-rule",
        "_id": "69ca291b03832a709c4fa899",
        "name": "Augusta Rule (IRC §280A(g))",
        "irc": "IRC §162, §280A, §280A(g)",
        "category": "General Planning",
        "overlap_group": "Augusta Rule (IRC §280A(g))",
        "applicable_forms": ["1040", "1120S", "1120", "1065"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            (s.get("Q_OWNS_PRIMARY_HOME", False) or
             s.get("Q_OWNS_SECONDARY_HOME", False) or
             s.get("Q_OWNS_BUILDING", False))
        ),

        "materiality_fn": lambda s: (
            70 if s.get("SIG_HAS_S_CORP_VERIFIED", False) and s.get("SIG_HIGH_TAX_LIABILITY", False) else 50
        ),

        "fed_savings_fn": lambda s: (
            28_000 * s.get("_fed_marginal_rate", 0)
        ),

        "state_savings_fn": lambda s: (
            28_000 * s.get("Q_STATE_MARGINAL_RATE", 0.05)
        ),

        "speed_days": 14,
        "complexity": 15,
        "audit_friction": 25,

        "plain_english": (
            "The Augusta Rule — named after the practice of Augusta, Georgia "
            "homeowners renting their homes during the Masters golf tournament "
            "— allows a homeowner to rent their personal residence to their "
            "own business for up to 14 days per year completely tax-free. "
            "The business gets a deduction for the rental payment as an "
            "ordinary business expense, but the owner pays zero income tax "
            "on the rental income received. For a high-income dentist, this "
            "means shifting up to $25,000–$30,000 out of the business as a "
            "deductible expense while the owner receives that same amount "
            "completely tax-free. The key requirements: the rental must be "
            "for legitimate business purposes (board meetings, team retreats), "
            "the rate must be at fair market value, and meeting records must "
            "be documented."
        ),

        "documentation": [
            "Meeting agendas and minutes for each rental day",
            "Attendance records for business meetings held at residence",
            "Fair market rental rate support (comparable rental listings or appraisal)",
            "Rental agreement between business and homeowner",
            "Business check/payment records showing rental payment to owner",
            "Owner's personal return — confirm rental income NOT reported (§280A(g) exclusion)",
        ],

        "cpa_handoff": [
            "§280A(g): if home rented <15 days/year, rental income excluded from gross income entirely",
            "Business deducts rental payment as §162 ordinary business expense",
            "Net effect: entity gets deduction; owner pays zero tax on income received",
            "Maximum: 14 days; rate must be fair market value — above-market rate is IRS red flag",
            "Documentation required: meeting minutes, agenda, attendance — not just calendar entries",
            "IRS scrutiny elevated: ensure genuine business purpose and arm's-length rental rate",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-032-energy-efficient-home-credit-builders",
        "name": "Energy Efficient Home Credit (Builders)",
        "_id": "69bdb3dae5397a28d4543f89",
        "irc": "IRC §45L, §45L(a), §45L(b), §45L(c), §45L(e)",
        "category": "Credits & Incentives",
        "overlap_group": None,
        "applicable_forms": ["1040", "1120"],
        "phase_1_eligible": True,
        "estimate_confidence": "MODERATE",

        "eligibility_logic": lambda s: (
            s.get("SIG_REAL_ESTATE_ACTIVITY", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("SIG_BUSINESS_PRESENT", False)
        ),

        "materiality_fn": lambda s: (
            50 if s.get("SIG_SCHEDULE_E_PRESENT", False) and s.get("SIG_HIGH_TAX_LIABILITY", False) else 30
        ),

        "fed_savings_fn": lambda s: (
    min(12_500, s.get("_obi", 0) * 0.02)
),

        "state_savings_fn": lambda s: (
    0
),

        "speed_days": 60,
        "complexity": 25,
        "audit_friction": 15,

        "plain_english": (
            "The §45L Energy Efficient Home Credit gives a dollar-for-dollar "
            "federal tax credit to builders and contractors who construct new "
            "homes that meet Energy Star or DOE Zero Energy Ready standards. "
            "The credit is $2,500 per unit for Energy Star certified homes "
            "and $5,000 per unit for Zero Energy Ready homes. This strategy "
            "applies to dentists who have a real estate development or "
            "construction business on the side — not to homebuyers. "
            "A dentist building even a small number of qualifying units "
            "can generate meaningful dollar-for-dollar tax credits. "
            "Third-party energy certification is required for each unit, "
            "and the credit reduces the basis of the dwelling unit built."
        ),

        "documentation": [
            "Form 8908 — Energy Efficient Home Credit (filed with return)",
            "Third-party energy rater certification for each qualifying unit",
            "Energy Star or DOE Zero Energy Ready Home certification documentation",
            "Construction records and cost basis per unit",
            "Prevailing wage compliance documentation (if applicable for maximum credit)",
            "Basis reduction schedule — credit reduces cost basis of each unit",
        ],

        "cpa_handoff": [
            "§45L credit: $2,500/unit (Energy Star) or $5,000/unit (Zero Energy Ready) — post-IRA 2022",
            "Eligible contractor = person who built or substantially reconstructed the unit",
            "Credit is dollar-for-dollar against federal tax — not a deduction",
            "Basis reduction: credit amount reduces cost basis of the qualifying dwelling unit",
            "Third-party certification required: IRS-approved energy rater must certify each unit",
            "Prevailing wage: must meet DOL prevailing wage requirements to preserve full credit amounts",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-033-tax-free-gifts-to-employees",
        "name": "Tax-Free Gifts to Employees",
        "_id": "69bdb3dae5397a28d4543f90",
        "irc": "IRC §102, §102(c), §132, §132(e), §274(j)",
        "category": "Compensation & Benefits",
        "overlap_group": "Employee Benefits",
        "applicable_forms": ["1120", "1120S"],
        "phase_1_eligible": True,
        "estimate_confidence": "MODERATE",

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_W2_PRESENT", False) and
            s.get("SIG_HIGH_INCOME", False)
        ),

        "materiality_fn": lambda s: (
            35 if s.get("SIG_BUSINESS_PRESENT", False) and s.get("SIG_W2_PRESENT", False) else 20
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_EDUCATIONAL_ASSISTANCE_DEDUCTION", 0) * 0.06 * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("Q_EDUCATIONAL_ASSISTANCE_DEDUCTION", 0) * 0.06 * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 10,

        "plain_english": (
            "The IRS allows dental practices to give employees certain "
            "non-cash gifts and awards completely tax-free — the practice "
            "gets a deduction, and the employee pays no income or payroll "
            "tax on the benefit. De minimis fringe benefits like a holiday "
            "gift basket, flowers, or occasional event tickets are excluded "
            "from employee income when their value is small enough that "
            "tracking them would be unreasonable. Employee achievement "
            "awards for length of service or safety — given as tangible "
            "non-cash property — are deductible up to $1,600 per employee "
            "under a qualified written plan. The critical rule: cash bonuses "
            "and gift cards never qualify and are always taxable wages. "
            "This is a low-complexity strategy best used to replace cash "
            "bonuses with qualifying non-cash recognition programs."
        ),

        "documentation": [
            "Written achievement award plan document (for qualified plan — $1,600 limit)",
            "Gift/award records showing non-cash tangible property (not cash or gift cards)",
            "Payroll records confirming qualifying amounts excluded from W-2 Box 1",
            "De minimis gift log — occasion, recipient, item, and fair market value",
        ],

        "cpa_handoff": [
            "§132(e) de minimis: low-value, occasional non-cash gifts excluded from employee income",
            "§274(j) achievement awards: tangible non-cash property only — $400 non-qualified / $1,600 qualified plan",
            "Cash and gift cards NEVER qualify — always taxable wages subject to FICA and income tax",
            "Practice deducts full cost as compensation expense; employee excludes from gross income",
            "Qualified written plan required to access $1,600 limit — must be documented before awards given",
            "Confirm W-2 treatment: qualifying awards excluded from Box 1; non-qualifying included",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-034-c-corporation-owned-life-insurance-eoli",
        "name": "C-Corporation-Owned Life Insurance (COLI/EOLI)",
        "irc": "IRC §101(a), §101(j), §264(a)(1), §264(f), §7702",
        "category": "Entity & Structuring",
        "overlap_group": "Life Insurance Planning",
        "applicable_forms": ["1120"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_C_CORP", False) and
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False)
        ),

        "materiality_fn": lambda s: (
            55 if s.get("SIG_HAS_C_CORP", False) and s.get("SIG_VERY_HIGH_INCOME", False) else 30
        ),

        "fed_savings_fn": lambda s: (
            20_000 * 0.21
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 90,
        "complexity": 55,
        "audit_friction": 20,

        "plain_english": (
            "A C-Corporation can own life insurance on a key employee or "
            "owner-dentist — a strategy known as Corporate-Owned Life "
            "Insurance (COLI) or Employer-Owned Life Insurance (EOLI). "
            "While the premiums are not deductible, the cash value inside "
            "the policy grows tax-deferred on the corporation's balance "
            "sheet, and the death benefit is received tax-free by the "
            "corporation — provided the IRS notice and consent requirements "
            "under §101(j) are satisfied. The insured employee must be "
            "notified and provide written consent before the policy is "
            "issued, and the corporation must file Form 8925 annually. "
            "Common uses include funding buy-sell agreements, replacing "
            "key person income, and providing liquidity for deferred "
            "compensation obligations."
        ),

        "documentation": [
            "Form 8925 — Report of Employer-Owned Life Insurance Contracts (filed annually)",
            "§101(j) notice and consent — written employee notification and consent before policy issued",
            "Life insurance policy owned by C-Corporation",
            "Buy-sell agreement or key person documentation (if applicable)",
            "Corporate board resolution authorizing policy purchase",
            "AMT analysis for C-Corp if COLI death benefit triggers preference item",
        ],

        "cpa_handoff": [
            "§264(a)(1): EOLI premiums NOT deductible — corporation is beneficiary",
            "§101(j): death benefit includable in income UNLESS notice/consent requirements met",
            "Notice/consent: insured must be notified and consent in writing before policy issued",
            "Form 8925: required annual filing reporting all EOLI contracts — do not miss",
            "Cash value: accumulates tax-deferred on corporate balance sheet; accessible via policy loans",
            "C-Corp AMT: COLI death benefit may be AMT preference item — confirm before structuring",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires policy design, underwriting/actuarial review, and compliance documentation before implementation.",
        ],

    },

    {
        "id": "DTTS-035-electing-out-of-partnership-treatment",
        "name": "Electing Out of Partnership Treatment",
        "_id": "69bdb3dbe5397a28d4543f97",
        "irc": "IRC §761(a), §1361, §1362",
        "category": "Entity & Structuring",
        "overlap_group": None,
        "applicable_forms": ["1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_PARTNERSHIP", False) and
            s["SIG_K1_PRESENT"] and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False)
        ),

        "materiality_fn": lambda s: (
            60 if s.get("SIG_MULTI_ENTITY", False) and s.get("SIG_HIGH_INCOME", False) else 40
        ),

        "fed_savings_fn": lambda s: (
    s.get("_obi", 0) * 0.30 * 0.153 * 0.9235
),

        "state_savings_fn": lambda s: (
    0
),

        "speed_days": 60,
        "complexity": 35,
        "audit_friction": 15,

        "plain_english": (
            "When two or more dentists co-own a business without incorporating, "
            "the IRS automatically treats it as a partnership — requiring "
            "a Form 1065 filing, K-1s for each partner, and self-employment "
            "tax on all profits. There are two main planning paths: electing "
            "out of partnership treatment entirely (available only for passive "
            "investment co-ownerships where each owner can track their own "
            "income), or converting the partnership to an S-Corporation. "
            "The S-Corp conversion is often the more impactful choice for "
            "active dental practices — it eliminates self-employment tax on "
            "profits above a reasonable owner salary, potentially saving "
            "thousands in FICA taxes annually. Both paths require careful "
            "analysis of the partnership agreement, partner eligibility, "
            "and state-specific filing requirements."
        ),

        "documentation": [
            "Form 2553 — S-Corporation election (if converting to S-Corp path)",
            "§761(a) election statement — attached to first return if electing out of subchapter K",
            "Partnership agreement review — confirm eligibility for election out or S-Corp conversion",
            "K-1 history and basis schedules per partner",
            "State entity conversion/registration documents if restructuring",
        ],

        "cpa_handoff": [
            "§761(a) election out: available only for qualifying investment co-ownerships — not active businesses",
            "Active dental partnerships: election out NOT available; consider S-Corp conversion instead",
            "S-Corp conversion: eliminates SE tax on profits above reasonable salary — file Form 2553",
            "SE tax savings on partnership: all OBI subject to 15.3% SE tax; S-Corp only salary portion",
            "Partnership → S-Corp: must meet eligibility (≤100 shareholders, US citizens/residents, one class of stock)",
            "Coordinate with entity restructure for full entity optimization review",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-036-accelerated-depreciation-via-leasehold-improvements",
        "name": "Accelerated Depreciation via Leasehold Improvements",
        "_id": "69bdb3dbe5397a28d4543f9f",
        "irc": "IRC §168, §168(e)(6), §168(k), §179, §179D",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Depreciation — Leasehold",
        "applicable_forms": ["1040", "1120", "1120S", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            (s.get("SIG_NO_DEPRECIATION", False) or s.get("SIG_LOW_DEPRECIATION", False))
        ),

        "materiality_fn": lambda s: (
            70 if s.get("SIG_NO_DEPRECIATION", False) and s.get("SIG_HIGH_TAX_LIABILITY", False) else
            50 if s.get("SIG_LOW_DEPRECIATION", False) else 35
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_COST_SEG_INCREMENTAL_DEDUCTION", 0) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("Q_COST_SEG_INCREMENTAL_DEDUCTION", 0) * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 30,
        "complexity": 30,
        "audit_friction": 15,

        "plain_english": (
            "When a dentist builds out or renovates a leased office space, "
            "those leasehold improvements qualify as Qualified Improvement "
            "Property (QIP) — a 15-year asset class eligible for accelerated "
            "depreciation. Instead of writing off a $300,000 build-out over "
            "39 years, the practice can deduct 60% in the first year through "
            "bonus depreciation (2024 rate), and elect to expense additional "
            "amounts under Section 179. Energy-efficient upgrades to lighting, "
            "HVAC, or building envelope may also qualify for the §179D "
            "commercial building deduction — up to $5.65 per square foot. "
            "A cost segregation study can identify additional personal "
            "property components in the build-out that depreciate even "
            "faster. This strategy is most powerful in the year improvements "
            "are placed in service."
        ),

        "documentation": [
            "Form 4562 — Depreciation and Amortization (§179 and bonus depreciation elections)",
            "Leasehold improvement invoices and contractor agreements",
            "Cost segregation study (if personal property reclassification pursued)",
            "§179D energy certification by qualified professional (if energy deduction claimed)",
            "Placed-in-service date documentation for each improvement category",
            "State depreciation schedule — many states decouple from federal bonus depreciation",
        ],

        "cpa_handoff": [
            "QIP: interior improvements to nonresidential leased space — 15-year MACRS, eligible for bonus",
            "Bonus depreciation 2024: 60% first-year deduction; phasing down 20%/yr through 2026",
            "§179: elect to expense up to $1,220,000 (2024); limited to active business taxable income",
            "§179D: energy efficient commercial building — up to $5.65/sq ft; requires energy certification",
            "Cost segregation: identify 5/7-year personal property within build-out for faster write-off",
            "State conformity: most states do NOT conform to federal bonus depreciation — run separate state schedule",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],

    },

    {
        "id": "DTTS-037-1033-involuntary-conversion-deferral",
        "name": "1033 Involuntary Conversion Deferral",
        "_id": "69bdb3dce5397a28d4543fa8",
        "irc": "IRC §1033, §1033(a)(1), §1033(a)(2), §1033(b), §1033(g), §1231",
        "category": "Real Estate & Depreciation",
        "overlap_group": None,
        "applicable_forms": ["1040", "1120", "1120S", "1065"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_REAL_ESTATE_ACTIVITY", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("SIG_HAS_DEPRECIATION", False)
        ),

        "materiality_fn": lambda s: (
            55 if s.get("SIG_REAL_ESTATE_ACTIVITY", False) and s.get("SIG_HIGH_TAX_LIABILITY", False) else 30
        ),

        "fed_savings_fn": lambda s: (
            250_000 * 0.238 * 0.20
        ),

        "state_savings_fn": lambda s: (
            0
        ),

        "speed_days": 45,
        "complexity": 35,
        "audit_friction": 20,

        "plain_english": (
            "If a dentist's business or investment property is destroyed by "
            "fire, condemned by a government authority, or subject to another "
            "involuntary conversion, the resulting insurance or condemnation "
            "proceeds can create a large taxable gain. Section 1033 allows "
            "that gain to be deferred — not forgiven — if the proceeds are "
            "reinvested in similar replacement property within the replacement "
            "period. For real property, that window is three years from the "
            "end of the tax year in which the gain occurred. The election "
            "must be made on the tax return, and the replacement property "
            "must be similar or related in service or use to the converted "
            "property. This is a situational strategy — it applies only when "
            "an involuntary conversion event has actually occurred."
        ),

        "documentation": [
            "§1033 election statement attached to return for year of gain",
            "Insurance or condemnation proceeds documentation",
            "Adjusted basis records for converted property",
            "Replacement property purchase agreement and closing documents",
            "Replacement period deadline calculation and tracking",
            "Similar-or-related-use analysis for replacement property",
        ],

        "cpa_handoff": [
            "§1033: gain deferred if replacement property acquired within replacement period",
            "Replacement period: 2 years general; 3 years for real property; extended for disasters",
            "Election required: must attach §1033 election statement to return — not automatic",
            "Basis carryover: replacement property takes reduced basis — gain deferred, not forgiven",
            "Similar/related use: stricter than §1031 like-kind — replacement must serve same function",
            "§1033(g): real property replacement can be like-kind (broader standard) if held for business/investment",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],

    },

    {
        "id": "DTTS-038-domestic-production-deduction-for-film-tv",
        "name": "Domestic Production Deduction for Film/TV",
        "_id": "69bdb3dce5397a28d4543fb1",
        "irc": "IRC §181, §181(a), §181(d), §181(f)",
        "category": "General Planning",
        "overlap_group": None,
        "applicable_forms": ["1040", "1120"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("_agi", 0) > 500_000
        ),

        "materiality_fn": lambda s: (
            40 if s.get("SIG_VERY_HIGH_INCOME", False) else 20
        ),

        "fed_savings_fn": lambda s: (
            500_000 * s.get("_fed_marginal_rate", 0) * 0.10
        ),

        "state_savings_fn": lambda s: (
            0
        ),

        "speed_days": 60,
        "complexity": 40,
        "audit_friction": 30,

        "plain_english": (
            "IRC §181 allows investors in qualifying domestic film, television, "
            "or live theatrical productions to immediately deduct their full "
            "production cost investment in the year it is paid — instead of "
            "capitalizing and amortizing the cost over the life of the project. "
            "For a high-income dentist who invests in a qualifying production "
            "where at least 75% of compensation goes to US workers, this "
            "election can create a substantial first-year deduction. The "
            "strategy is subject to at-risk rules — the investor must have "
            "genuine economic exposure — and passive activity rules may limit "
            "the deduction if the dentist does not materially participate. "
            "This is a niche strategy that applies only when there is an "
            "actual qualifying film or TV investment in place."
        ),

        "documentation": [
            "§181 election statement attached to return for year of investment",
            "Production agreement showing investor ownership interest",
            "US compensation certification — at least 75% of total compensation to US services",
            "At-risk amount documentation per §465",
            "Passive activity participation records if material participation claimed",
            "Recapture analysis if production ultimately does not qualify",
        ],

        "cpa_handoff": [
            "§181: immediate deduction of qualifying film/TV production costs vs. capitalization",
            "Limit: $15M per production ($20M in qualifying low-income/distressed communities)",
            "75% test: at least 75% of total compensation must be paid to US production services",
            "At-risk rules (§465): deduction limited to investor's genuine economic exposure",
            "Passive activity (§469): if passive investor, losses only offset passive income",
            "Recapture (§181(f)): if production doesn't ultimately qualify, prior deductions recaptured",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-039-section-453a-interest-charge-planning-large-installments",
        "name": "Section 453A Interest Charge Planning (Large Installments)",
        "_id": "69bdb3dde5397a28d4543fba",
        "irc": "IRC §453, §453(b), §453A, §453A(a), §453A(b), §453A(c), §1274",
        "category": "Exit & Sale",
        "overlap_group": "Practice Sale Exit",
        "applicable_forms": ["1040", "1120", "1120S", "1065"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("_agi", 0) > 500_000
        ),

        "materiality_fn": lambda s: (
            55 if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("_agi", 0) > 800_000 else 35
        ),

        "fed_savings_fn": lambda s: (
            50_000 * 0.20
        ),

        "state_savings_fn": lambda s: (
            0
        ),

        "speed_days": 60,
        "complexity": 45,
        "audit_friction": 20,

        "plain_english": (
            "When a dentist sells their practice and receives payments over "
            "multiple years through an installment sale, they generally only "
            "pay tax as payments arrive — spreading the gain and the tax bill. "
            "However, §453A imposes an annual interest charge when the total "
            "outstanding installment obligations exceed $5 million at year-end, "
            "effectively adding a cost to the deferral benefit on large sales. "
            "The planning goal is to structure installment notes so the "
            "outstanding balance stays below the $5 million threshold, or "
            "to evaluate whether the deferral benefit still exceeds the "
            "§453A interest cost. A critical trap to avoid: pledging the "
            "installment note as loan collateral triggers immediate gain "
            "recognition on the pledged amount — eliminating the deferral "
            "benefit entirely."
        ),

        "documentation": [
            "Form 6252 — Installment Sale Income (filed each year payments received)",
            "Installment sale agreement with payment schedule",
            "Year-end outstanding obligation balance calculation vs. $5M threshold",
            "§453A interest charge calculation if threshold exceeded",
            "Imputed interest analysis under §1274 if note is below-market rate",
            "Pledge analysis — confirm installment note is NOT pledged as collateral",
        ],

        "cpa_handoff": [
            "§453A: interest charge applies when outstanding installment obligations >$5M at year-end",
            "Interest charge = AFR × applicable % × deferred tax on obligations above $5M",
            "Planning: structure note payments to keep year-end balance below $5M threshold",
            "Pledge rule (§453A(c)): pledging note as collateral = deemed receipt → immediate gain",
            "§1274: below-market interest rate on note → IRS imputes interest; affects gain allocation",
            "Alternatives for large sales: structured sale, SCIN, private annuity — each with tradeoffs",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-040-hire-children-under-18",
        "name": "Hire Children Under 18",
        "_id": "69bdb3dde5397a28d4543fc3",
        "irc": "IRC §162, §3121(b)(3)(A), §3306(c)(5), §73, §1(g)",
        "category": "General Planning",
        "overlap_group": "Family Employment",
        "applicable_forms": ["1040", "1120S", "1120"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_DEPENDENTS_PRESENT", False) and
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False)
        ),

        "materiality_fn": lambda s: (
            65 if s.get("SIG_SCHEDULE_C_PRESENT", False) and s.get("SIG_HIGH_TAX_LIABILITY", False) else
            50 if s.get("SIG_DEPENDENTS_PRESENT", False) and s.get("SIG_HIGH_INCOME", False) else 35
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_HIRING_CHILDREN_WAGES", 0) * s.get("_fed_marginal_rate", 0) + s.get("Q_FICA_SAVINGS_CHILDREN", 0)
),

        "state_savings_fn": lambda s: (
    s.get("Q_HIRING_CHILDREN_WAGES", 0) * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 14,
        "complexity": 15,
        "audit_friction": 20,

        "plain_english": (
            "A dentist who owns their practice can hire their own children "
            "to perform real, documented work — and deduct the wages as an "
            "ordinary business expense. The child pays tax at their own lower "
            "rate, and their standard deduction ($14,600 in 2024) shelters "
            "the first $14,600 of wages from income tax entirely — so the "
            "family keeps more of what the practice earns. If the practice "
            "is structured as a sole proprietorship or a partnership owned "
            "entirely by the parents, wages paid to children under 18 are "
            "also exempt from FICA and FUTA — saving an additional 15.3% "
            "in payroll taxes. S-Corporations do not get this FICA exemption. "
            "The work must be real and the pay must be reasonable — the IRS "
            "scrutinizes this closely, so documented job descriptions, "
            "timesheets, and actual payment records are essential. "
            "Bonus: the child's earned wages can fund a Roth IRA."
        ),

        "documentation": [
            "Written job description for each child employee",
            "Timesheets or work logs showing hours and tasks performed",
            "Payroll records — actual checks or ACH transfers to child's account",
            "W-2 issued to child showing wages (Box 1) and FICA treatment",
            "Form 941 — confirm FICA exemption applied correctly for qualifying sole prop/partnership",
            "Child's tax return — confirm wages reported and standard deduction applied",
        ],

        "cpa_handoff": [
            "§162: wages deductible by practice as ordinary business expense — must be reasonable and bona fide",
            "§3121(b)(3)(A): FICA exempt for child under 18 working for parent's sole prop or parent partnership",
            "S-Corp/C-Corp: NO FICA exemption — child's wages subject to full FICA even if under 18",
            "Standard deduction: $14,600 (2024) shelters first $14,600 of child's wages from income tax",
            "Kiddie tax §1(g): applies to unearned income only — wages are earned income, taxed at child's rate",
            "Roth IRA opportunity: child can contribute up to earned wages (capped at $7,000 in 2024) to Roth IRA",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires related-party role, compensation, and documentation review before implementation.",
        ],

    },

    {
        "id": "DTTS-041-executive-bonus-plan-with-gross-up",
        "name": "Executive Bonus Plan (with Gross-Up)",
        "_id": "69bdb3dee5397a28d4543fcb",
        "irc": "IRC §162, §61, §7702",
        "category": "Compensation & Benefits",
        "overlap_group": "IRC §162 Executive Bonus Plans",
        "applicable_forms": ["1120", "1120S"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("SIG_W2_PRESENT", False)
        ),

        "materiality_fn": lambda s: (
            60 if s.get("SIG_HAS_S_CORP_VERIFIED", False) and s.get("SIG_HIGH_TAX_LIABILITY", False) else 40
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_EXEC_BONUS_TOTAL_DEDUCTION", 0) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("Q_EXEC_BONUS_TOTAL_DEDUCTION", 0) * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 30,
        "complexity": 25,
        "audit_friction": 15,

        "plain_english": (
            "An executive bonus plan — sometimes called a §162 bonus plan — "
            "allows a dental practice to pay a bonus to the owner-dentist "
            "that is used to fund a personally-owned life insurance policy. "
            "The practice deducts the bonus as ordinary compensation expense, "
            "and the policy is owned by the executive (not the business), "
            "so the cash value grows tax-deferred and the death benefit "
            "passes to heirs tax-free. The 'gross-up' layer adds a second "
            "bonus to cover the income tax on the first — so the executive "
            "ends up with the full premium going into the policy on a "
            "tax-neutral basis. The result is a practice deduction today "
            "plus tax-deferred wealth accumulation in a personally-owned "
            "policy with no corporate ownership complications."
        ),

        "documentation": [
            "Executive bonus plan agreement (written plan document)",
            "Life insurance policy owned by executive — not the practice",
            "W-2 showing bonus included in Box 1 as taxable wages",
            "Gross-up calculation worksheet showing total bonus and tax coverage",
            "Practice payroll records confirming both bonus layers paid",
            "Policy premium receipts confirming payment from executive's personal funds",
        ],

        "cpa_handoff": [
            "§162 bonus plan: practice pays premium bonus to executive as W-2 compensation",
            "Executive owns the policy — no EOLI/§101(j) notice/consent issues",
            "Gross-up: second bonus covers income tax on first — executive receives policy tax-neutral",
            "Practice deducts both bonus layers as ordinary compensation expense",
            "Cash value grows tax-deferred inside policy; death benefit tax-free to beneficiaries",
            "Golden handcuffs option: add vesting/repayment provisions to retain key staff",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-042-deducting-start-up-costs",
        "name": "Deducting Start-Up Costs",
        "_id": "69bdb3dfe5397a28d4543fd2",
        "irc": "IRC §195, §195(a), §195(b), §195(c), §248, §709",
        "category": "General Planning",
        "overlap_group": None,
        "applicable_forms": ["1040", "1120", "1120S", "1065"],
        "phase_1_eligible": True,
        "estimate_confidence": "MODERATE",

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_HIGH_INCOME", False)
        ),

        "materiality_fn": lambda s: (
            45 if s.get("SIG_HAS_S_CORP_VERIFIED", False) or s.get("SIG_SCHEDULE_C_PRESENT", False) else 25
        ),

        "fed_savings_fn": lambda s: (
    min(5_000, s.get("_agi", 0) * 0.005) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    min(5_000, s.get("_agi", 0) * 0.005) * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 5,

        "plain_english": (
            "When a dentist opens or acquires a new practice, the costs "
            "incurred before the business officially opens — market research, "
            "training, advertising, professional fees for the acquisition — "
            "are start-up costs that must be capitalized under §195. "
            "However, the tax code allows an election to immediately deduct "
            "up to $5,000 of those costs in the first year the business "
            "begins, with the remainder amortized over 15 years. The "
            "$5,000 immediate deduction phases out dollar-for-dollar when "
            "total start-up costs exceed $50,000. This is a frequently "
            "missed election — practitioners often capitalize these costs "
            "and never make the §195 election, delaying deductions "
            "unnecessarily. Organization costs for forming the entity "
            "(§248 for corporations, §709 for partnerships) receive the "
            "same treatment and should be tracked separately."
        ),

        "documentation": [
            "§195 election statement attached to return for first year of business",
            "Start-up cost schedule — itemized list of qualifying pre-opening costs",
            "Organization cost schedule — separately tracked from start-up costs",
            "180-month amortization schedule for remainder of costs after first-year deduction",
            "Practice acquisition closing documents (if costs relate to acquiring existing practice)",
        ],

        "cpa_handoff": [
            "§195: start-up costs must be capitalized — deductible only via §195 election",
            "Election: deduct up to $5,000 in year business begins; phase-out when total costs >$50K",
            "Phase-out: $1 reduction for each $1 over $50K — at $55K+, zero immediate deduction",
            "Remainder: amortize over 180 months starting month business begins",
            "Organization costs: separate election under §248 (corp) or §709 (partnership) — same $5K/$180M",
            "Common miss: no election made — costs sit on balance sheet, amortization never starts",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-043-oil-gas-idc",
        "name": "Oil & Gas Intangible Drilling Cost Deduction",
        "irc": "IRC §263(c)",
        "category": "Alternative Investments",
        "overlap_group": "Oil & Gas",
        "applicable_forms": ["1040", "1120"],
        "phase_1_eligible": False,  # Requires confirmed oil & gas investment

        "eligibility_logic": lambda s: (
            s.get("SIG_HIGH_INCOME", False) and
            s.get("Q_INVESTMENT_PORTFOLIO", 0) > 100_000  # Must have confirmed investment portfolio
        ),

        "materiality_fn": lambda s: (
            100 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
            85 if s.get("SIG_HIGH_INCOME") else
            70
        ),
        "fed_savings_fn": lambda s: (
            s.get("Q_INVESTMENT_PORTFOLIO", 100_000) * 0.70 * s.get("_fed_marginal_rate", 0)
        ),

        "state_savings_fn": lambda s: (
            100000 * 0.70 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
        ),

        "speed_days": 60,
        "complexity": 40,
        "audit_friction": 15,

        "plain_english": (
            "Oil and gas partnerships allow investors to deduct a large portion of "
            "intangible drilling costs immediately."
        ),

        "documentation": [
            "Investment partnership agreement",
            "Schedule K-1 with IDC allocation"
        ],

        "cpa_handoff": [
            "Verify IDC deduction eligibility",
            "Review partnership allocations"
        ],

        "prerequisites": ["Investment in oil and gas drilling partnership"],
    },

    {
        "id": "DTTS-044-in-plan-roth-rollover",
        "name": "In-Plan Roth Rollover",
        "_id": "69bdb3dfe5397a28d4543fd9",
        "irc": "IRC §402A, §402A(c)(4), §408A, §408A(d)(3)",
        "category": "Retirement Plans",
        "overlap_group": "Roth Conversion Strategy",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_RETIREMENT_PLAN", False) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False)
        ),

        "materiality_fn": lambda s: (
            60 if s.get("SIG_HAS_S_CORP") and s.get("SIG_HAS_RETIREMENT_PLAN") else
            50 if s.get("SIG_VERY_HIGH_INCOME") else
            35 if s.get("SIG_HIGH_INCOME") else
            25
        ),

        "fed_savings_fn": lambda s: (
            max(200_000 * (s.get("_fed_marginal_rate", 0) - 0.22), 0)
        ),

        "state_savings_fn": lambda s: (
            0
        ),

        "speed_days": 21,
        "complexity": 20,
        "audit_friction": 10,

        "plain_english": (
            "An in-plan Roth rollover allows a dentist to convert pre-tax "
            "retirement plan balances — 401(k), profit-sharing — into a "
            "designated Roth account within the same plan. The converted "
            "amount is taxable as ordinary income in the year of conversion, "
            "but all future growth and qualified distributions are completely "
            "tax-free. Under SECURE 2.0 (effective 2024), Roth 401(k) "
            "accounts no longer have required minimum distributions — "
            "allowing the balance to compound tax-free indefinitely. "
            "The strategy is most powerful when done in a year with lower "
            "than usual income or when large deductions (like cash balance "
            "contributions or bonus depreciation) are available to offset "
            "the conversion income. The mega backdoor Roth variant — "
            "converting after-tax 401(k) contributions — can add up to "
            "$43,500 of additional Roth funding annually beyond the "
            "standard contribution limit."
        ),

        "documentation": [
            "Plan document confirming in-plan Roth rollover feature is enabled",
            "Form 1099-R — issued for converted amount (code G or H)",
            "Form 8606 — tracks Roth conversion basis",
            "Conversion election form submitted to plan administrator",
            "Tax projection showing income impact of conversion in rollover year",
            "5-year holding period tracking for each conversion (for qualified distribution eligibility)",
        ],

        "cpa_handoff": [
            "§402A(c)(4): in-plan Roth rollover — pre-tax plan balance converted to Roth within same plan",
            "Tax treatment: converted amount includable in gross income; no 10% early withdrawal penalty",
            "SECURE 2.0: Roth 401(k) no longer subject to RMDs effective 2024 — major long-term benefit",
            "Timing: convert in years with large deductions (cash balance, §179) to minimize tax cost",
            "Mega backdoor Roth: after-tax 401(k) contributions → in-plan Roth rollover; up to $43,500 (2024)",
            "Form 1099-R issued; Form 8606 tracks basis; 5-year clock starts fresh for each conversion",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],

    },

    {
        "id": "DTTS-045-business-credit-card-optimization",
        "name": "Business Credit Card Optimization",
        "_id": "69bdb3e0e5397a28d4543fe0",
        "irc": "IRC §162, §274, §274(d)",
        "category": "Credits & Incentives",
        "overlap_group": None,
        "applicable_forms": ["1040", "1120", "1120S", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_HIGH_INCOME", False) and
            (s.get("SIG_PROFESSIONAL_FEES_PRESENT", False) or
             s.get("SIG_TRAVEL_PRESENT", False) or
             s.get("SIG_AUTO_TRUCK_PRESENT", False))
        ),

        "materiality_fn": lambda s: (
            40 if s.get("SIG_TRAVEL_PRESENT", False) and s.get("SIG_PROFESSIONAL_FEES_PRESENT", False) else 25
        ),

        "fed_savings_fn": lambda s: (
    s.get("_obi", 0) * 0.03 * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("_obi", 0) * 0.03 * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 7,
        "complexity": 5,
        "audit_friction": 5,

        "plain_english": (
            "Using a dedicated business credit card for all practice expenses "
            "is a low-complexity strategy that creates real tax and cash flow "
            "benefits. Business expenses are deductible when charged — not "
            "when the bill is paid — so charging large deductible items in "
            "December pulls those deductions into the current tax year even "
            "if payment doesn't happen until January. A dedicated card also "
            "creates a clean documentation trail for IRS substantiation "
            "purposes, eliminating mixed-use issues. Business rewards "
            "programs return 1.5–3% on spending as cash back or points "
            "that the IRS treats as a purchase price reduction — not taxable "
            "income. For a practice spending $150,000–$300,000 annually on "
            "deductible business expenses, this strategy generates meaningful "
            "timing benefits and non-taxable rewards with virtually no "
            "implementation complexity."
        ),

        "documentation": [
            "Dedicated business credit card statements (separate from personal)",
            "Business purpose notations on statements or expense log",
            "§274(d) substantiation for travel, meals: amount, date, place, purpose, attendees",
            "Year-end charge log for December acceleration strategy",
            "Annual rewards summary — confirm non-taxable treatment (price reduction, not income)",
        ],

        "cpa_handoff": [
            "§162: credit card charges deductible when incurred (charge date) — not when paid",
            "Year-end acceleration: Dec 31 charges deductible in current year regardless of payment date",
            "§274(d): substantiation required for travel/meals — card statement + purpose notation sufficient",
            "Rewards: IRS treats business card rewards as purchase price reduction — generally not taxable income",
            "Dedicated card: eliminates personal/business mixed-use issues and simplifies audit trail",
            "Separate card per entity if multi-entity — critical for correct expense allocation to each entity",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-046-asset-sale-to-intentionally-defective-grantor-trust",
        "name": "Asset Sale to Intentionally Defective Grantor Trust (IDGT)",
        "_id": "69bdb3e0e5397a28d4543fe8",
        "irc": "IRC §§671–679, §2511, §2512",
        "category": "Trusts & Estate",
        "overlap_group": "Grantor Trust Planning",
        "applicable_forms": ["1041", "709"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("SIG_DEPENDENTS_PRESENT", False) and
            s.get("_agi", 0) > 750_000
        ),

        "materiality_fn": lambda s: (
            70 if s.get("_agi", 0) > 1_000_000 and s.get("SIG_DEPENDENTS_PRESENT", False) else 50
        ),

        "fed_savings_fn": lambda s: (
            2_000_000 * 0.40 * 0.35
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 120,
        "complexity": 70,
        "audit_friction": 20,

        "plain_english": (
            "An Intentionally Defective Grantor Trust (IDGT) is one of the "
            "most powerful estate planning tools available for high-income "
            "dentists with appreciating assets. The trust is 'defective' on "
            "purpose — it is structured so that the grantor (the dentist) "
            "is treated as the owner for income tax purposes, but the assets "
            "inside the trust are completely outside the taxable estate. "
            "The dentist sells appreciating assets — practice equity, "
            "investment property, or a management company interest — to "
            "the trust in exchange for an installment note at the IRS "
            "minimum interest rate. Because the grantor is selling to "
            "their own grantor trust, no capital gains are recognized. "
            "All future appreciation on the sold assets compounds inside "
            "the trust and eventually passes to heirs free of estate tax. "
            "As an added benefit, when the grantor pays the trust's income "
            "tax each year, they are making additional tax-free transfers "
            "to the trust beneficiaries."
        ),

        "documentation": [
            "IDGT trust document with §675 swap power or other grantor trust trigger",
            "Seed gift documentation — Form 709 for initial 10% gift to trust",
            "Installment sale agreement between grantor and trust at AFR",
            "Qualified appraisal of assets sold to trust at date of sale",
            "Annual AFR documentation at time of note issuance",
            "Grantor trust income tax reporting — all trust income on grantor's Form 1040",
        ],

        "cpa_handoff": [
            "IDGT: grantor trust for income tax (§671) + completed gift for estate tax = powerful asymmetry",
            "Sale to IDGT: not a taxable event — grantor selling to themselves (§671 attribution)",
            "No capital gains at sale; future appreciation inside trust passes to heirs estate-tax-free",
            "Note: trust pays AFR interest to grantor; grantor receiving own trust's interest = not taxable",
            "Grantor pays trust's income tax annually — additional estate depletion and wealth transfer",
            "Seed gift (~10% of sale price) required: trust must have independent economic substance",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],

    },

    {
        "id": "DTTS-047-1042-rollover-sale-to-esop",
        "name": "1042 Rollover (Sale to ESOP)",
        "_id": "69bdb3e2e5397a28d4543ff2",
        "irc": "IRC §1042, §1042(a), §1042(b), §1042(c), §1042(d), §4975(e)(7)",
        "category": "Exit & Sale",
        "overlap_group": "ESOP Exit Strategy",
        "applicable_forms": ["1120", "1040"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_C_CORP", False) and
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False)
        ),

        "materiality_fn": lambda s: (
            80 if s.get("SIG_HAS_C_CORP", False) and s.get("SIG_VERY_HIGH_INCOME", False) else 40
        ),

        "fed_savings_fn": lambda s: (
            2_800_000 * 0.238 * 0.20
        ),

        "state_savings_fn": lambda s: (
            0
        ),

        "speed_days": 180,
        "complexity": 80,
        "audit_friction": 25,

        "plain_english": (
            "The §1042 rollover allows a C-Corporation owner to sell stock "
            "to an Employee Stock Ownership Plan (ESOP) and defer all "
            "capital gains taxes — potentially indefinitely. The seller "
            "reinvests the proceeds into stocks or bonds of other domestic "
            "operating companies (qualified replacement property), and the "
            "gain is deferred until those replacement investments are sold. "
            "The ESOP must own at least 30% of the company's stock after "
            "the sale, and the seller must have held the stock for at least "
            "three years. This is one of the most powerful exit planning "
            "strategies available — a dental practice owner selling a "
            "$3M C-Corp interest could defer over $600,000 in capital "
            "gains taxes. The strategy requires the practice to be "
            "structured as a C-Corporation and involves significant "
            "ESOP administration and legal complexity."
        ),

        "documentation": [
            "§1042 election statement attached to seller's Form 1040 for year of sale",
            "Form 8308 — Report of a Sale or Exchange of Certain Partnership Interests (if applicable)",
            "QRP purchase documentation within replacement period window",
            "ESOP plan document and trust agreement",
            "Form 5500 — annual ESOP plan reporting",
            "Stock holding period documentation — 3-year minimum hold confirmed",
            "30% ownership threshold analysis post-sale",
        ],

        "cpa_handoff": [
            "§1042: seller defers capital gain on C-Corp stock sale if proceeds reinvested in QRP",
            "Requirements: C-Corp stock; 3-year hold; ESOP owns 30%+ after sale; QRP election made",
            "QRP: domestic operating corp stocks/bonds only — not mutual funds, gov't bonds, or seller's company",
            "Basis carryover: QRP takes seller's carryover basis — gain deferred until QRP sold",
            "S-Corp: cannot use §1042; S-Corp ESOPs governed by §409(p) anti-abuse rules instead",
            "ESOP funding: corp contributions to ESOP to fund purchase are tax-deductible — additional benefit",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-048-1202-gain-exclusion-stacking-via-multiple-entities",
        "name": "1202 Gain Exclusion Stacking via Multiple Entities",
        "_id": "69bdb3e3e5397a28d4543ffc",
        "irc": "IRC §1202, §1202(a), §1202(b), §1202(c), §1202(e), §1202(h)",
        "category": "General Planning",
        "overlap_group": "Section 1202 (QSBS) Planning",
        "applicable_forms": ["1120", "1040"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_C_CORP", False) and
            s.get("SIG_MULTI_ENTITY", False) and
            s.get("SIG_VERY_HIGH_INCOME", False)
        ),

        "materiality_fn": lambda s: (
            75 if s.get("SIG_HAS_C_CORP", False) and s.get("SIG_MULTI_ENTITY", False) and s.get("SIG_VERY_HIGH_INCOME", False) else 40
        ),

        "fed_savings_fn": lambda s: (
            10_000_000 * 0.238 * 0.20
        ),

        "state_savings_fn": lambda s: (
            0
        ),

        "speed_days": 180,
        "complexity": 65,
        "audit_friction": 30,

        "plain_english": (
            "Section 1202 allows investors in qualifying small business "
            "C-Corporation stock to exclude up to 100% of their capital "
            "gains from federal tax — up to $10 million per taxpayer per "
            "issuing company. The 'stacking' strategy multiplies this "
            "exclusion by transferring shares to a spouse, children, or "
            "trusts — each of whom gets their own $10 million exclusion "
            "limit for the same stock. For a dentist who structures a "
            "non-clinical management company or real estate entity as a "
            "C-Corporation and eventually sells it, this exclusion can "
            "eliminate millions in capital gains taxes entirely. The key "
            "requirements are that the stock must be originally issued "
            "(not purchased on the secondary market), the corporation's "
            "gross assets must be under $50 million at issuance, and "
            "the stock must be held for more than five years. "
            "Important caveat: dental practices as health service businesses "
            "may be excluded — non-clinical entities in the structure "
            "are more likely to qualify."
        ),

        "documentation": [
            "QSBS certification from issuing corporation at time of stock issuance",
            "Gross assets documentation: corporation assets ≤$50M at issuance and immediately after",
            "Original issue confirmation — stock received directly from corporation (not secondary market)",
            "5-year holding period tracking per shareholder per entity",
            "Active business analysis — confirm ≥80% of assets in qualifying active trade/business",
            "Stacking transfer documentation — gift or sale records for transferred shares",
            "State conformity analysis — several major states do not conform to §1202",
        ],

        "cpa_handoff": [
            "§1202: 100% exclusion on QSBS gain (stock acquired after 9/27/2010) up to $10M per taxpayer per issuer",
            "Requirements: C-Corp; gross assets ≤$50M at issuance; original issue; 5-year hold; active business",
            "Dentistry health exclusion: §1202(e)(3)(A) excludes health services — clinical dental practice may NOT qualify",
            "Non-clinical entities (management co, real estate, lab) more likely to qualify — analyze separately",
            "Stacking: each taxpayer (spouse, children, trusts) gets own $10M exclusion per issuer",
            "State non-conformers: CA, NY, NJ, PA do not conform — large state tax still owed despite federal exclusion",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-049-oil-gas-intangible-drilling-costs-idc",
        "name": "Oil & Gas Intangible Drilling Costs (IDC)",
        "_id": "69bdb3e4e5397a28d4544004",
        "irc": "IRC §263(c), §469(c)(3), §613A, §57(a)(2)",
        "category": "General Planning",
        "overlap_group": None,
        "applicable_forms": ["1040", "1120"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("_agi", 0) > 500_000
        ),

        "materiality_fn": lambda s: (
            60 if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("_total_tax", 0) > 150_000 else 40
        ),

        "fed_savings_fn": lambda s: (
            140_000 * s.get("_fed_marginal_rate", 0) * 0.20
        ),

        "state_savings_fn": lambda s: (
            0
        ),

        "speed_days": 60,
        "complexity": 45,
        "audit_friction": 25,

        "plain_english": (
            "When a dentist invests in an oil and gas working interest, "
            "approximately 65–80% of the investment qualifies as intangible "
            "drilling costs (IDC) — deductible in full in the year the well "
            "is drilled under IRC §263(c). For a high-income dentist facing "
            "a $200,000 federal tax bill, a $200,000 oil and gas investment "
            "could generate roughly $140,000 in first-year deductions. "
            "The critical planning point is the working interest exception "
            "under §469(c)(3): unlike most investments, oil and gas working "
            "interests held directly (not through an LLC or limited partnership) "
            "are exempt from the passive activity rules — meaning IDC losses "
            "can offset ordinary dental practice income directly. "
            "The remaining tangible costs depreciate over seven years, and "
            "future production income benefits from percentage depletion. "
            "AMT exposure should be confirmed before implementation."
        ),

        "documentation": [
            "Working interest agreement confirming direct ownership (not LLC/LP structure for §469 exception)",
            "IDC election statement — confirm operator made §263(c) election",
            "Investment breakdown: IDC vs. tangible costs with percentage allocation",
            "Percentage depletion schedule (§613A) for ongoing production income",
            "AMT analysis — IDC is §57(a)(2) preference item; confirm AMT exposure",
            "Form 4562 for tangible cost depreciation over 7-year MACRS",
        ],

        "cpa_handoff": [
            "§263(c): IDC election allows immediate deduction of 65–80% of well investment in year 1",
            "§469(c)(3): working interest NOT passive — IDC losses offset ordinary income directly",
            "Working interest exception requires direct ownership — LLC/LP with limited liability = passive",
            "§57(a)(2): excess IDC is AMT preference item — confirm AMT exposure before recommending",
            "§613A: percentage depletion (15% small producers) shelters ongoing production income",
            "Tangible costs: remaining 20–35% depreciated over 7-year MACRS; not deductible as IDC",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-050-group-health-insurance-via-c-corp",
        "name": "Group Health Insurance via C-Corp",
        "_id": "69bdb3e4e5397a28d4544010",
        "irc": "IRC §105, §105(b), §106, §162, §125",
        "category": "Entity & Structuring",
        "overlap_group": "Health Insurance Deduction",
        "applicable_forms": ["1120"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_C_CORP", False) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False)
        ),

        "materiality_fn": lambda s: (
        55 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HAS_C_CORP") else
        35 if s.get("SIG_HIGH_INCOME") or s.get("SIG_HAS_C_CORP") else
        25
    ),

        "fed_savings_fn": lambda s: (
    (s.get("Q_HEALTH_PREMIUM", 0) * 1.0765) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("Q_HEALTH_PREMIUM", 0) * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 30,
        "complexity": 25,
        "audit_friction": 10,

        "plain_english": (
            "A C-Corporation can provide group health insurance to "
            "owner-employees with better tax treatment than any other "
            "entity structure. The corporation deducts 100% of premiums "
            "as a business expense, and the owner-employee excludes the "
            "premium value from their gross income entirely — no income "
            "tax, no FICA. This is more favorable than an S-Corporation, "
            "where shareholders owning more than 2% must include health "
            "premiums in their W-2 wages (even though the deduction is "
            "then available on the personal return). A C-Corp can also "
            "establish a Health Reimbursement Arrangement (HRA) to "
            "reimburse out-of-pocket medical expenses tax-free. "
            "For a dentist with a management company or holding entity "
            "structured as a C-Corporation, routing health insurance "
            "through that entity produces the cleanest tax result."
        ),

        "documentation": [
            "Group health insurance policy owned by C-Corporation",
            "Corporate board resolution authorizing health benefit plan",
            "HRA plan document if out-of-pocket reimbursements included",
            "W-2 for owner-employee confirming premiums NOT included in Box 1 (C-Corp treatment)",
            "Cafeteria plan document if §125 election used for employee premium elections",
            "Premium payment records showing C-Corp as policy holder and payor",
        ],

        "cpa_handoff": [
            "§106: employer-paid health premiums excluded from employee gross income — no income tax, no FICA",
            "C-Corp advantage over S-Corp: >2% S-Corp shareholder must include premiums in W-2; C-Corp avoids this",
            "§162: C-Corp deducts 100% of premiums as business expense — no AGI floor (unlike §213 individual)",
            "HRA: C-Corp can reimburse out-of-pocket medical expenses; employer deducts, employee excludes",
            "§125 cafeteria plan: can layer pre-tax employee elections on top of employer-paid coverage",
            "Coordinate with DTTS-034 (EOLI) and management company structuring if C-Corp entity being built",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires policy design, underwriting/actuarial review, and compliance documentation before implementation.",
        ],

    },

    {
        "id": "DTTS-051-non-qualified-deferred-compensation-nqdc-plan",
        "name": "Non-Qualified Deferred Compensation (NQDC) Plan",
        "_id": "69bdb3e5e5397a28d454401d",
        "irc": "IRC §409A, §409A(a), §409A(a)(2), §409A(a)(4), §457(f), §83",
        "category": "Compensation & Benefits",
        "overlap_group": "Deferred Compensation",
        "applicable_forms": ["1120", "1120S"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("SIG_W2_PRESENT", False)
        ),

        "materiality_fn": lambda s: (
            60 if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("SIG_W2_PRESENT", False) else 40
        ),

        "fed_savings_fn": lambda s: (
    s.get("_obi", 0) * 0.10 * max(0, s.get("_fed_marginal_rate", 0) - 0.22)
),

        "state_savings_fn": lambda s: (
    0
),

        "speed_days": 45,
        "complexity": 35,
        "audit_friction": 20,

        "plain_english": (
            "A Non-Qualified Deferred Compensation (NQDC) plan allows a "
            "high-income dentist to defer a portion of current compensation "
            "to future years — paying tax when the money is received in "
            "retirement rather than when it is earned today. For a dentist "
            "currently in the 37% bracket who expects to be in the 22% "
            "bracket in retirement, deferring $100,000 of salary saves "
            "$15,000 in federal tax on that amount alone. The plan must "
            "comply strictly with §409A — elections must be made before "
            "December 31 of the year before the compensation is earned, "
            "and distributions are limited to specific triggering events "
            "like separation from service or a fixed payment schedule. "
            "Unlike qualified retirement plans, NQDC balances are unsecured "
            "obligations of the practice — the dentist is a general creditor. "
            "Violations of §409A trigger immediate income inclusion plus a "
            "20% excise tax and interest, so plan design must be precise."
        ),

        "documentation": [
            "Written NQDC plan document compliant with §409A",
            "Deferral election form executed before Dec 31 of prior year",
            "Distribution trigger documentation (separation, fixed schedule, etc.)",
            "Annual account balance statements showing deferred amounts",
            "W-2 confirming deferred amounts excluded from Box 1 in deferral year",
            "§409A compliance review by qualified ERISA/tax counsel",
        ],

        "cpa_handoff": [
            "§409A: strict compliance required — election before Dec 31 prior year; limited distribution events",
            "§409A violation: immediate income inclusion + 20% excise tax + underpayment interest — severe",
            "Corporate deduction: practice deducts when compensation IS DISTRIBUTED (not when deferred)",
            "Tax benefit: defer compensation from high-income years to lower-income retirement years",
            "Unsecured obligation: NQDC balance is general creditor claim — not protected like qualified plans",
            "State trap: CA taxes NQDC at deferral if CA resident when deferred — confirm state rules",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-052-754-basis-adjustment-election-for-partnerships",
        "name": "754 Basis Adjustment Election for Partnerships",
        "_id": "69bdb3e5e5397a28d4544026",
        "irc": "IRC §754, §743(b), §734(b), §755, §732",
        "category": "Entity & Structuring",
        "overlap_group": None,
        "applicable_forms": ["1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_PARTNERSHIP", False) and
            s["SIG_K1_PRESENT"] and
            s.get("SIG_HIGH_INCOME", False)
        ),

        "materiality_fn": lambda s: (
            55 if s.get("SIG_MULTI_ENTITY", False) and s.get("SIG_HAS_DEPRECIATION", False) else 35
        ),

        "fed_savings_fn": lambda s: (
    s.get("_depreciation", 0) * 0.30 * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("_depreciation", 0) * 0.30 * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 30,
        "complexity": 35,
        "audit_friction": 15,

        "plain_english": (
            "When a dentist buys into a partnership or dental group practice, "
            "they typically pay fair market value for their interest — but "
            "the partnership's assets still reflect historical (often much "
            "lower) book values. Without a §754 election, the new partner "
            "would eventually be taxed on appreciation that occurred before "
            "they joined. The §754 election fixes this by adjusting the "
            "inside basis of partnership assets to match what the new "
            "partner actually paid — eliminating their exposure to "
            "pre-entry built-in gains. The election also creates additional "
            "depreciation deductions for the new partner on the step-up "
            "amount. The same election applies when a partner dies: "
            "combined with the §1014 stepped-up outside basis at death, "
            "a §754 election eliminates built-in gain on the decedent's "
            "share of partnership assets. Once made, the election is "
            "permanent and applies to all future transfers."
        ),

        "documentation": [
            "§754 election statement attached to Form 1065 for year of triggering transfer",
            "§743(b) adjustment calculation — purchase price vs. proportionate inside basis",
            "§755 allocation of basis adjustment among partnership assets",
            "Partner basis schedule before and after election",
            "Depreciation schedule for §743(b) step-up amount (allocated to depreciable assets)",
            "Form 1065 Schedule K-1 reflecting partner's adjusted inside basis",
        ],

        "cpa_handoff": [
            "§754 election: adjusts inside basis of partnership assets to match new partner's outside basis",
            "§743(b): triggered by sale/transfer of partnership interest; eliminates pre-entry built-in gain",
            "Election permanent: once made, applies to ALL future transfers — cannot revoke without IRS consent",
            "Death + §754: §1014 stepped-up outside basis + §754 inside step-up = eliminates built-in gain entirely",
            "§734(b): distribution-triggered adjustment — protects remaining partners from basis distortion",
            "§743(d) mandatory: if built-in loss >$250K, adjustment required regardless of §754 election",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-054-457-b-non-governmental-deferred-comp-plan",
        "name": "457(b) Non-Governmental Deferred Comp Plan",
        "_id": "69bdb3e6e5397a28d454402f",
        "irc": "IRC §457, §457(b), §457(b)(2), §457(b)(3), §457(e)(12)",
        "category": "General Planning",
        "overlap_group": "Deferred Compensation",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("SIG_W2_PRESENT", False)
        ),

        "materiality_fn": lambda s: (
        50 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        30 if s.get("SIG_HIGH_INCOME") or s.get("SIG_HIGH_TAX_LIABILITY") else
        20
    ),

        "fed_savings_fn": lambda s: (
    min(_LIM["elective_deferral_limit"], s.get("_wages", 0) * 0.10) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    min(_LIM["elective_deferral_limit"], s.get("_wages", 0) * 0.10) * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 21,
        "complexity": 20,
        "audit_friction": 10,

        "plain_english": (
            "Dentists employed by tax-exempt organizations — dental schools, "
            "hospital-affiliated practices, or federally qualified health "
            "centers — may have access to a §457(b) deferred compensation "
            "plan in addition to their 401(k) or 403(b). The key advantage: "
            "§457(b) contributions are completely separate from and do not "
            "reduce contributions to a 401(k) or 403(b) plan — meaning "
            "a dentist in this situation can defer an additional $23,000 "
            "(or $30,500 if age 50+) on top of their other retirement "
            "plan contributions. The deferred amounts are excluded from "
            "gross income until distributed. The non-governmental version "
            "differs from the governmental version in that assets remain "
            "general assets of the employer — the participant is an "
            "unsecured creditor. A special three-year catch-up provision "
            "allows up to double the annual limit in the final three years "
            "before normal retirement age for participants who under-deferred "
            "in prior years."
        ),

        "documentation": [
            "§457(b) plan document (maintained by tax-exempt employer)",
            "Deferral election form executed before compensation is earned",
            "Annual contribution limit calculation — confirm $23,000/$30,500 limit",
            "Stacking analysis — confirm §457(b) limit does not reduce §401(k)/§403(b) limits",
            "W-2 Box 12 Code G — §457(b) deferrals reported",
            "Three-year catch-up calculation if applicable",
        ],

        "cpa_handoff": [
            "§457(b): eligible for dentists employed by 501(c)(3) tax-exempt organizations only",
            "Contribution limit: $23,000 (2024); $30,500 age 50+; $46,000 three-year catch-up",
            "§457(e)(12): §457(b) limits are INDEPENDENT of §401(k)/§403(b) limits — can stack",
            "Non-governmental plan: assets remain general assets of employer — unsecured creditor risk",
            "Governmental §457(b): assets held in trust — different protection; different rules",
            "W-2 reporting: deferrals in Box 12 Code G; excluded from Box 1 income",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-055-offshore-trust-with-u-s-reporting-compliance",
        "name": "Offshore Trust with U.S. Reporting Compliance",
        "_id": "69bdb3e6e5397a28d4544038",
        "irc": "IRC §679, §6048, §6048(a), §6048(b), §6048(c), §6677",
        "category": "Trusts & Estate",
        "overlap_group": None,
        "applicable_forms": ["1041", "3520", "3520-A", "8938"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("_agi", 0) > 1_000_000
        ),

        "materiality_fn": lambda s: (
            50 if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("_agi", 0) > 1_500_000 else 30
        ),

        "fed_savings_fn": lambda s: (
            2_000_000 * 0.40 * 0.25
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 180,
        "complexity": 80,
        "audit_friction": 35,

        "plain_english": (
            "A properly structured offshore trust with full US reporting "
            "compliance is primarily an asset protection and estate planning "
            "tool — not an income tax reduction strategy. Under US tax law, "
            "a US person who creates a foreign trust with US beneficiaries "
            "is treated as the trust's grantor and pays tax on all trust "
            "income at their normal US rates. The benefit comes from the "
            "strong creditor protection that foreign trust law provides and "
            "the potential to remove assets from the taxable estate. "
            "This strategy carries the most demanding compliance obligations "
            "of any structure discussed — Form 3520 and Form 3520-A must be "
            "filed annually, FBAR and FATCA reporting apply, and failure "
            "to comply can trigger penalties of 35% of the trust's gross "
            "assets. This is exclusively for dentists with very high net "
            "worth, genuine asset protection objectives, and top-tier "
            "international tax counsel."
        ),

        "documentation": [
            "Form 3520 — creation/transfer to foreign trust (year of establishment)",
            "Form 3520-A — annual information return of foreign grantor trust",
            "FinCEN Form 114 (FBAR) — annual filing if foreign accounts >$10,000",
            "Form 8938 (FATCA) — if specified foreign financial assets exceed reporting thresholds",
            "Foreign trust document — jurisdiction, trustee, beneficiary designations",
            "Asset transfer records and valuations at date of funding",
        ],

        "cpa_handoff": [
            "§679: US grantor creating foreign trust with US beneficiaries = grantor trust; income taxed to grantor",
            "No US income tax reduction from offshore structure alone — grantor pays full US tax",
            "§6048: Form 3520 required year of creation/transfer AND each year distributions received",
            "Form 3520-A: annual trust information return — filed by trust or US owner by March 15",
            "§6677 penalties: 35% of gross reportable amount for failures — among highest IRS penalties",
            "FBAR + Form 8938: both required if foreign account/asset thresholds met — separate filings",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],

    },

    {
        "id": "DTTS-057-roth-conversions-during-low-income-years",
        "name": "Roth Conversions During Low-Income Years",
        "_id": "69bdb3e7e5397a28d4544040",
        "irc": "IRC §408A, §408A(d)(3), §402A, §72(t)",
        "category": "Retirement Plans",
        "overlap_group": "Roth Conversion Strategy",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_RETIREMENT_PLAN", False) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False)
        ),

        "materiality_fn": lambda s: (
            65 if s.get("SIG_RETIREMENT_UNDERFUNDED", False) and s.get("SIG_HIGH_TAX_LIABILITY", False) else
            45 if s.get("SIG_HAS_RETIREMENT_PLAN", False) else 25
        ),

        "fed_savings_fn": lambda s: (
            max(150_000 * (s.get("_fed_marginal_rate", 0) - 0.22), 0)
        ),

        "state_savings_fn": lambda s: (
            0
        ),

        "speed_days": 14,
        "complexity": 15,
        "audit_friction": 5,

        "plain_english": (
            "A Roth conversion moves pre-tax retirement savings into a "
            "Roth IRA — paying ordinary income tax on the converted amount "
            "now, in exchange for tax-free growth and distributions forever. "
            "The strategy is most powerful when done during low-income years: "
            "a year with a large business loss, significant bonus depreciation "
            "deductions, or a gap between leaving practice and starting "
            "required minimum distributions. The key technique is bracket "
            "filling — converting only enough to reach the top of the current "
            "tax bracket without crossing into the next. A dentist who "
            "normally pays 37% but has a year at 22% can convert $150,000 "
            "and save $22,500 in lifetime taxes on that amount. "
            "No income limit applies to conversions, there is no 10% penalty "
            "on conversion amounts, and Roth IRAs have no required minimum "
            "distributions — making them ideal for estate planning as well."
        ),

        "documentation": [
            "Form 1099-R — issued by IRA custodian for converted amount (Code 2 or 7)",
            "Form 8606 — tracks Roth conversion basis; filed with tax return",
            "Conversion amount analysis — bracket filling calculation",
            "5-year holding period start date for each conversion (qualified distribution clock)",
            "Tax projection showing net cost of conversion in low-income year vs. deferral",
            "State income tax analysis — confirm state treatment of Roth conversion",
        ],

        "cpa_handoff": [
            "§408A(d)(3): Roth conversion allowed from any traditional IRA or eligible plan; no income limit",
            "No 10% penalty on conversion (§72(t)(2)(A)(iv)); only applies to actual early withdrawals",
            "Tax cost: converted amount = ordinary income in conversion year; no special capital gains rate",
            "Bracket filling: convert only to top of current bracket — avoid crossing into higher bracket",
            "5-year rule: each conversion has own 5-year clock for qualified distribution purposes",
            "No RMDs: Roth IRA has no lifetime RMD requirement — ideal for estate planning",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],

    },

    {
        "id": "DTTS-058-section-1244-stock-loss-deduction",
        "name": "Section 1244 Stock Loss Deduction",
        "_id": "69bdb3e7e5397a28d4544047",
        "irc": "IRC §1244, §1244(a), §1244(c), §1244(d), §1211, §1212",
        "category": "General Planning",
        "overlap_group": None,
        "applicable_forms": ["1040", "1120"],
        "phase_1_eligible": True,
        "estimate_confidence": "LOW",

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_C_CORP", False) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False)
        ),

        "materiality_fn": lambda s: (
        45 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HAS_C_CORP") else
        25 if s.get("SIG_HIGH_INCOME") or s.get("SIG_HAS_C_CORP") else
        15
    ),

        "fed_savings_fn": lambda s: (
    s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.10 * 0.17
),

        "state_savings_fn": lambda s: (
    0
),

        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 10,

        "plain_english": (
            "Section 1244 is a simple but powerful planning tool for dentists "
            "who invest in or start C-Corporation ventures. When qualifying "
            "§1244 stock becomes worthless or is sold at a loss, the loss "
            "is treated as an ordinary loss — not a capital loss. This "
            "matters enormously: without §1244, a $100,000 loss on a failed "
            "investment can only offset $3,000 of ordinary income per year, "
            "with the rest carried forward indefinitely. With §1244, that "
            "same $100,000 loss for a married couple is fully deductible "
            "against dental practice income in the year of the loss. "
            "The qualifying requirements are simple: the stock must be "
            "C-Corporation stock issued directly to the taxpayer for money "
            "or property, and the corporation's total capitalization must "
            "have been $1 million or less at issuance. There is no special "
            "filing or election needed — just confirm the qualifying facts "
            "when the investment is made."
        ),

        "documentation": [
            "Stock certificate or subscription agreement confirming original issuance to taxpayer",
            "Capitalization records at time of issuance — confirm ≤$1M aggregate",
            "Evidence of consideration paid: money or property (not services)",
            "Loss documentation: sale proceeds or worthlessness evidence",
            "§1244 ordinary loss calculation: limited to $50K single / $100K MFJ per year",
        ],

        "cpa_handoff": [
            "§1244(a): loss on qualifying stock treated as ordinary loss up to $50K/$100K MFJ per year",
            "Without §1244: same loss = capital loss, limited to $3K/yr against ordinary income",
            "Qualifying stock: C-Corp; issued directly to taxpayer for money/property; corp capitalization ≤$1M",
            "Purchased stock: secondary market purchases do NOT qualify for §1244 treatment",
            "No election required: qualification determined by facts at issuance — document proactively",
            "Excess over annual limit: treated as capital loss; carryforward rules apply to excess",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-059-equipment-leasing-under-section-179",
        "name": "Equipment Leasing Under Section 179",
        "_id": "69bdb3e8e5397a28d454404e",
        "irc": "IRC §162, §168, §168(k), §179, §7701(e)",
        "category": "Exit & Sale",
        "overlap_group": None,
        "applicable_forms": ["1040", "1120", "1120S", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False)
        ),

        "materiality_fn": lambda s: (
            40 if s.get("SIG_HAS_DEPRECIATION", False) and s.get("SIG_HIGH_TAX_LIABILITY", False) else 25
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_ANNUAL_LEASE_PAYMENTS", 0) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("Q_ANNUAL_LEASE_PAYMENTS", 0) * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 10,

        "plain_english": (
            "Leasing high-ticket dental equipment — CBCT machines, laser "
            "systems, CAD/CAM units — rather than purchasing allows the "
            "practice to deduct 100% of lease payments as ordinary business "
            "expenses in each payment period, with no capitalization required. "
            "This contrasts with purchasing, where bonus depreciation (60% "
            "in 2024) front-loads the deduction but the remaining 40% "
            "is spread over seven years. For practices that prefer level, "
            "predictable deductions or that lack the cash to purchase "
            "outright, leasing provides full deductibility with simplified "
            "tax treatment. The lease must be structured as a true lease "
            "— not a disguised purchase — to receive this treatment. "
            "In low-income years or years when §179 has already been "
            "maximized, leasing may produce a better after-tax outcome "
            "than purchasing with delayed depreciation."
        ),

        "documentation": [
            "Equipment lease agreement — confirm true lease structure (not conditional sale)",
            "Annual lease payment schedule and payment records",
            "FMV purchase option analysis — confirm option price is not nominal",
            "Lessor residual value analysis — confirm ≥20% residual value retained by lessor",
            "Lease vs. buy comparison showing after-tax cost under each scenario",
        ],

        "cpa_handoff": [
            "§162: operating lease payments deductible in full as business expense — no capitalization",
            "True lease test: lessor must retain residual risk; purchase option must be at FMV, not nominal",
            "§7701(e): IRS may recharacterize lease as sale if economic substance = ownership — confirm structure",
            "Comparison: lease vs. purchase + bonus depreciation (60% in 2024) — NPV analysis recommended",
            "§179: if practice has not maxed §179, purchase + §179 expensing may produce better year-1 result",
            "State treatment: some states have sales/use tax on lease payments — confirm state-specific cost",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-061-reimbursement-of-educational-assistance",
        "name": "Reimbursement of Educational Assistance",
        "_id": "69bdb3e8e5397a28d4544055",
        "irc": "IRC §127, §127(a), §127(b), §127(c), §132(d), §162",
        "category": "Compensation & Benefits",
        "overlap_group": "Employee Benefits",
        "applicable_forms": ["1120", "1120S"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_W2_PRESENT", False) and
            s.get("SIG_HIGH_INCOME", False)
        ),

        "materiality_fn": lambda s: (
            35 if s.get("SIG_PROFESSIONAL_FEES_PRESENT", False) and s.get("SIG_W2_PRESENT", False) else 20
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_EDUCATIONAL_ASSISTANCE_DEDUCTION", 0) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("Q_EDUCATIONAL_ASSISTANCE_DEDUCTION", 0) * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 5,

        "plain_english": (
            "A dental practice can reimburse employees up to $5,250 per year "
            "for educational expenses — tuition, fees, books, and supplies — "
            "completely tax-free to the employee and fully deductible by the "
            "practice. The practice must have a written educational assistance "
            "plan under §127, and the benefit must be available to employees "
            "broadly (not just owners). For a practice with five employees "
            "taking CE courses, dental hygiene programs, or business "
            "management training, this creates over $26,000 in deductible "
            "expenses with zero income or payroll tax to the employees. "
            "Owner-dentists in S-Corporations cannot use the §127 exclusion "
            "for themselves, but CE credits and specialty training that "
            "maintain current dental skills may qualify as working condition "
            "fringe benefits under §132(d) — deductible by the practice "
            "and excluded from the owner's income without a dollar limit."
        ),

        "documentation": [
            "Written §127 educational assistance plan document",
            "Employee notification of plan availability",
            "Reimbursement receipts — tuition, fees, books, supplies",
            "W-2 confirming §127 reimbursements excluded from Box 1 (up to $5,250)",
            "Non-discrimination testing documentation — plan must not favor HCEs/5% owners",
            "§132(d) working condition fringe analysis for owner-dentist CE credits",
        ],

        "cpa_handoff": [
            "§127: up to $5,250/employee/year excluded from income — no income tax, no FICA",
            "Written plan required: must be in writing, available to employees, no HCE discrimination",
            ">2% S-Corp shareholders: §127 exclusion NOT available for themselves — use §132(d) instead",
            "§132(d) working condition fringe: CE credits maintaining dental skills deductible without §127 limit",
            "Graduate education: included since EGTRRA 2001 — employees pursuing advanced degrees qualify",
            "Practice deducts full reimbursement as §162 business expense — employer + employee both benefit",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-062-opportunity-zone-step-up-in-basis",
        "name": "Opportunity Zone Step-Up in Basis",
        "_id": "69bdb3fae5397a28d454405d",
        "irc": "IRC §1400Z-1, §1400Z-2, §1400Z-2(a), §1400Z-2(b), §1400Z-2(c)",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Opportunity Zone Planning",
        "applicable_forms": ["8949", "8997"],
        "phase_1_eligible": False,

        # Opportunity Zone requires a REALIZED capital gain to invest.
        # Without a confirmed sale event, this is a future-planning discussion only.
        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("_capital_gains", 0) > 0  # must have some capital gain
        ),

        # Event trigger: a sale must have occurred producing the deferrable gain
        "event_trigger_logic": lambda s: s.get("SIG_ASSET_SALE_EVENT", False),
        "event_note": "No asset sale / capital gain event detected — §1400Z-2 requires a realized gain to defer",
        "readiness_if_prereq_fail": "REQUIRES_EVENT",

        "materiality_fn": lambda s: (
            80 if s.get("_capital_gains", 0) > 500_000
            else 65 if s.get("_capital_gains", 0) > 200_000
            else 50
        ),

        "fed_savings_fn": lambda s: (
            # Defer + 10-year appreciation exclusion.
            # Conservative: tax on deferred gain × 20% LTCG + 3.8% NIIT
            max(0, s.get("_capital_gains", 0)) * 0.238 * 0.25   # 25% discount for deferral only
        ),

        "state_savings_fn": lambda s: (
            0  # most states don't conform to OZ exclusion
        ),

        "speed_days": 90,
        "complexity": 55,
        "audit_friction": 20,

        "plain_english": (
            "Qualified Opportunity Zones allow a dentist who has recently "
            "sold an appreciated asset — real estate, a practice interest, "
            "or an investment portfolio — to defer the capital gains tax "
            "by reinvesting the gain into a Qualified Opportunity Fund "
            "within 180 days. The deferred gain is now fully taxable by "
            "December 31, 2026, but the real remaining benefit is the "
            "10-year exclusion: if the QOF investment is held for at least "
            "10 years, all appreciation on the investment above the original "
            "deferred amount is completely excluded from income. A dentist "
            "who reinvests $1 million of capital gain into a QOF that grows "
            "to $3 million over 10 years would owe tax on the original $1M "
            "gain but pay zero tax on the $2M of growth. This strategy "
            "requires commitment to a 10-year illiquid investment and "
            "careful selection of a qualifying opportunity fund."
        ),

        "documentation": [
            "Form 8997 — Initial and Annual Statement of QOF Investments (filed annually)",
            "Form 8949 — report of deferred gain and QOF investment",
            "QOF subscription/investment agreement",
            "180-day window calculation from triggering sale date",
            "QOF 90% asset test documentation (QOF must maintain 90% QOZ property)",
            "10-year hold tracking — date of QOF investment for exclusion eligibility",
        ],

        "cpa_handoff": [
            "§1400Z-2(a): gain deferred if reinvested in QOF within 180 days of triggering sale",
            "§1400Z-2(b): deferred gain now fully includable Dec 31, 2026 — step-up benefit expired",
            "§1400Z-2(c): 10-year hold → ALL post-investment QOF appreciation EXCLUDED from income",
            "Key: only DEFERRED GAIN is eventually taxable; subsequent QOF growth is permanently excluded",
            "State conformity: many states (CA, NY, NJ, MA) do not conform — state tax still owed on appreciation",
            "Form 8997: annual filing required each year QOF interest held — do not miss",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],

    },

    {
        "id": "DTTS-063-family-limited-partnership-flp",
        "name": "Family Limited Partnership (FLP)",
        "_id": "69bdb3fce5397a28d4544074",
        "irc": "IRC §2036, §2701, §2702, §2703, §2704, §704(e)",
        "category": "Entity & Structuring",
        "overlap_group": "Family Entity Planning",
        "applicable_forms": ["1065", "709"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("SIG_DEPENDENTS_PRESENT", False) and
            s.get("_agi", 0) > 750_000
        ),

        "materiality_fn": lambda s: (
            70 if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("SIG_DEPENDENTS_PRESENT", False) and s.get("_agi", 0) > 1_000_000 else 45
        ),

        "fed_savings_fn": lambda s: (
            300_000 * 0.40 * 0.35
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 120,
        "complexity": 65,
        "audit_friction": 30,

        "plain_english": (
            "A Family Limited Partnership (FLP) allows a dentist to transfer "
            "assets to family members at a discount for gift and estate tax "
            "purposes. The dentist contributes assets — real estate, "
            "investments, or a management company interest — to the FLP "
            "and retains control as the general partner. Limited partnership "
            "interests are then gifted to children or grandchildren. "
            "Because LP interests lack voting control and have no public "
            "market, they receive valuation discounts of 20–40% compared "
            "to the underlying asset value. This means a $1 million gift "
            "of LP interests might be valued at only $700,000 for gift "
            "tax purposes — stretching the lifetime exemption further. "
            "Future appreciation compounds outside the estate in the "
            "children's hands. The IRS scrutinizes FLPs closely under "
            "§2036, so the partnership must have genuine business purpose, "
            "proper formalities must be maintained, and personal and "
            "partnership assets must not be commingled."
        ),

        "documentation": [
            "FLP partnership agreement — GP control provisions, LP rights, distribution rules",
            "Qualified appraisal supporting discount rate for LP interests",
            "Form 709 — Gift Tax Return for LP interest transfers",
            "Asset contribution records — confirm genuine transfer of assets to FLP",
            "Annual Form 1065 and K-1s for all partners",
            "§2036 risk analysis — confirm GP does not retain excess control over distributions",
        ],

        "cpa_handoff": [
            "FLP discount: LP interests valued at 20–40% discount for lack of control/marketability",
            "Gift tax savings: discount reduces taxable gift amount — stretches lifetime exemption",
            "§2036 risk: if GP retains too much control or comingles assets, IRS pulls FLP assets into estate",
            "Bona fide business purpose required: FLP must have non-tax business reason to withstand IRS challenge",
            "Income shifting: LP income flows to children — subject to kiddie tax if under 19/24",
            "§2704: proposed regulations may limit discount claims — monitor regulatory developments",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
            "Requires related-party role, compensation, and documentation review before implementation.",
        ],

    },

    {
        "id": "DTTS-064-qualified-longevity-annuity-contract-qlac",
        "name": "Qualified Longevity Annuity Contract (QLAC)",
        "_id": "69bdb3ffe5397a28d454408b",
        "irc": "Treas. Reg. §1.401(a)(9)-6, IRC §401(a)(9), §408(b)",
        "category": "Retirement Plans",
        "overlap_group": "Retirement Plan",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_RETIREMENT_PLAN", False) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("_retirement", 0) > 200_000
        ),

        "materiality_fn": lambda s: (
        50 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_RETIREMENT_UNDERFUNDED") else
        30 if s.get("SIG_HIGH_INCOME") or s.get("SIG_RETIREMENT_UNDERFUNDED") else
        20
    ),

        "fed_savings_fn": lambda s: (
            (8_000 * s.get("_fed_marginal_rate", 0)) + 3_000
        ),

        "state_savings_fn": lambda s: (
            8_000 * s.get("Q_STATE_MARGINAL_RATE", 0.05)
        ),

        "speed_days": 30,
        "complexity": 20,
        "audit_friction": 5,

        "plain_english": (
            "A Qualified Longevity Annuity Contract (QLAC) is an insurance "
            "product purchased inside an IRA or 401(k) that converts up to "
            "$200,000 of retirement savings into guaranteed lifetime income "
            "starting at age 80 or 85. The premium used to purchase the QLAC "
            "is excluded from the IRA balance for required minimum distribution "
            "calculations — reducing mandatory withdrawals for up to 12 years. "
            "For a dentist with a large IRA balance approaching age 73 "
            "and not needing all the RMD income, a QLAC reduces taxable "
            "withdrawals, potentially lowers Medicare premium surcharges "
            "(IRMAA), and reduces the percentage of Social Security benefits "
            "subject to income tax. The trade-off is illiquidity — the premium "
            "cannot be surrendered, and if the dentist dies before income "
            "payments begin, the premium is forfeited unless a "
            "return-of-premium rider is purchased."
        ),

        "documentation": [
            "QLAC annuity contract from insurance carrier",
            "IRA custodian confirmation of QLAC premium exclusion from RMD balance",
            "QLAC premium amount — confirm ≤$200,000 (2024 SECURE 2.0 limit)",
            "Income start date election (must begin by age 85)",
            "RMD recalculation schedule showing reduced RMDs during deferral period",
            "Return-of-premium rider documentation if death benefit elected",
        ],

        "cpa_handoff": [
            "QLAC: up to $200,000 (2024, indexed) of IRA/401(k) funds used to purchase deferred annuity",
            "RMD exclusion: QLAC premium excluded from IRA balance for §401(a)(9) RMD calculation",
            "Income deferral: payments can be deferred to age 85 — reduces RMDs for up to 12 years",
            "Secondary benefits: lower RMD income → reduced IRMAA, lower SS taxation, Roth conversion room",
            "Trade-off: illiquid; no surrender value; premium forfeited if death before income start date",
            "SECURE 2.0: eliminated the 25% IRA balance cap — flat $200,000 limit now applies",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],

    },

    {
        "id": "DTTS-065-529-college-savings-plan",
        "name": "529 College Savings Plan",
        "_id": "69bdb400e5397a28d4544093",
        "irc": "IRC §529, §529(a), §529(b), §529(c)(3), §529(c)(2)(B)",
        "category": "General Planning",
        "overlap_group": None,
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_DEPENDENTS_PRESENT", False) and
            s.get("SIG_HIGH_INCOME", False)
        ),

        "materiality_fn": lambda s: (
            45 if s.get("SIG_DEPENDENTS_PRESENT", False) and s.get("SIG_STATE_RETURN_PRESENT", False) else 30
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.10 * 0.238
),

        "state_savings_fn": lambda s: (
    s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.10 * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 7,
        "complexity": 5,
        "audit_friction": 2,

        "plain_english": (
            "A 529 college savings plan allows a dentist to invest money for "
            "a child's education with tax-free growth and tax-free withdrawals "
            "for qualified education expenses. While contributions are not "
            "federally deductible, most states offer a deduction for "
            "contributions to the in-state plan. The superfunding provision "
            "allows a dentist to contribute up to $90,000 per child in a "
            "single year ($180,000 for a couple) and spread it over five "
            "years for gift tax purposes — removing a large amount from "
            "the taxable estate while using only the annual gift tax exclusion. "
            "Under SECURE 2.0, unused 529 balances (after 15 years) can "
            "be rolled over to a Roth IRA for the beneficiary — up to "
            "$35,000 lifetime — eliminating the concern about over-funding. "
            "This is a low-complexity, high-impact strategy for any dentist "
            "with children and education funding goals."
        ),

        "documentation": [
            "529 account opening documents and beneficiary designations",
            "Contribution records per beneficiary per year",
            "Form 709 for superfunding election — 5-year averaging statement required",
            "State 529 deduction documentation (if state deduction available)",
            "Qualified expense receipts for distributions taken",
            "SECURE 2.0 Roth rollover tracking — 15-year account age and $35,000 lifetime limit",
        ],

        "cpa_handoff": [
            "§529: no federal deduction for contributions; growth and qualified distributions tax-free",
            "Superfunding: $90K/beneficiary ($180K MFJ) — elect 5-year gift tax averaging on Form 709",
            "Estate removal: superfunded amounts removed from estate immediately; future growth also outside estate",
            "SECURE 2.0 Roth rollover: after 15 years, up to $35K to Roth IRA; subject to annual Roth limits",
            "State deduction: most states offer deduction for in-state plan contributions — confirm state rules",
            "K-12: §529 distributions for K-12 tuition up to $10K/yr per beneficiary — federal qualified expense",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-066-self-rental-to-business",
        "name": "Self-Rental to Business",
        "_id": "69bdb402e5397a28d454409a",
        "irc": "IRC §469, §469(c), §469(l)(1), §162, §1231",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Real Estate — Self Rental",
        "applicable_forms": ["1040", "1120S", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_REAL_ESTATE_ACTIVITY", False) and
            s.get("SIG_HAS_S_CORP_VERIFIED", False) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_RENT_EXPENSE_PRESENT", False)
        ),

        "materiality_fn": lambda s: (
            65 if s.get("SIG_HAS_S_CORP_VERIFIED", False) and s.get("SIG_REAL_ESTATE_ACTIVITY", False) and s.get("SIG_HIGH_INCOME", False) else 40
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_MGMT_CO_REVENUE", 0) * 0.153 * 0.9235
),

        "state_savings_fn": lambda s: (
    0
),

        "speed_days": 30,
        "complexity": 30,
        "audit_friction": 20,

        "plain_english": (
            "A self-rental arrangement allows a dentist who owns their "
            "office building or equipment to rent it to their own practice "
            "— shifting income from the practice (which may be subject to "
            "payroll taxes) to rental income (which is not subject to "
            "self-employment or FICA taxes). The practice deducts the rent "
            "as a business expense, and the owner receives rental income "
            "that can be partially sheltered by depreciation on the property. "
            "An important tax rule applies: under the self-rental recharacterization "
            "rule of §469, rental income from property rented to a business "
            "in which the owner materially participates is non-passive — "
            "it cannot be sheltered by passive losses from other rental "
            "properties. The primary planning benefit is the FICA/SE tax "
            "savings on income shifted to the rental channel, plus the "
            "ability to accelerate depreciation deductions on the property."
        ),

        "documentation": [
            "Lease agreement between owner and dental practice at fair market rent",
            "Fair market rent appraisal or comparable rental analysis",
            "Schedule E — rental income and depreciation for owner's property",
            "Form 8582 — passive activity loss analysis (self-rental income non-passive)",
            "Depreciation schedule for rental property (Form 4562)",
            "Grouping election documentation if §469(c)(7) real estate professional status claimed",
        ],

        "cpa_handoff": [
            "Self-rental rule (Temp. Reg. §1.469-2(f)(6)): rental income from property rented to materially-participated business = non-passive",
            "Non-passive rental income: cannot be offset by passive losses from other rental properties",
            "Rental losses: remain passive even under self-rental rule — cannot offset non-passive income",
            "Tax benefit: rental income not subject to SE tax or FICA — vs. salary/S-Corp distribution comparison",
            "Rent must be at fair market value — related-party rent above FMV subject to §482 reallocation",
            "Grouping election: §469(c)(7) real estate professionals may group rental with business — different passive rules",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],

    },

    {
        "id": "DTTS-067-net-operating-loss-nol-carryforward",
        "name": "Net Operating Loss (NOL) Carryforward",
        "_id": "69c26f23cdaa7f875cd42144",
        "irc": "IRC §172, §172(a), §172(b), §172(f), §167, §168, §469",
        "category": "Real Estate & Depreciation",
        "overlap_group": None,
        "applicable_forms": ["1040", "1120", "1120S", "1065"],
        "phase_1_eligible": True,

        # NOL only applies if the current year has a net loss OR a prior NOL carryover exists.
        # A profitable entity with no NOL gets zero benefit from this strategy.
        "eligibility_logic": lambda s: (
            (s.get("_obi", 0) < 0 or s.get("SIG_NOL_CARRYOVER_CONFIRMED", False)) and
            (s.get("SIG_HAS_DEPRECIATION", False) or s.get("SIG_REAL_ESTATE_ACTIVITY", False)
             or s.get("SIG_BUSINESS_PRESENT", False))
        ),

        # Prerequisite: must have confirmed NOL (either current-year or carryover)
        "prerequisites_logic": lambda s: (
            s.get("_obi", 0) < 0 or s.get("SIG_NOL_CARRYOVER_CONFIRMED", False)
        ),
        "readiness_if_prereq_fail": "REQUIRES_EVENT",
        "readiness_note": "NOL strategy requires a confirmed net operating loss — no loss detected in current return",

        "materiality_fn": lambda s: (
            65 if s.get("SIG_NOL_CARRYOVER_CONFIRMED") and s.get("SIG_HIGH_TAX_LIABILITY") else
            50 if s.get("_obi", 0) < 0 else 30
        ),

        "fed_savings_fn": lambda s: (
            # NOL benefit = NOL amount × 80% limitation × marginal rate.
            # Use actual loss if available; else 0 (can't estimate without confirmed loss).
            abs(min(0, s.get("_obi", 0))) * 0.80 * s.get("_fed_marginal_rate", 0.37)
            if s.get("_obi", 0) < 0
            else s.get("_nol_amount", 0) * 0.80 * s.get("_fed_marginal_rate", 0.37)
        ),

        "state_savings_fn": lambda s: (
            abs(min(0, s.get("_obi", 0))) * 0.80 *
            (s.get("_state_tax", 0) / s.get("_agi", 1) if s.get("_agi", 0) else 0.05)
        ),

        "speed_days": 14,
        "complexity": 20,
        "audit_friction": 10,

        "plain_english": (
            "A Net Operating Loss occurs when a business or investment "
            "activity generates deductions that exceed income in a given year — "
            "most commonly through large depreciation deductions from bonus "
            "depreciation, cost segregation, or §179 expensing. Under current "
            "law, NOLs can be carried forward indefinitely and applied against "
            "up to 80% of taxable income in future years. For a dentist who "
            "generates a large depreciation deduction in a year with high "
            "income, the excess deduction becomes an NOL that reduces taxes "
            "in subsequent high-income years. The strategy is most relevant "
            "when depreciation-heavy investments or real estate activities "
            "produce losses that exceed current-year income, or when a "
            "dentist deliberately accelerates depreciation to create an NOL "
            "that will shield future practice income. State NOL rules vary "
            "significantly and should be modeled separately."
        ),

        "documentation": [
            "NOL computation schedule — modified taxable income calculation per §172(d)",
            "NOL carryforward tracking schedule — year of origin, amount, remaining balance",
            "80% limitation calculation for each carryforward year",
            "Depreciation schedules generating the NOL (Form 4562)",
            "State NOL analysis — separate computation for each state with different rules",
        ],

        "cpa_handoff": [
            "§172: NOL deductible in carryforward year up to 80% of taxable income (post-TCJA 2017)",
            "Indefinite carryforward: post-2017 NOLs never expire — carry forward until fully utilized",
            "80% cap: in any year, NOL deduction limited to 80% of taxable income — 20% always taxable",
            "Pre-2018 NOLs: different rules — 20-year carryforward, no 80% limitation, 2-year carryback",
            "CARES Act: 2018–2020 NOLs could be carried back 5 years — confirm if any prior-year opportunities",
            "State NOL: many states have shorter carryforward periods or different % limits — model separately",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],

    },

    {
        "id": "DTTS-068-business-interest-deduction-optimization",
        "name": "Business Interest Deduction Optimization",
        "_id": "69bdb406e5397a28d45440a8",
        "irc": "IRC §163(j), §163(j)(1), §163(j)(2), §163(j)(3), §163(j)(7)",
        "category": "General Planning",
        "overlap_group": None,
        "applicable_forms": ["1040", "1120", "1120S", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False)
        ),

        "materiality_fn": lambda s: (
            50 if s.get("SIG_HAS_S_CORP_VERIFIED", False) and s.get("SIG_HAS_DEPRECIATION", False) else 30
        ),

        "fed_savings_fn": lambda s: (
    s.get("_obi", 0) * 0.05 * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("_obi", 0) * 0.05 * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 21,
        "complexity": 25,
        "audit_friction": 10,

        "plain_english": (
            "Section 163(j) limits the deduction for business interest expense "
            "to 30% of a practice's adjusted taxable income — meaning a "
            "dentist with significant business debt may be unable to deduct "
            "all their interest in a given year. The most important planning "
            "point is the small business exemption: practices with average "
            "gross receipts of $29 million or less over the prior three years "
            "are completely exempt from §163(j) and can deduct all business "
            "interest without limitation. For larger practices or those above "
            "the threshold, optimization involves maximizing adjusted taxable "
            "income to increase the 30% deduction cap — which requires "
            "coordinating depreciation elections with interest deductibility. "
            "Disallowed interest carries forward indefinitely, so tracking "
            "and planning for future utilization is critical. Real estate "
            "businesses can elect out of §163(j) entirely in exchange for "
            "using the slower ADS depreciation method."
        ),

        "documentation": [
            "Form 8990 — Limitation on Business Interest Expense Under §163(j)",
            "Gross receipts calculation for small business exemption ($29M threshold)",
            "ATI computation — adjusted taxable income for 30% limitation calculation",
            "Disallowed interest carryforward schedule by year of origin",
            "Real property election statement if §163(j)(7) election made",
            "State §163(j) conformity analysis — many states decouple from federal limit",
        ],

        "cpa_handoff": [
            "§163(j): business interest deductible up to 30% of ATI + business interest income",
            "Small business exemption: gross receipts ≤$29M (2024) average prior 3 years → §163(j) does NOT apply",
            "ATI post-2021: depreciation/amortization NO LONGER added back — harder to pass 30% test",
            "Disallowed interest: carries forward indefinitely at entity level (partnership) or shareholder level (S-Corp)",
            "Real property election: elect out of §163(j) → all interest deductible; must use ADS depreciation",
            "Depreciation trade-off: reducing accelerated depreciation increases ATI → more interest deductible",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-069-section-280f-luxury-auto-depreciation-cap",
        "name": "Section 280F — Luxury Auto Depreciation Cap",
        "_id": "69c26f23cdaa7f875cd4214a",
        "irc": "IRC §274, §280F, §280F(a), §280F(d)(5), §280F(d)(6), §168(k), §179(b)(5)",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Depreciation — Vehicle",
        "applicable_forms": ["1040", "1120", "1120S", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_AUTO_TRUCK_PRESENT", False) and
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False)
        ),

        "materiality_fn": lambda s: (
            50 if s.get("SIG_AUTO_TRUCK_PRESENT", False) and s.get("SIG_HIGH_TAX_LIABILITY", False) else 30
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_179_INCREMENTAL_DEDUCTION", 0) * 0.60 * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("Q_179_INCREMENTAL_DEDUCTION", 0) * 0.60 * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 14,
        "complexity": 15,
        "audit_friction": 20,

        "plain_english": (
            "The IRS caps annual depreciation on passenger automobiles — "
            "no matter how expensive — at $20,400 in year one (2024, "
            "with bonus depreciation). A dentist buying a $100,000 luxury "
            "sedan is limited to the same first-year deduction as someone "
            "buying a $50,000 car. The planning strategy is to purchase "
            "a vehicle with a gross vehicle weight rating (GVWR) above "
            "6,000 pounds — large SUVs like the Suburban, Expedition, "
            "or Tahoe, or work trucks like the F-250. These vehicles are "
            "exempt from the luxury auto caps, allowing 60% bonus "
            "depreciation in year one (2024 rate). Section 179 for heavy "
            "SUVs is limited to $30,500, but bonus depreciation is not "
            "capped. A $70,000 heavy SUV used 100% for business can "
            "generate a $42,000 first-year deduction — more than double "
            "what the luxury auto cap would allow on a comparable car. "
            "Mileage logs and business use documentation are required."
        ),

        "documentation": [
            "Vehicle purchase documentation — confirm GVWR >6,000 lbs for heavy vehicle strategy",
            "Mileage log — business vs. personal use documentation (§274(d) listed property)",
            "Form 4562 — depreciation and amortization; bonus depreciation election",
            "§179 election for heavy SUV if applicable (limited to $30,500 in 2024)",
            "Business use percentage calculation — must be >50% for any depreciation",
            "State depreciation schedule — most states decouple from federal bonus depreciation",
        ],

        "cpa_handoff": [
            "§280F(a): luxury auto cap — year 1: $20,400 (bonus) / $12,400 (no bonus); applies to GVWR ≤6,000 lbs",
            "Heavy vehicle exception: GVWR >6,000 lbs = no luxury auto cap; full bonus depreciation applies",
            "§179 heavy SUV: limited to $30,500 (2024); bonus depreciation on remaining basis not capped",
            "Business use: depreciation limited to business use %; <50% business use = ADS required, no bonus",
            "Substantiation: mileage log or actual expense method required for all listed property vehicles",
            "State conformity: most states do not allow federal bonus depreciation — run state depreciation separately",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],

    },
    {
        "id": "DTTS-070-asset-protection-trust-structure-dapt",
        "name": "Asset Protection Trust Structure (DAPT)",
        "_id": "69bdb408e5397a28d45440b0",
        "irc": "IRC §671, §677, §2036, §167, §168, §469",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Domestic Asset Protection Trust (DAPT)",
        "applicable_forms": ["1041"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("_agi", 0) > 750_000
        ),

        "materiality_fn": lambda s: (
            60 if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("_agi", 0) > 1_000_000 else 35
        ),

        "fed_savings_fn": lambda s: (
            2_000_000 * 0.40 * 0.20
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 120,
        "complexity": 70,
        "audit_friction": 25,

        "plain_english": (
            "A Domestic Asset Protection Trust (DAPT) is a self-settled "
            "irrevocable trust established in a favorable state — Alaska, "
            "Nevada, South Dakota, Delaware, or Wyoming — that allows the "
            "dentist to be a discretionary beneficiary while shielding "
            "assets from future creditors. Unlike a traditional irrevocable "
            "trust, the grantor can receive distributions at the trustee's "
            "discretion, while future creditors (including malpractice "
            "plaintiffs) are barred from reaching trust assets after the "
            "applicable statute of limitations expires (typically 2–4 years). "
            "The trust is structured as a grantor trust for income tax — "
            "meaning the dentist still pays all income taxes on trust "
            "earnings, which itself constitutes an additional tax-free "
            "wealth transfer to the trust beneficiaries. "
            "Existing creditors are not protected, and federal bankruptcy "
            "law may limit DAPT effectiveness in some circumstances. "
            "This is primarily an asset protection and estate planning tool, "
            "not an income tax reduction strategy."
        ),

        "documentation": [
            "DAPT trust document — sited in favorable state (AK, NV, SD, DE, or WY)",
            "Independent trustee appointment documentation (qualified trustee in trust state required)",
            "Asset transfer records and valuations at date of funding",
            "Statute of limitations analysis — confirm no existing creditors at transfer date",
            "Grantor trust income tax reporting — all trust income on grantor's Form 1040",
            "§2036 risk analysis — confirm grantor does not retain prohibited control or interest",
        ],

        "cpa_handoff": [
            "DAPT: self-settled irrevocable trust; grantor is discretionary beneficiary; future creditors barred",
            "Income tax: grantor trust (§671/677) — trust income taxed to grantor; no income tax reduction",
            "Wealth transfer: grantor paying trust's income taxes = gift-tax-free wealth transfer to trust",
            "§2036 risk: excess retained control or ascertainable standard may pull assets into estate",
            "Existing creditors: DAPT does NOT protect against existing creditors or fraudulent transfers",
            "Federal bankruptcy: 10-year lookback period under 11 USC §548 — federal courts may override state DAPT",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],

    },

    {
        "id": "DTTS-071-partial-asset-sale-with-installment-1031",
        "name": "Partial Asset Sale with Installment + 1031",
        "_id": "69bdb40ae5397a28d45440b9",
        "irc": "IRC §453, §453(b), §453A, §1031, §1031(a), §1031(b), §453(f)(6)",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Practice Sale Exit",
        "applicable_forms": ["1040", "1120", "1120S", "1065"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_REAL_ESTATE_ACTIVITY", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("Q_PRACTICE_SALE_PLANNED", False)
        ),

        # Event trigger: actual sale must have occurred OR be contractually planned
        "event_trigger_logic": lambda s: (
            s.get("SIG_PROPERTY_SALE_EVENT", False) or
            s.get("SIG_INSTALLMENT_SALE_EVENT", False) or
            s.get("Q_PRACTICE_SALE_PLANNED", False)
        ),
        "event_note": "No property sale or installment sale event detected in return data",
        "readiness_if_prereq_fail": "REQUIRES_EVENT",

        "materiality_fn": lambda s: (
            70 if s.get("Q_PRACTICE_SALE_PLANNED") and s.get("SIG_VERY_HIGH_INCOME", False) else 30
        ),

        "fed_savings_fn": lambda s: (
            (max(0, s.get("_capital_gains", 0)) * 0.20 * 0.50)  # 50% deferral via 1031
            if s.get("Q_PRACTICE_SALE_PLANNED", False)
            else 0
        ),

        "state_savings_fn": lambda s: (
            (max(0, s.get("_capital_gains", 0)) * 0.20 * 0.50
             * s.get("Q_STATE_MARGINAL_RATE", 0.04))
            if s.get("Q_PRACTICE_SALE_PLANNED", False)
            else 0
        ),

        "speed_days": 90,
        "complexity": 65,
        "audit_friction": 25,

        "plain_english": (
            "A partial installment + 1031 strategy combines two powerful "
            "tax deferral tools on the same real estate sale. When a dentist "
            "sells an investment property, a portion of the proceeds is "
            "rolled into a like-kind replacement property via a §1031 "
            "exchange — deferring the capital gain on that portion entirely. "
            "The remaining cash proceeds are structured as an installment "
            "sale — spreading the taxable gain on that portion over multiple "
            "years and avoiding a large single-year tax spike. The combination "
            "can dramatically reduce the tax cost of an exit: for a $2M "
            "property with $1.6M of gain, the dentist might defer $1M of "
            "gain via the 1031 exchange and spread the remaining $600K "
            "over five years rather than recognizing it all at once. "
            "Depreciation recapture (§1250 unrecaptured gain at 25%) "
            "cannot be deferred and must be recognized first. "
            "Qualified intermediary coordination is essential when "
            "combining installment notes with a 1031 exchange."
        ),

        "documentation": [
            "§1031 exchange agreement with qualified intermediary",
            "45-day identification and 180-day closing timeline documentation",
            "Installment sale agreement for non-exchanged portion (Form 6252)",
            "Depreciation recapture calculation — §1250 unrecaptured gain (25% rate)",
            "Replacement property closing documents and basis calculation",
            "§453A interest charge analysis if deferred obligation exceeds $5M",
        ],

        "cpa_handoff": [
            "Partial 1031: exchange portion of sale proceeds into like-kind replacement; defer capital gain",
            "Installment §453: remaining proceeds received over time; gain recognized proportionally as paid",
            "§453(f)(6): installment note received IN exchange = boot — use QI to prevent tainting exchange",
            "§1250 recapture: unrecaptured §1250 gain taxed at 25% — cannot be deferred via 1031 or installment",
            "§453A: if deferred installment obligation face >$5M, interest charge applies on deferred tax",
            "State conformity: most states conform to §453; ~10 states do not conform to §1031 — check",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],

    },

    {
        "id": "DTTS-072-entity-classification-election-check-the-box",
        "name": "Entity Classification Election (Check-the-Box)",
        "_id": "69bdb40ae5397a28d45440c1",
        "irc": "Treas. Reg. §301.7701-3, §301.7701-2, §301.7701-3(c), IRC §482",
        "category": "Entity & Structuring",
        "overlap_group": "Entity Conversion",
        "applicable_forms": ["8832"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_MULTI_ENTITY", False) and
            s.get("SIG_HIGH_INCOME", False) and
            (s.get("SIG_HAS_PARTNERSHIP", False) or s["SIG_K1_PRESENT"])
        ),

        "materiality_fn": lambda s: (
            55 if s.get("SIG_MULTI_ENTITY", False) and s.get("SIG_HIGH_INCOME", False) else 30
        ),

        "fed_savings_fn": lambda s: (
    s.get("_obi", 0) * 0.15 * 0.153 * 0.9235
),

        "state_savings_fn": lambda s: (
    0
),

        "speed_days": 30,
        "complexity": 35,
        "audit_friction": 15,

        "plain_english": (
            "The check-the-box election allows an LLC or other eligible "
            "business entity to choose how it is taxed for federal purposes — "
            "as a sole proprietorship (disregarded), partnership, C-Corporation, "
            "or S-Corporation. For dentists with multi-entity structures, "
            "this is a powerful restructuring tool: a partnership can be "
            "converted to an S-Corporation to access payroll tax savings, "
            "or to a C-Corporation to enable QSBS planning or retained "
            "earnings at the 21% corporate rate. Single-member LLCs "
            "currently filing as disregarded entities can elect S-Corp "
            "treatment — combined with a reasonable salary — to shield "
            "a portion of practice income from self-employment taxes. "
            "The election is filed on Form 8832 and can be made retroactive "
            "up to 75 days, allowing prior-year fixes. "
            "Important: changing an entity's classification can trigger "
            "deemed tax events — full modeling required before filing."
        ),

        "documentation": [
            "Form 8832 — Entity Classification Election (filed with IRS service center)",
            "Form 2553 — S-Corp election (if electing S-Corp status after CTB to corporation)",
            "Prior entity tax return confirming default classification being changed",
            "Deemed liquidation/contribution tax analysis if changing from partnership to corporation",
            "State election filings — several states require separate state CTB election",
            "Effective date calculation — retroactive up to 75 days; prospective up to 12 months",
        ],

        "cpa_handoff": [
            "Treas. Reg. §301.7701-3: eligible entity elects classification on Form 8832",
            "Default: domestic multi-member LLC = partnership; single-member LLC = disregarded",
            "Common use: disregarded/partnership → S-Corp (Form 8832 + Form 2553 sequence)",
            "Conversion consequence: partnership → corp = deemed §708 termination + §351 contribution",
            "Retroactive election: up to 75 days before filing — can correct prior classification",
            "State non-conformity: ~10 states do not honor federal CTB election — separate state analysis required",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-073-business-use-of-home-by-partner",
        "name": "Business Use of Home by Partner",
        "_id": "69bdb40be5397a28d45440c8",
        "irc": "IRC §162, §280A, §280A(c)(1), §280A(c)(6), §167, §168",
        "category": "General Planning",
        "overlap_group": "Home Office Deduction",
        "applicable_forms": ["1065", "1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_PARTNERSHIP", False) and
            s["SIG_K1_PRESENT"] and
            s.get("SIG_HIGH_INCOME", False)
        ),

        "materiality_fn": lambda s: (
        40 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HAS_PARTNERSHIP") else
        20 if s.get("SIG_HIGH_INCOME") or s.get("SIG_HAS_PARTNERSHIP") else
        15
    ),

        "fed_savings_fn": lambda s: (
    s.get("_agi", 0) * 0.005 * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("_agi", 0) * 0.005 * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 20,

        "plain_english": (
            "A dentist who is a partner in a dental partnership can deduct "
            "the business use of their home as an unreimbursed partner "
            "expense — reported on Schedule E rather than as an employee "
            "expense. This is a significant advantage over S-Corporation "
            "shareholders, who lost the ability to deduct home office "
            "expenses as employees after the 2018 tax reform. "
            "The deduction covers a proportionate share of home expenses "
            "— mortgage interest, utilities, insurance, repairs, and "
            "depreciation — based on the percentage of home square footage "
            "used exclusively and regularly for partnership business "
            "(administrative work, billing, client meetings). "
            "The partnership agreement should reflect that the partner "
            "is expected or required to maintain a home office for "
            "partnership business. S-Corporation owners who want a similar "
            "benefit should instead use an accountable plan reimbursement "
            "arrangement through the corporation."
        ),

        "documentation": [
            "Form 8829 — Expenses for Business Use of Your Home",
            "Floor plan or diagram showing exclusive use area and total home square footage",
            "Partnership agreement provision reflecting home office requirement/authorization",
            "Calendar/meeting logs showing business use of home office space",
            "Annual home expense records: mortgage interest, utilities, insurance, repairs",
            "Depreciation schedule for home office portion (cost basis, placed-in-service date)",
        ],

        "cpa_handoff": [
            "UPE: partner home office deductible as unreimbursed partner expense on Schedule E — not employee restriction",
            "§280A(c)(6): W-2 employees cannot deduct home office post-TCJA 2018 — partnership structure avoids this",
            "Exclusive use: space must be used ONLY for business — no personal use permitted in office area",
            "S-Corp alternative: S-Corp pays accountable plan reimbursement to owner for home office costs",
            "Home office sale: depreciation claimed creates §1250 recapture on home sale — track and disclose",
            "Overlap with DTTS-031 (Augusta Rule): separate space from §280A(g) meeting rental — do not double-count",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-074-bonus-depreciation-on-used-property",
        "name": "Bonus Depreciation on Used Property",
        "_id": "69bdb40ee5397a28d45440cf",
        "irc": "IRC §168(k), §168(k)(1), §168(k)(2)(A), §168(k)(2)(A)(ii), §168(k)(6)",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Depreciation — Bonus §168(k)",
        "applicable_forms": ["1040", "1120", "1120S", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            (s.get("SIG_HAS_DEPRECIATION", False) or s.get("SIG_LOW_DEPRECIATION", False))
        ),

        "materiality_fn": lambda s: (
            65 if s.get("SIG_HIGH_TAX_LIABILITY", False) and s.get("SIG_LOW_DEPRECIATION", False) else 45
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_179_INCREMENTAL_DEDUCTION", 0) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("Q_179_INCREMENTAL_DEDUCTION", 0) * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 21,
        "complexity": 25,
        "audit_friction": 15,

        "plain_english": (
            "The Tax Cuts and Jobs Act of 2017 eliminated the 'original use' "
            "requirement for bonus depreciation — meaning used equipment and "
            "property acquired from an unrelated party now qualifies for "
            "first-year bonus depreciation just like new property. "
            "For dentists, this is particularly powerful when acquiring "
            "an existing dental practice: the purchase price allocated "
            "to equipment, furniture, and fixtures can receive 60% "
            "bonus depreciation in 2024 — creating a massive year-one "
            "deduction on the acquisition. A $500,000 allocation to "
            "qualifying used equipment generates a $300,000 deduction "
            "in the acquisition year. The used property must not have "
            "been previously used by the buyer, a related party, or "
            "a predecessor — so buying a second location's equipment "
            "from an unrelated seller qualifies; buying equipment from "
            "the dentist's own other practice does not."
        ),

        "documentation": [
            "Asset purchase agreement or allocation schedule (Form 8594 for business acquisitions)",
            "Evidence property was NOT previously used by taxpayer, related party, or predecessor",
            "Form 4562 — bonus depreciation election for placed-in-service year",
            "Asset description and MACRS recovery period classification",
            "State depreciation schedule — most states require separate state add-back for bonus",
            "§179 election if layering §179 with used property bonus depreciation",
        ],

        "cpa_handoff": [
            "§168(k)(2)(A)(ii): used property qualifies for bonus depreciation post-TCJA (after 9/27/2017)",
            "2024 bonus rate: 60%; phase-down continues — 40% in 2025, 20% in 2026, 0% after",
            "Related-party exclusion: property previously used by buyer, related party, or predecessor does NOT qualify",
            "Practice acquisition: allocate purchase price to FF&E/equipment; qualifies for used property bonus",
            "Form 8594: required for asset acquisitions — allocation between asset classes determines bonus eligibility",
            "State: most states decouple from federal bonus — run state depreciation at MACRS rates separately",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],

    },

    {
        "id": "DTTS-076-intra-family-loans-with-afr",
        "name": "Intra-Family Loans with AFR",
        "_id": "69bdb412e5397a28d45440d7",
        "irc": "IRC §7872, §7872(a), §7872(c), §7872(d), §7872(f)(2), §1274",
        "category": "General Planning",
        "overlap_group": "Family Entity Planning",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("SIG_DEPENDENTS_PRESENT", False) and
            s.get("Q_INVESTMENT_PORTFOLIO", 0) > 100_000  # §7872: need capital to lend
        ),

        "materiality_fn": lambda s: (
            50 if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("SIG_DEPENDENTS_PRESENT", False) else 30
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.035
),

        "state_savings_fn": lambda s: (
    min(
        s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.035,
        s.get("Q_INVESTMENT_PORTFOLIO", 0) * s.get("Q_STATE_MARGINAL_RATE", 0.05) * 0.50
    )
),

        "speed_days": 21,
        "complexity": 20,
        "audit_friction": 15,

        "plain_english": (
            "An intra-family loan allows a dentist to lend money to children, "
            "grandchildren, or a family trust at the IRS minimum interest "
            "rate (the Applicable Federal Rate, or AFR). As long as the "
            "loan charges at least the AFR, there is no gift tax element "
            "and no imputed income under §7872. The wealth transfer benefit "
            "comes from the spread: if the borrowed funds are invested and "
            "earn more than the AFR, the excess return accumulates in the "
            "child's hands — outside the dentist's taxable estate — "
            "without using any gift tax exemption. For example, lending "
            "$1 million at a 4.5% AFR while the child earns 8% on the "
            "funds transfers $35,000 per year in wealth to the next "
            "generation at no gift tax cost. The loan must be documented "
            "with a written promissory note, actual interest payments must "
            "be made, and the dentist reports the interest received as "
            "ordinary income."
        ),

        "documentation": [
            "Written promissory note at minimum AFR rate (published monthly by IRS Rev. Rul.)",
            "Amortization schedule showing principal and interest payments",
            "Evidence of actual interest payments received (bank records)",
            "Lender reports interest income on Schedule B",
            "Borrower investment account records showing use of loan proceeds",
            "§7872(d) de minimis analysis if loan ≤$10,000",
        ],

        "cpa_handoff": [
            "§7872: charge at least the AFR — below-market loans trigger imputed gift + income to lender",
            "AFR rates: short-term (<3yr), mid-term (3–9yr), long-term (>9yr) — published monthly in IRS Rev. Rul.",
            "Wealth transfer: spread between AFR paid to parent and investment return stays with child estate-tax-free",
            "No gift exemption used: loan at AFR = no taxable gift; only investment return above AFR transferred",
            "Lender: reports AFR interest received as ordinary income on Schedule B",
            "Borrower: may deduct interest if proceeds used for investment (§163(d)) or business (§162)",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires related-party role, compensation, and documentation review before implementation.",
        ],

    },

    {
        "id": "DTTS-077-installment-sale-to-intentionally-defective-grantor-trust",
        "name": "Installment Sale to Intentionally Defective Grantor Trust",
        "_id": "69bdb414e5397a28d45440e6",
        "irc": "IRC §453, §453(b), §671, §675, §§671–679, §1274",
        "category": "Trusts & Estate",
        "overlap_group": "Grantor Trust Planning",
        "applicable_forms": ["1041", "709"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("SIG_DEPENDENTS_PRESENT", False) and
            s.get("_agi", 0) > 750_000
        ),

        "materiality_fn": lambda s: (
            70 if s.get("_agi", 0) > 1_000_000 and s.get("SIG_DEPENDENTS_PRESENT", False) else 45
        ),

        "fed_savings_fn": lambda s: (
            3_000_000 * 0.40 * 0.30
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 120,
        "complexity": 75,
        "audit_friction": 20,

        "plain_english": (
            "An installment sale to an Intentionally Defective Grantor Trust "
            "combines two powerful tax tools: the grantor trust rules (which "
            "make the sale non-taxable) and an installment note (which "
            "provides a structured payment stream). The dentist sells "
            "an appreciating asset — practice equity, a management company "
            "interest, or investment real estate — to an irrevocable trust "
            "in exchange for a promissory note bearing the AFR rate. "
            "Because the trust is a grantor trust, the sale is treated "
            "as the dentist selling to themselves — no capital gains are "
            "recognized. The asset appreciates inside the trust, while "
            "the dentist's estate contains only the declining note balance "
            "(as the trust makes principal payments). The interest payments "
            "the trust makes to the dentist are also non-taxable — a "
            "grantor trust paying interest to its own grantor. "
            "All appreciation above the note amount compounds in the "
            "trust and eventually passes to heirs estate-tax-free."
        ),

        "documentation": [
            "IDGT trust document with §675 swap power (or other grantor trust trigger)",
            "Promissory note from trust to grantor at minimum AFR rate",
            "Qualified appraisal of asset sold to trust at date of sale",
            "Seed gift documentation (Form 709) — 10% of note face as initial gift to trust",
            "Annual note payment records — principal and interest actually paid by trust",
            "Form 6252 — not required (grantor trust sale is non-taxable); document non-recognition rationale",
        ],

        "cpa_handoff": [
            "Installment sale to IDGT: §671 grantor trust = grantor selling to themselves; no capital gains recognized",
            "Note at AFR: trust pays principal + AFR interest to grantor; interest received not taxable (grantor trust)",
            "Estate freeze: estate contains only declining note balance; trust holds appreciating asset outside estate",
            "Seed gift: ~10% of note face gifted to trust first — establishes trust's economic substance to repay note",
            "Grantor pays trust's income taxes annually — additional estate depletion and wealth transfer",
            "vs. DTTS-046 (general IDGT): this variant specifically uses §453 installment note as transfer mechanism",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],

    },

    {
        "id": "DTTS-078-esop-employee-stock-ownership-plan-setup",
        "name": "ESOP (Employee Stock Ownership Plan) Setup",
        "_id": "69bdb416e5397a28d45440f5",
        "irc": "IRC §4975(e)(7), §1042, §401(a), §404(a)(9), §404(k), §1368, §409(p)",
        "category": "Compensation & Benefits",
        "overlap_group": "ESOP Exit Strategy",
        "applicable_forms": ["1120", "1120S"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            (s.get("SIG_HAS_C_CORP", False) or s.get("SIG_HAS_S_CORP_VERIFIED", False)) and
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False)
        ),

        "materiality_fn": lambda s: (
            80 if s.get("SIG_HAS_S_CORP_VERIFIED", False) and s.get("SIG_VERY_HIGH_INCOME", False) else
            60 if s.get("SIG_HAS_C_CORP", False) and s.get("SIG_VERY_HIGH_INCOME", False) else 30
        ),

        "fed_savings_fn": lambda s: (
            min(s.get("_obi", 0), 500_000) * s.get("_fed_marginal_rate", 0) * 0.15
            if s.get("SIG_HAS_S_CORP_VERIFIED", False)
            else 125_000 * 0.21 * 0.15
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 365,
        "complexity": 85,
        "audit_friction": 30,

        "plain_english": (
            "An Employee Stock Ownership Plan (ESOP) is a qualified retirement "
            "plan that holds employer stock and offers some of the most powerful "
            "tax benefits available to dental practice owners. For an S-Corporation "
            "that becomes 100% ESOP-owned, all corporate income flows to "
            "the ESOP trust — which is tax-exempt — meaning the corporation "
            "effectively pays no federal income tax. This is the single "
            "most powerful ongoing income tax elimination strategy available "
            "in the tax code. For C-Corporation owners, the §1042 rollover "
            "allows deferral of all capital gains on the sale to the ESOP "
            "(see DTTS-047). The corporation can also deduct contributions "
            "to the ESOP of up to 25% of covered payroll annually. "
            "Important caveat for dentists: state dental practice laws may "
            "restrict who can own a dental professional corporation — "
            "ESOP feasibility requires a professional corporation law "
            "analysis in the practice state before proceeding."
        ),

        "documentation": [
            "ESOP plan document (§401(a) qualified plan requirements)",
            "ESOP trust agreement",
            "Form 5500 — annual plan reporting",
            "Annual ESOP valuation by independent appraiser (required annually)",
            "§409(p) synthetic equity analysis for S-Corp ESOP",
            "State professional corporation law analysis — ESOP ownership of dental practice permissibility",
        ],

        "cpa_handoff": [
            "S-Corp 100% ESOP: income flows to tax-exempt ESOP trust — no federal income tax at entity level",
            "§404(a)(9): contributions to ESOP deductible up to 25% of covered payroll (leveraged ESOP)",
            "§1042 C-Corp: owner can defer capital gains on sale to ESOP (requires C-Corp, 30% ESOP threshold)",
            "§409(p): S-Corp ESOP anti-abuse — disqualified persons synthetic equity cap; must be monitored",
            "Professional corp: state dental licensing board may restrict ESOP ownership — feasibility study required",
            "Annual valuation: ESOP must have independent FMV appraisal annually — significant ongoing cost",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-079-tax-efficient-entity-merger",
        "name": "Tax-Efficient Entity Merger",
        "_id": "69bdb417e5397a28d45440fe",
        "irc": "IRC §368, §368(a)(1)(A), §381, §382, §482, §708, §708(b), §704(c)",
        "category": "Entity & Structuring",
        "overlap_group": None,
        "applicable_forms": ["1120", "1120S", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_MULTI_ENTITY", False) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False)
        ),

        "materiality_fn": lambda s: (
            55 if s.get("SIG_MULTI_ENTITY", False) and s.get("SIG_HIGH_TAX_LIABILITY", False) else 30
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_MGMT_CO_REVENUE", 0) * 0.15 * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("Q_MGMT_CO_REVENUE", 0) * 0.15 * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 90,
        "complexity": 50,
        "audit_friction": 20,

        "plain_english": (
            "A tax-efficient entity merger consolidates multiple dental "
            "entities — practice entities, management companies, or "
            "multiple location LLCs — into a simpler structure. "
            "For dentists who have accumulated several entities over time, "
            "consolidation reduces compliance costs (multiple returns, "
            "accounting fees, payroll setups) and simplifies income "
            "allocation. Corporate mergers under §368 can be done "
            "tax-free when properly structured. Partnership mergers under "
            "§708 consolidate the entities with built-in gain tracking. "
            "The simplest approach for LLC-heavy structures is using "
            "check-the-box elections to convert entities to disregarded "
            "status — effectively merging them for tax purposes without "
            "a formal legal merger transaction. "
            "Key risks: if any entity has NOL carryforwards, §382 "
            "ownership change rules may limit future NOL utilization "
            "after merger; and built-in gains in contributed property "
            "must be tracked under §704(c)."
        ),

        "documentation": [
            "State law merger documents (articles of merger, plan of merger)",
            "Form 8832 for CTB elections used in conjunction with merger",
            "Tax-free reorganization analysis — §368 requirements: business purpose, COBE, COI",
            "§382 ownership change analysis if merged entity has NOL carryforwards",
            "§704(c) built-in gain schedule for contributed property from merged entity",
            "Final tax returns for terminated entities (short-period returns)",
        ],

        "cpa_handoff": [
            "§368: corporate merger can be tax-free if business purpose, COBE, and COI requirements met",
            "§708: partnership merger — continuing partnership inherits; terminated partnership files final return",
            "CTB alternative: convert entities to disregarded via Form 8832 — simplest tax-free 'merger'",
            "§382 risk: if merged entity has NOL carryforward, ownership change = annual NOL utilization cap",
            "§704(c): built-in gains/losses in contributed property must be tracked and allocated to contributors",
            "State law: separate state merger filings required; state tax conformity to §368/§708 varies",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-080-deferred-sales-trust-dst",
        "name": "Deferred Sales Trust (DST)",
        "_id": "69bdb419e5397a28d454410e",
        "irc": "IRC §453, §453(b), §671–679, §2501, §2511",
        "category": "Trusts & Estate",
        "overlap_group": "Grantor Trust Planning",
        "applicable_forms": ["1041"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            (s.get("SIG_REAL_ESTATE_ACTIVITY", False) or s.get("SIG_SCHEDULE_E_PRESENT", False)) and
            s.get("_agi", 0) > 500_000
        ),

        "materiality_fn": lambda s: (
            50 if s.get("SIG_REAL_ESTATE_ACTIVITY", False) and s.get("SIG_VERY_HIGH_INCOME", False) else 25
        ),

        "fed_savings_fn": lambda s: (
            166_600 * 0.25
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 90,
        "complexity": 75,
        "audit_friction": 40,

        "plain_english": (
            "A Deferred Sales Trust (DST) is a marketed tax strategy that "
            "uses the installment sale rules (§453) to defer capital gains "
            "recognition when selling an appreciated asset. Instead of "
            "selling directly to a buyer, the owner sells to an independently "
            "managed trust in exchange for an installment note — the trust "
            "then sells to the actual buyer and invests the proceeds. "
            "The owner receives installment payments over time and "
            "recognizes gain proportionally as payments arrive. "
            "Unlike an IDGT (which eliminates gain entirely because "
            "the trust is treated as the seller themselves), a DST "
            "only defers gain via §453 — it is still fully taxable, "
            "just spread over multiple years. "
            "Important warning: the IRS has scrutinized DST structures "
            "aggressively. If the trust is found to be acting as the "
            "seller's agent, the entire gain is recognized in the "
            "year of sale. This strategy carries significant audit "
            "risk and should only be pursued after thorough review "
            "by independent tax counsel — not through a promoter."
        ),

        "documentation": [
            "Independent third-party trust document (NOT grantor trust — separate taxpayer)",
            "Installment sale agreement between seller and DST at FMV",
            "Independent trustee appointment and investment mandate",
            "§453 gain calculation and deferral schedule",
            "IRS scrutiny analysis — confirm DST not acting as seller's agent",
            "Independent tax counsel opinion (not promoter opinion) on §453 treatment",
        ],

        "cpa_handoff": [
            "DST: §453 installment sale to third-party trust; gain deferred over payment term — NOT eliminated",
            "Different from IDGT: DST is NOT grantor trust — sale IS taxable; only deferred via installment",
            "Agent risk: if IRS determines trust is seller's agent, entire gain recognized in year of sale",
            "IRS scrutiny: DST structures have been challenged; some treated as listed transactions — high audit friction",
            "Independent counsel: require non-promoter independent opinion before recommending; avoid packaged promoter deals",
            "Alternative: consider §1031 exchange (full deferral) or installment sale directly to buyer (simpler §453)",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],

    },
    {
        "id": "DTTS-081-section-754-election-after-partner-death",
        "name": "Section 754 Election after Partner Death",
        "_id": "69bdb41ae5397a28d454411e",
        "irc": "IRC §754, §743(b), §1014, §734(b), §743(d)",
        "category": "General Planning",
        "overlap_group": None,
        "applicable_forms": ["1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_PARTNERSHIP", False) and
            s["SIG_K1_PRESENT"] and
            s.get("SIG_HIGH_INCOME", False)
        ),

        "materiality_fn": lambda s: (
        50 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HAS_PARTNERSHIP") else
        30 if s.get("SIG_HIGH_INCOME") or s.get("SIG_HAS_PARTNERSHIP") else
        20
    ),

        "fed_savings_fn": lambda s: (
    s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.10 * s.get("_fed_marginal_rate", 0) * 5
),

        "state_savings_fn": lambda s: (
    s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.10 * s.get("Q_STATE_MARGINAL_RATE", 0.05) * 5
),

        "speed_days": 30,
        "complexity": 25,
        "audit_friction": 10,

        "plain_english": (
            "When a dental partner dies, their heirs inherit the partnership "
            "interest at a stepped-up basis equal to the fair market value "
            "at death — but the partnership's internal asset basis stays "
            "at its historical cost. Without a §754 election, the heir "
            "would be taxed on income that economically represents "
            "appreciation that occurred before they even owned the interest. "
            "A §754 election instructs the partnership to adjust the heir's "
            "share of inside basis up to FMV — eliminating this phantom "
            "income going forward. The adjustment is made under §743(b) "
            "and reduces the heir's future taxable income from the partnership "
            "by the amount of the step-up, amortized over the applicable "
            "recovery periods. The election must be made on a timely filed "
            "Form 1065 for the year of death and is permanent once made. "
            "For partnerships with significantly appreciated assets, "
            "the §754 election after a partner's death is almost always "
            "beneficial to the successor."
        ),

        "documentation": [
            "Form 1065 with §754 election statement attached (timely filed for year of transfer)",
            "§743(b) basis adjustment calculation schedule",
            "Qualified appraisal of partnership interest at date of partner's death",
            "Estate tax return (Form 706) confirming FMV basis step-up under §1014",
            "Partnership agreement and ownership records confirming transfer to heir",
            "§743(d) built-in loss analysis — mandatory adjustment if loss >$250K",
        ],

        "cpa_handoff": [
            "§754 election: filed with Form 1065 for year of death — one-time election; applies to all future transfers",
            "§743(b): step-up equal to difference between heir's outside basis (FMV) and share of inside basis",
            "§1014 basis: heir's outside basis = FMV at date of death; §754 aligns inside basis to match",
            "Amortization: §743(b) adjustments amortized over applicable MACRS/§197 periods for each asset",
            "Irrevocable: §754 election cannot be revoked without IRS consent — model impact before electing",
            "§743(d): if partnership has built-in loss >$250K, §743(b) adjustment is mandatory regardless of election",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-082-gifting-appreciated-stock-to-family",
        "name": "Gifting Appreciated Stock to Family",
        "_id": "69bdb41ce5397a28d4544126",
        "irc": "IRC §2501, §2503(b), §1015, §1(g), §2505",
        "category": "General Planning",
        "overlap_group": "Family Entity Planning",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_DEPENDENTS_PRESENT", False)
        ),

        "materiality_fn": lambda s: (
            50 if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("SIG_DEPENDENTS_PRESENT", False) else 30
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.05 * 0.238
),

        "state_savings_fn": lambda s: (
    s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.05 * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 7,
        "complexity": 10,
        "audit_friction": 5,

        "plain_english": (
            "Gifting appreciated stock to family members can shift capital "
            "gains from the dentist's high tax bracket to a lower-bracket "
            "family member — or eliminate them entirely if the recipient "
            "is in the 0% long-term capital gains bracket. Each year, "
            "a dentist can gift up to $18,000 per recipient ($36,000 "
            "if married filing jointly) with no gift tax and no Form 709 "
            "required. The recipient inherits the dentist's original cost "
            "basis, not the current value — so the gain isn't eliminated, "
            "just shifted. If an adult child with little other income "
            "receives and sells the stock, they may owe zero capital gains "
            "tax on the appreciation. Two important traps: the 'kiddie tax' "
            "rules tax unearned income of children under 19 (or full-time "
            "students under 24) at the parent's rate, eliminating the benefit "
            "for young children. And gifting loses the step-up in basis "
            "that would occur at death — so if the dentist is not estate-tax "
            "exposed, holding appreciated stock until death may be better."
        ),

        "documentation": [
            "Brokerage transfer records showing shares gifted (date, FMV, number of shares)",
            "Form 709 if gifts exceed $18,000/donee/year or if splitting gifts with spouse",
            "Donor's basis records provided to donee (§1015 carryover basis documentation)",
            "Kiddie tax analysis: confirm donee is not subject to §1(g) (age ≥19 or non-student)",
            "Donee income analysis: confirm donee in 0% or 15% LTCG bracket before recommending",
            "Estate plan integration: confirm gift is consistent with overall estate plan",
        ],

        "cpa_handoff": [
            "§1015 carryover basis: donee inherits donor's adjusted basis — no step-up; gain shifts, not eliminates",
            "§1(g) kiddie tax: child under 19 (student under 24) — unearned income taxed at parent's rate; no bracket benefit",
            "§2503(b) annual exclusion: $18K/donee/yr ($36K MFJ gift-splitting); no Form 709 required",
            "0% LTCG bracket: 2024 threshold ~$47,025 single / ~$94,050 MFJ — confirm donee income before gifting",
            "vs. death step-up: gifting loses §1014 step-up; holding until death better if estate not taxable",
            "Estate reduction: FMV removed from estate; future appreciation also escapes estate — no clawback",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires related-party role, compensation, and documentation review before implementation.",
        ],

    },

    {
        "id": "DTTS-083-prepaid-expenses-via-management-company",
        "name": "Prepaid Expenses via Management Company",
        "_id": "69bdb41ee5397a28d454412e",
        "irc": "IRC §461, §461(h), §461(h)(3)(A), §482, §162, Treas. Reg. §1.263(a)-4(f)",
        "category": "Entity & Structuring",
        "overlap_group": "Management Company",
        "applicable_forms": ["1120S", "1120", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_MULTI_ENTITY", False) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False)
        ),

        "materiality_fn": lambda s: (
            45 if s.get("SIG_MULTI_ENTITY", False) and s.get("SIG_HIGH_TAX_LIABILITY", False) else 25
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_MGMT_CO_REVENUE", 0) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("Q_MGMT_CO_REVENUE", 0) * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 14,
        "complexity": 20,
        "audit_friction": 15,

        "plain_english": (
            "A dentist with a management company structure can prepay "
            "management fees before year-end and deduct them in the current "
            "tax year under the 12-month rule — as long as the benefit period "
            "does not extend beyond 12 months from the first date of benefit "
            "and does not cross into the second tax year following payment. "
            "This accelerates the deduction by 12 months, reducing current-year "
            "taxable income at the cost of a smaller deduction next year. "
            "The management company (typically on the cash method) recognizes "
            "the fee as income when received — but if the management company "
            "has its own deductible expenses or lower effective tax rate, "
            "there may be a combined tax benefit. The management fee must "
            "reflect actual arm's-length value of services provided — "
            "the IRS can reallocate income under §482 if the fee is "
            "set arbitrarily to shift income between related entities."
        ),

        "documentation": [
            "Management services agreement between practice and management company",
            "12-month rule analysis: confirm benefit does not extend beyond 12 months from first benefit date",
            "Payment records showing prepayment made before year-end",
            "Arm's-length fee study or comparable services analysis (§482 support)",
            "Management company income recognition records",
            "Form 8832 if management company classification requires CTB election",
        ],

        "cpa_handoff": [
            "Treas. Reg. §1.263(a)-4(f): 12-month rule — prepaid expense deductible if benefit ≤12 months from first use and ≤end of following tax year",
            "§461(h): accrual-method practice must meet economic performance — services must be rendered within period",
            "Cash-method practice: prepayment deductible in year paid if 12-month rule met — simpler analysis",
            "§482: management fee must be arm's-length FMV of actual services; IRS can reallocate if fee is arbitrary",
            "Management company income: cash-method management company recognizes income when received — timing mismatch opportunity",
            "State: most states conform to federal prepaid expense rules; confirm state method conformity",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-084-section-105-medical-reimbursement-plan-hra-flexibility-qsehra-ichra-etc",
        "name": "Section §105 Medical Reimbursement Plan HRA Flexibility (QSEHRA, ICHRA, etc.)",
        "_id": "69bdb41fe5397a28d4544136",
        "irc": "IRC §105, §105(b), §105(h), §106, §9831(d), §213",
        "category": "Compensation & Benefits",  # corrected from source JSON "Trusts & Estate"
        "overlap_group": "Health Insurance Deduction",
        "applicable_forms": ["1120", "1120S"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_W2_PRESENT", False) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("Q_HEALTH_PREMIUM", 0) > 0 and  # §105: needs premium to reimburse
            s.get("SIG_HEALTH_INS_EXPENSE", False)
        ),

        "materiality_fn": lambda s: (
            55 if s.get("SIG_HEALTH_INS_EXPENSE", False) and s.get("SIG_HAS_C_CORP", False) else
            40 if s.get("SIG_HEALTH_INS_EXPENSE", False) and s.get("SIG_HIGH_INCOME", False) else 20
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_HEALTH_PREMIUM", 0) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("Q_HEALTH_PREMIUM", 0) * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 21,
        "complexity": 20,
        "audit_friction": 10,

        "plain_english": (
            "A Health Reimbursement Arrangement (HRA) allows a dental practice "
            "to reimburse employees — including the owner-dentist — for health "
            "insurance premiums and qualified medical expenses tax-free. "
            "There are two main flavors: QSEHRA (for practices with fewer than "
            "50 full-time employees) reimburses up to $12,450 per family annually "
            "with no income tax or FICA on the reimbursement; ICHRA (available "
            "to any size employer) has no dollar cap and allows reimbursement "
            "of individual plan premiums. Unlike individual medical expense "
            "deductions (which require exceeding 7.5% of AGI), HRA "
            "reimbursements are fully excluded from income from dollar one. "
            "Important nuance: S-Corporation shareholders owning more than 2% "
            "cannot participate in a §125 cafeteria plan — but can often still "
            "benefit from a properly designed ICHRA or have premiums treated "
            "as W-2 income and then deducted above-the-line. C-Corporation "
            "owners receive the full §105/106 benefit with no restrictions."
        ),

        "documentation": [
            "Written HRA plan document (QSEHRA or ICHRA — separate document required)",
            "QSEHRA: 90-day advance notice to employees before plan year start",
            "ICHRA: employee notice requirement (90 days before plan year)",
            "Proof of employee's individual insurance coverage (required for reimbursement)",
            "§105(h) non-discrimination testing for self-insured plans (if applicable)",
            "S-Corp >2% shareholder: premium treatment as W-2 income + §162(l) above-line deduction analysis",
        ],

        "cpa_handoff": [
            "QSEHRA (§9831(d)): <50 FTE employer; max $6,150/individual, $12,450/family (2024); excluded from employee income",
            "ICHRA: any size employer; reimburse individual plan premiums; no dollar cap; must offer to employee class",
            "§105(h): non-discrimination rules — HMC cannot receive benefits not available to lower-paid employees",
            "S-Corp >2% shareholder: excluded from §106 group health plan; premium added to W-2; deduct §162(l) on 1040",
            "C-Corp owner: full §105/106 benefit; employer deducts; excluded from employee income — most favorable",
            "ACA: ICHRA satisfies employer mandate if affordable; employee cannot take premium tax credit if ICHRA affordable",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-085-roth-401-k-and-mega-backdoor-roth",
        "name": "Roth 401(k) and Mega Backdoor Roth",
        "_id": "69bdb420e5397a28d454414b",
        "irc": "IRC §402A, §402A(b), §401(m), §408A, §402(c), §401(k)(2)(B)",
        "category": "Retirement Plans",
        "overlap_group": "Roth Conversion Strategy",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_W2_PRESENT", False) and
            s.get("SIG_HAS_RETIREMENT_PLAN", False)
        ),

        "materiality_fn": lambda s: (
            75 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HAS_RETIREMENT_PLAN") else
            60 if s.get("SIG_HIGH_INCOME") and s.get("SIG_HAS_RETIREMENT_PLAN") else
            45 if s.get("SIG_HIGH_INCOME") else
            30
        ),

        "fed_savings_fn": lambda s: (
            23_000 * ((1.07 ** 15) - 1) * 0.238 * 0.15
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 21,
        "complexity": 20,
        "audit_friction": 5,

        "plain_english": (
            "High-income dentists cannot contribute directly to a Roth IRA "
            "(income limits phase out at $240,000 for married filers in 2024) "
            "— but the Roth 401(k) and mega backdoor Roth bypass that restriction "
            "entirely. A Roth 401(k) simply means designating regular elective "
            "deferrals (up to $23,000 in 2024, plus $7,500 catch-up if 50+) "
            "as Roth — after-tax today, tax-free forever. The mega backdoor "
            "Roth goes further: if the dental practice's 401(k) plan allows "
            "after-tax (non-Roth) contributions AND in-service withdrawals, "
            "the dentist can contribute up to $46,000 more in after-tax "
            "dollars, then immediately roll them to a Roth IRA. This creates "
            "up to $69,000 per year in total Roth-eligible contributions — "
            "dramatically accelerating tax-free retirement wealth. "
            "The key requirements: the plan document must explicitly permit "
            "after-tax contributions and in-service distributions — most "
            "off-the-shelf plan documents do not; a custom plan amendment "
            "is needed."
        ),

        "documentation": [
            "401(k) plan document amendment permitting after-tax contributions and in-service withdrawals",
            "Roth 401(k) deferral election designation form",
            "Form 1099-R for in-service distribution of after-tax contributions (code G rollover)",
            "Form 8606 tracking Roth IRA basis from rollover contributions",
            "§415 annual addition limit calculation confirming room for after-tax contributions",
            "SECURE 2.0: Roth catch-up requirement for participants with wages >$145K (2024+)",
        ],

        "cpa_handoff": [
            "Roth 401(k) (§402A): no income limit; after-tax contributions; qualified distributions tax-free",
            "Mega backdoor: after-tax (non-Roth) §401(m) contributions → in-service withdrawal → Roth IRA rollover",
            "Plan document: must permit both after-tax contributions AND in-service distributions — most don't by default",
            "§415 limit: $69,000 total (2024) — elective + employer + after-tax combined cannot exceed this",
            "Conversion taxation: only earnings on after-tax contributions taxable at conversion; basis is not",
            "SECURE 2.0: after 2023, catch-up contributions for >$145K earners must be Roth — verify plan amendment",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],

    },

    {
        "id": "DTTS-086-lifetime-learning-credit",
        "name": "Lifetime Learning Credit",
        "_id": "69bdb421e5397a28d4544160",
        "irc": "IRC §25A, §25A(b), §25A(d), §25A(f), §25A(g)(2)",
        "category": "Credits & Incentives",
        "overlap_group": "Education Credits",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_DEPENDENTS_PRESENT", False) and s.get("_agi", 0) < _LIM["llc_phaseout_mfj"]  # LLC phases out at $180K MFJ
        ),

        "materiality_fn": lambda s: (
            40 if s.get("_agi", 0) < 160_000 else
            20 if s.get("_agi", 0) < _LIM["llc_phaseout_mfj"] else
            15  # dependent child scenario only
        ),

        "fed_savings_fn": lambda s: (
            max(2_000 * max(0, 1 - max(0, (s.get("_agi", 0) - (_LIM["llc_phaseout_mfj"] - 20_000)) / 20_000)), 0)
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 7,
        "complexity": 5,
        "audit_friction": 5,

        "plain_english": (
            "The Lifetime Learning Credit provides a tax credit of 20% of "
            "the first $10,000 paid for qualified tuition and related expenses — "
            "up to a maximum of $2,000 per tax return. Unlike the American "
            "Opportunity Credit (which is limited to the first four years of "
            "college), the LLC applies to any year of post-secondary education "
            "including graduate school, professional courses, and continuing "
            "education. However, the credit phases out completely at $180,000 "
            "AGI for married filers — meaning most practice-owner dentists "
            "above that threshold receive no benefit themselves. The credit "
            "is most valuable for associate dentists in early career, dental "
            "students, or dentist-owners whose dependent children are in "
            "college or graduate school. For higher-income dentists, the "
            "§127 employer educational assistance exclusion (up to $5,250 "
            "tax-free through the practice) often provides greater benefit "
            "than the LLC — the two cannot be stacked on the same expenses."
        ),

        "documentation": [
            "Form 1098-T from eligible educational institution (required to claim credit)",
            "Tuition payment receipts and records",
            "Form 8863 — Education Credits",
            "Phaseout calculation if AGI between $160K–$180K MFJ",
            "§25A(g)(2) coordination: confirm same expenses not deducted under §127 or §222",
            "Dependent student eligibility: confirm student is claimed as dependent on return",
        ],

        "cpa_handoff": [
            "§25A(b): LLC = 20% × first $10,000 qualified tuition = $2,000 max credit per return (not per student)",
            "Phaseout 2024: $160K–$180K MFJ; $80K–$90K single — fully phased out above upper limit",
            "High-income practice owners: typically fully phased out; most useful for associates or dependent children",
            "No double benefit: §25A(g)(2) — cannot claim LLC on expenses also excluded under §127 (employer plan)",
            "Continuing education: courses at eligible post-secondary institutions qualify even for existing practitioners",
            "vs. §127: employer educational assistance ($5,250 tax-free) often higher value at practice-owner income levels",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-089-qualified-disability-trust-qdt-deduction",
        "name": "Qualified Disability Trust (QDT) Deduction",
        "_id": "69bdb424e5397a28d4544168",
        "irc": "IRC §642(b)(2)(C), §642(b)(3), §661, §662, §1(e)",
        "category": "Trusts & Estate",
        "overlap_group": None,
        "applicable_forms": ["1041"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_DEPENDENTS_PRESENT", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False)
        ),

        "materiality_fn": lambda s: (
            40 if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("SIG_DEPENDENTS_PRESENT", False) else 20
        ),

        "fed_savings_fn": lambda s: (
            7_500 + 1_757
        ),

        "state_savings_fn": lambda s: (
            50_000 * s.get("Q_STATE_MARGINAL_RATE", 0.03)
        ),

        "speed_days": 90,
        "complexity": 50,
        "audit_friction": 15,

        "plain_english": (
            "A Qualified Disability Trust (QDT) is an irrevocable trust "
            "established for the sole benefit of a disabled individual who "
            "meets the Social Security Administration's disability definition. "
            "Unlike a standard complex trust — which is entitled to only a "
            "$300 exemption and hits the top 37% tax bracket at just $15,200 "
            "of income — a QDT gets the full individual personal exemption "
            "($5,050 in 2024) and can distribute income to the disabled "
            "beneficiary who is taxed at their own typically lower rates. "
            "For a dentist with a disabled child, sibling, or spouse, a QDT "
            "(often structured as a Special Needs Trust to protect government "
            "benefit eligibility) allows the practice to fund a trust that "
            "provides lifelong financial support — while keeping the "
            "beneficiary eligible for SSI and Medicaid. The trust must be "
            "established before the beneficiary turns 65, and the disability "
            "must meet the SSA §1614(a)(3) standard."
        ),

        "documentation": [
            "QDT trust document (irrevocable; sole benefit of disabled individual)",
            "SSA disability determination documentation for beneficiary (§1614(a)(3))",
            "Form 1041 — annual trust income tax return with QDT exemption claimed",
            "§661/662 DNI analysis if distributing income to beneficiary",
            "Special Needs Trust coordination if preserving SSI/Medicaid eligibility",
            "Beneficiary age confirmation: must be established before age 65",
        ],

        "cpa_handoff": [
            "§642(b)(2)(C): QDT uses individual personal exemption ($5,050 in 2024) vs. $300 for complex trust",
            "Disability: beneficiary must meet SSA §1614(a)(3) — total disability; not merely health-impaired",
            "Income distribution: §661/662 DNI distributed to disabled beneficiary taxed at their rate (typically lower than trust's compressed rates)",
            "Trust rates: trusts hit 37% at $15,200 (2024) — distributing income to beneficiary avoids this compression",
            "SNT coordination: QDT can be combined with Special Needs Trust structure to preserve SSI/Medicaid",
            "NOTE: Source JSON cites §101/§2042 (life insurance) — those are not QDT authority; §642(b)(2)(C) is correct",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],

    },

    {
        "id": "DTTS-090-installment-sale-to-esop-with-1042-rollover",
        "name": "Installment Sale to ESOP with §1042 Rollover",
        "_id": "69bdb425e5397a28d4544177",
        "irc": "IRC §1042, §1042(a), §1042(b), §1042(c), §1042(d), §453, §4975(e)(7)",
        "category": "Exit & Sale",
        "overlap_group": "ESOP Exit Strategy",
        "applicable_forms": ["1120", "1040"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_C_CORP", False) and
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False)
        ),

        "materiality_fn": lambda s: (
            85 if s.get("SIG_HAS_C_CORP", False) and s.get("SIG_VERY_HIGH_INCOME", False) else 30
        ),

        "fed_savings_fn": lambda s: (
            2_700_000 * 0.238 * 0.25
        ),

        "state_savings_fn": lambda s: (
            2_700_000 * s.get("Q_STATE_MARGINAL_RATE", 0.05) * 0.15
        ),

        "speed_days": 365,
        "complexity": 85,
        "audit_friction": 25,

        "plain_english": (
            "When a C-Corporation dental practice owner sells at least 30% "
            "of their stock to an ESOP, they can elect under §1042 to defer — "
            "and potentially eliminate — all capital gains on the sale. "
            "The seller takes the proceeds and reinvests them in 'Qualified "
            "Replacement Property' (QRP) — typically floating-rate bonds or "
            "private operating company stock. The gain is deferred as long "
            "as the QRP is held. If the seller holds the QRP until death, "
            "heirs receive a stepped-up basis and the original deferred gain "
            "disappears entirely — a permanent tax elimination. Combining "
            "§1042 with an installment note from the ESOP creates additional "
            "flexibility: the seller receives payments over time and can "
            "manage QRP reinvestment timing. Critical requirements: the "
            "entity must be a C-Corporation (not S-Corp), the ESOP must "
            "own ≥30% after the sale, and the stock must have been held "
            "at least three years. State dental licensing laws may limit "
            "ESOP ownership of professional dental corporations."
        ),

        "documentation": [
            "§1042 election statement filed with seller's Form 1040 for year of sale",
            "Statement of consent from corporation (§1042(e) anti-disposal provisions)",
            "QRP purchase records within 15-month window (3 months before / 12 months after sale)",
            "ESOP purchase agreement and independent FMV appraisal",
            "Proof ESOP owns ≥30% of C-Corp after sale",
            "Form 5500 — ESOP annual plan return; Form 6252 — installment income if installment used",
        ],

        "cpa_handoff": [
            "§1042: C-Corp only; ESOP must own ≥30% post-sale; stock held ≥3 years; §1042 election on Form 1040",
            "QRP: proceeds must be reinvested in domestic C-Corp securities not actively traded within 15 months",
            "Deferred gain: QRP sale triggers deferred gain recognition; hold QRP until death → §1014 step-up eliminates gain",
            "§453 installment: installment note from ESOP can spread remaining non-§1042 portion; complex interaction",
            "Professional corp: state dental licensing restricts ESOP ownership — C-Corp dental PC feasibility varies by state",
            "Anti-disposal: §1042(e) — if corporation disposes of equivalent securities within 3 years, excise tax applies",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-091-defined-benefit-plan",
        "name": "Defined Benefit Plan",
        "_id": "69bdb426e5397a28d4544190",
        "irc": "IRC §401(a), §412, §415(b), §404(a)(1), §430, §436, §411, §416",
        "category": "Retirement Plans",
        "overlap_group": "Retirement Plan",
        "applicable_forms": ["1120S", "1120"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            (s.get("SIG_NO_RETIREMENT_PLAN", False) or s.get("SIG_RETIREMENT_UNDERFUNDED", False)) and
            s.get("SIG_W2_PRESENT", False) and
            (s.get("SIG_HAS_S_CORP_VERIFIED", False) or
             s.get("SIG_SELF_EMPLOYED", False) or
             s.get("SIG_BUSINESS_PRESENT", False))  # must have a business to sponsor the plan
        ),

        "materiality_fn": lambda s: (
            85 if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("SIG_NO_RETIREMENT_PLAN", False) else
            70 if s.get("SIG_HIGH_INCOME", False) and s.get("SIG_NO_RETIREMENT_PLAN", False) else
            50
        ),

        "fed_savings_fn": lambda s: (
            # DB contribution = actuarially determined.  Without actuary we use:
            #   - If questionnaire provides amount → use it (capped at §415 limit)
            #   - Else → use _max_db_contribution (age-proxy, set in SignalEngine)
            min(
                s.get("Q_CASH_BALANCE_INCREMENTAL", s.get("_max_db_contribution", 175_000)),
                275_000  # §415(b) absolute cap
            ) * s.get("_fed_marginal_rate", 0.37)
        ),

        "state_savings_fn": lambda s: (
            min(
                s.get("Q_CASH_BALANCE_INCREMENTAL", s.get("_max_db_contribution", 175_000)),
                275_000
            ) * (s.get("_state_tax", 0) / s.get("_agi", 1) if s.get("_agi", 0) else 0.05)
        ),

        "speed_days": 60,
        "complexity": 45,
        "audit_friction": 15,

        "plain_english": (
            "A defined benefit (DB) pension plan allows a dental practice "
            "to make far larger tax-deductible contributions than a standard "
            "401(k) — especially for older dentists who need to catch up on "
            "retirement savings. While a solo 401(k) maxes out at $69,000 "
            "per year, a DB plan contribution is actuarially determined based "
            "on the promised retirement benefit, the dentist's age, and years "
            "to retirement. A 52-year-old dentist targeting the §415 maximum "
            "benefit may contribute $150,000 or more per year — all "
            "fully deductible. The plan can be combined with a 401(k) "
            "for even larger total contributions. Two important downsides: "
            "DB plans require minimum funding every year regardless of "
            "income (missing contributions triggers a 10% excise tax), "
            "and an enrolled actuary must certify contributions annually "
            "at a cost of $2,000–$5,000 per year. Top-heavy rules "
            "also require minimum contributions for non-key employees "
            "in practices with staff."
        ),

        "documentation": [
            "DB plan document (§401(a) qualified plan; enrolled actuary required)",
            "Annual actuarial certification of minimum required contribution (§412/§430)",
            "Form 5500 annual plan return",
            "§415(b) benefit limit calculation confirming deductibility",
            "Top-heavy analysis (§416) — minimum contribution for non-key employees if >60% key",
            "§4972 excise tax monitoring — confirm contributions do not exceed §404(a)(1) deductible limit",
        ],

        "cpa_handoff": [
            "DB plan: actuarially determined contribution; far exceeds DC plan limits; age-sensitive — more powerful for older dentists",
            "§415(b): max annual benefit $275K (2024); contribution sized to fund that benefit based on age and return assumptions",
            "Mandatory funding (§412/§430): must contribute minimum every year; failure = §4972 10% excise tax",
            "Top-heavy (§416): small practice DB plans almost always top-heavy — minimum 2% employer contribution for non-key staff",
            "Actuary: enrolled actuary (EA) required annually to certify funding — $2K–$5K/yr cost",
            "Combination: DB + 401(k) profit-sharing allowed; DB absorbs bulk of §415 room; 401(k) adds employee deferral",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],

    },

    {
        "id": "DTTS-093-s-corp-reasonable-compensation-planning",
        "name": "S-Corp Reasonable Compensation Planning",
        "_id": "69bdb428e5397a28d45441a2",
        "irc": "IRC §162, §1366, §3121, §3121(a), §61, §1402(a)(2), Rev. Rul. 74-44",
        "category": "Entity & Structuring",
        "overlap_group": "S-Corp Compensation",
        "applicable_forms": ["1120S"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_S_CORP_VERIFIED", False) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("_distributions", 0) > 0 and  # must actually have distributions to optimize
            (s.get("SIG_LOW_OWNER_WAGES", False) or s.get("SIG_HIGH_DISTRIBUTIONS_VS_WAGES", False))
        ),

        "materiality_fn": lambda s: (
            75 if s.get("SIG_LOW_OWNER_WAGES", False) and s.get("SIG_HIGH_INCOME", False) else
            55 if s.get("SIG_HAS_S_CORP_VERIFIED", False) and s.get("SIG_HIGH_INCOME", False) else 35
        ),

        "fed_savings_fn": lambda s: (
    max(0, (s.get("_wages", 0) - s.get("_obi", 0) * 0.40)) * 0.153 * 0.9235
    if s.get("_wages", 0) > s.get("_obi", 0) * 0.40
    else 0  # already optimized or under-paying — no NEW savings from this strategy
),

        "state_savings_fn": lambda s: (
    0
),

        "speed_days": 14,
        "complexity": 30,
        "audit_friction": 25,

        "plain_english": (
            "⚠ AUDIT RISK: S-Corp owners must pay themselves reasonable compensation. "
            "If current W-2 wages are below 30–40% of practice income, the IRS will "
            "likely reclassify distributions as wages on audit — with back FICA taxes, "
            "interest, and penalties. Recommended action: raise salary to a defensible "
            "level (typically $150K–$200K for a dentist with $400K+ income), documented "
            "with ADA/MGMA compensation surveys. This restructuring also unlocks large "
            "retirement plan contributions — see Salary + Retirement Restructure strategy."
        ),

        "documentation": [
            "Industry salary survey or comparable practitioner wage study (MGMA, ADA compensation survey)",
            "Board minutes or resolution documenting officer compensation decision",
            "Form W-2 reflecting salary paid and FICA withheld",
            "1120S officer compensation disclosure (Schedule E, Part II)",
            "Distribution records separate from payroll (to demonstrate proper split)",
            "Prior year officer comp history to document consistent treatment",
        ],

        "cpa_handoff": [
            "§3121: wages to shareholder-employees subject to FICA; K-1 distributions are not — FICA arbitrage is the core benefit",
            "Rev. Rul. 74-44: IRS will reclassify distributions as wages if compensation unreasonably low",
            "Reasonable comp: salary should reflect FMV of services; ADA / MGMA survey data supports documentation",
            "Audit risk: S-Corps with low wages / high distributions flagged by IRS DIF scoring — document proactively",
            "SS wage base $168,600 (2024): savings on distributions below base = 15.3%; above base = 2.35% (Medicare only)",
            "Interaction with retirement plans: salary (W-2) drives retirement plan contribution capacity; optimize accordingly",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-095-net-investment-income-tax-niit-avoidance",
        "name": "Net Investment Income Tax (NIIT) Avoidance",
        "_id": "69bdb42be5397a28d45441a9",
        "irc": "IRC §1411, §1411(c), §1411(c)(4), §469, §1411(c)(2)",
        "category": "Real Estate & Depreciation",
        "overlap_group": None,
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HIGH_INCOME", False) and
            (s.get("SIG_REAL_ESTATE_ACTIVITY", False) or s.get("SIG_SCHEDULE_E_PRESENT", False)) and
            s.get("_agi", 0) > 250_000
        ),

        "materiality_fn": lambda s: (
            55 if s.get("SIG_REAL_ESTATE_ACTIVITY", False) and s.get("SIG_VERY_HIGH_INCOME", False) else 35
        ),

        "fed_savings_fn": lambda s: (
    s.get("_niit", 0) if s.get("_niit", 0) > 0 else s.get("_agi", 0) * 0.038 * 0.10
),

        "state_savings_fn": lambda s: (
    0
),

        "speed_days": 30,
        "complexity": 25,
        "audit_friction": 20,

        "plain_english": (
            "The Net Investment Income Tax (NIIT) adds a 3.8% surcharge "
            "on investment income — interest, dividends, rents, royalties, "
            "and passive business gains — for dentists with MAGI above "
            "$250,000 (married) or $200,000 (single). Practice income "
            "from an active S-Corporation is already exempt. The main "
            "exposure for dentists is rental income from investment properties "
            "(passive by default) and capital gains on investment real estate. "
            "Avoidance strategies include converting passive rental income "
            "to active by materially participating in the rental activity "
            "(e.g., short-term rentals where the average stay is 7 days or "
            "fewer and the dentist materially participates), using the §469 "
            "grouping election to aggregate activities, or restructuring "
            "entities so the dentist has active involvement. Installment "
            "sales can spread gain across multiple years, reducing the "
            "NIIT base in any single year. For dentists with substantial "
            "rental portfolios, the 3.8% savings can be material — "
            "$500,000 of reclassified passive income = $19,000 saved."
        ),

        "documentation": [
            "Form 8960 — Net Investment Income Tax calculation",
            "§469 material participation log (750+ hours for real estate professional; hours by activity for material participation tests)",
            "Grouping election statement (Treas. Reg. §1.469-11) if grouping rental activities",
            "Short-term rental analysis: confirm average stay ≤7 days and material participation for active treatment",
            "S-Corp/partnership activity analysis: confirm active vs. passive classification for each entity",
            "Installment sale schedule if spreading gain to reduce annual NIIT exposure",
        ],

        "cpa_handoff": [
            "§1411: 3.8% NIIT on lesser of NII or MAGI above threshold ($250K MFJ / $200K single)",
            "NII includes: passive rental income, dividends, interest, royalties, passive activity gains",
            "S-Corp practice income: active (material participation) → excluded from NII; passive → included",
            "Real estate professional: 750+ hours RE activities + more time in RE than any other profession — dentist rarely qualifies",
            "Short-term rental: avg stay ≤7 days = not rental activity under §469 → active if materially participates → no NIIT",
            "Grouping: §1.469-11 grouping election aggregates activities; material participation in group = all active → no NIIT",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],

    },

    {
        "id": "DTTS-096-self-directed-ira-solo-401-k-for-re-notes",
        "name": "Self-Directed IRA / Solo 401(k) for RE & Notes",
        "_id": "69bdb42de5397a28d45441b1",
        "irc": "IRC §408, §408(a), §408(e)(1), §4975, §4975(c), §511, §512, §401",
        "category": "Retirement Plans",
        "overlap_group": "Retirement Plan",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HIGH_INCOME", False) and
            (s.get("SIG_HAS_RETIREMENT_PLAN", False) or s.get("SIG_REAL_ESTATE_ACTIVITY", False))
        ),

        "materiality_fn": lambda s: (
            65 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_REAL_ESTATE_ACTIVITY") else
            45 if s.get("SIG_REAL_ESTATE_ACTIVITY") and s.get("SIG_HAS_RETIREMENT_PLAN") else
            35 if s.get("SIG_HIGH_INCOME") else
            20
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_CASH_BALANCE_INCREMENTAL", 0) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("Q_CASH_BALANCE_INCREMENTAL", 0) * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 30,
        "complexity": 25,
        "audit_friction": 15,

        "plain_english": (
            "A self-directed IRA or solo 401(k) allows a dentist to invest "
            "retirement funds in alternative assets — real estate, promissory "
            "notes, private equity, or even interests in other dental practices "
            "— with all income and gains sheltered from current taxes inside "
            "the account. Unlike standard IRAs that only hold stocks and "
            "mutual funds, a self-directed account can hold virtually any "
            "investment the IRS doesn't specifically prohibit. The most "
            "important rule is the prohibited transaction restriction: the "
            "dentist cannot buy property they already own, lend the IRA "
            "money to themselves or family members, or personally benefit "
            "from IRA investments — any prohibited transaction disqualifies "
            "the entire account, making all funds immediately taxable. "
            "If the IRA uses debt financing (mortgage) to buy real estate, "
            "the leveraged portion generates Unrelated Business Taxable Income "
            "(UBTI) — the IRA pays taxes on that at trust rates. A Roth "
            "solo 401(k) avoids this issue for qualified plan investors."
        ),

        "documentation": [
            "SDIRA custodian agreement (specialized custodian required — Equity Trust, Pensco, etc.)",
            "Investment-specific documentation (real estate deed, promissory note, LLC operating agreement)",
            "§4975 prohibited transaction analysis before each investment",
            "UBTI/UBIT analysis if debt-financing real estate in IRA (Form 990-T if UBTI >$1,000)",
            "Solo 401(k) plan document if using plan instead of IRA (must permit alternative investments)",
            "Annual fair market valuation of non-traded IRA assets (required by custodian)",
        ],

        "cpa_handoff": [
            "§408(e)(1): IRA income tax-exempt; §511/512: UBTI applies to debt-financed income inside IRA",
            "§4975(c): prohibited transactions — no self-dealing; IRA cannot transact with owner, spouse, lineal descendants, or their businesses",
            "§4975 disqualification: prohibited transaction = entire IRA deemed distributed; full tax + 10% penalty in year of violation",
            "UBTI on leveraged RE: IRA using mortgage to buy RE generates UDFI (unrelated debt-financed income) = UBTI; Form 990-T",
            "Solo 401(k): qualified plan UDFI exception for RE doesn't exist unless structured properly; REIT alternative avoids UBTI",
            "Roth SDIRA: same prohibited transaction rules; same UBTI; but tax-free growth and distributions — preferred vehicle",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],

    },

    {
        "id": "DTTS-097-tax-efficient-sale-via-grantor-retained-annuity-trust-grat",
        "name": "Tax-Efficient Sale via Grantor Retained Annuity Trust (GRAT)",
        "_id": "69bdb42fe5397a28d45441ba",
        "irc": "IRC §2702, §2702(b), §7520, §2036, §671–677, §2001",
        "category": "Trusts & Estate",
        "overlap_group": "Grantor Trust Planning",
        "applicable_forms": ["1041", "709"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("SIG_DEPENDENTS_PRESENT", False) and
            s.get("_agi", 0) > 750_000
        ),

        "materiality_fn": lambda s: (
            65 if s.get("_agi", 0) > 1_000_000 and s.get("SIG_DEPENDENTS_PRESENT", False) else 40
        ),

        "fed_savings_fn": lambda s: (
            1_458_000 * 0.40 * 0.30
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 90,
        "complexity": 60,
        "audit_friction": 20,

        "plain_english": (
            "A Grantor Retained Annuity Trust (GRAT) allows a dentist to "
            "transfer appreciating assets to heirs with little or no gift tax. "
            "The dentist transfers an asset — practice equity, DSO stock, or "
            "an investment portfolio — to the GRAT and receives back a fixed "
            "annuity payment each year for the trust's term. The annuity is "
            "sized so the present value equals the asset's value at transfer, "
            "making the taxable gift approximately zero. If the asset grows "
            "faster than the IRS hurdle rate (currently around 5%), all "
            "appreciation above that rate passes to the remainder beneficiaries "
            "(children or a trust for them) free of estate and gift tax. "
            "If the asset doesn't beat the hurdle rate, the asset simply "
            "flows back to the dentist via annuity payments — no harm, no foul. "
            "The key risk: if the dentist dies during the GRAT term, the "
            "assets return to the estate. GRATs work best with short terms "
            "or rolling multi-year GRATs to minimize mortality risk."
        ),

        "documentation": [
            "GRAT trust document with qualified annuity interest terms",
            "Independent appraisal of transferred asset at date of transfer",
            "§7520 rate determination for month of transfer (IRS publishes monthly)",
            "Form 709 — gift tax return (even if taxable gift = $0, disclosure required)",
            "Annual annuity payment records (payments must be made on schedule)",
            "§2036 mortality risk analysis — confirm grantor health and term selection",
        ],

        "cpa_handoff": [
            "§2702: retained annuity interest valued at PV of annuity payments under §7520 rate; excess = taxable gift",
            "Zeroed-out GRAT: annuity sized so PV of all payments = asset FMV; taxable gift ≈ $0",
            "Hurdle rate: §7520 rate (AFR × 120%); all growth above hurdle passes to heirs estate-tax-free",
            "§2036 mortality: grantor death during term = assets included in estate; shorter terms and rolling GRATs reduce risk",
            "Grantor trust: GRAT is grantor trust; all income/gain on grantor's return during term; grantor pays tax = additional wealth transfer",
            "Timing: use when §7520 rate is LOW (larger annuity value = smaller gift) AND asset expected to appreciate significantly",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],

    },

    {
        "id": "DTTS-099-insurance-dedicated-fund-idf-within-ppli",
        "name": "Insurance-Dedicated Fund (IDF) within PPLI",
        "_id": "69bdb430e5397a28d45441c3",
        "irc": "IRC §7702, §7702(a), §817(h), §817(h)(1), §101(a), §72",
        "category": "Insurance & Risk",
        "overlap_group": "Life Insurance Planning",
        "applicable_forms": ["1040"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("_agi", 0) > 1_000_000
        ),

        "materiality_fn": lambda s: (
            65 if s.get("_agi", 0) > 1_500_000 else 40
        ),

        "fed_savings_fn": lambda s: (
            (200_000 * 0.238 - 20_000) * 0.20
        ),

        "state_savings_fn": lambda s: (
            200_000 * 0.05 * 0.20
        ),

        "speed_days": 180,
        "complexity": 75,
        "audit_friction": 25,

        "plain_english": (
            "Private Placement Life Insurance (PPLI) with an Insurance-Dedicated "
            "Fund (IDF) allows a high-net-worth dentist to invest large sums "
            "in hedge funds or private equity strategies inside a life insurance "
            "wrapper — sheltering all investment returns from current income tax. "
            "Instead of paying tax on dividends, interest, and capital gains "
            "each year, the dentist's investments grow tax-deferred inside the "
            "policy, and can ultimately be accessed through tax-free policy loans "
            "or passed as an income-tax-free death benefit. The IDF is a "
            "special fund created exclusively for PPLI policies — the same "
            "strategy used by certain hedge funds is not available to direct "
            "investors but is accessible inside the insurance wrapper. "
            "Critical compliance requirements: the policyholder cannot "
            "direct specific investments (investor control doctrine); the "
            "IDF must be sufficiently diversified under §817(h); and the "
            "insurance charges (typically 0.5%–1.5% per year) must be "
            "justified by the tax savings. Minimum investments typically "
            "start at $1 million to $5 million."
        ),

        "documentation": [
            "PPLI policy document with §7702 compliance analysis",
            "§817(h) diversification memorandum for IDF",
            "Investor control analysis (Rev. Rul. 2003-92) confirming no prohibited investor control",
            "IDF offering memorandum confirming fund offered to multiple PPLI policies",
            "Insurance cost/benefit analysis: mortality charges vs. annual tax savings",
            "Offshore policy: FBAR/Form 8938 reporting if offshore carrier used",
        ],

        "cpa_handoff": [
            "§7702: policy must qualify as life insurance under CVAT or GPT; annual income not taxed inside qualifying policy",
            "§817(h): IDF must meet diversification requirements; no single investment >55% of assets",
            "Investor control: Rev. Rul. 2003-92 — policyholder cannot direct specific IDF investments; must be managed independently",
            "Tax deferral: all interest, dividends, capital gains inside policy grow tax-deferred; loans from policy not taxable",
            "Death benefit: §101(a) exclusion — death benefit income-tax-free to beneficiaries",
            "Insurance charges: typically 0.5%–1.5%/yr; model break-even against annual tax savings before recommending",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires policy design, underwriting/actuarial review, and compliance documentation before implementation.",
        ],

    },

    {
        "id": "DTTS-100-net-unrealized-appreciation-nua-tax-planning",
        "name": "Net Unrealized Appreciation (NUA) Tax Planning",
        "_id": "69bdb433e5397a28d45441cc",
        "irc": "IRC §402(e)(4), §402(e)(4)(A), §402(e)(4)(D), §402(a), §1(h)",
        "category": "General Planning",
        "overlap_group": "Retirement Plan",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_RETIREMENT_PLAN", False) and
            (s.get("SIG_HAS_S_CORP_VERIFIED", False) or s.get("SIG_HAS_C_CORP", False)) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("_retirement", 0) > 200_000
        ),

        "materiality_fn": lambda s: (
        50 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HAS_RETIREMENT_PLAN") else
        30 if s.get("SIG_HIGH_INCOME") or s.get("SIG_HAS_RETIREMENT_PLAN") else
        20
    ),

        "fed_savings_fn": lambda s: (
            min(s.get("_retirement", 0) * 0.75, 1_500_000) * (s.get("_fed_marginal_rate", 0) - 0.20) * 0.20
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 30,
        "complexity": 25,
        "audit_friction": 10,

        "plain_english": (
            "If a dentist's 401(k) or ESOP holds employer stock that has "
            "appreciated significantly inside the plan, the Net Unrealized "
            "Appreciation (NUA) rules offer a powerful tax break. Instead "
            "of rolling all plan assets to an IRA (which would make all future "
            "distributions taxable as ordinary income), the dentist takes the "
            "employer stock out in kind as part of a lump-sum distribution. "
            "The cost basis of the stock is taxed as ordinary income immediately "
            "— but the appreciation (NUA) is not taxed until the stock is sold, "
            "and then only at favorable long-term capital gains rates (0%, 15%, "
            "or 20%) — regardless of how long the dentist holds the shares "
            "after distribution. For employer stock that has grown from "
            "$500,000 to $2 million inside the plan, converting $1.5 million "
            "of NUA from 37% ordinary income rates to 20% capital gains rates "
            "saves over $250,000 in taxes. All other plan assets (non-employer "
            "securities) should be rolled to an IRA normally."
        ),

        "documentation": [
            "Form 1099-R with Box 6 showing NUA amount (plan administrator must report)",
            "Employer securities cost basis records from plan (plan must document cost basis)",
            "Lump-sum distribution documentation: entire plan balance distributed in one tax year",
            "Triggering event confirmation: separation from service, age 59½, disability, or death",
            "In-kind distribution of employer securities (not sold inside plan first)",
            "IRA rollover of non-employer-security assets (avoid rolling employer stock to IRA — NUA lost)",
        ],

        "cpa_handoff": [
            "§402(e)(4): NUA on employer securities distributed in lump-sum = excluded from gross income at distribution",
            "NUA taxed as LTCG when sold: regardless of holding period after distribution; 0%/15%/20% rates apply",
            "Cost basis: employer's cost basis in stock = ordinary income at distribution; §72(t) 10% penalty may apply if under 59½",
            "Do NOT roll employer securities to IRA: IRA rollover destroys NUA treatment; all future distributions become ordinary income",
            "Lump-sum requirement: entire plan balance must be distributed in one tax year; triggered by one of four qualifying events",
            "Form 1099-R: Box 6 must show NUA — verify plan administrator reports correctly; cost basis in Box 2a",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },
    {
        "id": "DTTS-101-delaware-incomplete-non-grantor-trust-ding",
        "name": "Delaware Incomplete Non-Grantor Trust (DING)",
        "_id": "69bdb434e5397a28d45441d5",
        "irc": "IRC §2501, §2511, §§671–679, §641, §661, §662, §2036",
        "category": "Trusts & Estate",
        "overlap_group": "Estate Trust Planning",
        "applicable_forms": ["1041"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("SIG_STATE_RETURN_PRESENT", False) and
            s.get("_state_tax", 0) > 30_000  # material state tax burden required
        ),

        "materiality_fn": lambda s: (
            65 if s.get("_state_tax", 0) > 50_000 and s.get("SIG_VERY_HIGH_INCOME", False) else 35
        ),

        "fed_savings_fn": lambda s: (
            500_000 * 0.10 * 0.25
        ),

        "state_savings_fn": lambda s: (
            min(
                min(s.get("_agi", 0) * 0.20, 500_000) * s.get("Q_STATE_MARGINAL_RATE", 0.08),
                500_000 * 0.10 * 0.25  # cap at federal savings level
            )
        ),

        "speed_days": 120,
        "complexity": 70,
        "audit_friction": 30,

        "plain_english": (
            "A Delaware Incomplete Non-Grantor Trust (DING) is an advanced "
            "estate and tax planning structure used by high-income dentists "
            "in high-tax states like California and New York. The dentist "
            "transfers investment assets to a trust sited in Delaware, Nevada, "
            "or another state with no income tax. The transfer is deliberately "
            "structured as an 'incomplete gift' — the dentist retains certain "
            "powers to change beneficiaries — so no gift tax is owed at funding. "
            "The trust is also designed as a non-grantor trust, meaning it files "
            "its own tax return and pays federal income tax itself. Because the "
            "trust is administered in a no-tax state and the grantor is not a "
            "beneficiary, the dentist's home state arguably cannot tax the trust's "
            "income. For a California dentist paying 13.3% state income tax on "
            "$500,000 of investment income, a successful DING saves $66,500 in "
            "state taxes annually. However, California and New York actively "
            "challenge these structures and may assert nexus based on the "
            "grantor's residency — this strategy requires specialized estate "
            "planning counsel and a current-law state nexus analysis."
        ),

        "documentation": [
            "DING trust document (Delaware/Nevada siting; incomplete gift design; non-grantor structure)",
            "Qualified appraisal of assets transferred to trust",
            "Non-grantor trust analysis confirming §§671–677 not triggered",
            "State nexus analysis: confirm grantor's home state (CA/NY) cannot assert income tax on trust",
            "Form 1041 — annual trust income tax return (trust pays federal income tax)",
            "PLR reliance memo if structure deviates from PLR 200246013 / PLR 200612002 validated designs",
        ],

        "cpa_handoff": [
            "§2511 incomplete gift: grantor retains power to change beneficiaries → gift never completed → no gift tax at funding",
            "Non-grantor: trust avoids §§671–677; files Form 1041; trust pays its own federal income tax at compressed trust rates",
            "State savings: trust sited in DE/NV (no state income tax) — home state cannot tax trust income if no nexus",
            "CA/NY risk: CA FTB aggressively challenges DING nexus; CA asserts tax on CA-resident grantor's trust income — get current state analysis",
            "Federal trade-off: trust income taxed at compressed trust rates (37% at $15,200); mitigate by distributing to lower-bracket beneficiaries",
            "PLR guidance: structures validated in PLR 200246013 / 200612002; deviations require independent counsel review",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],

    },

    {
        "id": "DTTS-103-deductible-advisory-planning-fees",
        "name": "Deductible Advisory/Planning Fees",
        "_id": "69bdb435e5397a28d45441dd",
        "irc": "IRC §162, §162(a), §212",
        "category": "General Planning",
        "overlap_group": None,
        "applicable_forms": ["1040", "1120", "1120S", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_HIGH_INCOME", False) and
            (s.get("SIG_NO_TAX_PLANNING_FEES", False) or s.get("SIG_PROFESSIONAL_FEES_PRESENT", False))
        ),

        "materiality_fn": lambda s: (
            55 if s.get("SIG_NO_TAX_PLANNING_FEES", False) and s.get("SIG_HIGH_TAX_LIABILITY", False) else 30
        ),

        "fed_savings_fn": lambda s: (
    s.get("_obi", 0) * 0.03 * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("_obi", 0) * 0.03 * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 7,
        "complexity": 5,
        "audit_friction": 5,

        "plain_english": (
            "Tax planning, CPA, and advisory fees paid in connection with the "
            "dental practice are fully deductible as ordinary and necessary "
            "business expenses under §162. This includes fees for tax return "
            "preparation, tax planning engagements, legal advice on business "
            "structure, and financial advisory services related to the practice. "
            "The critical distinction: fees routed through the business entity "
            "(S-Corp, partnership, or Schedule C) are fully deductible under §162 "
            "with no floor or limitation. In contrast, personal investment advisory "
            "fees (managing a brokerage portfolio) fall under §212 — which was "
            "suspended by the 2017 Tax Cuts and Jobs Act and is not deductible "
            "on individual returns through at least 2025. The planning opportunity "
            "is to ensure that all advisory and planning fees with a business "
            "nexus are invoiced to and paid by the business entity, not "
            "personally. For a dentist paying $30,000/year in advisory fees "
            "and in the 37% bracket, routing fees through the entity saves "
            "approximately $11,100 in federal taxes."
        ),

        "documentation": [
            "Invoices from CPA, tax advisor, financial planner — addressed to the business entity",
            "Engagement letters documenting business-nexus of advisory services",
            "Payment records showing fees paid by the entity (not personal funds)",
            "§162 vs. §212 classification analysis: confirm fees relate to business, not personal investment management",
            "TCJA note: §212 deductions suspended 2018–2025 on individual returns — do not deduct investment advisory fees on Schedule A",
        ],

        "cpa_handoff": [
            "§162: business-related advisory fees (CPA, tax planning, legal, strategy) fully deductible on entity return — no floor",
            "§212 SUSPENDED: investment advisory fees on personal 1040 not deductible 2018–2025 (TCJA §11045)",
            "Routing matters: fee paid by S-Corp = §162 deduction on 1120S; same fee paid personally = §212 = zero deduction",
            "SIG_NO_TAX_PLANNING_FEES: flag dentist paying >$100K tax with no visible professional fees — missed deduction",
            "State conformity: most states conform to §162; some states (e.g., CA) did not fully conform to TCJA — §212 may still be deductible at state level",
            "Related strategies: §127 educational assistance, §132(d) working condition fringe — coordinate with advisory fee deductions to avoid double-claiming",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-104-credit-shelter-trust-bypass-trust",
        "name": "Credit Shelter Trust (Bypass Trust)",
        "_id": "69bdb43ae5397a28d45441e5",
        "irc": "IRC §2010, §2010(c)(2)(B), §2056, §2010(c)(5)(A), §2001, §1014",
        "category": "Trusts & Estate",
        "overlap_group": "Estate Trust Planning",
        "applicable_forms": ["1041", "706"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("SIG_DEPENDENTS_PRESENT", False) and
            s.get("_agi", 0) > 750_000
        ),

        "materiality_fn": lambda s: (
            70 if s.get("_agi", 0) > 1_000_000 and s.get("SIG_DEPENDENTS_PRESENT", False) else 40
        ),

        "fed_savings_fn": lambda s: (
            13_610_000 * 0.40 * 0.30
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 120,
        "complexity": 55,
        "audit_friction": 10,

        "plain_english": (
            "A Credit Shelter Trust (also called a Bypass Trust or Family Trust) "
            "is a foundational estate planning tool for married dentists with "
            "significant wealth. When the first spouse dies, assets equal to the "
            "federal estate tax exemption ($13.61 million in 2024) are placed in "
            "an irrevocable trust for the benefit of children or other heirs. "
            "Because these assets bypass the surviving spouse's estate, they are "
            "not subject to estate tax when the surviving spouse later dies — "
            "effectively using both spouses' exemptions and potentially sheltering "
            "up to $27 million from estate tax. Portability (electing to carry "
            "over the deceased spouse's unused exemption) is simpler but doesn't "
            "protect future appreciation inside the trust from estate tax. "
            "Two critical timing issues: (1) this structure must be in place "
            "in the will or trust before death — it cannot be created retroactively; "
            "and (2) the TCJA estate tax exemption is scheduled to be cut "
            "roughly in half after 2025 — dentists with estates between $7 million "
            "and $27 million have a limited window before that sunset takes effect."
        ),

        "documentation": [
            "Revocable living trust or will with CST/bypass trust provisions at first death",
            "Form 706 — estate tax return filed at first death (also to elect portability if applicable)",
            "Bypass trust funding documentation: assets re-titled to trust after first death",
            "§1014 basis analysis: CST assets do not receive step-up at surviving spouse's death — embedded gains",
            "TCJA sunset planning memo: 2026 exemption reduction impacts estate over ~$7M",
            "Portability comparison: document CST vs. portability analysis and client decision",
        ],

        "cpa_handoff": [
            "§2056: unlimited marital deduction — transfers to spouse avoid estate tax at first death but don't use first spouse's exemption",
            "CST: funds bypass trust at first death up to exemption amount; bypass trust assets NOT in surviving spouse's taxable estate",
            "§2010(c)(5)(A) portability: alternative to CST — surviving spouse elects DSUE on Form 706; simpler but no appreciation sheltering",
            "CST advantage over portability: all appreciation inside CST after first death escapes estate tax; portability DSUE is fixed dollar amount",
            "§1014 trade-off: CST assets don't get step-up at second death (no §1014 basis reset); assets in QTIP/marital trust DO get step-up",
            "TCJA sunset: exemption drops to ~$7M in 2026; couples with $7M–$27M estates should fund bypass provisions before Dec 31, 2025",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],

    },

    {
        "id": "DTTS-107-private-placement-life-insurance-ppli",
        "name": "Private Placement Life Insurance (PPLI)",
        "_id": "69bdb43de5397a28d45441ee",
        "irc": "IRC §7702, §7702A, §817(h), §101(a), §72, §264(a)(1)",
        "category": "Insurance & Risk",
        "overlap_group": "Life Insurance Planning",
        "applicable_forms": ["1040"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("_agi", 0) > 1_000_000
        ),

        "materiality_fn": lambda s: (
            70 if s.get("_agi", 0) > 2_000_000 else 45
        ),

        "fed_savings_fn": lambda s: (
            (300_000 * 0.238 - 30_000) * 0.20
        ),

        "state_savings_fn": lambda s: (
            300_000 * 0.05 * 0.20
        ),

        "speed_days": 180,
        "complexity": 80,
        "audit_friction": 25,

        "plain_english": (
            "Private Placement Life Insurance (PPLI) is a customized life "
            "insurance policy designed for high-net-worth dentists that wraps "
            "an investment portfolio inside a life insurance contract — "
            "converting taxable investment returns into tax-deferred or "
            "tax-free wealth. The dentist funds the policy with $1 million "
            "or more, and the policy's sub-accounts invest in hedge funds, "
            "private equity, or other alternative strategies. All investment "
            "returns grow inside the policy without current income tax. "
            "The death benefit passes to beneficiaries income-tax-free under "
            "§101(a), and the dentist can access policy cash value through "
            "tax-free loans during life. PPLI is distinct from DTTS-099 "
            "(IDF within PPLI) in that DTTS-107 covers the full PPLI wrapper "
            "strategy including premium financing and estate planning "
            "integration through an ILIT. Key risks: (1) over-funding the "
            "policy beyond IRS limits converts it to a Modified Endowment "
            "Contract (MEC), making withdrawals taxable; (2) the investor "
            "control doctrine requires that policy management be independent; "
            "and (3) insurance charges must be justified by tax savings."
        ),

        "documentation": [
            "PPLI policy document with §7702 CVAT/GPT compliance analysis",
            "§7702A MEC test: confirm premium funding does not exceed 7-pay test",
            "§817(h) diversification memo for sub-account investments",
            "Investor control analysis (Rev. Rul. 2003-92) — independent sub-account manager required",
            "ILIT trust document if policy held in irrevocable life insurance trust for estate planning",
            "Premium financing documentation if leveraged structure used; §264 interest deductibility analysis",
        ],

        "cpa_handoff": [
            "§7702: policy must qualify as life insurance under CVAT or GPT; income inside qualifying policy not taxed annually",
            "§7702A MEC: over-funding beyond 7-pay test = MEC; MEC withdrawals/loans = LIFO taxation + 10% penalty under 59½",
            "§817(h): sub-accounts must be diversified; policyholder cannot direct specific investments (investor control doctrine)",
            "§101(a): death benefit income-tax-free; if held in ILIT, also outside estate for estate tax purposes",
            "§264(a)(1): premiums for life insurance on own life NOT deductible; premium financing interest also generally not deductible",
            "Relationship to DTTS-099: DTTS-099 = IDF sub-account investment strategy; DTTS-107 = full PPLI wrapper + estate/premium financing planning",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires policy design, underwriting/actuarial review, and compliance documentation before implementation.",
        ],

    },

    {
        "id": "DTTS-110-domestic-production-activities-deduction",
        "name": "Domestic Production Activities Deduction",
        "_id": "69bdb441e5397a28d45441f6",
        "irc": "IRC §199 [REPEALED 2018]; see §199A (QBI deduction) as current replacement",
        "category": "General Planning",
        "overlap_group": None,
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_MULTI_ENTITY", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("Q_MGMT_CO_REVENUE", 0) > 0  # needs management co income
        ),

        "materiality_fn": lambda s: (
            50 if s.get("SIG_QBI_MISSING", False) and s.get("SIG_HIGH_INCOME", False) else 10
        ),

        "fed_savings_fn": lambda s: (
    max(s.get("_obi", 0), s.get("_wages", 0)) * 0.20 * s.get("_fed_marginal_rate", 0) * 0.30
),

        "state_savings_fn": lambda s: (
    0
),

        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 5,

        "plain_english": (
            "The Domestic Production Activities Deduction (§199 DPAD) was "
            "a deduction of up to 9% of qualified domestic production income — "
            "but it was fully repealed by the Tax Cuts and Jobs Act effective "
            "for tax years beginning after December 31, 2017. Dental practices "
            "cannot use §199 DPAD for current tax years. The replacement "
            "benefit for dental practice owners is the §199A Qualified Business "
            "Income (QBI) deduction — a 20% deduction on pass-through business "
            "income available to eligible dentists. If a dental practice is "
            "showing no QBI deduction on the return despite having business "
            "income, that represents a potentially missed opportunity worth "
            "investigating. Note that dental practices are classified as "
            "Specified Service Trades or Businesses (SSTBs) under §199A, "
            "which limits or eliminates the QBI deduction for high-income "
            "dentists above the income thresholds ($383,900 MFJ in 2024)."
        ),

        "documentation": [
            "NOTE: §199 DPAD repealed 2018 — do not claim on current-year returns",
            "§199A QBI deduction: Form 8995 or Form 8995-A — assess QBI opportunity instead",
            "SSTB analysis: dental services = SSTB; QBI deduction phased out above $383,900 MFJ (2024)",
            "QBI deduction: if below threshold, 20% × lesser of QBI or taxable income (less net capital gain)",
            "W-2 wages: SSTB limited by 50% of W-2 wages paid above threshold — optimize salary level",
        ],

        "cpa_handoff": [
            "§199 DPAD: REPEALED effective tax years beginning after Dec 31, 2017 — zero benefit for 2018+ returns",
            "Redirect to §199A: 20% QBI deduction for pass-through income; limited for SSTBs above income threshold",
            "SSTB threshold 2024: $383,900 MFJ / $191,950 single — fully phased out $100K above threshold",
            "Dental SSTB: 'health' SSTB includes dental services — practice income subject to SSTB limitation",
            "Non-clinical entities: management company income may not be SSTB — separate entities can preserve QBI",
            "SIG_QBI_MISSING: if dentist has OBI >$100K but $0 QBI deduction, investigate SSTB structure and threshold position",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-111-foreign-tax-credit",
        "name": "Foreign Tax Credit",
        "_id": "69bdb445e5397a28d45441fd",
        "irc": "IRC §901, §904, §904(d), §27, §905",
        "category": "Credits & Incentives",
        "overlap_group": None,
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_SCHEDULE_E_PRESENT", False)
        ),

        "materiality_fn": lambda s: (
            35 if s.get("SIG_HIGH_INCOME", False) and s.get("SIG_SCHEDULE_E_PRESENT", False) else 15
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.01
),

        "state_savings_fn": lambda s: (
    0
),

        "speed_days": 7,
        "complexity": 10,
        "audit_friction": 5,

        "plain_english": (
            "If a dentist's investment portfolio includes international funds, "
            "ADRs, or foreign ETFs, the fund company often withholds foreign "
            "income taxes on dividends before they are paid. These foreign "
            "taxes show up in Box 7 of the Form 1099-DIV and can be claimed "
            "as a dollar-for-dollar credit against U.S. income tax — "
            "significantly more valuable than taking them as a deduction. "
            "The Foreign Tax Credit (FTC) under §901 directly reduces "
            "the U.S. tax owed rather than reducing taxable income. "
            "For a dentist in the 37% bracket who paid $5,000 in foreign "
            "withholding taxes, the FTC saves $5,000 versus $1,850 as a "
            "deduction. The credit is limited to the U.S. tax allocable "
            "to foreign-source income under §904 and excess credits carry "
            "forward 10 years. For small amounts ($300 or less for single "
            "filers; $600 or less for married), the credit can be claimed "
            "directly on Form 1040 without filing Form 1116."
        ),

        "documentation": [
            "Form 1099-DIV Box 7 showing foreign taxes paid by fund/ETF",
            "Form 1116 — Foreign Tax Credit calculation (required unless de minimis exception applies)",
            "§904 limitation worksheet: foreign source income / worldwide income ratio",
            "§904(d) basket analysis: passive vs. general category income",
            "Prior year excess FTC carryforward (carry back 1 year; carry forward 10 years)",
        ],

        "cpa_handoff": [
            "§901: FTC = dollar-for-dollar credit for income taxes paid to foreign governments; always prefer over deduction",
            "De minimis exception: ≤$300 single / ≤$600 MFJ — claim credit directly on 1040 without Form 1116",
            "§904 limitation: FTC capped at U.S. tax × (foreign income / worldwide income); cannot shelter U.S.-source income",
            "§904(d) baskets: passive (most dentist investors) vs. general; cannot cross-use excess credits between baskets",
            "Carryover: unused FTC carried back 1 year, forward 10 years — track on Form 1116, Part III",
            "vs. §911: if dentist has foreign earned income AND foreign taxes — cannot use both FTC and §911 FEIE on same income",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-112-rental-loss-offset-for-active-participation",
        "name": "Rental Loss Offset for Active Participation",
        "_id": "69bdb44ae5397a28d4544204",
        "irc": "IRC §469, §469(c), §469(i), §469(i)(2), §469(i)(3), §469(g), §469(c)(7)",
        "category": "Real Estate & Depreciation",
        "overlap_group": None,
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_REAL_ESTATE_ACTIVITY", False) and
            s.get("SIG_SCHEDULE_E_PRESENT", False) and
            s.get("SIG_HAS_DEPRECIATION", False)
        ),

        "materiality_fn": lambda s: (
            50 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_REAL_ESTATE_ACTIVITY") else
            30 if s.get("SIG_HIGH_INCOME") or s.get("SIG_REAL_ESTATE_ACTIVITY") else
            20
        ),

        "fed_savings_fn": lambda s: (
    min(s.get("_depreciation", 0), 25_000) * s.get("_fed_marginal_rate", 0) * 0.10
),

        "state_savings_fn": lambda s: (
    0
),

        "speed_days": 14,
        "complexity": 15,
        "audit_friction": 15,

        "plain_english": (
            "Rental property losses are normally 'passive' under the tax code "
            "and can only offset passive income — not the dentist's practice "
            "income. There is one exception: if the dentist 'actively participates' "
            "in the rental (approving tenants, setting rents, approving repairs — "
            "even through a property manager), up to $25,000 of rental losses "
            "can be deducted against ordinary income each year. However, "
            "this $25,000 special allowance phases out completely once "
            "adjusted gross income exceeds $150,000 — meaning most practicing "
            "dentists above that threshold receive zero current benefit. "
            "The practical value for high-income dentists is different: "
            "unused rental losses are 'suspended' and accumulate each year. "
            "When the property is eventually sold, all accumulated suspended "
            "losses are released in full against any income — creating a "
            "potentially large tax deduction at the time of sale. "
            "Tracking and documenting these suspended losses every year "
            "on Form 8582 is essential to capture the full future benefit."
        ),

        "documentation": [
            "Form 8582 — Passive Activity Loss Limitations (annual filing required to track suspended losses)",
            "Active participation documentation: property management decisions, lease approvals, repair authorizations",
            "§469(i) phase-out calculation: MAGI vs. $100K–$150K thresholds",
            "Suspended passive loss carryforward schedule (from prior Form 8582s)",
            "§469(g) disposition analysis: full release of suspended losses when entire property sold",
            "Depreciation schedules supporting rental loss calculation",
        ],

        "cpa_handoff": [
            "§469(i): $25K special allowance for active participation — phases out $1:$2 above $100K MAGI; fully out at $150K",
            "Most dentists: fully phased out of current deduction; losses suspended annually on Form 8582",
            "Suspended loss value: all suspended passive losses released when entire activity disposed of in taxable transaction (§469(g))",
            "Active vs. material participation: §469(i) only requires active participation (management decisions); not full material participation test",
            "Real estate professional: §469(c)(7) — >750 hours in RE + RE as primary activity; dentist rarely qualifies",
            "Form 8582: must be filed every year rental property exists even if no current deduction — tracks suspended losses",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],

    },

    {
        "id": "DTTS-114-intentionally-delaying-qcd-recognition",
        "name": "Intentionally Delaying QCD Recognition",
        "_id": "69bdb44de5397a28d454420c",
        "irc": "IRC §408(d)(8), §170, §401(a)(9)",
        "category": "Charitable & Foundations",
        "overlap_group": "Charitable Giving",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_RETIREMENT_PLAN", False) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("_retirement", 0) > 100_000
        ),

        "materiality_fn": lambda s: (
        50 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        30 if s.get("SIG_HIGH_INCOME") or s.get("SIG_HIGH_TAX_LIABILITY") else
        20
    ),

        "fed_savings_fn": lambda s: (
            min(105_000, s.get("_retirement", 0) * 0.30) * s.get("_fed_marginal_rate", 0)
        ),

        "state_savings_fn": lambda s: (
            min(105_000, s.get("_retirement", 0) * 0.30) * s.get("Q_STATE_MARGINAL_RATE", 0.05)
        ),

        "speed_days": 7,
        "complexity": 10,
        "audit_friction": 5,

        "plain_english": (
            "A Qualified Charitable Distribution (QCD) allows IRA owners "
            "age 70½ and older to donate up to $105,000 per year directly "
            "from an IRA to a qualified charity — and the distribution is "
            "completely excluded from gross income. This is far more "
            "powerful than taking the IRA distribution as income and then "
            "deducting the charitable contribution. If the dentist takes "
            "$105,000 out of the IRA, that amount is taxable income; a "
            "separate charitable deduction might not offset it fully due "
            "to AGI percentage limits, standard deduction, and SALT cap "
            "interactions. With a QCD, the $105,000 never hits the tax "
            "return as income at all — directly reducing AGI and avoiding "
            "Medicare IRMAA surcharges and other income-based phase-outs. "
            "The 'intentional delay' angle means strategically timing QCDs "
            "to high-income years when the AGI reduction is most valuable — "
            "for example, the year a DSO transition or other large income "
            "event occurs, directing the IRA RMD as a QCD in that year "
            "maximizes the benefit."
        ),

        "documentation": [
            "Taxpayer age confirmation: must be 70½ or older on date of distribution",
            "QCD instruction letter to IRA custodian: direct payment to charity required (not to owner then forwarded)",
            "Charity qualification: qualified public charity under §170(b)(1)(A); NOT to donor-advised fund or private foundation",
            "Acknowledgment letter from charity with date, amount, and no-goods-or-services statement",
            "RMD analysis: confirm QCD amount counts toward current year RMD",
            "Form 1099-R: QCD reported as full distribution; taxpayer must manually exclude on 1040 Line 4b",
        ],

        "cpa_handoff": [
            "§408(d)(8): QCD requires age 70½+; up to $105,000/yr (2024, indexed); directly from IRA to qualified charity",
            "Income exclusion: QCD never included in gross income; no deduction — but AGI reduction is the benefit",
            "RMD satisfaction: QCD counts toward annual RMD (§401(a)(9) RMD begins at age 73 per SECURE 2.0)",
            "Form 1040 reporting: 1099-R shows full distribution; taxpayer writes 'QCD' on Line 4b and excludes amount",
            "Charity restriction: public charity only; NOT to donor-advised funds, supporting orgs, or private foundations",
            "Timing strategy: direct QCDs to high-income years (liquidity events, partial practice sales) for maximum AGI benefit",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-115-dynasty-trust-for-multi-gen-wealth-transfer",
        "name": "Dynasty Trust for Multi-Gen Wealth Transfer",
        "_id": "69bdb44fe5397a28d4544215",
        "irc": "IRC §2501, §2511, §2631, §2642, §2613, §§671–679, §2036, §2041",
        "category": "Trusts & Estate",
        "overlap_group": "Estate Trust Planning",
        "applicable_forms": ["1041", "709"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("SIG_DEPENDENTS_PRESENT", False) and
            s.get("_agi", 0) > 1_000_000
        ),

        "materiality_fn": lambda s: (
            65 if s.get("_agi", 0) > 2_000_000 and s.get("SIG_DEPENDENTS_PRESENT", False) else 35
        ),

        "fed_savings_fn": lambda s: (
            5_000_000 * ((1.07 ** 30) - 1) * 0.40 * 0.35
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 120,
        "complexity": 70,
        "audit_friction": 15,

        "plain_english": (
            "A Dynasty Trust is an irrevocable trust designed to hold family "
            "wealth for multiple generations — potentially indefinitely — "
            "without ever paying estate tax or Generation-Skipping Transfer "
            "tax. The dentist funds the trust using the lifetime gift and GST "
            "exemptions ($13.61 million in 2024, per person), allocates the "
            "GST exemption to the trust, and then all future distributions "
            "to children, grandchildren, and great-grandchildren pass "
            "completely free of both estate tax and GST tax. The trust must "
            "be sited in a state that has abolished the Rule Against Perpetuities "
            "— Delaware, South Dakota, Nevada, and Wyoming are the most popular. "
            "The compounding effect is extraordinary: $5 million invested at "
            "7% grows to $147 million over 50 years, all inside a structure "
            "that skips estate tax at every generation. Assets in the trust "
            "are also protected from the beneficiaries' creditors, divorce, "
            "and lawsuits. The TCJA estate tax exemption is scheduled to drop "
            "significantly after 2025 — creating urgency to fund dynasty "
            "trusts before the exemption reduction."
        ),

        "documentation": [
            "Dynasty trust document (RAP-free state: DE/SD/NV/WY; non-grantor; irrevocable)",
            "Form 709 — gift tax return with GST exemption allocation for trust funding",
            "§2642 GST inclusion ratio computation: zero-out trust with GST exemption allocation",
            "Independent qualified appraisal of assets contributed to trust",
            "§2041 power-of-appointment analysis: beneficiaries cannot hold GPOA (estate inclusion)",
            "TCJA sunset memo: fund trust before 2026 exemption reduction",
        ],

        "cpa_handoff": [
            "§2631: GST exemption $13.61M (2024); allocate to dynasty trust on Form 709 → inclusion ratio = zero → all distributions GST-free",
            "§2642: inclusion ratio = GST exemption allocated / value of trust; zero ratio = no GST tax on any distribution",
            "RAP-free states: DE/SD/NV/WY abolished Rule Against Perpetuities; trust can exist indefinitely",
            "§2041: beneficiaries must NOT hold General Power of Appointment (GPOA) — GPOA inclusion in beneficiary estate",
            "Estate freeze: assets in trust grow without estate tax at any generation; all appreciation escapes transfer taxes",
            "TCJA sunset: $13.61M exemption drops to ~$7M in 2026; fund dynasty trust in 2024–2025 window; no clawback rule protects prior gifts",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],

    },

    {
        "id": "DTTS-116-r-d-tax-credit",
        "name": "R&D Tax Credit",
        "_id": "69bdb450e5397a28d454421e",
        "irc": "IRC §41, §41(b), §41(d), §41(d)(4), §280C(c), §174",
        "category": "Credits & Incentives",
        "overlap_group": "R&D Tax Credit",
        "applicable_forms": ["1040", "1120"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False)
        ),

        "materiality_fn": lambda s: (
            40 if s.get("SIG_HIGH_TAX_LIABILITY", False) and s.get("SIG_BUSINESS_PRESENT", False) else 15
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.02 * 0.14
),

        "state_savings_fn": lambda s: (
    s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.02 * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 60,
        "complexity": 35,
        "audit_friction": 25,

        "plain_english": (
            "The Research and Development Tax Credit (§41) provides a credit "
            "of up to 20% of qualified research expenditures — including wages "
            "paid to employees doing research and development, research supplies, "
            "and contract research costs. For dental practices, qualifying "
            "activities are narrow: developing novel treatment protocols, "
            "custom designing dental devices or digital prosthetics, building "
            "proprietary software for practice management or diagnostics, or "
            "conducting genuine experimental research into new dental techniques. "
            "Standard patient care, adapting existing procedures, and following "
            "established dental protocols do not qualify. Dentists who develop "
            "novel digital workflows (e.g., custom CAD/CAM implant designs, "
            "AI-assisted diagnostic tools, or proprietary practice management "
            "software) may have significant qualifying R&D wages and supplies. "
            "An important change: starting in 2022, R&D expenses must be "
            "capitalized and amortized over 5 years rather than expensed "
            "immediately — this interacts with the credit calculation under §280C. "
            "Many states also offer their own R&D credits that can be stacked."
        ),

        "documentation": [
            "Form 6765 — Credit for Increasing Research Activities",
            "4-part qualified research test documentation: purpose, uncertainty, experimentation, technological nature",
            "Employee time allocation records: hours spent on qualified vs. non-qualified activities",
            "Qualified wages calculation: W-2 wages of employees spending time on R&D activities",
            "Project-level research contemporaneous documentation (lab notebooks, design documents, testing records)",
            "§280C election analysis: reduced credit option vs. reduced §174 deduction",
        ],

        "cpa_handoff": [
            "§41: R&D credit = 20% of regular method or 14% ASC (Alternative Simplified Credit) of qualified research expenses above base",
            "4-part test (§41(d)): (1) permitted purpose, (2) technical uncertainty, (3) process of experimentation, (4) technological — all 4 required",
            "Dental exclusions: routine patient care, adapting existing procedures, surveys, social science — NOT qualified",
            "Dental inclusions: novel device/appliance R&D, custom software dev, clinical protocol innovation with genuine uncertainty",
            "§174 amortization (2022+): R&D expenses must be amortized 5yr domestic / 15yr foreign; affects QRE timing",
            "§280C: if full §41 credit claimed, must reduce §174 deduction by credit amount; or elect reduced credit (× (1 - tax rate))",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-118-backdoor-roth-ira",
        "name": "Backdoor Roth IRA",
        "_id": "69bdb451e5397a28d4544234",
        "irc": "IRC §408A, §408A(c)(3)(B), §408(o), §408A(d)(3), §408(d)(2)",
        "category": "Retirement Plans",
        "overlap_group": "Retirement Plan",
        "overlap_group": "Roth Conversion Strategy",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HIGH_INCOME", False) and
            s.get("_agi", 0) > 240_000  # above direct Roth IRA income limit (2024 MFJ)
        ),

        "materiality_fn": lambda s: (
            45 if s.get("_agi", 0) > 240_000 and s.get("SIG_W2_PRESENT", False) else 25
        ),

        "fed_savings_fn": lambda s: (
    min(8_000, s.get("_wages", 0) * 0.02) * 0.238
),

        "state_savings_fn": lambda s: (
    0
),

        "speed_days": 7,
        "complexity": 10,
        "audit_friction": 5,

        "plain_english": (
            "High-income dentists are barred from contributing directly to a "
            "Roth IRA — the income limit phases out completely at $240,000 "
            "for married filers in 2024. The backdoor Roth IRA is a legal "
            "workaround: the dentist first makes a nondeductible contribution "
            "of $7,000 ($8,000 if age 50 or older) to a traditional IRA — "
            "there is no income limit for this step. Then, the dentist "
            "converts the traditional IRA to a Roth IRA. Because the "
            "contribution was after-tax (nondeductible), there is no additional "
            "tax on the conversion, and the money is now in a Roth account "
            "growing tax-free forever. The critical trap is the pro-rata rule: "
            "if the dentist has other pre-tax IRA funds (like a rollover IRA "
            "from a prior 401(k)), the IRS aggregates all IRA balances when "
            "calculating the taxable portion of the conversion — making much "
            "of the conversion taxable. The fix is to first roll pre-tax IRA "
            "funds back into the current employer's 401(k) plan, then execute "
            "the backdoor conversion with a clean slate."
        ),

        "documentation": [
            "Form 8606 — Nondeductible IRAs (file every year nondeductible contribution made; tracks IRA basis)",
            "Form 1099-R — IRA conversion distribution; Form 5498 — IRA conversion receipt",
            "Pro-rata analysis: aggregate all pre-tax IRA balances on Dec 31 of conversion year",
            "Rollback strategy: if pre-tax IRA exists, document rollover back to employer 401(k) before conversion",
            "Timing: contribute and convert in same tax year to minimize earnings at conversion",
        ],

        "cpa_handoff": [
            "§408(o): nondeductible traditional IRA contribution — no income limit; $7,000 ($8,000 if 50+) in 2024; tracks basis on Form 8606",
            "§408A(d)(3): conversion of pre-tax IRA to Roth = taxable; conversion of after-tax (basis) = tax-free",
            "§408(d)(2) pro-rata rule: IRS aggregates ALL traditional/SEP/SIMPLE IRA balances on Dec 31; taxable ratio = pre-tax / total",
            "Pro-rata fix: roll pre-tax IRA balance into current employer 401(k) (if plan accepts) before Dec 31 of conversion year",
            "Step transaction doctrine: backdoor Roth is well-established and IRS has not challenged it; do promptly after contribution",
            "Form 8606: must be filed every year with nondeductible contribution; and again in year of conversion — tracks basis permanently",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],

    },

    {
        "id": "DTTS-119-employer-401-k-match",
        "name": "Employer 401(k) Match",
        "_id": "69bdb453e5397a28d454424a",
        "irc": "IRC §401(a), §401(k), §401(m), §415(c), §404(a)(3), §416, §411",
        "category": "Retirement Plans",
        "overlap_group": "Retirement Plan",
        "applicable_forms": ["1120S", "1120"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_W2_PRESENT", False) and
            s.get("SIG_HIGH_INCOME", False) and
            (s.get("SIG_HAS_RETIREMENT_PLAN", False) or s.get("SIG_NO_RETIREMENT_PLAN", False))
        ),

        "materiality_fn": lambda s: (
            60 if s.get("SIG_NO_RETIREMENT_PLAN", False) and s.get("SIG_HIGH_INCOME", False) else
            40 if s.get("SIG_HAS_RETIREMENT_PLAN", False) and s.get("SIG_W2_PRESENT", False) else 20
        ),

        "fed_savings_fn": lambda s: (
    s.get("_wages", 0) * 0.03 * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("_wages", 0) * 0.03 * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 30,
        "complexity": 20,
        "audit_friction": 5,

        "plain_english": (
            "For dental practice owners, setting up or optimizing the employer "
            "401(k) match is one of the most direct ways to maximize retirement "
            "contributions and reduce current taxes. Without a match or safe harbor "
            "election, the IRS requires annual non-discrimination testing (the ADP "
            "test) — if the non-owner employees don't contribute enough to the plan, "
            "the dentist's own contributions are limited and excess amounts must be "
            "refunded. By adopting a Safe Harbor 401(k) — committing to match "
            "100% on the first 3% plus 50% on the next 2% of employee compensation, "
            "or a flat 3% employer contribution for all eligible employees — "
            "the practice permanently eliminates ADP/ACP testing. The owner can "
            "then maximize contributions up to the $69,000 annual IRS limit for "
            "2024 ($76,500 if age 50 or older) regardless of how much staff "
            "contributes. The employer match cost itself is a fully deductible "
            "business expense, and the owner's contributions grow tax-deferred "
            "inside the plan."
        ),

        "documentation": [
            "Plan document with safe harbor election and match formula",
            "Annual safe harbor notice to employees (required before plan year begins)",
            "ADP/ACP test results (if not safe harbor) — confirm owner contribution limits",
            "Payroll records confirming match calculations and timely deposit",
            "§415 annual additions limit worksheet: employee + employer ≤ $69,000 (2024)",
            "§416 top-heavy test: if key employees >60% of plan value, minimum 3% employer contribution required for non-key employees",
        ],

        "cpa_handoff": [
            "§401(m): employer matching contributions subject to ACP test unless safe harbor plan adopted",
            "Safe harbor: 100% match on first 3% + 50% on next 2% (enhanced) OR 3% non-elective for all eligible employees — eliminates ADP/ACP testing",
            "§415(c): total annual additions (employee + employer) capped at $69,000 (2024); catch-up additional $7,500 if age 50+",
            "§404(a)(3): employer match deductible up to 25% of total plan participant compensation paid during year",
            "§416 top-heavy: if key employees own >60% of plan benefits, minimum 3% employer contribution required for non-key staff",
            "Safe harbor deadline: must be adopted by Oct 1 of plan year (new plan); existing plan amendment by Nov 30 to take effect next year",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],

    },

    {
        "id": "DTTS-120-captive-insurance-831-b",
        "name": "Captive Insurance (831(b))",
        "_id": "69bdb454e5397a28d4544260",
        "irc": "IRC §831(b), §162, §953(d), §7701(o)",
        "category": "Insurance & Risk",
        "overlap_group": "Captive Insurance (IRC §831(b))",
        "applicable_forms": ["1120"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("_total_tax", 0) > 100_000
        ),

        "materiality_fn": lambda s: (
            70 if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("_total_tax", 0) > 150_000 else 40
        ),

        "fed_savings_fn": lambda s: (
            500_000 * s.get("_fed_marginal_rate", 0) * 0.20
        ),

        "state_savings_fn": lambda s: (500_000 * 0.05 * s.get("Q_STATE_MARGINAL_RATE", 0.20)),

        "speed_days": 180,
        "complexity": 75,
        "audit_friction": 45,

        "plain_english": (
            "A captive insurance company is an insurance company that the dentist "
            "owns, which insures the dental practice against genuine business risks. "
            "Under IRC §831(b), small insurance companies with premiums up to "
            "$2.8 million per year pay no income tax on premium revenue — only on "
            "investment income. The dental practice deducts the premiums as a "
            "business expense, and the premiums accumulate inside the captive "
            "as a growing asset owned by the dentist. This strategy requires "
            "the captive to insure real risks that the practice genuinely faces — "
            "such as regulatory defense costs, cyber liability, business "
            "interruption, or other coverage gaps — with premiums set by an "
            "independent actuary at arm's-length rates. The IRS has aggressively "
            "audited captive arrangements since 2014 and has designated many as "
            "Listed Transactions requiring Form 8886 disclosure. Improperly "
            "structured captives — those with implausible risks, inflated "
            "premiums, or no real risk distribution — have been repeatedly "
            "invalidated in Tax Court. A properly structured captive with "
            "genuine risk, actuarial pricing, and risk distribution remains "
            "legally viable but requires expert insurance and tax counsel."
        ),

        "documentation": [
            "Captive domicile license and formation documents (state or offshore)",
            "§831(b) election filed with captive's first tax return (Form 1120-PC)",
            "Independent actuarial study: arm's-length premium determination for each risk covered",
            "Risk distribution analysis: confirm genuine risk shifting from operating company to captive",
            "Form 8886 — Reportable Transaction Disclosure Statement (if arrangement meets IRS Notice 2016-66 / 2023-10 criteria)",
            "Claims history and policy documentation for each risk covered",
            "IRS Notice 2016-66 / 2023-10 compliance memo: confirm arrangement does not trigger listed transaction reporting",
        ],

        "cpa_handoff": [
            "§831(b): captive with ≤$2.8M net written premiums (2024) elects to pay tax only on investment income — premium income tax-free to captive",
            "§162: operating company deducts premiums as ordinary business expense — requires genuine risk shifting + risk distribution",
            "Risk distribution: IRS requires distribution among multiple insured risks or multiple insureds; single-dentist single-risk = sham",
            "IRS Notice 2016-66 / 2023-10: micro-captive arrangements 'of interest' — Form 8886 required; do not proceed without compliance analysis",
            "Tax Court: Avrahami (2017), Syzygy (2019), Reserve Mechanical (2018) — all invalidated; lessons: actuarial premiums, real risk, genuine distribution",
            "Recommendation: only proceed with independent (non-promoter) insurance counsel; reject any arrangement promising guaranteed deduction without real risk",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires policy design, underwriting/actuarial review, and compliance documentation before implementation.",
        ],

    },

    {
        "id": "DTTS-121-fringe-benefits-commuter-transportation",
        "name": "Fringe Benefits: Commuter/Transportation",
        "_id": "69bdb457e5397a28d4544275",
        "irc": "IRC §132(f), §132(f)(1), §125, §274(a)(4)",
        "category": "Compensation & Benefits",
        "overlap_group": "Employee Benefits",
        "applicable_forms": ["1120", "1120S"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_W2_PRESENT", False) and
            s.get("SIG_HIGH_INCOME", False)
        ),

        "materiality_fn": lambda s: (
            30 if s.get("SIG_W2_PRESENT", False) and s.get("SIG_HIGH_INCOME", False) else 15
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_EDUCATIONAL_ASSISTANCE_DEDUCTION", 0) * 0.12 * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("Q_EDUCATIONAL_ASSISTANCE_DEDUCTION", 0) * 0.12 * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 14,
        "complexity": 5,
        "audit_friction": 2,

        "plain_english": (
            "Dental practices can provide employees (including the dentist-owner "
            "if on W-2) with up to $315 per month in tax-free transit or vanpool "
            "benefits and up to $315 per month in tax-free qualified parking — "
            "for a total of $7,560 per year that is completely excluded from "
            "the employee's gross income and exempt from FICA payroll taxes. "
            "These amounts are adjusted for inflation annually. The benefit "
            "can be funded either by the employer directly or through a "
            "pre-tax payroll reduction via a §125 cafeteria plan (where the "
            "employee redirects salary to pay for the commuter benefit pre-tax). "
            "A notable TCJA change: the employer no longer gets a tax deduction "
            "for providing these benefits (§274 eliminated the deduction for "
            "2018 onward) — but the employee income exclusion and FICA savings "
            "remain fully intact. For a dental practice with multiple employees "
            "commuting to the office or using employer-provided parking, "
            "formalizing a commuter benefit program creates measurable "
            "FICA savings for the practice and income exclusions for employees "
            "at minimal cost."
        ),

        "documentation": [
            "§132(f) commuter benefit plan document or §125 cafeteria plan amendment",
            "Monthly benefit records: transit passes, parking receipts, or transit card statements",
            "Payroll records confirming exclusion from employee W-2 Box 1 wages",
            "§125 plan election forms (if employee pre-tax salary reduction method used)",
            "Note: employer DEDUCTION eliminated by TCJA §274(a)(4) — benefit cost not deductible; FICA savings still apply",
        ],

        "cpa_handoff": [
            "§132(f): $315/month transit + $315/month qualified parking = $7,560/yr excluded from employee gross income + FICA (2024 limits, indexed)",
            "§274(a)(4) TCJA: employer CANNOT deduct qualified transportation fringe expenses paid after 2017; but employee exclusion intact",
            "FICA savings: employer saves 7.65% × benefit amount in FICA; employee saves 7.65% as well via pre-tax reduction",
            "§125 salary reduction: employee can redirect pre-tax salary to fund commuter benefits — reduces W-2 wages and FICA base",
            "Bicycle commuting: §132(f)(1)(D) suspended by TCJA 2018–2025; do not include bicycle benefits in plan during this period",
            "Payroll reporting: employer excludes qualified transportation fringe from Box 1 (federal wages) and Boxes 3/5 (FICA wages) on W-2",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-122-home-equity-loan-interest-deduction-biz",
        "name": "Home Equity Loan Interest Deduction (Biz)",
        "_id": "69bdb459e5397a28d454427c",
        "irc": "IRC §163(h), §163(h)(3)(C), §163(a), Temp. Reg. §1.163-8T",
        "category": "General Planning",
        "overlap_group": None,
        "applicable_forms": ["1040", "1120S", "1120"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False)
        ),

        "materiality_fn": lambda s: (
            35 if s.get("SIG_BUSINESS_PRESENT", False) and s.get("SIG_HIGH_TAX_LIABILITY", False) else 15
        ),

        "fed_savings_fn": lambda s: (
    s.get("_obi", 0) * 0.05 * 0.07 * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    0
),

        "speed_days": 7,
        "complexity": 10,
        "audit_friction": 10,

        "plain_english": (
            "The Tax Cuts and Jobs Act (2017) eliminated the deduction for home "
            "equity loan interest when the loan is used for purposes other than "
            "buying or improving the home. However, there is a powerful planning "
            "opportunity using the IRS interest tracing rules: if a dentist "
            "takes a home equity loan and uses the proceeds to fund the dental "
            "practice or purchase business equipment, the interest on that loan "
            "is classified as business interest — fully deductible as an ordinary "
            "business expense under §162, not limited by the mortgage interest "
            "rules. The key is meticulous documentation: the dentist must trace "
            "the loan proceeds directly to business use (bank transfers showing "
            "funds going from home equity loan to business account) and maintain "
            "those records. The interest deduction follows the use of the money, "
            "not the collateral. A dentist borrowing $200,000 at 7% and using "
            "it for practice equipment saves approximately $5,180 per year in "
            "federal taxes at the 37% rate — on top of any equipment depreciation "
            "deductions available."
        ),

        "documentation": [
            "Home equity loan agreement and balance statement",
            "Bank records tracing loan proceeds to business account (Temp. Reg. §1.163-8T)",
            "Business use documentation: invoice/receipt for equipment or practice expenditure funded",
            "Interest allocation worksheet: confirm proceeds allocated 100% to business vs. personal use",
            "§163(h)(3)(C) TCJA memo: confirm interest NOT deductible as home mortgage interest; instead traced to business use under §163(a)",
        ],

        "cpa_handoff": [
            "§163(h)(3)(C) TCJA: home equity interest deductible as mortgage interest ONLY if proceeds used to buy/build/improve home (2018–2025)",
            "Temp. Reg. §1.163-8T tracing: interest follows use of proceeds — proceeds to business = §162 business interest; to investment = §163(d) investment interest",
            "Documentation: trace funds from HELOC disbursement to business bank account to business expenditure — no gap in chain",
            "Segregation: if proceeds split between business and personal use, allocate interest proportionally",
            "§163(j): business interest subject to 30% ATI limitation (§163(j)) for practices >$29M gross receipts; small biz exemption applies to most dental practices",
            "Practical note: use separate HELOC tranche entirely for business → cleaner tracing; avoid commingling with personal use proceeds",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-123-american-opportunity-credit",
        "name": "American Opportunity Credit",
        "_id": "69bdb45ae5397a28d4544283",
        "irc": "IRC §25A, §25A(b), §25A(d), §25A(f), §25A(g)(2)",
        "category": "Credits & Incentives",
        "overlap_group": "Education Credits",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_DEPENDENTS_PRESENT", False) and
            s.get("_agi", 0) < _LIM["llc_phaseout_mfj"]  # phased out above $180K MFJ
        ),

        "materiality_fn": lambda s: (
            45 if s.get("SIG_DEPENDENTS_PRESENT", False) and s.get("_agi", 0) < 160_000 else
            20 if s.get("_agi", 0) < _LIM["llc_phaseout_mfj"] else 5
        ),

        "fed_savings_fn": lambda s: (
            max(2_500 * max(0, 1 - max(0, (s.get("_agi", 0) - (_LIM["llc_phaseout_mfj"] - 20_000)) / 20_000)), 0)
            if s.get("_agi", 0) < _LIM["llc_phaseout_mfj"] else 0
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 7,
        "complexity": 5,
        "audit_friction": 5,

        "plain_english": (
            "The American Opportunity Tax Credit (AOTC) provides up to $2,500 "
            "per eligible student per year as a dollar-for-dollar credit against "
            "federal income tax for qualified college education expenses — tuition, "
            "fees, and required course materials. The credit covers the first four "
            "years of higher education only and requires the student to be enrolled "
            "at least half-time in a degree program. Unlike a deduction, a credit "
            "directly reduces the tax owed; up to $1,000 of the AOTC is even "
            "refundable, meaning it can produce a refund even if no tax is owed. "
            "However, the AOTC phases out completely once adjusted gross income "
            "exceeds $180,000 for married couples filing jointly — which means "
            "most actively practicing dentists receive no benefit. The planning "
            "opportunity applies in two scenarios: (1) associate dentists or "
            "new graduates with income below the threshold, and (2) dependents "
            "who file their own returns and can claim the credit independently "
            "if they are not claimed as dependents."
        ),

        "documentation": [
            "Form 8863 — Education Credits",
            "Form 1098-T from eligible educational institution (EIN of school, tuition billed/paid)",
            "Student enrollment verification: at least half-time, degree or credential program, years 1–4",
            "Qualified expense receipts: tuition, fees, required books and supplies",
            "§25A(g)(2) anti-double-benefit: confirm same expenses not used for §529 exclusion or §127 educational assistance deduction",
            "No felony drug conviction: confirm student eligibility",
        ],

        "cpa_handoff": [
            "§25A(b): AOTC = 100% of first $2,000 + 25% of next $2,000 = $2,500 max; 40% refundable ($1,000 max refund)",
            "Phase-out: $160K–$180K MFJ (2024); fully phased out at $180K — most dental practice owners ineligible",
            "First 4 years only: student in years 5+ uses §25A(c) Lifetime Learning Credit instead",
            "No double benefit: cannot use same expenses for §529 qualified distribution AND AOTC (§25A(g)(2))",
            "Dependent strategy: if dependent has income, may be better to NOT claim as dependent — dependent claims AOTC on own return at lower AGI",
            "vs. LLC: AOTC $2,500 max; LLC $2,000 max — both same income phase-out; AOTC preferred if in years 1–4",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-124-s-corp-health-reimbursement-arrangement-qsehra",
        "name": "S-Corp Health Reimbursement Arrangement (QSEHRA)",
        "_id": "69bdb45be5397a28d454428a",
        "irc": "IRC §105, §105(b), §105(h), §106, §9831(d)",
        "category": "Entity & Structuring",
        "overlap_group": "Health Insurance Deduction",
        "applicable_forms": ["1120S"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_S_CORP_VERIFIED", False) and
            s.get("SIG_W2_PRESENT", False) and
            s.get("SIG_HIGH_INCOME", False) and
            s.get("Q_HEALTH_PREMIUM", 0) > 0 and  # §9831(d): needs premium to reimburse
            s.get("SIG_HEALTH_INS_EXPENSE", False)
        ),

        "materiality_fn": lambda s: (
            50 if s.get("SIG_HEALTH_INS_EXPENSE", False) and s.get("SIG_HAS_S_CORP_VERIFIED", False) else 25
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_HEALTH_PREMIUM", 0) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("Q_HEALTH_PREMIUM", 0) * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 14,
        "complexity": 15,
        "audit_friction": 5,

        "plain_english": (
            "A Qualified Small Employer Health Reimbursement Arrangement (QSEHRA) "
            "allows S-Corp dental practices with fewer than 50 employees — and "
            "no existing group health plan — to reimburse employees for "
            "individual health insurance premiums and qualified medical expenses "
            "tax-free. In 2024, the limits are $6,150 per year for self-only "
            "coverage and $12,450 for family coverage. For non-owner employees, "
            "reimbursements are fully excluded from income and FICA taxes. "
            "The situation for the dentist-owner is different: as a greater-than "
            "2% S-Corp shareholder, reimbursements must be included in W-2 wages, "
            "but the dentist can then deduct health insurance premiums on the "
            "front page of the personal tax return under §162(l). The practical "
            "planning value is structuring these reimbursements correctly so the "
            "deduction is captured at the right level and FICA treatment is "
            "handled properly. For dental practices without a group plan, "
            "the ICHRA (Individual Coverage HRA) is often a more flexible "
            "alternative with no employer size limit."
        ),

        "documentation": [
            "QSEHRA plan document with annual limits and eligible expense definitions",
            "Annual written notice to employees before plan year: amount of QSEHRA benefit",
            "ACA PTC coordination notice: employees must report QSEHRA amount to marketplace to adjust premium tax credit",
            "Reimbursement request records: individual health insurance premium invoices or qualified medical receipts",
            "W-2 reporting for >2% S-Corp shareholders: QSEHRA benefit included in Box 1; §162(l) deduction on 1040",
            "Employee count verification: employer must have <50 full-time equivalent employees",
        ],

        "cpa_handoff": [
            "§9831(d) QSEHRA: employer <50 employees, no group health plan; reimburses individual insurance + medical up to $12,450 family (2024)",
            ">2% S-Corp shareholder exception: §106 does not apply; reimbursement included in W-2 wages; owner deducts as §162(l) self-employed health insurance",
            "Employee benefit: reimbursement excluded from income and FICA for non-owner employees (§105(b))",
            "ACA PTC interaction: if employee gets premium tax credit, QSEHRA benefit reduces PTC dollar-for-dollar; must notify employees",
            "No group plan: QSEHRA prohibited if employer provides any group health plan; cannot run both simultaneously",
            "vs. ICHRA: IRS Notice 2019-45; no employer size limit; can be offered alongside group health plan for certain classes; more flexible than QSEHRA for growing practices",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-126-corporate-aircraft-deduction",
        "name": "Corporate Aircraft Deduction",
        "_id": "69bdb45ce5397a28d4544291",
        "irc": "IRC §162, §274, §274(a), §274(e)(2), §280F, §168(k)",
        "category": "General Planning",
        "overlap_group": None,
        "applicable_forms": ["1120", "1120S"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("SIG_TRAVEL_PRESENT", False) and
            s.get("_agi", 0) > 750_000
        ),

        "materiality_fn": lambda s: (
            55 if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("SIG_TRAVEL_PRESENT", False) else 25
        ),

        "fed_savings_fn": lambda s: (
            (480_000 + 120_000) * s.get("_fed_marginal_rate", 0) * 0.15
        ),

        "state_savings_fn": lambda s: (
            (480_000 + 120_000) * 0.05 * 0.15
        ),

        "speed_days": 60,
        "complexity": 40,
        "audit_friction": 30,

        "plain_english": (
            "Dentists who own or are considering owning an aircraft for "
            "business travel can deduct a significant portion of the costs "
            "against dental practice income. The aircraft purchase itself "
            "can be eligible for bonus depreciation (60% in 2024) — "
            "meaning a $1 million aircraft used 80% for business could "
            "generate $480,000 in first-year depreciation deductions. "
            "Annual operating costs — fuel, maintenance, hangar, crew, "
            "insurance — are deductible in proportion to business use. "
            "The key compliance requirement is maintaining detailed flight logs "
            "documenting every flight's business purpose, passengers, and "
            "destination. When the aircraft is used for personal travel, "
            "the owner must recognize imputed income calculated using the "
            "IRS's Standard Industry Fare Level (SIFL) formula — which is "
            "typically far less than the actual aircraft cost — and this "
            "is added to the owner's W-2. Entertainment use (flying clients "
            "to sporting events) has been non-deductible since 2018. "
            "This strategy only makes sense for practices with genuine "
            "multi-location or regional travel needs and AGI well above "
            "$750,000."
        ),

        "documentation": [
            "Flight logs: date, pilot, passengers, departure/destination, business purpose for every flight",
            "Business vs. personal use percentage calculation (annually)",
            "§280F listed property: business use must exceed 50% for unrestricted depreciation",
            "SIFL imputed income calculation for personal flights (Reg. §1.61-21(g)): add to employee W-2",
            "Form 4562 — depreciation; §168(k) bonus depreciation election",
            "§274(e)(2) documentation for entertainment-adjacent flights: confirm treated as W-2 compensation",
        ],

        "cpa_handoff": [
            "§162: business-use aircraft operating costs (fuel, maintenance, hangar) fully deductible; personal-use portion NOT deductible",
            "§280F listed property: aircraft must be >50% business use; if ≤50%, mandatory ADS depreciation (slower schedule)",
            "§168(k) bonus: 60% first-year bonus depreciation in 2024 on business-use share; 40% in 2025; 20% in 2026",
            "SIFL method (Reg. §1.61-21(g)): IRS-prescribed formula for imputing income on personal flights; far below actual cost; add to W-2",
            "§274(a) entertainment: flights to sporting events, concerts, vacations = NOT deductible (TCJA eliminated entertainment deduction)",
            "§274(e)(2) exception: entertainment flight treated as employee compensation (W-2) allows employer deduction",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-128-reclassify-income-to-capital-gains",
        "name": "Reclassify Income to Capital Gains",
        "_id": "69bdb45de5397a28d4544298",
        "irc": "IRC §1221, §1231, §1(h), §1239, §1245, §1250",
        "category": "Exit & Sale",
        "overlap_group": "Practice Sale Exit",
        "applicable_forms": ["1040", "1120S"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("SIG_BUSINESS_PRESENT", False)
        ),

        "materiality_fn": lambda s: (
            55 if s.get("SIG_HIGH_TAX_LIABILITY", False) and s.get("SIG_HAS_DEPRECIATION", False) else 30
        ),

        "fed_savings_fn": lambda s: (
    s.get("_distributions", 0) * 0.20 * 0.17
),

        "state_savings_fn": lambda s: (
    s.get("_distributions", 0) * 0.20 * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 30,
        "complexity": 25,
        "audit_friction": 15,

        "plain_english": (
            "Reclassifying ordinary income as capital gains is one of the "
            "highest-leverage tax planning moves available to a dental practice "
            "owner, because the rate differential can be enormous: ordinary "
            "income is taxed up to 37% while long-term capital gains are taxed "
            "at a maximum 20% federal rate. The most common opportunity arises "
            "at practice sale: the way the purchase price is allocated among "
            "assets determines how much is ordinary income (equipment depreciation "
            "recapture, covenants not to compete) versus capital gains (goodwill, "
            "practice going concern value). Strategic allocation of more value "
            "to goodwill and less to ordinary income assets can save hundreds "
            "of thousands of dollars on a large practice sale. During ongoing "
            "operations, §1231 assets (dental equipment held more than one year) "
            "generate capital gain character when sold. The §1239 trap must be "
            "avoided: selling depreciable property to a related party (spouse, "
            "80%-owned entity) converts all gain back to ordinary income."
        ),

        "documentation": [
            "Form 8949 — Sales and Other Dispositions of Capital Assets",
            "Schedule D — Capital Gains and Losses",
            "Asset allocation agreement (§1060 / Form 8594): both buyer and seller must report consistent allocation",
            "Holding period documentation: asset acquisition dates to confirm >1 year for §1231 gain treatment",
            "§1245 recapture analysis: depreciation taken on sold equipment = ordinary income regardless of capital gain treatment",
            "§1239 related-party analysis: confirm buyer and seller are not related (>80% ownership) for depreciable assets",
        ],

        "cpa_handoff": [
            "§1221: goodwill and going concern value = capital assets; taxed at 20% LTCG + 3.8% NIIT vs. 37% ordinary",
            "§1231: depreciable business property held >1 year = §1231 gain (LTCG character); §1245 recapture = ordinary income on prior depreciation",
            "§1060 / Form 8594: buyer and seller must use consistent asset allocation; IRS compares buyer's and seller's Forms 8594",
            "Goodwill vs. covenant: goodwill = capital gain; covenant not to compete = ordinary income to seller AND ordinary deduction to buyer",
            "§1239: related-party sale of depreciable property → ALL gain ordinary (not just recapture); check for >80% ownership",
            "Practice sale strategy: allocate maximum to goodwill / going concern; minimize covenant amount and equipment allocation",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-129-private-annuity-sale-to-children",
        "name": "Private Annuity Sale to Children",
        "_id": "69bdb45ee5397a28d45442a0",
        "irc": "IRC §7872, §453, §1274, §72, §2501, §2512(b); IRS Notice 2006-96",
        "category": "Exit & Sale",
        "overlap_group": "Practice Sale Exit",
        "applicable_forms": ["1040"],
        "phase_1_eligible": False,

        "eligibility_logic": lambda s: (
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("SIG_DEPENDENTS_PRESENT", False) and
            s.get("_agi", 0) > 750_000
        ),

        "materiality_fn": lambda s: (
            35 if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("SIG_DEPENDENTS_PRESENT", False) else 15
        ),

        "fed_savings_fn": lambda s: (
            500_000 * 0.30 * 0.40 * 0.25  # probability weight 25%
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 90,
        "complexity": 50,
        "audit_friction": 25,

        "plain_english": (
            "A private annuity sale to children was once a popular way for "
            "practice owners to transfer assets to the next generation and defer "
            "capital gains — the parent sold the practice or other assets to "
            "the children in exchange for annuity payments over the parent's "
            "lifetime, spreading the tax over many years. However, the IRS "
            "eliminated the gain deferral benefit in 2006 (Notice 2006-96): "
            "all gain is now recognized in the year of sale, making private "
            "annuities largely obsolete for capital gain deferral. The remaining "
            "estate planning value is narrow: because annuity payments stop at "
            "the parent's death, the transferred asset's future appreciation "
            "is removed from the parent's estate. But this must be weighed "
            "against the immediate income tax hit in the year of transfer. "
            "For most high-income dentists, an installment sale to an "
            "Intentionally Defective Grantor Trust (DTTS-077) or an "
            "intra-family loan (DTTS-076) will achieve superior results "
            "with better tax treatment."
        ),

        "documentation": [
            "Private annuity agreement: IRS actuarial tables (§7520 rate) used to determine fair annuity payment amount",
            "Gift tax analysis: if annuity undervalued vs. FMV of transferred asset → taxable gift (§2501/§2512(b))",
            "Immediate gain recognition notice (Notice 2006-96): all gain in year of transfer; no installment election available",
            "§72 exclusion ratio for each annuity payment: return of basis / gain / ordinary income components",
            "Comparison memo: private annuity vs. installment sale to IDGT (DTTS-077) — document why private annuity selected if applicable",
        ],

        "cpa_handoff": [
            "Notice 2006-96: private annuity = all gain recognized in year of sale (after Oct 18, 2006); no installment deferral available",
            "§7872/§1274: annuity payments must use §7520 rate (IRS actuarial tables); insufficient payments = gift tax on difference",
            "§72: each annuity payment allocates among: excludable basis, capital gain, and ordinary income per exclusion ratio",
            "Estate planning value: post-transfer appreciation and annuity payments remaining in hands of children at parent death",
            "§453 recharacterization: if annuity has fixed term with balloon, IRS may recharacterize as installment sale — different rules apply",
            "Better alternatives: DTTS-077 (installment sale to IDGT) defers gain entirely; DTTS-076 (intra-family loan at AFR) avoids gift tax risk",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires related-party role, compensation, and documentation review before implementation.",
        ],

    },

    {
        "id": "DTTS-131-management-company-set-up-as-a-c-corporation",
        "name": "Management Company Set up as a C-corporation",
        "_id": "69bdb45fe5397a28d45442ad",
        "irc": "IRC §482, Treas. Reg. §301.7701-3, IRC §11, §162, §351",
        "category": "Entity & Structuring",
        "overlap_group": "Management Company",
        "applicable_forms": ["1120"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_S_CORP_VERIFIED", False) and
            s.get("SIG_VERY_HIGH_INCOME", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False)
        ),

        "materiality_fn": lambda s: (
            60 if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("SIG_HAS_S_CORP_VERIFIED", False) else 35
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_MGMT_CO_REVENUE", 0) * max(0, s.get("_fed_marginal_rate", 0) - 0.21)
),

        "state_savings_fn": lambda s: (
    s.get("Q_MGMT_CO_REVENUE", 0) * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 60,
        "complexity": 45,
        "audit_friction": 20,

        "plain_english": (
            "A C-corporation management company allows a dental practice to "
            "split income between the operating practice (usually an S-Corp) "
            "and a separately owned C-Corporation that provides genuine "
            "management, administrative, and support services. The dental "
            "practice pays arm's-length management fees to the C-Corp — "
            "these fees are deductible to the practice, reducing the income "
            "that flows through to the dentist at 37%. The C-Corp retains "
            "those management fees at the flat 21% corporate tax rate, "
            "a significant rate differential. The retained earnings inside "
            "the C-Corp can then be used to fund executive life insurance, "
            "non-qualified deferred compensation plans, or other corporate "
            "benefits. The critical risk is double taxation: money retained "
            "in the C-Corp and eventually distributed as dividends is taxed "
            "again at 20% — so the long-term exit strategy must be planned "
            "carefully. The management fees must also be genuinely arm's-length "
            "and supportable under §482, not inflated amounts designed purely "
            "to shift income."
        ),

        "documentation": [
            "Management services agreement: specific services described, arm's-length fee benchmarked to market rates",
            "§482 arm's-length pricing analysis: comparable uncontrolled transactions supporting fee amount",
            "Form 8832 — Entity Classification Election if electing C-Corp treatment for existing LLC",
            "Form 1120 — C-Corp tax return (21% flat rate on retained management fee income)",
            "Fringe benefit plan documents: §106 health coverage, §132 benefits, deferred comp if applicable",
            "Exit strategy analysis: §301 dividend (20% LTCG), §302 redemption, or §338 stock sale — model tax cost before establishing C-Corp",
        ],

        "cpa_handoff": [
            "§482: management fees between S-Corp and C-Corp must be arm's-length; IRS can reallocate if inflated; document with comparable market data",
            "§11: C-Corp pays flat 21% on retained earnings; vs. dentist's 37% personal rate — rate differential is the benefit",
            "Double taxation: C-Corp earnings → 21% corp tax; dividend to dentist → 20% LTCG tax; effective rate ~36.8% combined; plan exit carefully",
            "Fringe benefits: C-Corp employee (dentist) can receive §106 health insurance, §132 benefits, fully deductible to C-Corp — not available in S-Corp",
            "State law: dental professional corporation laws may limit who can own C-Corp management company; check state dental board regulations",
            "§1374 built-in gains: if converting existing S-Corp to C-Corp, §1374 5-year built-in gains tax applies on pre-conversion appreciation",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-133-cafeteria-plan",
        "name": "Cafeteria Plan",
        "_id": "69bdb460e5397a28d45442be",
        "irc": "IRC §125, §125(d), §125(f), §125(i), §106, §79, §21(b)(2)",
        "category": "Compensation & Benefits",
        "overlap_group": "Employee Benefits",
        "applicable_forms": ["1120", "1120S"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_W2_PRESENT", False) and
            s.get("SIG_HIGH_INCOME", False)
        ),

        "materiality_fn": lambda s: (
            45 if s.get("SIG_HEALTH_INS_EXPENSE", False) and s.get("SIG_W2_PRESENT", False) else
            30 if s.get("SIG_DEPENDENTS_PRESENT", False) and s.get("SIG_W2_PRESENT", False) else 20
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_EDUCATIONAL_ASSISTANCE_DEDUCTION", 0) * 1.80 * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    s.get("Q_EDUCATIONAL_ASSISTANCE_DEDUCTION", 0) * 1.80 * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 5,

        "plain_english": (
            "A §125 Cafeteria Plan is one of the most cost-effective employee "
            "benefits a dental practice can offer. It allows employees to "
            "redirect a portion of their salary — before taxes — to pay for "
            "health insurance premiums, Flexible Spending Accounts (FSAs) "
            "for medical expenses (up to $3,300 in 2024), and Dependent Care "
            "FSAs for childcare (up to $5,000 in 2024). These amounts are "
            "excluded from federal income tax and FICA payroll taxes, saving "
            "both the employee and the employer money. The employer saves "
            "7.65% in FICA taxes on every dollar redirected pre-tax, which "
            "on a staff of five can amount to thousands of dollars annually. "
            "The plan must be documented in writing, and annual elections must "
            "be made before the plan year begins. One important restriction: "
            "S-Corp shareholders owning more than 2% of the company cannot "
            "participate in the cafeteria plan — the dentist-owner must address "
            "health insurance through a different mechanism, specifically the "
            "§162(l) self-employed health insurance deduction."
        ),

        "documentation": [
            "§125 cafeteria plan document: written plan required with description of benefits and election procedures",
            "Annual benefit elections: signed employee elections before each plan year (irrevocable mid-year except qualifying life events)",
            "FSA health: $3,300 limit (2024); $640 rollover permitted; use-it-or-lose-it on excess",
            "Dependent care FSA: $5,000/yr ($2,500 MFS); coordinate with §21 dependent care credit",
            "Nondiscrimination testing: eligibility, concentration, and benefits tests — annual requirement",
            "Payroll records: confirm pre-tax elections excluded from W-2 Boxes 1, 3, and 5",
            "NOTE: >2% S-Corp shareholders EXCLUDED from §125 participation per §125(b)(1)(B)",
        ],

        "cpa_handoff": [
            "§125: pre-tax elections reduce employee W-2 gross income AND FICA wages — saves income tax + payroll tax for employee; FICA for employer",
            "Health FSA: §125(i) — $3,300/yr (2024 indexed); $640 rollover; employer may contribute additionally",
            "Dep care FSA: $5,000/yr; reduces §21 dependent care credit dollar-for-dollar — coordinate: credit usually worth less than FSA for high-income taxpayers",
            "§125(b)(1)(B) S-Corp owner exclusion: >2% shareholder cannot participate in §125 cafeteria plan; use §162(l) for health insurance instead",
            "Nondiscrimination: §125 plan must pass eligibility test, concentration test (key employees <25% of benefits), and benefits test annually",
            "State tax: most states conform to §125 federal exclusion; CA does conform for §125 health/FSA; check state for dep care FSA",
        ],

        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],

    },

    {
        "id": "DTTS-134-home-office",
        "name": "Home Office / Administrative Office Deduction",
        "_id": "69c26f34cdaa7f875cd42243",
        "irc": "IRC §280A(c)",
        "category": "Deduction & Reimbursement",
        "applicable_forms": ["1040", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            not s.get("SIG_W2_ONLY", False) and
            not s.get("SIG_HAS_S_CORP_VERIFIED", False) and  # §280A(c): S-Corp owners cannot deduct home office personally
            (s.get("SIG_SCHEDULE_C_PRESENT", False) or s.get("SIG_HAS_PARTNERSHIP", False)
             or (s.get("SIG_SELF_EMPLOYED", False) and s.get("SIG_BUSINESS_PRESENT", False)))
        ),

        "materiality_fn": lambda s: (
        70 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        55 if s.get("SIG_HIGH_INCOME") else
        40
    ),
        "fed_savings_fn": lambda s: (
    s.get("Q_HEALTH_PREMIUM", 5_000) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    5000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 15,

        "plain_english": (
            "A home administrative office used exclusively for management and "
            "administrative work may qualify as a deductible business expense."
        ),

        "documentation": [
            "Square footage measurements",
            "Business use documentation",
            "Home office expense records"
        ],

        "cpa_handoff": [
            "Confirm principal place of business test",
            "Prepare Form 8829 if applicable"
        ],

        "prerequisites": [],
    },

    {
        "id": "DTTS-135-business-travel",
        "name": "Business Travel Expenses",
        "_id": "69c26f35cdaa7f875cd42246",
        "irc": "IRC §162(a)(2)",
        "category": "Deduction & Reimbursement",
        "applicable_forms": ["1040", "1120", "1120S", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and s.get("SIG_TRAVEL_PRESENT", False)
        ),

        "materiality_fn": lambda s: (
        70 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        55 if s.get("SIG_HIGH_INCOME") else
        40
    ),
        "fed_savings_fn": lambda s: (
    s.get("Q_HEALTH_PREMIUM", 8_000) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    8000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 7,
        "complexity": 10,
        "audit_friction": 20,

        "plain_english": (
            "Travel expenses are deductible when the primary purpose of the trip "
            "is business, such as attending conferences, training, or meetings."
        ),

        "documentation": [
            "Conference registration",
            "Travel receipts",
            "Business meeting agenda"
        ],

        "cpa_handoff": [
            "Verify business purpose of travel",
            "Confirm qualifying business days"
        ],

        "prerequisites": [
            "Documented business purpose for travel"
        ],
    },
    {
        "id": "DTTS-139-c-corp-fringe-benefits",
        "name": "Fringe Benefits (For C-corporations)",
        "_id": "69c26f35cdaa7f875cd42249",
        "irc": "IRC §132, §105, §106",
        "category": "Deduction & Reimbursement",
        "applicable_forms": ["1120"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: s.get("SIG_HAS_C_CORP", False),

        "materiality_fn": lambda s: (
        80 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        65 if s.get("SIG_HIGH_INCOME") else
        50
    ),
        "fed_savings_fn": lambda s: (
    s.get("Q_HEALTH_PREMIUM", 20_000) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    20000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 30,
        "complexity": 25,
        "audit_friction": 10,

        "plain_english": (
            "C-corporations can provide owner-employees with tax-deductible fringe benefits "
            "such as health insurance or medical reimbursement plans that are not taxable "
            "to the owner."
        ),

        "documentation": [
            "Corporate benefit plan documents",
            "Health insurance payment records",
            "Board approval of benefits"
        ],

        "cpa_handoff": [
            "Confirm benefit qualifies under IRC §132 or §105",
            "Ensure proper payroll reporting"
        ],

        "prerequisites": ["Operating C-Corporation"],
    },

    {
        "id": "DTTS-140-accountable-plan",
        "name": "Accountable Plan (Reimbursement Plan)",
        "_id": "69bdb461e5397a28d45442d2",
        "irc": "IRC §62(a)(2)(A), Reg §1.62-2",
        "category": "Deduction & Reimbursement",
        "applicable_forms": ["1120", "1120S", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            (
                s.get("SIG_HAS_S_CORP_VERIFIED", False) or  # S-Corp owners always have reimbursable expenses
                s.get("SIG_HAS_S_CORP", False) or
                s.get("SIG_RENT_EXPENSE_PRESENT", False) or
                s.get("SIG_AUTO_TRUCK_PRESENT", False) or
                s.get("SIG_TRAVEL_PRESENT", False) or
                s.get("SIG_PROFESSIONAL_FEES_PRESENT", False)
            )
        ),

        "materiality_fn": lambda s: (
            65 if s.get("SIG_AUTO_TRUCK_PRESENT", False) or s.get("SIG_TRAVEL_PRESENT", False) else 50
        ),

        "fed_savings_fn": lambda s: (
    s.get("Q_HEALTH_DEDUCTION_AVAILABLE", 15_000) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    15000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 5,

        "plain_english": (
            "An accountable plan allows your practice to reimburse you tax-free for "
            "legitimate business expenses you paid personally, such as mileage, "
            "continuing education, and supplies."
        ),

        "documentation": [
            "Written accountable plan document",
            "Expense reports with receipts",
            "Business purpose documentation"
        ],

        "cpa_handoff": [
            "Draft accountable plan document",
            "Train staff on expense reporting"
        ],

        "prerequisites": ["Operating business entity"],
    },

    {
        "id": "DTTS-142-schedule-c-to-scorp",
        "name": "Schedule C → S-Corp Conversion (SE Tax Protection)",
        "_id": "69c26f36cdaa7f875cd42257",
        "irc": "IRC §1361-1362, §1402",
        "category": "Entity & Income Structuring",
        "overlap_group": "Entity Conversion",
        "applicable_forms": ["1040", "1120S"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_SCHEDULE_C_PRESENT", False) and s.get("_obi", 0) > 80000
        ),

        "materiality_fn": lambda s: (
        100 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        85 if s.get("SIG_HIGH_INCOME") else
        70
    ),
        "fed_savings_fn": lambda s: (
    max(0, s.get("_obi", 0) * 0.60) * 0.153
),

        "state_savings_fn": lambda s: 0,

        "speed_days": 60,
        "complexity": 30,
        "audit_friction": 10,

        "plain_english": (
            "Operating as a Schedule C exposes all business profit to self-employment tax. "
            "Converting to an S-Corporation allows part of the profit to be taken as "
            "distributions instead of wages, reducing payroll tax exposure."
        ),

        "documentation": [
            "Articles of incorporation",
            "S-Corp election (Form 2553)",
            "Payroll setup",
            "Reasonable compensation documentation"
        ],

        "cpa_handoff": [
            "File Form 2553 before election deadline",
            "Establish payroll system",
            "Determine reasonable compensation"
        ],

        "prerequisites": [
            "Business income typically above $80K",
            "State licensing board approval may be required"
        ],
    },

    {
        "id": "DTTS-143-s-corp-to-c-corp-profit-protection",
        "name": "S-Corporation to C-Corp (Profit Protection Strategy)",
        "_id": "69c26f36cdaa7f875cd4225a",
        "irc": "IRC §11, §301",
        "category": "Entity & Income Structuring",
        "overlap_group": "Entity Conversion",
        "applicable_forms": ["1120S", "1120"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            (
                s.get("SIG_BUSINESS_PRESENT", False) and
                not s.get("SIG_HAS_S_CORP_VERIFIED", False)  # §280A(c): same S-Corp exclusion as home office
            )
        ),

        "materiality_fn": lambda s: (
        75 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        60 if s.get("SIG_HIGH_INCOME") else
        45
    ),
        "fed_savings_fn": lambda s: (
    s.get("Q_MGMT_CO_REVENUE", 40_000) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    10000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 90,
        "complexity": 40,
        "audit_friction": 15,

        "plain_english": (
            "In some cases, converting an S-corporation to a C-corporation can allow "
            "profits to be retained at the corporate tax rate rather than flowing "
            "through to the owner's individual tax return."
        ),

        "documentation": [
            "Corporate election documentation",
            "Board approval of structure change",
            "Corporate tax projections"
        ],

        "cpa_handoff": [
            "Analyze double taxation implications",
            "Prepare corporate tax projections"
        ],

        "prerequisites": ["Significant retained earnings expected"],
    },

    {
        "id": "DTTS-144-profit-sharing-plan",
        "name": "Profit-Sharing Retirement Plan",
        "_id": "69c26f37cdaa7f875cd4225d",
        "irc": "IRC §401(a)",
        "category": "Retirement & Benefits",
        "overlap_group": "Retirement Plan",
        "applicable_forms": ["1120S", "1120"],
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and  # Business owner
            s.get("SIG_NO_RETIREMENT_PLAN", False) and
            not s.get("SIG_W2_ONLY", False)          # Not a pure W-2 employee
        ),

        "materiality_fn": lambda s: (
        90 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        75 if s.get("SIG_HIGH_INCOME") else
        60
    ),
        "fed_savings_fn": lambda s: (
    min(
        min(_LIM["defined_contribution_limit"], s.get("Q_CASH_BALANCE_INCREMENTAL", min(_LIM["defined_contribution_limit"], max(s.get("_obi", 0), s.get("_wages", 0)) * 0.25 if s.get("_obi", 0) > 0 else 20_000))),
        s.get("_max_retirement_at_current_w2", 69_000)
    ) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    min(66000, max(s.get("_obi", 0), s.get("_wages", 0)) * 0.25) *
    (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 30,
        "complexity": 20,
        "audit_friction": 5,

        "plain_english": (
            "A profit-sharing retirement plan allows businesses to contribute "
            "a portion of profits to retirement accounts while receiving "
            "tax deductions for the contributions."
        ),

        "documentation": [
            "Plan adoption agreement",
            "Contribution calculations",
            "Employee eligibility records"
        ],

        "cpa_handoff": [
            "Establish retirement plan",
            "Calculate annual deductible contribution"
        ],

        "prerequisites": [],
    },

    {
        "id": "DTTS-145-cash-balance",
        "name": "Cash Balance Plan — IRC §401(a)",
        "_id": "69c26f37cdaa7f875cd42260",
        "irc": "IRC §401(a), §412",
        "category": "Retirement & Benefits",
        "overlap_group": "Retirement Plan",
        "applicable_forms": ["1120S", "1120"],
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",

        "eligibility_logic": lambda s: (
            s.get("SIG_HIGH_INCOME", False) and s.get("SIG_NO_RETIREMENT_PLAN", False)
        ),

        "materiality_fn": lambda s: 95 if s.get("_agi", 0) > 600000 else 80,

        "fed_savings_fn": lambda s: (
    min(
        s.get("Q_CASH_BALANCE_INCREMENTAL", min(300_000, max(s.get("_obi", 0), s.get("_wages", 0)) * 0.25 if s.get("_obi", 0) > 0 else s.get("_agi", 0) * 0.05)),
        s.get("_max_retirement_at_current_w2", 69_000)  # capped by actual W-2 wages
    ) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    min(300000, s.get("_agi", 0) * 0.25) *
    (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 90,
        "complexity": 40,
        "audit_friction": 10,

        "plain_english": (
            "A Cash Balance Plan allows high-income dentists to contribute large "
            "tax-deductible retirement contributions each year, often exceeding "
            "$100,000 annually depending on age and income."
        ),

        "documentation": [
            "Actuarial certification",
            "Plan document",
            "Annual Form 5500",
            "Contribution calculation"
        ],

        "cpa_handoff": [
            "Engage actuary for contribution calculation",
            "Establish plan before year-end"
        ],

        "prerequisites": [
            "Consistent business income",
            "Actuarial firm engaged"
        ],
    },

    {
        "id": "DTTS-146-self-directed-retirement-plan",
        "name": "Self-Directed Traditional Retirement Plan",
        "_id": "69c26f38cdaa7f875cd42263",
        "irc": "IRC §408",
        "category": "Retirement & Benefits",
        "overlap_group": "Retirement Plan",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: s.get("SIG_HIGH_INCOME", False),

        "materiality_fn": lambda s: (
        65 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        50 if s.get("SIG_HIGH_INCOME") else
        35
    ),
        "fed_savings_fn": lambda s: (
    min(7_000, s.get("Q_CASH_BALANCE_INCREMENTAL", 7_000), s.get("_max_retirement_at_current_w2", 69_000)) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    7500 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 14,
        "complexity": 15,
        "audit_friction": 5,

        "plain_english": (
            "Self-directed IRAs allow investments in real estate, private equity, "
            "and other alternative assets while maintaining normal IRA tax advantages."
        ),

        "documentation": [
            "Self-directed IRA custodian agreement",
            "Investment documentation"
        ],

        "cpa_handoff": [
            "Confirm prohibited transaction compliance"
        ],

        "prerequisites": ["Self-directed IRA custodian"],
    },

    {
        "id": "DTTS-147-412e3-plan",
        "name": "412(e)(3) Plans",
        "_id": "69c26f38cdaa7f875cd42266",
        "irc": "IRC §412(e)(3)",
        "category": "Retirement & Benefits",
        "overlap_group": "Retirement Plan",
        "applicable_forms": ["1120S", "1120"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_HIGH_INCOME", False) and s.get("SIG_NO_RETIREMENT_PLAN", False)
        ),

        "materiality_fn": lambda s: (
        100 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        85 if s.get("SIG_HIGH_INCOME") else
        70
    ),
        "fed_savings_fn": lambda s: (
    min(
        min(200_000, s.get("Q_CASH_BALANCE_INCREMENTAL", min(200_000, max(s.get("_obi", 0), s.get("_wages", 0)) * 0.20 if s.get("_obi", 0) > 0 else s.get("_agi", 0) * 0.04))),
        s.get("_max_retirement_at_current_w2", 69_000)  # capped by actual W-2
    ) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    min(200000, s.get("_agi", 0) * 0.20) *
    (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 90,
        "complexity": 40,
        "audit_friction": 10,

        "plain_english": (
            "A 412(e)(3) plan is a fully insured defined benefit plan allowing "
            "large tax-deductible contributions funded through insurance or annuity contracts."
        ),

        "documentation": [
            "Plan document",
            "Insurance policy contracts",
            "Actuarial calculations"
        ],

        "cpa_handoff": [
            "Engage pension actuary",
            "Establish insurance funding structure"
        ],

        "prerequisites": ["High consistent income"],
    },

    {
        "id": "DTTS-149-sep-ira",
        "name": "SEP IRA",
        "_id": "69c26f39cdaa7f875cd42269",
        "irc": "IRC §408(k)",
        "category": "Retirement & Benefits",
        "overlap_group": "Retirement Plan",
        "applicable_forms": ["1040", "1120S", "1120"],
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            not s.get("SIG_W2_ONLY", False) and
            (s.get("SIG_SELF_EMPLOYED", False) or s.get("SIG_HAS_S_CORP_VERIFIED", False)
             or s.get("SIG_HAS_PARTNERSHIP", False) or s.get("SIG_SCHEDULE_C_PRESENT", False))
        ),

        "materiality_fn": lambda s: (
        85 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        70 if s.get("SIG_HIGH_INCOME") else
        55
    ),
        "fed_savings_fn": lambda s: (
            # SEP: 25% of net compensation, capped at §415(c) limit ($69K for 2024).
            # Use _max_sep_contribution if set by SignalEngine consistency layer (preferred).
            # Fallback: 25% of the larger of OBI or W-2 wages, capped.
            min(
                s.get("_max_sep_contribution",
                      min(_LIM["defined_contribution_limit"],
                          max(s.get("_obi_positive", 0), s.get("_wages", 0)) * 0.25)),
                _LIM["defined_contribution_limit"]
            ) * s.get("_fed_marginal_rate", 0.37)
        ),

        "state_savings_fn": lambda s: (
            min(
                s.get("_max_sep_contribution",
                      min(_LIM["defined_contribution_limit"],
                          max(s.get("_obi_positive", 0), s.get("_wages", 0)) * 0.25)),
                _LIM["defined_contribution_limit"]
            ) * (s.get("_state_tax", 0) / s.get("_agi", 1) if s.get("_agi", 0) else 0)
        ),

        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 5,

        "plain_english": (
            "A SEP-IRA allows business owners to contribute up to 25% of compensation "
            "toward retirement with minimal administrative complexity."
        ),

        "documentation": [
            "SEP-IRA adoption agreement",
            "Contribution calculations",
            "IRA custodian statements"
        ],

        "cpa_handoff": [
            "Confirm contribution limits",
            "Record deduction on business return"
        ],

        "prerequisites": ["Self-employment or business income"],
    },

    {
        "id": "DTTS-150-solo-401k",
        "name": "Solo 401(k)",
        "_id": "69bdb463e5397a28d45442e2",
        "irc": "IRC §402(g), §415",
        "category": "Retirement & Benefits",
        "overlap_group": "Retirement Plan",
        "applicable_forms": ["1040", "1120S"],
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_NO_RETIREMENT_PLAN", False) and
            not s.get("SIG_W2_ONLY", False) and
            (s.get("SIG_SELF_EMPLOYED", False) or s.get("SIG_HAS_S_CORP_VERIFIED", False)
             or s.get("SIG_HAS_PARTNERSHIP", False) or s.get("SIG_SCHEDULE_C_PRESENT", False))
        ),

        "materiality_fn": lambda s: (
        95 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        80 if s.get("SIG_HIGH_INCOME") else
        65
    ),
        "fed_savings_fn": lambda s: (
            # Solo 401k: employee deferral ($23K) + employer 25% of net comp, total ≤ $69K.
            # Use _max_solo401k_total from SignalEngine if available.
            min(
                s.get("_max_solo401k_total",
                      min(_LIM["defined_contribution_limit"],
                          _LIM["elective_deferral_limit"] +
                          max(s.get("_obi_positive", 0), s.get("_wages", 0)) * 0.25)),
                _LIM["defined_contribution_limit"]
            ) * s.get("_fed_marginal_rate", 0.37)
        ),

        "state_savings_fn": lambda s: (
            min(
                s.get("_max_solo401k_total",
                      min(_LIM["defined_contribution_limit"],
                          _LIM["elective_deferral_limit"] +
                          max(s.get("_obi_positive", 0), s.get("_wages", 0)) * 0.25)),
                _LIM["defined_contribution_limit"]
            ) * (s.get("_state_tax", 0) / s.get("_agi", 1) if s.get("_agi", 0) else 0)
        ),

        "speed_days": 21,
        "complexity": 15,
        "audit_friction": 5,

        "plain_english": (
            "A Solo 401(k) allows self-employed professionals with no full-time "
            "employees to make both employee and employer contributions."
        ),

        "documentation": [
            "Plan adoption agreement",
            "Contribution calculations",
            "Form 5500-EZ if plan exceeds $250K"
        ],

        "cpa_handoff": [
            "Establish plan before year-end",
            "Calculate maximum deductible contribution"
        ],

        "prerequisites": ["No full-time non-owner employees"],
    },
    {
        "id": "DTTS-151-simple-ira",
        "name": "SIMPLE IRA",
        "_id": "69bdb464e5397a28d45442f4",
        "irc": "IRC §408(p)",
        "category": "Retirement & Benefits",
        "overlap_group": "Retirement Plan",
        "applicable_forms": ["1120S", "1120"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            (
                s.get("SIG_NO_RETIREMENT_PLAN", False) or
                s.get("SIG_RETIREMENT_UNDERFUNDED", False)
            ) and
            s.get("SIG_W2_PRESENT", False)  # must have employees for SIMPLE
        ),

        "materiality_fn": lambda s: (
        70 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        55 if s.get("SIG_HIGH_INCOME") else
        40
    ),
        "fed_savings_fn": lambda s: (
    min(
        min(16_000, s.get("Q_CASH_BALANCE_INCREMENTAL", min(16_000, s.get("_wages", 0) * 0.50 if s.get("_wages", 0) > 0 else 5_000))),
        s.get("_max_retirement_at_current_w2", 69_000)
    ) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    15500 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 21,
        "complexity": 10,
        "audit_friction": 5,

        "plain_english": (
            "A SIMPLE IRA is a retirement plan designed for small businesses. "
            "It allows employees to defer salary while the employer provides a "
            "matching contribution."
        ),

        "documentation": [
            "SIMPLE IRA adoption agreement",
            "Employee contribution records"
        ],

        "cpa_handoff": [
            "Ensure plan established before October 1",
            "Confirm employer match contributions"
        ],

        "prerequisites": ["Small business with ≤100 employees"],
    },

    {
        "id": "DTTS-153-1031-exchange",
        "name": "§1031 Exchange",
        "_id": "69c26f3bcdaa7f875cd4227d",
        "irc": "IRC §1031",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Real Estate — 1031 Exchange",
        "applicable_forms": ["1040", "1120", "1120S", "1065"],
        "phase_1_eligible": True,

        # §1031 requires an ACTUAL disposition (sale) of real property plus a
        # replacement purchase. It cannot apply without a realized capital gain or
        # confirmed sale event.  A mere ownership of real estate is not sufficient.
        "eligibility_logic": lambda s: (
            s.get("SIG_REAL_ESTATE_ASSET", False) and
            s.get("SIG_CAPITAL_GAIN_REALIZED", False) and   # must have realized gain
            (
                s.get("SIG_REAL_ESTATE_DEPRECIATION", False) or  # confirmed property w/ depr
                s.get("Q_HAS_RENTAL_PROPERTIES", False) or
                s.get("Q_OWNS_BUILDING", False)
            )
        ),

        "materiality_fn": lambda s: (
            100 if s.get("SIG_VERY_HIGH_INCOME") and s.get("_capital_gains", 0) > 200_000
            else 85 if s.get("_capital_gains", 0) > 100_000
            else 70
        ),
        "fed_savings_fn": lambda s: (
            # Estimate deferral benefit: capital gains tax deferred on property sale
            max(0, s.get("_capital_gains", 0)) * 0.20  # ~20% LTCG rate on deferred gain
        ),

        "state_savings_fn": lambda s: (
            max(0, s.get("_capital_gains", 0)) * 0.20 *
            (s.get("_state_tax", 0) / s.get("_agi", 1) if s.get("_agi", 0) else 0)
        ),

        "speed_days": 120,
        "complexity": 35,
        "audit_friction": 10,

        "plain_english": (
            "A §1031 exchange allows taxpayers to defer capital gains tax when selling "
            "investment real estate and reinvesting in another qualifying property."
        ),

        "documentation": [
            "Qualified intermediary agreement",
            "Property sale and purchase contracts",
            "Exchange timeline documentation"
        ],

        "cpa_handoff": [
            "Engage qualified intermediary",
            "Track 45-day identification and 180-day closing deadlines"
        ],

        "prerequisites": ["Sale of investment or business real estate with realized capital gain"],
    },

    {
        "id": "DTTS-154-real-estate-professional-status",
        "name": "Real Estate Professional Status (IRC §469)",
        "_id": "69bdb465e5397a28d454430e",
        "irc": "IRC §469",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Real Estate — Professional Status",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        # REPE requires: actual rental losses suspended under passive rules (Form 8582)
        # that would be released as ordinary deductions upon REPE qualification.
        # Without documented rental losses, REPE has zero benefit.
        "eligibility_logic": lambda s: (
            s.get("SIG_REAL_ESTATE_ACTIVITY", False) and
            s.get("SIG_SCHEDULE_E_PRESENT", False) and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("SIG_REAL_ESTATE_DEPRECIATION", False) and   # confirmed Sch E depreciation
            (
                s.get("SIG_RENTAL_NET_LOSS", False) or          # confirmed net rental loss
                s.get("Q_HAS_RENTAL_PROPERTIES", False)         # or questionnaire-confirmed
            )
        ),

        "materiality_fn": lambda s: (
            100 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_RENTAL_NET_LOSS") else
            85  if s.get("SIG_HIGH_INCOME") and s.get("SIG_RENTAL_NET_LOSS") else
            60  if s.get("Q_HAS_RENTAL_PROPERTIES") else
            40
        ),
        "fed_savings_fn": lambda s: (
            # Savings = suspended rental losses (or estimated) × marginal rate.
            # Use actual _rental_net_loss if available; otherwise cap to Schedule E depreciation.
            max(
                s.get("_rental_net_loss", 0),               # actual net loss
                s.get("_schedule_e_depreciation", 0),       # or depr as proxy
            ) * s.get("_fed_marginal_rate", 0.37)
            if (s.get("_rental_net_loss", 0) > 0 or s.get("_schedule_e_depreciation", 0) > 0)
            else 0.0
        ),

        "state_savings_fn": lambda s: (
            max(
                s.get("_rental_net_loss", 0),
                s.get("_schedule_e_depreciation", 0),
            ) * (s.get("_state_tax", 0) / s.get("_agi", 1) if s.get("_agi", 0) else 0)
        ),

        "speed_days": 90,
        "complexity": 40,
        "audit_friction": 25,

        "plain_english": (
            "Real Estate Professional Status allows qualifying taxpayers to use "
            "rental losses to offset active income such as professional earnings."
        ),

        "documentation": [
            "Time logs for real estate activity (750+ hour threshold)",
            "Property management documentation",
            "Material participation records",
            "Form 8582 passive activity loss worksheets"
        ],

        "cpa_handoff": [
            "Verify 750-hour test and >50% services in real property trades",
            "Prepare Form 8582 adjustments for released passive losses"
        ],

        "prerequisites": ["Active rental properties with net losses suspended under §469"],
    },

    {
        "id": "DTTS-155-short-term-rentals",
        "name": "Short-Term Rentals (Active Participation Strategy)",
        "_id": "69c26f3ccdaa7f875cd4228c",
        "irc": "Treas. Reg. §1.469-1T(e)(3)(ii)(A)",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Real Estate — Short-Term Rental",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_REAL_ESTATE_ACTIVITY", False) and
            (s.get("SIG_REAL_ESTATE_DEPRECIATION", False) or
             s.get("Q_HAS_RENTAL_PROPERTIES", False) or
             s.get("Q_OWNS_BUILDING", False))
        ),

        "materiality_fn": lambda s: (
        100 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        90 if s.get("SIG_HIGH_INCOME") else
        75
    ),
        "fed_savings_fn": lambda s: (
    s.get("Q_COST_SEG_INCREMENTAL_DEDUCTION", 120_000) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    120000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 90,
        "complexity": 35,
        "audit_friction": 20,

        "plain_english": (
            "Short-term rentals with average stays under seven days may qualify "
            "as active businesses rather than passive rentals, allowing losses "
            "to offset other income."
        ),

        "documentation": [
            "Rental booking records",
            "Average stay calculations",
            "Material participation logs"
        ],

        "cpa_handoff": [
            "Confirm average rental period",
            "Verify material participation"
        ],

        "prerequisites": ["Short-term rental property ownership"],
    },

    {
        "id": "DTTS-156-rd-tax-credit",
        "name": "Research & Development Tax Credit",
        "_id": "69c26f3ccdaa7f875cd4228f",
        "irc": "IRC §41",
        "category": "Credits & Special Incentives",
        "overlap_group": "R&D Tax Credit",
        "applicable_forms": ["1040", "1120"],
        "phase_1_eligible": False,  # Requires confirmed R&D activities
        "estimate_confidence": "LOW",

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_DENTIST_CONFIRMED", False) and
            s.get("Q_MGMT_CO_REVENUE", 0) > 0  # Proxy for confirmed qualified activities
        ),

        "materiality_fn": lambda s: (
        85 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        70 if s.get("SIG_HIGH_INCOME") else
        55
    ),
        "fed_savings_fn": lambda s: (
    s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.05 * 0.14
),

        "state_savings_fn": lambda s: (
    s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.05 * s.get("Q_STATE_MARGINAL_RATE", 0.05)
),

        "speed_days": 60,
        "complexity": 30,
        "audit_friction": 20,

        "plain_english": (
            "Businesses that develop new processes, technologies, or products may "
            "qualify for the federal research and development tax credit."
        ),

        "documentation": [
            "Project documentation",
            "Employee time tracking",
            "Qualified research expense calculations"
        ],

        "cpa_handoff": [
            "Prepare Form 6765",
            "Document qualified research expenses"
        ],

        "prerequisites": ["Qualified research activity"],
    },
    {
        "id": "DTTS-157-se-health-insurance",
        "name": "Self-Employed Health Insurance Premium Deduction",
        "_id": "69c26f3dcdaa7f875cd42292",
        "irc": "IRC §162(l)",
        "category": "Deduction & Reimbursement",
        "overlap_group": "Health Insurance Deduction",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            not s.get("SIG_HAS_C_CORP", False) and
            not s.get("SIG_HEALTH_INS_EXPENSE", False) and  # Not already deducted via entity
            (s.get("Q_HEALTH_PREMIUM", 0) > 0 or  # Questionnaire confirms premium
             s.get("Q_HEALTH_DEDUCTION_AVAILABLE", 0) > 0)  # or deduction amount confirmed
        ),

        "materiality_fn": lambda s: (
        70 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        55 if s.get("SIG_HIGH_INCOME") else
        40
    ),
        "fed_savings_fn": lambda s: (
    s.get("Q_HEALTH_DEDUCTION_AVAILABLE", 25_000) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    25000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 7,
        "complexity": 5,
        "audit_friction": 5,

        "plain_english": (
            "Self-employed taxpayers may deduct 100% of health insurance premiums "
            "for themselves and their family as an above-the-line deduction."
        ),

        "documentation": [
            "Health insurance premium statements",
            "Proof of self-employed status"
        ],

        "cpa_handoff": [
            "Verify deduction on Schedule 1",
            "Confirm taxpayer not eligible for employer plan"
        ],

        "prerequisites": [
            "Self-employed income",
            "No employer-sponsored health coverage"
        ],
    },

    {
        "id": "DTTS-158-self-rental-grouping",
        "name": "Self-Rental Grouping Strategy",
        "_id": "69c26f3dcdaa7f875cd42295",
        "irc": "IRC §469, Reg. §1.469-4",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Real Estate — Self Rental",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        # Self-rental grouping requires: (1) taxpayer owns a business AND
        # (2) taxpayer also owns/leases the BUILDING to that business.
        # Without confirmed building ownership (Q_OWNS_BUILDING or confirmed
        # depreciation on a commercial property), this strategy is inapplicable.
        "eligibility_logic": lambda s: (
            s.get("SIG_REAL_ESTATE_ACTIVITY", False) and
            (s.get("SIG_HAS_S_CORP_VERIFIED", False) or
             s.get("SIG_BUSINESS_PRESENT", False)) and
            (s.get("Q_OWNS_BUILDING", False) or          # confirmed by questionnaire
             s.get("Q_OWNS_PRACTICE_BUILDING", False))   # alternate questionnaire key
        ),

        # Prerequisite: questionnaire must confirm building ownership
        "prerequisites_logic": lambda s: (
            s.get("Q_OWNS_BUILDING", False) or s.get("Q_OWNS_PRACTICE_BUILDING", False)
        ),
        "readiness_if_prereq_fail": "PREREQUISITE_BUILD",
        "readiness_note": "Questionnaire needed — confirm practice building ownership before analysis",

        "materiality_fn": lambda s: (
            85 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
            70 if s.get("SIG_HIGH_INCOME") else
            50
        ),
        "fed_savings_fn": lambda s: (
            # Savings = building depreciation losses that become deductible against active income
            # Use actual schedule E depreciation if available; else conservative estimate
            max(
                s.get("_schedule_e_depreciation", 0),
                s.get("_rental_net_loss", 0),
            ) * s.get("_fed_marginal_rate", 0.37)
            if (s.get("_schedule_e_depreciation", 0) > 0 or s.get("_rental_net_loss", 0) > 0)
            else 0.0  # no savings if we can't confirm a loss
        ),

        "state_savings_fn": lambda s: (
            max(s.get("_schedule_e_depreciation", 0), s.get("_rental_net_loss", 0)) *
            (s.get("_state_tax", 0) / s.get("_agi", 1) if s.get("_agi", 0) else 0)
        ),

        "speed_days": 45,
        "complexity": 30,
        "audit_friction": 15,

        "plain_english": (
            "When a dentist owns both the dental practice and the building used by the "
            "practice, the rental activity may sometimes be grouped with the business. "
            "This may allow depreciation losses from the building to offset practice income."
        ),

        "documentation": [
            "Lease agreement between entities",
            "Ownership documentation for practice building",
            "Grouping election statement (filed with return)"
        ],

        "cpa_handoff": [
            "Prepare grouping election statement",
            "Review passive activity rules — Reg. §1.469-4"
        ],

        "prerequisites": [
            "Confirmed ownership of practice building (separate entity or direct ownership)",
            "Lease agreement between building entity and practice entity",
        ],
    },

    {
        "id": "DTTS-160-solo-owner-health-strategy",
        "name": "Solo Owner Strategy (Health Care Planning)",
        "_id": "69c26f3ecdaa7f875cd42298",
        "irc": "IRC §105, §106",
        "category": "Retirement & Benefits",
        "overlap_group": "Health Insurance Deduction",
        "applicable_forms": ["1040", "1120S"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_HEALTH_INS_EXPENSE", False) and
            not s.get("SIG_HAS_S_CORP_VERIFIED", False)  # S-Corp owners use DTTS-003 instead
        ),

        "materiality_fn": lambda s: (
        75 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        60 if s.get("SIG_HIGH_INCOME") else
        45
    ),
        "fed_savings_fn": lambda s: (
    s.get("Q_HEALTH_PREMIUM", 15_000) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    15000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 30,
        "complexity": 20,
        "audit_friction": 10,

        "plain_english": (
            "Practice owners may structure healthcare reimbursements and insurance "
            "payments through the business entity to create tax-deductible benefits."
        ),

        "documentation": [
            "Insurance payment records",
            "Reimbursement documentation"
        ],

        "cpa_handoff": [
            "Review healthcare reimbursement structure"
        ],

        "prerequisites": ["Practice ownership"],
    },

    {
        "id": "DTTS-162-small-business-health-credit",
        "name": "Small Business Health Insurance Tax Credit",
        "_id": "69c26f3ecdaa7f875cd4229b",
        "irc": "IRC §45R",
        "category": "Credits & Special Incentives",
        "overlap_group": "Health Insurance Deduction",
        "applicable_forms": ["1120", "1120S", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("SIG_W2_PRESENT", False) and
            s.get("SIG_HEALTH_INS_EXPENSE", False) and
            not s.get("SIG_VERY_HIGH_INCOME", False)  # credit phases out for large practices
        ),

        "materiality_fn": lambda s: (
        75 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        60 if s.get("SIG_HIGH_INCOME") else
        45
    ),
        "fed_savings_fn": lambda s: (
    min(10_000, s.get("_wages", 0) * 0.05)
),

        "state_savings_fn": lambda s: (
    0
),

        "speed_days": 30,
        "complexity": 20,
        "audit_friction": 10,

        "plain_english": (
            "Small businesses providing employee health insurance through the "
            "SHOP marketplace may qualify for a federal tax credit covering a "
            "portion of premium costs."
        ),

        "documentation": [
            "Health insurance marketplace records",
            "Employee coverage documentation"
        ],

        "cpa_handoff": [
            "Prepare Form 8941",
            "Verify eligibility thresholds"
        ],

        "prerequisites": ["Employer-provided health insurance"],
    },

    {
        "id": "DTTS-164-business-use-vehicle",
        "name": "Business Use of Personal Vehicle Deduction",
        "_id": "69c26f3fcdaa7f875cd4229e",
        "irc": "IRC §162, §274(d)",
        "category": "Deduction & Reimbursement",
        "applicable_forms": ["1040", "1120S", "1120", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False),

        "materiality_fn": lambda s: (
        65 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        50 if s.get("SIG_HIGH_INCOME") else
        35
    ),
        "fed_savings_fn": lambda s: (
    s.get("Q_HEALTH_PREMIUM", 7_500) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    7500 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 7,
        "complexity": 5,
        "audit_friction": 10,

        "plain_english": (
            "Dentists who use a personal vehicle for business purposes can deduct "
            "mileage or actual vehicle expenses related to practice activities."
        ),

        "documentation": [
            "Mileage logs",
            "Vehicle expense receipts"
        ],

        "cpa_handoff": [
            "Confirm business mileage percentage",
            "Apply standard mileage or actual expense method"
        ],

        "prerequisites": ["Vehicle used for business activities"],
    },

    {
        "id": "DTTS-165-vacation-home-tax-strategy",
        "name": "Vacation / Second Home Business Strategy",
        "_id": "69c26f3fcdaa7f875cd422a1",
        "irc": "IRC §280A",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Real Estate — Vacation Home",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("Q_OWNS_SECONDARY_HOME", False) or
            (s.get("SIG_REAL_ESTATE_ACTIVITY", False) and
             (s.get("SIG_REAL_ESTATE_DEPRECIATION", False) or s.get("Q_HAS_RENTAL_PROPERTIES", False)))
        ),

        "materiality_fn": lambda s: (
        85 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        70 if s.get("SIG_HIGH_INCOME") else
        55
    ),
        "fed_savings_fn": lambda s: (
    s.get("Q_COST_SEG_INCREMENTAL_DEDUCTION", 60_000) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    60000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 60,
        "complexity": 30,
        "audit_friction": 25,

        "plain_english": (
            "Certain vacation properties may qualify for tax deductions when used "
            "as short-term rentals or business-related properties with proper documentation."
        ),

        "documentation": [
            "Rental records",
            "Expense documentation",
            "Usage logs"
        ],

        "cpa_handoff": [
            "Verify personal vs rental usage",
            "Confirm eligibility under §280A rules"
        ],

        "prerequisites": ["Vacation property with rental or business use"],
    },

    {
        "id": "DTTS-166-charitable-contributions",
        "name": "Charitable Contributions Strategy",
        "_id": "69c26f40cdaa7f875cd422a4",
        "irc": "IRC §170",
        "category": "Charitable & Community",
        "overlap_group": "Charitable Giving",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("_agi", 0) > 100_000 and
            s.get("SIG_HIGH_TAX_LIABILITY", False) and
            s.get("Q_INVESTMENT_PORTFOLIO", 0) > 0  # need appreciated assets to donate
        ),

        "materiality_fn": lambda s: (
        70 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        55 if s.get("SIG_HIGH_INCOME") else
        40
    ),
        "fed_savings_fn": lambda s: (
    s.get("Q_HEALTH_PREMIUM", 15_000) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    15000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 5,

        "plain_english": (
            "Charitable donations to qualified organizations can provide tax "
            "deductions while supporting community initiatives and outreach."
        ),

        "documentation": [
            "Donation receipts",
            "Charity acknowledgment letters"
        ],

        "cpa_handoff": [
            "Verify charity qualification",
            "Apply AGI deduction limits"
        ],

        "prerequisites": ["Donations made to qualified charities"],
    },

    {
        "id": "DTTS-167-section-179-equipment",
        "name": "Section 179 Equipment Deduction",
        "_id": "69c26f41cdaa7f875cd422a7",
        "irc": "IRC §179",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Depreciation — Section 179",
        "applicable_forms": ["1040", "1120", "1120S", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            s.get("Q_179_INCREMENTAL_DEDUCTION", 0) > 0  # only if equipment actually planned
        ),

        "materiality_fn": lambda s: (
        95 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        80 if s.get("SIG_HIGH_INCOME") else
        65
    ),
        "fed_savings_fn": lambda s: (
    s.get("Q_INVESTMENT_PORTFOLIO", 100_000) * 0.20 * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    100000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 14,
        "complexity": 15,
        "audit_friction": 5,

        "plain_english": (
            "Section 179 allows immediate expensing of qualifying equipment purchases "
            "instead of depreciating them over several years."
        ),

        "documentation": [
            "Equipment purchase invoices",
            "Placed-in-service documentation"
        ],

        "cpa_handoff": [
            "Confirm asset eligibility",
            "Prepare Form 4562"
        ],

        "prerequisites": ["Business equipment purchases"],
    },

    {
        "id": "DTTS-171-film-production-credit",
        "name": "Film & Media Production Tax Incentives",
        "_id": "69c26f41cdaa7f875cd422aa",
        "irc": "IRC §181",
        "category": "Credits & Special Incentives",
        "applicable_forms": ["1040", "1120"],
        "phase_1_eligible": False,  # Requires confirmed investment

        "eligibility_logic": lambda s: (
            s.get("SIG_HIGH_INCOME", False) and
            s.get("Q_INVESTMENT_PORTFOLIO", 0) > 100_000  # Requires confirmed investment capacity
        ),

        "materiality_fn": lambda s: (
        85 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        70 if s.get("SIG_HIGH_INCOME") else
        55
    ),
        "fed_savings_fn": lambda s: (
    s.get("Q_INVESTMENT_PORTFOLIO", 75_000) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: 0,

        "speed_days": 90,
        "complexity": 45,
        "audit_friction": 15,

        "plain_english": (
            "Certain investments in film, television, and media production may "
            "qualify for accelerated deductions or state tax incentives."
        ),

        "documentation": [
            "Production investment agreement",
            "Production budget certification"
        ],

        "cpa_handoff": [
            "Verify eligibility for §181 treatment",
            "Confirm state credit documentation"
        ],

        "prerequisites": ["Investment in qualifying production project"],
    },

    {
        "id": "DTTS-172-entity-structuring-layering",
        "name": "Entity Structuring & Layering (Income Shifting)",
        "_id": "69c26f42cdaa7f875cd422ad",
        "irc": "IRC §162, §482",
        "category": "Entity & Income Structuring",
        "overlap_group": "Entity & Income Structuring",
        "applicable_forms": ["1040", "1120S", "1120", "1065"],
        "phase_1_eligible": False,  # Requires confirmed multi-entity structure

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and s.get("SIG_HIGH_INCOME", False) and
            (s.get("SIG_MULTI_ENTITY", False) or s.get("SIG_VERY_HIGH_INCOME", False))
        ),

        "materiality_fn": lambda s: (
        95 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        80 if s.get("SIG_HIGH_INCOME") else
        65
    ),
        "fed_savings_fn": lambda s: (
    s.get("Q_NON_SSTB_INCOME", 50_000) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    50000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 90,
        "complexity": 45,
        "audit_friction": 20,

        "plain_english": (
            "Advanced tax planning sometimes uses multiple entities to separate "
            "operations, management, and real estate ownership."
        ),

        "documentation": [
            "Operating agreements",
            "Intercompany agreements",
            "Transfer pricing documentation"
        ],

        "cpa_handoff": [
            "Review entity structure",
            "Confirm arm's-length transactions"
        ],

        "prerequisites": ["Multiple related business entities"],
    },

    {
        "id": "DTTS-173-bonus-depreciation",
        "name": "Bonus Depreciation Strategy — §168(k)",
        "_id": "69bdb466e5397a28d454431f",
        "irc": "IRC §168(k)",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Depreciation — Bonus §168(k)",
        "applicable_forms": ["1040", "1120", "1120S", "1065"],
        "phase_1_eligible": True,

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and s.get("SIG_LOW_DEPRECIATION", False)
        ),

        "materiality_fn": lambda s: 75 if s.get("SIG_LOW_DEPRECIATION", False) else 50,

        "fed_savings_fn": lambda s: (
            s.get("_depreciation", 0) * 0.60 * s.get("_fed_marginal_rate", 0)
            if s.get("_depreciation", 0)
            else 100000 * s.get("_fed_marginal_rate", 0)
        ),

        "state_savings_fn": lambda s: 0,

        "speed_days": 30,
        "complexity": 20,
        "audit_friction": 10,

        "plain_english": (
            "Bonus depreciation allows accelerated expensing of qualified equipment "
            "and improvements in the year placed in service."
        ),

        "documentation": [
            "Asset purchase records",
            "Placed-in-service documentation",
            "Form 4562"
        ],

        "cpa_handoff": [
            "Confirm asset eligibility",
            "Verify state depreciation rules"
        ],

        "prerequisites": ["Assets placed in service during the tax year"],
    },

    {
        "id": "DTTS-174-private-family-foundation",
        "name": "Private Family Foundation",
        "_id": "69bdb466e5397a28d454433d",
        "irc": "IRC §501(c)(3)",
        "category": "Charitable & Community",
        "applicable_forms": ["1040", "990-PF"],
        "phase_1_eligible": False,  # Requires confirmed charitable goals

        "eligibility_logic": lambda s: (
            s.get("SIG_HIGH_INCOME", False) and
            (s.get("Q_GOAL_LEGACY", False) or
             s.get("Q_HAS_INVESTMENT_PORTFOLIO", False))  # Must have portfolio or legacy goals
        ),

        "materiality_fn": lambda s: (
        100 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        85 if s.get("SIG_HIGH_INCOME") else
        70
    ),
        "fed_savings_fn": lambda s: (
    min(s.get("Q_INVESTMENT_PORTFOLIO", 200_000), s.get("_agi", 0) * 0.30)
    * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    min(200000, s.get("_agi", 0) * 0.30) * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 120,
        "complexity": 50,
        "audit_friction": 20,

        "plain_english": (
            "A private family foundation allows individuals to donate assets, "
            "receive charitable deductions, and control how charitable funds "
            "are distributed over time."
        ),

        "documentation": [
            "Foundation formation documents",
            "Donation records",
            "Annual Form 990-PF filings"
        ],

        "cpa_handoff": [
            "Establish foundation structure",
            "Prepare annual filings"
        ],

        "prerequisites": ["High income and charitable planning goals"],
        "overlap_group": "Charitable — Foundation",
    },

    {
        "id": "DTTS-175-family-management-company",
        "name": "Family Management Company",
        "_id": "69c26f43cdaa7f875cd422cd",
        "irc": "IRC §162",
        "category": "Entity & Income Structuring",
        "overlap_group": "Management Company",
        "applicable_forms": ["1120S", "1120", "1065"],
        "phase_1_eligible": False,  # Requires confirmed family employment

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_DEPENDENTS_PRESENT", False)  # Must have family members
        ),

        "materiality_fn": lambda s: (
        90 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        75 if s.get("SIG_HIGH_INCOME") else
        60
    ),
        "fed_savings_fn": lambda s: (
    s.get("Q_C_CORP_RETAINED_EARNINGS", 40_000) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    40000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 90,
        "complexity": 40,
        "audit_friction": 20,

        "plain_english": (
            "A family management company can centralize administrative services for "
            "multiple related businesses and allow income shifting among family members "
            "when structured properly."
        ),

        "documentation": [
            "Management company operating agreement",
            "Intercompany service agreements",
            "Payroll records for family members"
        ],

        "cpa_handoff": [
            "Confirm arm's-length management fees",
            "Review entity ownership structure"
        ],

        "prerequisites": ["Multiple related business entities"],
    },

    {
        "id": "DTTS-176-management-company",
        "name": "Management Company Structure",
        "_id": "69bdb46ae5397a28d454435f",
        "irc": "IRC §162",
        "category": "Entity & Income Structuring",
        "overlap_group": "Management Company",
        "applicable_forms": ["1120S", "1120", "1065"],
        "phase_1_eligible": False,  # Requires confirmed multi-entity structure

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and
            (s.get("SIG_MULTI_ENTITY", False) or s.get("Q_MGMT_CO_REVENUE", 0) > 0)
        ),

        "materiality_fn": lambda s: (
        85 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        70 if s.get("SIG_HIGH_INCOME") else
        55
    ),
        "fed_savings_fn": lambda s: (
    s.get("Q_MGMT_CO_REVENUE", 30_000) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    30000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 60,
        "complexity": 35,
        "audit_friction": 15,

        "plain_english": (
            "A management company can provide administrative and operational services "
            "to operating entities, allowing centralized expense management and "
            "potential tax planning opportunities."
        ),

        "documentation": [
            "Management company service agreements",
            "Fee allocation schedules"
        ],

        "cpa_handoff": [
            "Verify service fee reasonableness",
            "Confirm proper accounting treatment"
        ],

        "prerequisites": ["Operating business entity"],
    },

    {
        "id": "DTTS-177-holding-company",
        "name": "Holding Company Structure",
        "_id": "69c26f44cdaa7f875cd422d8",
        "irc": "IRC §351",
        "category": "Entity & Income Structuring",
        "overlap_group": "Holding Company",
        "applicable_forms": ["1120", "1120S"],
        "phase_1_eligible": False,  # Requires confirmed multiple entities or IP assets

        "eligibility_logic": lambda s: (
            s.get("SIG_BUSINESS_PRESENT", False) and s.get("SIG_HIGH_INCOME", False) and
            s.get("SIG_MULTI_ENTITY", False)
        ),

        "materiality_fn": lambda s: (
        95 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        80 if s.get("SIG_HIGH_INCOME") else
        65
    ),
        "fed_savings_fn": lambda s: (
    s.get("Q_NON_SSTB_INCOME", 50_000) * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    50000 * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 90,
        "complexity": 40,
        "audit_friction": 20,

        "plain_english": (
            "A holding company structure separates ownership of assets such as real estate "
            "or intellectual property from operating businesses, providing tax planning "
            "opportunities and asset protection."
        ),

        "documentation": [
            "Holding company formation documents",
            "Intercompany agreements"
        ],

        "cpa_handoff": [
            "Review ownership structure",
            "Confirm proper tax elections"
        ],

        "prerequisites": ["Multiple related entities or assets"],
    },

    {
        "id": "DTTS-179-mineral-donations",
        "name": "Mineral Rights Charitable Donation",
        "_id": "69c26f45cdaa7f875cd422db",
        "irc": "IRC §170",
        "category": "Charitable & Community",
        "applicable_forms": ["1040"],
        "phase_1_eligible": False,  # Requires confirmed mineral rights ownership

        "eligibility_logic": lambda s: (
            s.get("SIG_HIGH_INCOME", False) and
            s.get("Q_INVESTMENT_PORTFOLIO", 0) > 100_000 and  # needs significant portfolio
            s.get("SIG_HIGH_TAX_LIABILITY", False)
        ),

        "materiality_fn": lambda s: (
        100 if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY") else
        85 if s.get("SIG_HIGH_INCOME") else
        70
    ),
        "fed_savings_fn": lambda s: (
    min(s.get("Q_INVESTMENT_PORTFOLIO", 150_000), s.get("_agi", 0) * 0.30)
    * s.get("_fed_marginal_rate", 0)
),

        "state_savings_fn": lambda s: (
    min(150000, s.get("_agi", 0) * 0.30) * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
),

        "speed_days": 120,
        "complexity": 45,
        "audit_friction": 25,

        "plain_english": (
            "Donating mineral rights to a qualified charity can generate a charitable "
            "deduction based on the appraised value of the asset."
        ),

        "documentation": [
            "Qualified appraisal of mineral rights",
            "Donation records"
        ],

        "cpa_handoff": [
            "Confirm charitable deduction eligibility",
            "Review appraisal documentation"
        ],

        "prerequisites": ["Ownership of mineral rights or energy assets"],
        "overlap_group": "Charitable — Mineral Rights",
    },

    {
        "id": "DTTS-200-backdoor-roth-ira",
        "name": "Backdoor Roth IRA for High-Income W-2 Employees",
        "_id": "69c26f45cdaa7f875cd422de",
        "irc": "IRC §408A, §408A(c)(3)(B)",
        "category": "Retirement Plans",
        "overlap_group": "Roth Conversion Strategy",
        "applicable_forms": ["1040"],
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",

        "eligibility_logic": lambda s: (
            s.get("SIG_W2_ONLY", False) and
            s.get("_agi", 0) > 240_000 and
            not s.get("SIG_HAS_RETIREMENT_PLAN", False)
        ),

        "materiality_fn": lambda s: 70 if s.get("_agi", 0) > 300_000 else 50,

        "fed_savings_fn": lambda s: 7_000 * s.get("_fed_marginal_rate", 0.32),

        "state_savings_fn": lambda s: 0,

        "speed_days": 7,
        "complexity": 10,
        "audit_friction": 5,

        "plain_english": (
            "High-income W-2 employees cannot contribute directly to a Roth IRA due to income limits. "
            "The Backdoor Roth IRA is a legal workaround: make a non-deductible Traditional IRA contribution "
            "($7,000 for 2024, or $8,000 if age 50+) and immediately convert it to Roth. This allows "
            "tax-free growth and withdrawals in retirement, even for high earners."
        ),

        "documentation": [
            "Form 8606 (Nondeductible IRAs)",
            "IRA custodian conversion records"
        ],

        "cpa_handoff": [
            "Ensure no other pre-tax IRA balances (pro-rata rule)",
            "File Form 8606 annually",
            "Complete conversion promptly after contribution"
        ],

        "prerequisites": [
            "No existing Traditional IRA, SEP IRA, or SIMPLE IRA balances",
            "W-2 income sufficient to make IRA contribution"
        ],
    },

    {
        "id": "DTTS-COMBO-salary-retirement-restructure",
        "name": "Salary + Retirement Plan Restructure",
        "_id": "69c26f46cdaa7f875cd422e1",
        "irc": "IRC §162, §401(a), §412, §415(c), §3121",
        "category": "Retirement & Benefits",
        "overlap_group": "Salary Retirement Combo",
        "applicable_forms": ["1120S"],
        "phase_1_eligible": True,
        "estimate_confidence": "MODERATE",

        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_S_CORP_VERIFIED", False) and
            s.get("SIG_LOW_OWNER_WAGES", False) and
            s.get("SIG_NO_RETIREMENT_PLAN", False) and
            s.get("SIG_RETIREMENT_W2_CONSTRAINED", False) and
            s.get("_obi", 0) > 200_000
        ),

        "materiality_fn": lambda s: (
            95 if s.get("_obi", 0) > 400_000 else
            85 if s.get("_obi", 0) > 250_000 else
            70
        ),

        "fed_savings_fn": lambda s: (
            (lambda target, wages, marg: (
                min(target * 0.60 + 23_000, 143_000) * marg   # CB ≈ 60% of salary + $23K deferral, cap at $143K
                - (
                    (min(target, 168_600) * 0.153 + max(0, target - 168_600) * 0.029)  # new FICA
                    - (min(wages, 168_600) * 0.153 + max(0, wages - 168_600) * 0.029)  # old FICA
                ) * (1 - 0.50 * marg)   # employer half (50%) is deductible at marginal rate
            ))(
                min(s.get("_obi", 0) * 0.40, 200_000),  # target salary
                s.get("_wages", 0),                       # current wages
                s.get("_fed_marginal_rate", 0),           # marginal rate
            )
        ),

        "state_savings_fn": lambda s: (
            min(min(s.get("_obi", 0) * 0.40, 200_000) * 0.60 + 23_000, 143_000) *
            s.get("Q_STATE_MARGINAL_RATE", 0.093)
        ),

        "speed_days": 60,
        "complexity": 35,
        "audit_friction": 15,

        "plain_english": (
            "This is the highest-impact restructuring for an S-Corp dentist with "
            "low W-2 wages and no retirement plan. Step 1: Raise your S-Corp salary "
            "to a defensible level (~40% of practice income, documented with ADA/MGMA "
            "surveys). Step 2: Implement a Cash Balance Plan (or Solo 401(k) + DB combo) "
            "and contribute the maximum allowable amount — typically $100K–$140K+ "
            "per year depending on age. The retirement contributions create large "
            "tax deductions that far exceed the additional FICA cost of raising your "
            "salary. Net federal savings of $20K–$30K per year after FICA cost, "
            "plus $10K–$13K in state savings. This single restructuring captures "
            "more value than all other strategies combined."
        ),

        "documentation": [
            "ADA/MGMA reasonable compensation study",
            "Board resolution setting officer compensation",
            "Retirement plan adoption agreement",
            "Annual contribution calculations",
            "Form W-2 reflecting new salary level",
        ],

        "cpa_handoff": [
            "Set salary at defensible level with compensation study documentation",
            "Implement retirement plan before year-end (or by tax filing deadline for SEP)",
            "Calculate optimal contribution: Solo 401(k) vs Cash Balance based on age",
            "FICA impact: model exact OASDI/Medicare cost at new salary level",
            "Net benefit analysis: retirement tax savings minus FICA cost increase",
        ],

        "prerequisites": [
            "S-Corp entity in place",
            "Reasonable compensation study completed",
            "Retirement plan selected and adopted",
        ],
    },
    {
    "id": "DTTS-227-nol-carryforward",
    "name": "Net Operating Loss (NOL) Carryforward",
    "_id": "69c26f23cdaa7f875cd42144",
    "irc": "IRC §172",
    "category": "Tax Loss Utilization",
    "overlap_group": "Loss Strategies",
    "phase_1_eligible": True,
    "estimate_confidence": "HIGH",
    
    "eligibility_logic": lambda s: (
        (s.get("SIG_HAS_S_CORP", False) or s.get("SIG_HAS_C_CORP", False) or s.get("SIG_BUSINESS_PRESENT", False)) and
        s.get("_obi", 0) < 0  # Loss detected
    ),
    
    "materiality_fn": lambda s: (
        95 if abs(s.get("_obi", 0)) > 100_000 else
        80 if abs(s.get("_obi", 0)) > 50_000 else
        60 if abs(s.get("_obi", 0)) > 10_000 else
        40
    ),
    
    "fed_savings_fn": lambda s: (
        abs(s.get("_obi", 0)) * s.get("_fed_marginal_rate", 0.24) * 0.30  # Probability-weighted
    ),
    
    "state_savings_fn": lambda s: (
        abs(s.get("_obi", 0)) * s.get("Q_STATE_MARGINAL_RATE", 0.05) * 0.20
    ),
    
    "speed_days": 14,
    "complexity": 15,
    "audit_friction": 5,
    
    "plain_english": (
        "This business has a net operating loss (NOL) of ${_obi:,.0f} for the tax year. "
        "This loss can be carried forward indefinitely to offset future taxable income, "
        "reducing future tax liability. At a {_fed_marginal_rate:.0%} marginal rate, "
        "this loss represents approximately ${_nol_amount:,.0f} in future tax savings."
    ),
    
    "documentation": [
        "NOL computation worksheet",
        "Tax return showing loss",
        "NOL carryforward tracking schedule"
    ],
    
    "cpa_handoff": [
        "Track NOL carryforward indefinitely (post-2018 rules)",
        "80% limitation applies when utilizing",
        "State NOL rules may differ significantly",
        "Consider §382 ownership change limitations"
    ],
    
    "prerequisites": [
        "Net operating loss in current year",
        "Track NOL for future utilization"
    ],
},

    # ══════════════════════════════════════════════════════════════════════════
    # LOSS-SCENARIO STRATEGIES — COMPREHENSIVE SUITE
    # Triggered when _planning_mode == "LOSS" or SIG_NOL_CARRYOVER is True.
    # Each strategy is anchored to specific IRC sections, uses form-verified
    # signals, and provides actionable documentation for the CPA handoff.
    # ══════════════════════════════════════════════════════════════════════════

    # ── §1366(d) S-Corp Shareholder Basis Restoration ───────────────────────
    {
        "id": "DTTS-228-scorp-basis-restoration",
        "name": "S-Corp Shareholder Basis Restoration (§1366(d))",
        "_id": "69c51ed0c2965eadfe41b1a4",
        "irc": "IRC §1366(d), §1367, §1374, Reg. §1.1366-2",
        "category": "Tax Loss Utilization",
        "overlap_group": "Loss Strategies — Basis",
        "applicable_forms": ["1120S"],
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",

        "eligibility_logic": lambda s: (
            s.get("SIG_1366D_BASIS_REVIEW", False) and
            s.get("_planning_mode") == "LOSS" and
            s.get("_entity_has_s_corp", False)
        ),

        "materiality_fn": lambda s: (
            95 if s.get("_s_corp_loss_magnitude", 0) > 200_000 else
            85 if s.get("_s_corp_loss_magnitude", 0) > 100_000 else
            75 if s.get("_s_corp_loss_magnitude", 0) > 50_000 else
            60
        ),

        "fed_savings_fn": lambda s: (
            # Value of unlocking suspended losses = loss magnitude × rate
            # Only probability-weight by 70% because basis adequacy unknown without basis schedule
            min(s.get("_s_corp_loss_magnitude", 0), 500_000) *
            s.get("_fed_marginal_rate", 0.37) * 0.70
        ),

        "state_savings_fn": lambda s: (
            min(s.get("_s_corp_loss_magnitude", 0), 500_000) *
            s.get("Q_STATE_MARGINAL_RATE", 0.09) * 0.50
        ),

        "speed_days": 30,
        "complexity": 25,
        "audit_friction": 10,

        "plain_english": (
            "Under §1366(d), an S-Corp shareholder can only deduct their share of "
            "the entity's loss to the extent of their adjusted stock basis plus any "
            "bona fide loans made directly to the corporation. If your current basis "
            "is insufficient to absorb this year's loss, the excess is suspended — "
            "not lost — and carries forward until basis is restored. The fix is "
            "straightforward: (1) make a direct shareholder loan to the S-Corp before "
            "year-end to restore basis, or (2) contribute additional capital. Either "
            "action restores basis dollar-for-dollar and immediately unlocks the "
            "suspended loss deduction. A shareholder basis schedule must be maintained "
            "annually (Form 7203) — failure to file Form 7203 is now an automatic IRS "
            "audit trigger for S-Corp loss deductions."
        ),

        "documentation": [
            "Shareholder basis schedule (stock + debt basis, updated annually)",
            "Form 7203 — S Corporation Shareholder Stock and Debt Basis Limitations (required with loss)",
            "Shareholder loan agreement (promissory note at market interest rate, direct to S-Corp)",
            "Board minutes authorizing capital contribution or loan",
            "Prior-year basis carryforward schedule",
        ],

        "cpa_handoff": [
            "File Form 7203 — IRS now requires this form whenever a loss, distribution, or loan repayment occurs",
            "Stock basis: add capital contributions, income allocations; subtract distributions, loss allocations",
            "Debt basis: only direct loans from shareholder to S-Corp — third-party loans backed by shareholder DO NOT create basis",
            "Suspended losses: carry forward indefinitely; deductible when basis restored or S-Corp interest disposed",
            "Loan basis: interest accrues and must be reported; avoid demand notes (IRS scrutiny on bona fide debt)",
            "Document shareholder loan with promissory note, board resolution, and market interest rate",
            "Check open years for prior suspended loss carryforwards — they may be deductible now if basis restored",
        ],

        "prerequisites": [
            "Confirm current shareholder basis (stock + debt) before recommending loan injection",
            "Review Form 7203 or basis schedule from prior-year return",
        ],
    },

    # ── §469 Passive Activity Loss — Grouping Election ───────────────────────
    {
        "id": "DTTS-229-469-pal-grouping-election",
        "name": "Passive Activity Loss — §469 Grouping Election",
        "_id": "69c51f21c2965eadfe41b1c8",
        "irc": "IRC §469, §469(c)(7), Reg. §1.469-4, §1.469-9",
        "category": "Tax Loss Utilization",
        "overlap_group": "Loss Strategies — PAL",
        "applicable_forms": ["1120S", "1065", "1040"],
        "phase_1_eligible": True,
        "estimate_confidence": "MODERATE",

        "eligibility_logic": lambda s: (
            (s.get("SIG_469_PAL_REVIEW", False) or s.get("SIG_469_GROUPING_ELECTION", False)) and
            (s.get("_planning_mode") == "LOSS" or s.get("SIG_REAL_ESTATE_ACTIVITY", False))
        ),

        "materiality_fn": lambda s: (
            90 if s.get("_loss_magnitude", 0) > 100_000 else
            75 if s.get("_loss_magnitude", 0) > 50_000 else
            60
        ),

        "fed_savings_fn": lambda s: (
            # PAL grouping converts passive losses to active; saves at ordinary rate
            min(s.get("_loss_magnitude", 0), 300_000) *
            s.get("_fed_marginal_rate", 0.37) * 0.55  # 55% probability — requires TP to materially participate
        ),

        "state_savings_fn": lambda s: (
            min(s.get("_loss_magnitude", 0), 300_000) *
            s.get("Q_STATE_MARGINAL_RATE", 0.09) * 0.40
        ),

        "speed_days": 45,
        "complexity": 30,
        "audit_friction": 20,

        "plain_english": (
            "§469 separates business activities into 'active' and 'passive.' Losses from "
            "passive activities can ONLY offset passive income — they cannot reduce W-2 wages "
            "or ordinary business income. However, a taxpayer who materially participates in "
            "an activity (500+ hours/year, or meets one of seven IRS tests) can classify it "
            "as active, making losses immediately deductible. The §469 grouping election "
            "allows related activities (e.g., dental practice + management company, or "
            "multiple practice locations) to be treated as a single activity for material "
            "participation testing. Real estate professionals (750+ hours in real property "
            "trades) under §469(c)(7) can fully deduct rental losses even above $25K. "
            "Filing the grouping election statement with the return is permanent — it cannot "
            "be revoked without IRS consent — so proper analysis before election is critical."
        ),

        "documentation": [
            "Grouping election statement attached to timely filed (or amended) return",
            "Material participation time logs (contemporaneous records — 500+ hours per activity)",
            "§469(c)(7) Real Estate Professional hours log (750+ hours and >50% of work time in real property)",
            "Activity-by-activity income/loss schedule",
            "Prior-year suspended PAL carryforward schedule",
        ],

        "cpa_handoff": [
            "Seven material participation tests (§1.469-5T): 500-hr primary test; 100-hr substantial test; facts-and-circumstances",
            "Grouping election: once made, all grouped activities tested together — increases likelihood of material participation",
            "Real estate professional status: 750+ hours AND more than 50% of total work hours in real property trades (§469(c)(7))",
            "Rental real estate: $25K special allowance for active participants phases out $50K–$100K AGI ($25K–$50K MFJ)",
            "Suspended PALs released upon complete taxable disposition of the activity (§469(g))",
            "NIIT: passive income is subject to 3.8% NIIT; active business income is not — grouping can reduce NIIT exposure",
            "Self-rental rule (§1.469-2(f)(6)): renting property to your own S-Corp is NOT passive — income is recharacterized as active",
        ],

        "prerequisites": [
            "Document material participation hours BEFORE year-end (contemporaneous logs required by regulations)",
            "Review prior-year PAL carryforwards on Form 8582",
            "Confirm whether grouping election was made in a prior year (binding if yes)",
        ],
    },

    # ── §465 At-Risk Limitation ───────────────────────────────────────────────
    {
        "id": "DTTS-230-465-at-risk-planning",
        "name": "§465 At-Risk Limitation Planning",
        "_id": "69c51f5ac2965eadfe41b1e6",
        "irc": "IRC §465, Reg. §1.465-1, §1.465-8",
        "category": "Tax Loss Utilization",
        "overlap_group": "Loss Strategies — At-Risk",
        "applicable_forms": ["1120S", "1065", "1040"],
        "phase_1_eligible": True,
        "estimate_confidence": "MODERATE",

        "eligibility_logic": lambda s: (
            s.get("SIG_465_AT_RISK_REVIEW", False) and
            s.get("_planning_mode") == "LOSS"
        ),

        "materiality_fn": lambda s: (
            80 if s.get("_loss_magnitude", 0) > 100_000 else
            65 if s.get("_loss_magnitude", 0) > 50_000 else
            50
        ),

        "fed_savings_fn": lambda s: (
            min(s.get("_loss_magnitude", 0), 250_000) *
            s.get("_fed_marginal_rate", 0.37) * 0.50
        ),

        "state_savings_fn": lambda s: (
            min(s.get("_loss_magnitude", 0), 250_000) *
            s.get("Q_STATE_MARGINAL_RATE", 0.09) * 0.35
        ),

        "speed_days": 30,
        "complexity": 30,
        "audit_friction": 15,

        "plain_english": (
            "§465 limits deductible losses to the amount you are 'at risk' — essentially, "
            "money you could lose if the activity fails. At-risk amounts include cash invested, "
            "property contributed (at adjusted basis), and personally guaranteed recourse debt. "
            "Nonrecourse financing (where the lender has no personal recourse against you) does "
            "NOT increase at-risk basis, with an exception for qualified nonrecourse real estate "
            "financing. The planning opportunity: if losses exceed current at-risk amounts, "
            "restructure financing to convert nonrecourse to recourse debt (personal guarantee), "
            "or inject additional cash/property before year-end. Losses suspended by §465 carry "
            "forward (Form 6198) and are released in future years when at-risk amounts increase. "
            "§465 is tested annually and separately from §469 PAL rules."
        ),

        "documentation": [
            "Form 6198 — At-Risk Limitations (filed with return when loss exceeds at-risk amount)",
            "At-risk basis schedule (cash invested, property basis, guaranteed recourse debt)",
            "Loan documents distinguishing recourse vs nonrecourse (lender/bank confirmation letter)",
            "Personal guarantee agreements on entity debt",
        ],

        "cpa_handoff": [
            "At-risk basis ≠ §1366 stock basis — compute separately under §465 rules",
            "Recourse debt increases at-risk basis (TP personally liable); nonrecourse generally does not",
            "Exception: qualified nonrecourse real estate financing from qualified lenders (§465(b)(6)) counts",
            "Suspended §465 losses carry forward on Form 6198; released when at-risk amount increases",
            "Recapture: if at-risk drops below zero (e.g., debt restructured to nonrecourse), §465(e) recapture applies",
            "§465 applies activity-by-activity — cannot aggregate across activities",
        ],

        "prerequisites": [
            "Prepare Form 6198 at-risk computation before loss deduction is claimed",
            "Obtain loan documents and confirm recourse/nonrecourse status",
        ],
    },

    # ── §168(k) Depreciation Timing Optimization in Loss Year ────────────────
    {
        "id": "DTTS-231-168k-loss-year-timing",
        "name": "Bonus Depreciation Timing Election in Loss Year (§168(k))",
        "_id": "69c51f97c2965eadfe41b204",
        "irc": "IRC §168(k), §168(k)(7), §168(b)(2)(D), Reg. §1.168(k)-2",
        "category": "Tax Loss Utilization",
        "overlap_group": "Loss Strategies — Depreciation",
        "applicable_forms": ["1120S", "1120", "1065"],
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",

        "eligibility_logic": lambda s: (
            s.get("SIG_168_DEPRECIATION_TIMING", False) and
            s.get("_planning_mode") == "LOSS" and
            s.get("SIG_HAS_DEPRECIATION", False)
        ),

        "materiality_fn": lambda s: (
            88 if s.get("_depreciation", 0) > 100_000 else
            72 if s.get("_depreciation", 0) > 50_000 else
            55
        ),

        "fed_savings_fn": lambda s: (
            # In a loss year: opt OUT of bonus depreciation to reduce the NOL (which has
            # only 80% utilization in future years at unknown rate) and instead take
            # straight-line depreciation now. Rate arbitrage benefit:
            # Current NOL × (1 - 80%) × current rate = 20% of depreciation × rate
            # vs. future income year: same deduction at future rate (potentially higher)
            # Model: if deferred to high-income year, save rate differential
            s.get("_depreciation", 0) *
            max(0.0, s.get("_fed_marginal_rate", 0.37) - 0.21) * 0.40  # 40% probability of higher future rate
        ),

        "state_savings_fn": lambda s: (
            s.get("_depreciation", 0) * s.get("Q_STATE_MARGINAL_RATE", 0.09) * 0.25
        ),

        "speed_days": 14,
        "complexity": 20,
        "audit_friction": 5,

        "plain_english": (
            "§168(k) bonus depreciation is a timing election — taking bonus depreciation "
            "accelerates a future deduction into the current year. In a LOSS year, this is "
            "often the WRONG move: additional depreciation deepens the NOL, which can only "
            "offset 80% of future taxable income per year (§172 limitation). A deduction "
            "that increases a current-year loss saves 80% × your future rate — but the same "
            "deduction taken in a profitable future year saves 100% × your future rate. "
            "The election to OPT OUT of bonus depreciation is made class-by-class on Form "
            "4562. This converts MACRS 5-year/7-year property to straight-line, spreading "
            "the deduction over the recovery period — often producing more total tax benefit "
            "when future income years are at higher marginal rates. Exception: if the NOL "
            "will be fully absorbed next year, the 80% limitation doesn't cost much, and "
            "accelerating may still be optimal. Model both scenarios before electing."
        ),

        "documentation": [
            "Form 4562 — Depreciation and Amortization (elect out of bonus by property class)",
            "Written depreciation schedule showing MACRS vs. straight-line comparison",
            "NOL utilization projection (years to full absorption at estimated future income)",
            "Rate arbitrage analysis: current-year loss rate vs. projected future income year rate",
        ],

        "cpa_handoff": [
            "Election to opt out of §168(k) bonus: made on Form 4562, Part II — by MACRS property class (5-yr, 7-yr, etc.)",
            "Election must be made by due date (including extensions) of the tax return — NOT retroactively revocable",
            "2024 bonus rate: 60% for property placed in service in 2024; decreasing 20%/yr through 2027",
            "QIP (qualified improvement property): 15-year property with 60% bonus — consider opting out in loss year",
            "§179 cannot create or increase a loss (§179(b)(3)); use regular MACRS or straight-line instead",
            "Model: compare PV of NOL carryforward (80% utilized) vs. straight-line deductions in future income years",
            "State conformity: many states do NOT conform to federal bonus depreciation — check state-level impact separately",
        ],

        "prerequisites": [
            "Confirm total §168(k) depreciation taken in current year on Form 4562",
            "Model NOL absorption timeline before electing out",
        ],
    },

    # ── §461(l) Excess Business Loss Limitation ───────────────────────────────
    {
        "id": "DTTS-232-461l-excess-business-loss",
        "name": "Excess Business Loss Limitation Planning (§461(l))",
        "_id": "69c52026c2965eadfe41b222",
        "irc": "IRC §461(l), §461(l)(3), TCJA §11012, extended through 2028",
        "category": "Tax Loss Utilization",
        "overlap_group": "Loss Strategies — EBL",
        "applicable_forms": ["1040", "1120S", "1065"],
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",

        "eligibility_logic": lambda s: (
            s.get("SIG_461L_EXCESS_BUSINESS_LOSS", False) and
            s.get("_planning_mode") == "LOSS"
        ),

        "materiality_fn": lambda s: (
            92 if s.get("_461l_excess_amount", 0) > 200_000 else
            78 if s.get("_461l_excess_amount", 0) > 100_000 else
            65
        ),

        "fed_savings_fn": lambda s: (
            # EBL excess becomes an NOL — the cost is a one-year deferral at 80% future use
            # Exposure: excess × rate × (1 - 80%) = 20% deferral cost
            # But if taxpayer doesn't know about EBL, they may deduct too much → penalty risk
            s.get("_461l_excess_amount", 0) *
            s.get("_fed_marginal_rate", 0.37) * 0.20  # Planning value = avoidance of underpayment penalty
        ),

        "state_savings_fn": lambda s: 0.0,  # §461(l) is federal; states vary widely

        "speed_days": 14,
        "complexity": 20,
        "audit_friction": 10,

        "plain_english": (
            "§461(l) caps how much of your business losses you can deduct against non-business "
            "income (like W-2 wages or investment income) in a single tax year. For 2024, "
            "the limit is $305,000 for single filers and $610,000 for married-filing-jointly. "
            "Any losses above this threshold are NOT lost — they convert to a Net Operating "
            "Loss (NOL) carryforward, subject to the 80% ATI limitation in future years. "
            "The trap: taxpayers who over-deduct (not realizing the §461(l) cap applies) "
            "expose themselves to IRS notices, accuracy-related penalties, and potential "
            "carryforward recalculation. The planning action is to correctly calculate the "
            "EBL at year-end, convert the excess to an NOL carryforward, and project the "
            "utilization timeline so the client understands when the benefit will be realized."
        ),

        "documentation": [
            "Form 461 — Limitation on Business Losses (filed with Form 1040)",
            "NOL carryforward tracking schedule (excess EBL becomes NOL §461(l)(2))",
            "Business vs. non-business income classification worksheet",
            "State EBL conformity analysis (many states do not conform to §461(l))",
        ],

        "cpa_handoff": [
            "§461(l) applies at the individual level — aggregates losses from all business activities",
            "2024 threshold: $305,000 single / $610,000 MFJ (indexed for inflation annually)",
            "Excess EBL converts to NOL under §172 — carry forward indefinitely, 80% ATI limit applies",
            "W-2 wages and capital gains are NOT business income for EBL purposes (they cannot offset EBL)",
            "Filing Form 461: aggregates net loss from all trade/business activities; excess moves to Schedule 1",
            "State nonconformity: most states ignore §461(l) — state may allow full deduction that federal caps",
            "Planning: if near threshold, consider timing income recognition or deferring deductions to next year",
        ],

        "prerequisites": [
            "Aggregate all business income/loss items before applying EBL cap",
            "File Form 461 — failure to file is an understatement exposure",
        ],
    },

    # ── §172 NOL Carryforward — Enhanced Planning ────────────────────────────
    {
        "id": "DTTS-233-172-nol-optimization",
        "name": "NOL Carryforward Optimization & Utilization Planning (§172)",
        "_id": "69c520f7c2965eadfe41b240",
        "irc": "IRC §172, §172(a)(2), §172(b)(1)(A), §172(d), TCJA §13302",
        "category": "Tax Loss Utilization",
        "overlap_group": "Loss Strategies",
        "applicable_forms": ["1120S", "1120", "1065", "1040"],
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",

        "eligibility_logic": lambda s: (
            s.get("SIG_172_NOL_CARRYFORWARD", False) or
            (s.get("SIG_NOL_CARRYOVER", False) and s.get("_nol_total_pool", 0) > 10_000)
        ),

        "materiality_fn": lambda s: (
            95 if s.get("_nol_total_pool", 0) > 500_000 else
            88 if s.get("_nol_total_pool", 0) > 200_000 else
            78 if s.get("_nol_total_pool", 0) > 100_000 else
            65 if s.get("_nol_total_pool", 0) > 50_000 else
            50
        ),

        "fed_savings_fn": lambda s: (
            # NOL value = pool × 80% utilization × loss_tax_rate
            # Discount by 85% for time value (approximate PV of 2-year absorption)
            s.get("_nol_total_pool", 0) * 0.80 *
            s.get("_loss_tax_rate", 0.32) * 0.85
        ),

        "state_savings_fn": lambda s: (
            # State NOL rules vary; use 50% probability factor
            s.get("_nol_total_pool", 0) * 0.80 *
            s.get("Q_STATE_MARGINAL_RATE", 0.09) * 0.50
        ),

        "speed_days": 21,
        "complexity": 20,
        "audit_friction": 8,

        "plain_english": (
            "A Net Operating Loss (NOL) is a valuable tax asset. Under post-TCJA rules "
            "(§172), NOLs are carried forward indefinitely (no 2-year carryback for most "
            "businesses) and can offset up to 80% of taxable income in any future year. "
            "This means an NOL of $500,000 becomes a $400,000 deduction against your next "
            "year's income — saving $148,000 in federal tax at a 37% rate. The planning "
            "priorities: (1) maintain a precise NOL tracking schedule by tax year (different "
            "tax years may have different carryback/carryforward rules), (2) time income "
            "recognition to maximize NOL absorption in the earliest profitable year, (3) "
            "avoid unnecessary income deferrals that delay NOL utilization, and (4) if "
            "business ownership changes by more than 50%, assess §382 annual limitation "
            "risk immediately — it can permanently reduce the annual NOL utilization amount "
            "to a fraction of the §382 base rate × value of the company at change date."
        ),

        "documentation": [
            "NOL carryforward tracking schedule by tax year (origination year matters for pre/post-TCJA rules)",
            "Form 1045 or Form 1139 — Application for Tentative Refund (if carryback applies)",
            "§382 ownership change analysis (if any sale/transfer of >50% interest in 3-year window)",
            "State NOL schedule (state rules may differ materially — California: 2-year suspension; NY: conforms)",
            "Tax return sections showing NOL deduction (Schedule 1 line 8a for individual; line 29a for 1120)",
        ],

        "cpa_handoff": [
            "Track NOL by origination year — pre-2018 NOLs have 20-year carryforward and 2-year carryback (different rules!)",
            "80% ATI limitation (§172(a)(2)): can never use more than 80% of current-year taxable income from NOL in any year",
            "Post-2017 NOLs: no carryback for C-Corps (except farming/property casualty insurance); 2-year carryback for individuals",
            "§382 limitation: if ownership change >50% in 3 years, annual NOL use capped at: FMV × long-term tax-exempt rate",
            "Assess §382 BEFORE any partnership admission, equity sale, or recapitalization event",
            "State tracking: many states have shorter carryforward periods (CA: 20 years; NY: 20 years; TX: no income tax)",
            "Ordering: §172 NOL used AFTER all current-year deductions — don't reduce other deductions thinking NOL will cover",
            "Income acceleration strategy: if large NOL, may want to accelerate income into current or next year to absorb NOL faster",
        ],

        "prerequisites": [
            "Obtain prior-year NOL carryforward schedule from prior CPA",
            "Review §382 ownership history for last 3 years",
        ],
    },

    # ── §704(d) Partnership Basis Planning ────────────────────────────────────
    {
        "id": "DTTS-234-704d-partnership-basis",
        "name": "Partnership Basis Restoration & §704(d) Loss Planning",
        "_id": "69c52163c2965eadfe41b25e",
        "irc": "IRC §704(d), §722, §733, §743, §752, Reg. §1.704-1(d)",
        "category": "Tax Loss Utilization",
        "overlap_group": "Loss Strategies — Basis",
        "applicable_forms": ["1065"],
        "phase_1_eligible": True,
        "estimate_confidence": "MODERATE",

        "eligibility_logic": lambda s: (
            s.get("SIG_704D_BASIS_REVIEW", False) and
            s.get("_planning_mode") == "LOSS" and
            s.get("_entity_has_partnership", False)
        ),

        "materiality_fn": lambda s: (
            88 if s.get("_partnership_loss_magnitude", 0) > 150_000 else
            75 if s.get("_partnership_loss_magnitude", 0) > 75_000 else
            60
        ),

        "fed_savings_fn": lambda s: (
            min(s.get("_partnership_loss_magnitude", 0), 400_000) *
            s.get("_fed_marginal_rate", 0.37) * 0.65
        ),

        "state_savings_fn": lambda s: (
            min(s.get("_partnership_loss_magnitude", 0), 400_000) *
            s.get("Q_STATE_MARGINAL_RATE", 0.09) * 0.45
        ),

        "speed_days": 30,
        "complexity": 35,
        "audit_friction": 15,

        "plain_english": (
            "A partner's outside basis in a partnership determines how much loss they can "
            "currently deduct under §704(d). Outside basis starts with the partner's capital "
            "contribution and is increased by their share of partnership income and additional "
            "contributions; it is reduced by distributions and loss allocations. Partnership "
            "debt (recourse and certain nonrecourse) also increases outside basis under §752 "
            "— this is a key advantage over S-Corp basis rules. Planning actions: (1) make "
            "additional cash contributions before year-end to restore basis; (2) if the "
            "partnership has nonrecourse debt, confirm the partner's §752 share is properly "
            "allocated to basis; (3) consider a §754 election if a partner's interest is "
            "sold or transferred — it steps up inside basis to match outside basis, preventing "
            "double-counting of loss. Suspended losses carry forward to the partner and are "
            "deducted in future years when basis is restored, or on full disposition."
        ),

        "documentation": [
            "Partner outside basis schedule (updated annually with allocations from K-1)",
            "Partnership debt allocation schedule (recourse vs. nonrecourse per §752)",
            "§754 election statement (if applicable — once made, applies to all future transfers)",
            "Form 8308 — Report of sale or exchange of partnership interests",
            "Prior-year suspended §704(d) loss carryforward schedule",
        ],

        "cpa_handoff": [
            "Outside basis ≠ capital account — outside basis includes partner's share of recourse and qualified nonrecourse debt",
            "Recourse debt: allocated to partner bearing economic risk of loss (usually the personal guarantor)",
            "Qualified nonrecourse real estate debt: allocated based on profit-sharing ratio",
            "§704(d) suspended losses: carry forward to same partner; deductible in future year when basis increases",
            "§754 election: if a partner's interest is transferred and the election is in place, inside basis adjusts under §743(b)",
            "Check §1.752-3 regulations for allocation of nonrecourse debt when there is minimum gain or §704(c) gain",
            "§704(d) losses apply BEFORE §465 at-risk test and §469 PAL test — stack properly",
        ],

        "prerequisites": [
            "Obtain partnership agreement and capital account schedule",
            "Request Schedule K-1 Line 20(N) — partner's share of recourse liabilities",
        ],
    },

    # ── §1244 Ordinary Stock Loss ─────────────────────────────────────────────
    {
        "id": "DTTS-235-1244-ordinary-stock-loss",
        "name": "§1244 Ordinary Loss on Small Business Stock",
        "_id": "69c5219ec2965eadfe41b287",
        "irc": "IRC §1244, §1244(b), §1244(c), Reg. §1.1244(a)-1",
        "category": "Tax Loss Utilization",
        "overlap_group": "Loss Strategies — Stock",
        "applicable_forms": ["1040", "1120S"],
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",

        "eligibility_logic": lambda s: (
            s.get("SIG_1244_STOCK_LOSS", False) and
            s.get("_planning_mode") == "LOSS" and
            s.get("_entity_has_s_corp", False)
        ),

        "materiality_fn": lambda s: (
            85 if s.get("_s_corp_loss_magnitude", 0) > 100_000 else
            70 if s.get("_s_corp_loss_magnitude", 0) > 50_000 else
            55
        ),

        "fed_savings_fn": lambda s: (
            # §1244 converts up to $50K ($100K MFJ) of stock loss from capital to ordinary
            # Savings = (ordinary rate − capital rate) × eligible amount
            min(s.get("_s_corp_loss_magnitude", 0),
                100_000 if "MFJ" in (s.get("_filing_status") or "MFJ") else 50_000) *
            max(0.0, s.get("_fed_marginal_rate", 0.37) - 0.20)  # rate differential vs LTCG
        ),

        "state_savings_fn": lambda s: (
            min(s.get("_s_corp_loss_magnitude", 0), 100_000) *
            s.get("Q_STATE_MARGINAL_RATE", 0.09) * 0.50
        ),

        "speed_days": 14,
        "complexity": 15,
        "audit_friction": 5,

        "plain_english": (
            "§1244 allows shareholders of a small domestic corporation (that has received "
            "≤ $1 million in equity contributions) to deduct up to $50,000 ($100,000 MFJ) "
            "of stock losses as ORDINARY losses — not capital losses. This is enormously "
            "valuable: an ordinary loss offsets W-2 wages, self-employment income, and "
            "other ordinary income at up to 37%. A capital loss, by contrast, is limited to "
            "$3,000/year against ordinary income (excess carries forward). For a dentist "
            "with significant S-Corp stock that has declined in value, §1244 can convert a "
            "trapped capital loss into an immediate ordinary deduction. Key requirement: "
            "the stock must have been originally issued directly to the taxpayer (not purchased "
            "in a secondary market), and the corporation must have been a domestic corporation "
            "when the stock was issued with total equity contributions ≤ $1 million."
        ),

        "documentation": [
            "Stock certificate or subscription agreement (evidence of original issuance)",
            "Corporate records showing total capital contributions ≤ $1M at time of issuance",
            "Basis records for §1244 stock (original issue price)",
            "Form 4797 Part II (ordinary loss portion) or Schedule D/Form 8949 (capital loss portion)",
        ],

        "cpa_handoff": [
            "§1244 limit: $50K single / $100K MFJ per year — excess is capital loss",
            "Requirements: stock originally issued by domestic corporation for money or property; equity raised ≤ $1M",
            "Loss reported on Form 4797 Part II as ordinary loss (not Schedule D)",
            "S-Corp: §1244 applies to original stock issuances; transfers of stock from a prior holder do NOT qualify",
            "Ordinary loss can offset any income — no $3K/year cap unlike capital losses",
            "Basis: use adjusted stock basis (cost basis + §1366 income − §1366 losses − distributions)",
        ],

        "prerequisites": [
            "Confirm stock was originally issued to the taxpayer (not purchased from another shareholder)",
            "Obtain corporate records showing cumulative equity contributions",
        ],
    },

    # ── Accountable Plan — Loss Year Expense Capture ──────────────────────────
    {
        "id": "DTTS-236-accountable-plan-loss-year",
        "name": "Accountable Plan — Comprehensive Expense Capture in Loss Year",
        "_id": "69c52214c2965eadfe41b2c1",
        "irc": "IRC §62(a)(2)(A), §162, Reg. §1.62-2, §1.162-17",
        "category": "Business Deductions",
        "overlap_group": "Accountable Plan",
        "applicable_forms": ["1120S", "1065", "1040"],
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",

        "eligibility_logic": lambda s: (
            s.get("SIG_ACCOUNTABLE_PLAN", False) and
            (s.get("_planning_mode") == "LOSS" or s.get("SIG_HAS_S_CORP_VERIFIED", False)) and
            s.get("_wages", 0) > 50_000  # must have some compensation to reimburse against
        ),

        "materiality_fn": lambda s: (
            80 if s.get("_wages", 0) > 200_000 else
            65 if s.get("_wages", 0) > 100_000 else
            50
        ),

        "fed_savings_fn": lambda s: (
            # In a loss year: capturing expenses through accountable plan converts
            # non-deductible employee business expenses (post-TCJA Schedule A elimination)
            # into entity-level deductions that increase the NOL (§172) or reduce
            # pass-through income. Estimated uncaptured expenses: 3-6% of wages.
            s.get("_wages", 0) * 0.04 * s.get("_fed_marginal_rate", 0.37)
        ),

        "state_savings_fn": lambda s: (
            s.get("_wages", 0) * 0.04 * s.get("Q_STATE_MARGINAL_RATE", 0.09)
        ),

        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 5,

        "plain_english": (
            "Post-TCJA (2018+), employees can NO LONGER deduct unreimbursed business "
            "expenses on Schedule A — the miscellaneous itemized deduction was eliminated. "
            "This means any business expenses you pay personally (home office, continuing "
            "education, professional dues, auto mileage, phone) are completely non-deductible "
            "unless your S-Corp or partnership reimburses you under a formal accountable plan "
            "(Reg. §1.62-2). An accountable plan requires: (1) business purpose documentation, "
            "(2) expense substantiation within a reasonable period (typically 60 days), and "
            "(3) return of any excess reimbursements within 120 days. In a loss year, this is "
            "especially critical: personal business expenses flowing through the entity increase "
            "the entity's deductions (deepening the NOL), which has future value. Common "
            "uncaptured items: home office (§280A), auto mileage (§179), cell phone, "
            "professional subscriptions, and continuing education (§117/§132)."
        ),

        "documentation": [
            "Written accountable plan policy document (board-approved)",
            "Monthly expense reports with receipts/substantiation",
            "Mileage log (date, destination, business purpose, miles) — required §274 substantiation",
            "Home office calculation (Form 8829 or simplified method)",
        ],

        "cpa_handoff": [
            "Reimbursements under qualified accountable plan: excluded from W-2 wages AND from FICA (§3401(a)(19))",
            "Reimbursements NOT under accountable plan: included in W-2 wages and subject to FICA — costly error",
            "Key: plan must be in writing, expense reporting must be timely (60-day rule), excess returned (120-day rule)",
            "Home office: must be exclusive and regular use; simplified method = $5/sq ft up to 300 sq ft ($1,500 max)",
            "Auto: standard mileage rate (2024: 67¢/mile) OR actual expense method (depreciation + gas + insurance + repairs)",
            "Cell phone: if business-use >50%, deductible at business-use percentage",
            "Schedule this BEFORE year-end — can backdate for expenses paid during the year if plan was technically in place",
        ],

        "prerequisites": [
            "Adopt written accountable plan policy — board resolution or operating agreement amendment",
        ],
    },

    # ── QOZ — Qualified Opportunity Zone for Loss-Year Capital Gains ──────────
    {
        "id": "DTTS-237-qoz-loss-year-capital-gain-deferral",
        "name": "Qualified Opportunity Zone Investment — Capital Gain Deferral in Loss Year",
        "_id": "69c526fec2965eadfe41b327",
        "irc": "IRC §1400Z-1, §1400Z-2, §1400Z-2(b)(2)(B), Reg. §1.1400Z2(a)-1",
        "category": "Tax Loss Utilization",
        "overlap_group": "QOZ Investment",
        "applicable_forms": ["1040", "1120S", "1065"],
        "phase_1_eligible": True,
        "estimate_confidence": "MODERATE",

        "eligibility_logic": lambda s: (
            s.get("SIG_QOZ_LOSS_YEAR_PAIRING", False) and
            s.get("_capital_gains", 0) > 50_000
        ),

        "materiality_fn": lambda s: (
            85 if s.get("_capital_gains", 0) > 300_000 else
            72 if s.get("_capital_gains", 0) > 150_000 else
            58
        ),

        "fed_savings_fn": lambda s: (
            # QOZ defers capital gains tax for 5-10 years; in a loss year where NOL
            # exists, the strategic pairing is: use NOL to cover ordinary income,
            # defer LTCG via QOZ — net = no tax in loss year while preserving NOL
            # Savings = deferred tax × time value (10% discount for 5-year deferral)
            min(s.get("_capital_gains", 0), 1_000_000) *
            (0.20 + 0.038) * 0.10  # LTCG + NIIT rate × 10% time-value benefit
        ),

        "state_savings_fn": lambda s: 0.0,  # State conformity varies; conservative

        "speed_days": 180,
        "complexity": 45,
        "audit_friction": 20,

        "plain_english": (
            "If you have recognized capital gains in a year when your business also has "
            "an operating loss, a Qualified Opportunity Zone (QOZ) investment lets you "
            "defer (and potentially exclude) those capital gains. By investing the gain "
            "amount into a Qualified Opportunity Fund (QOF) within 180 days of the "
            "triggering sale, you defer federal tax on the original gain until December 31, "
            "2026 (or earlier disposition). Meanwhile, your business NOL offsets ordinary "
            "income while the capital gain tax is deferred — effectively a two-pronged "
            "deferral. If the QOF investment is held for 10+ years, the appreciation on "
            "the QOF investment itself is EXCLUDED from income entirely. The original "
            "deferred gain is recognized in 2026 (or earlier), but your NOL carryforward "
            "may be available to partially offset it. This pairing requires coordinated "
            "timing of the QOF investment, NOL utilization projection, and 2026 deferral "
            "income recognition planning."
        ),

        "documentation": [
            "QOF subscription agreement and Form 8996 (QOF self-certification)",
            "Form 8949 — deferral election (sale of asset, gain invested in QOF within 180 days)",
            "Form 8997 — Initial and Annual Statement of QOZ Business Investments",
            "QOF offering memorandum confirming 90% qualified property test",
            "Investment date confirmation (180-day reinvestment window from triggering sale)",
        ],

        "cpa_handoff": [
            "180-day reinvestment window from the date of sale — partnership K-1 gains have extended window to invest",
            "Form 8949 deferral election: must be made with the tax return for the year of the triggering sale",
            "Original gain recognized: December 31, 2026 (legislation pending extension) or earlier QOF disposition",
            "10-year hold: appreciation in QOF interest excluded from income under §1400Z-2(c)",
            "Basis: QOF interest basis = $0 initially; increases to FMV at recognition date if held 10+ years",
            "NOL pairing: project 2026 income including deferred QOZ gain — NOL carryforward may offset a portion",
            "State conformity: only ~40 states conform to federal QOZ rules — verify state-level deferral availability",
        ],

        "prerequisites": [
            "Capital gain realized in 2024 (triggering event must have occurred)",
            "Identify qualifying QOF within 180 days of triggering sale",
        ],
    },

    # ── §382 Ownership Change — NOL Limitation Warning ───────────────────────
    {
        "id": "DTTS-238-382-nol-ownership-change",
        "name": "§382 NOL Limitation — Ownership Change Risk Assessment",
        "_id": "69c5273dc2965eadfe41b350",
        "irc": "IRC §382, §382(a), §382(b), §382(l)(3), Reg. §1.382-2T",
        "category": "Tax Loss Utilization",
        "overlap_group": "Loss Strategies",
        "applicable_forms": ["1120", "1120S"],
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",

        "eligibility_logic": lambda s: (
            s.get("SIG_382_OWNERSHIP_CHANGE_RISK", False) and
            s.get("SIG_NOL_CARRYOVER", False) and
            s.get("_nol_total_pool", 0) > 50_000
        ),

        "materiality_fn": lambda s: (
            95 if s.get("_nol_total_pool", 0) > 500_000 else
            85 if s.get("_nol_total_pool", 0) > 200_000 else
            70
        ),

        "fed_savings_fn": lambda s: (
            # §382 exposure = value of NOL that could be permanently limited
            # If ownership change occurred, annual NOL use = FMV × long-term tax-exempt rate (~4.5% 2024)
            # Simplified: warn that 70% of NOL value may be permanently restricted
            s.get("_nol_total_pool", 0) *
            s.get("_loss_tax_rate", 0.32) * 0.70  # protective value = preserve NOL from §382 loss
        ),

        "state_savings_fn": lambda s: 0.0,

        "speed_days": 30,
        "complexity": 40,
        "audit_friction": 10,

        "plain_english": (
            "§382 is one of the most dangerous traps for businesses with accumulated losses. "
            "If ownership of a corporation changes by more than 50 percentage points within a "
            "rolling 3-year period, the annual amount of pre-change NOL that can offset "
            "post-change income is permanently capped. The cap is calculated as: "
            "(FMV of company on the change date) × (long-term tax-exempt rate, ~4.5% in 2024). "
            "For a practice worth $2 million, the annual NOL utilization cap would be roughly "
            "$90,000/year — meaning a $500,000 NOL would take over 5 years to absorb, "
            "dramatically reducing its present value. Triggering events include: partner "
            "buyouts, new investor admissions (even small equity sales to third parties), "
            "practice acquisitions, ESOP transactions, and even certain debt-to-equity "
            "conversions. CRITICAL: assess §382 BEFORE any ownership transaction, not after."
        ),

        "documentation": [
            "§382 ownership change analysis (5% shareholder tracking over rolling 36 months)",
            "Stock transfer records and cap table history (3-year look-back period)",
            "FMV appraisal of corporation on the ownership change date",
            "§382 annual limitation computation: FMV × long-term tax-exempt rate",
            "Segregation of pre-change and post-change NOLs",
        ],

        "cpa_handoff": [
            "§382 applies to corporations (C-Corp and S-Corp) — partnerships under §704 rules",
            "5% shareholder rule: track all shareholders owning 5%+ of stock; aggregate smaller holders as 'public group'",
            "Ownership change: >50 percentage point shift in 5% shareholders within 3 years = triggering event",
            "Annual §382 limitation: FMV of old loss corporation × applicable federal rate (long-term tax-exempt rate)",
            "Built-in gains/losses (§382(h)): if company has net built-in gain at change date, §382 limit increased for 5 years",
            "Section 382(l)(5): bankruptcy exception — no annual limit if pre-change loss corporation emerges from Chapter 11",
            "Assess BEFORE any practice sale, partner admission, ESOP, or equity financing transaction",
        ],

        "prerequisites": [
            "Review 3-year ownership transfer history BEFORE recommending any equity transactions",
            "Obtain cap table or shareholder records for 36-month look-back",
        ],
    },

    # ── R&D Payroll Tax Credit in Loss Year (§41) ─────────────────────────────
    {
        "id": "DTTS-239-rd-payroll-offset-loss-year",
        "name": "R&D Tax Credit — Payroll Tax Offset for Loss-Year Startups (§41)",
        "_id": "69c527f6c2965eadfe41b379",
        "irc": "IRC §41, §41(h), §3111(f), IRS Form 6765",
        "category": "Tax Credits",
        "overlap_group": "R&D Tax Credit",
        "applicable_forms": ["1040", "1120", "1120S", "1065"],
        "phase_1_eligible": True,
        "estimate_confidence": "MODERATE",

        "eligibility_logic": lambda s: (
            s.get("SIG_41_RD_PAYROLL_OFFSET", False) and
            s.get("_wages", 0) > 50_000
        ),

        "materiality_fn": lambda s: (
            85 if s.get("_wages", 0) > 200_000 else
            70 if s.get("_wages", 0) > 100_000 else
            55
        ),

        "fed_savings_fn": lambda s: (
            # §41(h) credit: up to $250,000 ($500K for 2023+ per IRA) against employer payroll taxes
            # Gross credit = qualified research wages × 20% (simplified method: fixed-base% × gross receipts)
            # Eligible startups: <5 years old, gross receipts <$5M
            min(s.get("_wages", 0) * 0.06, 250_000)  # ~6% of QRW as credit proxy; capped at $250K
        ),

        "state_savings_fn": lambda s: (
            min(s.get("_wages", 0) * 0.03, 100_000) * 0.40  # state R&D credit availability varies
        ),

        "speed_days": 60,
        "complexity": 35,
        "audit_friction": 25,

        "plain_english": (
            "The §41 Research & Development (R&D) Tax Credit normally offsets income tax — "
            "useless in a loss year when there's no income tax to offset. However, §41(h) "
            "allows qualified small businesses (gross receipts < $5M and in business < 5 years) "
            "to elect to use up to $250,000 ($500,000 after 2022 IRA amendments) of the R&D "
            "credit against EMPLOYER PAYROLL TAXES (the employer's share of FICA). This is "
            "real cash — not a deferred asset. Qualifying research activities for dental "
            "practices may include: development of new clinical protocols, software customization "
            "for practice management, clinical trials, dental technology integration projects, "
            "or novel treatment methodology development. The activities must be technological "
            "in nature, have a permitted purpose (improve function/performance/quality), "
            "involve elimination of uncertainty, and follow a process of experimentation."
        ),

        "documentation": [
            "Form 6765 — Credit for Increasing Research Activities",
            "Contemporaneous research project documentation (project descriptions, personnel time allocation)",
            "Time tracking records for employees performing qualified research",
            "Qualified research expense (QRE) calculation: wages + supplies + contract research × 65%",
            "4-part test analysis for each claimed research activity (technological, permitted purpose, uncertainty, experimentation)",
        ],

        "cpa_handoff": [
            "Payroll tax offset election: made on Form 8974 — elected on Form 6765, Line 44 on original return (cannot amend)",
            "2024 limit: $250,000/year against employer FICA; $500,000 if business qualifies under IRA rules",
            "Eligible startup: ≤5 years old AND gross receipts ≤$5M for current year AND prior 5 years",
            "Credit calculation: 20% × (QRE − base amount); simplified credit = 14% × QREs above 50% of 3-yr avg",
            "Documentation critical: courts and IRS require contemporaneous records for §41 claims",
            "Dental R&D examples: clinical trial for new procedure, EMR system customization, 3D printing dental device development",
            "Note: pure discovery (academic research), market research, and post-commercial development do NOT qualify",
        ],

        "prerequisites": [
            "Confirm business is ≤5 years old with gross receipts ≤$5M",
            "Document qualifying research activities BEFORE claiming credit",
        ],
    },

    # ── Qualified Improvement Property (QIP) — Loss Year Depreciation ─────────
    {
        "id": "DTTS-240-qip-loss-year",
        "name": "Qualified Improvement Property (QIP) — Depreciation in Loss Year",
        "_id": "69c52831c2965eadfe41b397",
        "irc": "IRC §168(e)(6), §168(k), §179, CARES Act §2307",
        "category": "Tax Loss Utilization",
        "overlap_group": "Loss Strategies — Depreciation",
        "applicable_forms": ["1120S", "1120", "1065"],
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",

        "eligibility_logic": lambda s: (
            s.get("SIG_QIP_OPPORTUNITY", False) and
            s.get("_planning_mode") == "LOSS" and
            (s.get("_depreciation", 0) > 0 or s.get("SIG_HAS_DEPRECIATION", False))
        ),

        "materiality_fn": lambda s: (
            82 if s.get("_depreciation", 0) > 150_000 else
            68 if s.get("_depreciation", 0) > 75_000 else
            52
        ),

        "fed_savings_fn": lambda s: (
            # QIP insight: in a loss year, consider whether QIP was
            # assigned correct 15-year life (vs 39-year non-residential)
            # Reclassification from 39-yr to 15-yr = accelerated deduction
            # Even in loss year, QIP that should have been 15-yr MACRS adds to NOL value
            s.get("_depreciation", 0) * 0.30 *  # ~30% of total dep may be misclassified QIP
            s.get("_loss_tax_rate", 0.32) * 0.80  # 80% of tax value preserved via NOL
        ),

        "state_savings_fn": lambda s: (
            s.get("_depreciation", 0) * 0.30 *
            s.get("Q_STATE_MARGINAL_RATE", 0.09) * 0.50
        ),

        "speed_days": 30,
        "complexity": 25,
        "audit_friction": 10,

        "plain_english": (
            "Qualified Improvement Property (QIP) — interior improvements to nonresidential "
            "real property after it's first placed in service — was fixed by the CARES Act "
            "in 2020 to qualify for 15-year MACRS with 60% bonus depreciation (2024). "
            "Before the fix (pre-2020), QIP was mistakenly assigned a 39-year life, meaning "
            "taxpayers who made improvements before 2020 may have over $50,000–$300,000 of "
            "uncorrected depreciation sitting on their fixed asset schedule at the wrong life. "
            "In a loss year, reclassifying QIP from 39-year to 15-year and claiming the "
            "accelerated deduction deepens the current NOL — which carries forward at full "
            "value. Alternatively, a §481(a) automatic accounting method change (Form 3115) "
            "can catch up all missed QIP depreciation in a SINGLE year. For a dental practice "
            "with $500K of leasehold improvements placed in service between 2018 and 2020, "
            "the catch-up deduction from a Form 3115 could be $100K–$200K or more."
        ),

        "documentation": [
            "Form 3115 — Application for Change in Accounting Method (automatic consent #7 for QIP reclassification)",
            "Fixed asset register with placed-in-service dates and current depreciation lives",
            "Cost segregation study or engineering analysis identifying QIP vs. structural components",
            "Building lease and landlord consent if leasehold improvements",
        ],

        "cpa_handoff": [
            "QIP definition: interior improvement to existing nonresidential real property, not enlargement/elevator/escalator/internal structural framework",
            "15-year MACRS (150% DB) + 60% bonus depreciation in 2024 (decreasing 20%/yr through 2027)",
            "Form 3115 automatic consent #7: catch-up missed QIP depreciation; §481(a) adjustment in year of change",
            "CARES Act retroactive fix: applies to QIP placed in service after 12/31/2017 — prior-year returns can be amended",
            "In loss year: §481(a) catch-up deduction increases current-year NOL (full value preserved for future utilization)",
            "Cost segregation: look for 5-year and 7-year personal property that was lumped into 39-year building cost at purchase",
            "§179 limitation: QIP qualifies for §179 but cannot create/increase a loss — use bonus depreciation instead",
        ],

        "prerequisites": [
            "Review fixed asset schedule for 39-year property that may qualify as QIP",
            "Confirm QIP placed in service after 12/31/2017",
        ],
    },

]