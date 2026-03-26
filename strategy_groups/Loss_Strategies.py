from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-227-nol-carryforward",
        "name": "Net Operating Loss (NOL) Carryforward",
        "irc": "IRC §172",
        "category": "Tax Loss Utilization",
        "overlap_group": "Loss Strategies",
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",
        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_S_CORP", False)
            or s.get("SIG_HAS_C_CORP", False)
            or s.get("SIG_BUSINESS_PRESENT", False)
        )
        and s.get("_obi", 0) < 0,
        "materiality_fn": lambda s: (
            95
            if abs(s.get("_obi", 0)) > 100000
            else (
                80
                if abs(s.get("_obi", 0)) > 50000
                else 60 if abs(s.get("_obi", 0)) > 10000 else 40
            )
        ),
        "fed_savings_fn": lambda s: abs(s.get("_obi", 0))
        * s.get("_fed_marginal_rate", 0.24)
        * 0.3,
        "state_savings_fn": lambda s: abs(s.get("_obi", 0))
        * s.get("Q_STATE_MARGINAL_RATE", 0.05)
        * 0.2,
        "speed_days": 14,
        "complexity": 15,
        "audit_friction": 5,
        "plain_english": "This business has a net operating loss (NOL) of ${_obi:,.0f} for the tax year. This loss can be carried forward indefinitely to offset future taxable income, reducing future tax liability. At a {_fed_marginal_rate:.0%} marginal rate, this loss represents approximately ${_nol_amount:,.0f} in future tax savings.",
        "prerequisites": [
            "Net operating loss in current year",
            "Track NOL for future utilization",
        ],
    },
    {
        "id": "DTTS-228-1366d-basis-optimization",
        "name": "IRC §1366(d) Shareholder Basis Limitation Optimization",
        "irc": "IRC §1366(d)",
        "category": "Entity Structure",
        "overlap_group": "Loss Strategies",
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",
        "eligibility_logic": lambda s: (
            s.get("SIG_1366D_BASIS_REVIEW", False)
            and s.get("_planning_mode") == "LOSS"
            and s.get("_entity_has_s_corp", False)
        ),
        "materiality_fn": lambda s: (
            90 if s.get("_loss_value", 0) > 50_000
            else 75 if s.get("_loss_value", 0) > 20_000
            else 55
        ),
        "fed_savings_fn": lambda s: s.get("_loss_value", 0) * 0.50,
        "state_savings_fn": lambda s: s.get("_loss_value", 0) * 0.05,
        "speed_days": 30,
        "complexity": 35,
        "audit_friction": 15,
        "plain_english": (
            "S-Corp losses passed through to shareholders are limited to the shareholder's "
            "adjusted basis in stock and debt under IRC §1366(d). Documenting and maximizing "
            "basis through loans or additional capital contributions can unlock the full "
            "deductibility of current-year losses, preserving significant tax value."
        ),
        "prerequisites": [
            "Confirm shareholder basis schedule is current",
            "Document any shareholder loans to the S-Corp",
            "Review capital contributions made during the year",
        ],
    },
    {
        "id": "DTTS-229-465-at-risk-review",
        "name": "IRC §465 At-Risk Limitation Review",
        "irc": "IRC §465",
        "category": "Entity Structure",
        "overlap_group": "Loss Strategies",
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",
        "eligibility_logic": lambda s: (
            s.get("SIG_465_AT_RISK_REVIEW", False)
            and s.get("_planning_mode") == "LOSS"
            and (s.get("_entity_has_s_corp", False) or s.get("_entity_has_partnership", False))
        ),
        "materiality_fn": lambda s: (
            80 if s.get("_loss_value", 0) > 30_000
            else 60 if s.get("_loss_value", 0) > 10_000
            else 45
        ),
        "fed_savings_fn": lambda s: s.get("_loss_value", 0) * 0.175,
        "state_savings_fn": lambda s: s.get("_loss_value", 0) * 0.025,
        "speed_days": 15,
        "complexity": 25,
        "audit_friction": 10,
        "plain_english": (
            "Pass-through losses may be limited by at-risk rules under IRC §465. "
            "Reviewing the shareholder's at-risk amount — including amounts borrowed "
            "for which the shareholder is personally liable — can expand deductible "
            "loss beyond the current limitation."
        ),
        "prerequisites": [
            "Obtain Form 6198 (At-Risk Limitations) if applicable",
            "Document shareholder recourse vs. non-recourse debt",
            "Confirm amounts at-risk at year-end",
        ],
    },
    {
        "id": "DTTS-230-469-pal-release",
        "name": "IRC §469 Passive Activity Loss Release Strategy",
        "irc": "IRC §469",
        "category": "Entity Structure",
        "overlap_group": "Loss Strategies",
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",
        "eligibility_logic": lambda s: (
            s.get("SIG_469_PAL_REVIEW", False)
            and s.get("_planning_mode") == "LOSS"
            and (s.get("_entity_has_s_corp", False) or s.get("_entity_has_partnership", False))
        ),
        "materiality_fn": lambda s: (
            85 if s.get("_loss_value", 0) > 40_000
            else 65 if s.get("_loss_value", 0) > 15_000
            else 50
        ),
        "fed_savings_fn": lambda s: s.get("_loss_value", 0) * 0.275,
        "state_savings_fn": lambda s: s.get("_loss_value", 0) * 0.04,
        "speed_days": 45,
        "complexity": 40,
        "audit_friction": 20,
        "plain_english": (
            "If the S-Corp or partnership activity is classified as passive for the shareholder, "
            "the operating loss is suspended until passive income exists or the activity is "
            "disposed. Establishing material participation or restructuring activity classification "
            "can release suspended losses and unlock their full tax value."
        ),
        "prerequisites": [
            "Document hours of material participation in the activity",
            "Review passive activity loss carryforward schedule",
            "Confirm taxpayer meets one of the seven material participation tests",
        ],
    },
    {
        "id": "DTTS-231-168-depreciation-timing",
        "name": "IRC §168/§168(k) Depreciation Timing Optimization",
        "irc": "IRC §168, §168(k)",
        "category": "Depreciation",
        "overlap_group": "Loss Strategies",
        "phase_1_eligible": True,
        "estimate_confidence": "MEDIUM",
        "eligibility_logic": lambda s: (
            s.get("SIG_168_DEPRECIATION_TIMING", False)
            and s.get("_planning_mode") in ("LOSS", "INCOME")
            and (
                s.get("_entity_has_s_corp", False)
                or s.get("_entity_has_partnership", False)
                or s.get("_entity_has_c_corp", False)
            )
        ),
        "materiality_fn": lambda s: (
            75 if (s.get("_depreciation", 0) or 0) > 50_000
            else 55 if (s.get("_depreciation", 0) or 0) > 15_000
            else 40
        ),
        "fed_savings_fn": lambda s: (s.get("_depreciation", 0) or 0) * 0.05,
        "state_savings_fn": lambda s: (s.get("_depreciation", 0) or 0) * 0.015,
        "speed_days": 60,
        "complexity": 30,
        "audit_friction": 12,
        "plain_english": (
            "With depreciation already claimed this year, reviewing the timing of future "
            "depreciation elections — including bonus depreciation under IRC §168(k) — "
            "can accelerate deductions into higher-income years or defer them to years "
            "when the entity returns to profitability, maximizing the tax value of each dollar."
        ),
        "prerequisites": [
            "Review Form 4562 depreciation schedule",
            "Identify assets eligible for bonus depreciation",
            "Confirm placed-in-service dates and applicable recovery periods",
        ],
    },
    {
        "id": "DTTS-232-accountable-plan",
        "name": "Reg. §1.62-2 Accountable Plan Implementation",
        "irc": "IRC §62, Reg. §1.62-2",
        "category": "Compensation",
        "overlap_group": "Loss Strategies",
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",
        "eligibility_logic": lambda s: (
            s.get("SIG_ACCOUNTABLE_PLAN", False)
            and s.get("_entity_has_s_corp", False)
        ),
        "materiality_fn": lambda s: 60,
        "fed_savings_fn": lambda s: 1_750,
        "state_savings_fn": lambda s: 250,
        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 5,
        "plain_english": (
            "Owner-employees reimbursed for business expenses under an IRS-compliant accountable "
            "plan receive reimbursements tax-free and the corporation deducts them. This reduces "
            "FICA on the reimbursement amounts and improves the deductible expense base, "
            "benefiting both income and loss years."
        ),
        "prerequisites": [
            "Adopt a written accountable plan reimbursement policy",
            "Require adequate substantiation (receipts) for all reimbursements",
            "Ensure timely return of excess reimbursements",
        ],
    },
    {
        "id": "DTTS-233-172-nol-c-corp",
        "name": "IRC §172 Net Operating Loss Carryforward Planning (C-Corp)",
        "irc": "IRC §172",
        "category": "Loss Optimization",
        "overlap_group": "Loss Strategies",
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",
        "eligibility_logic": lambda s: (
            s.get("SIG_172_NOL_CARRYFORWARD", False)
            and s.get("_planning_mode") == "LOSS"
            and s.get("_entity_has_c_corp", False)
        ),
        "materiality_fn": lambda s: (
            90 if s.get("_loss_value", 0) > 50_000
            else 75 if s.get("_loss_value", 0) > 20_000
            else 55
        ),
        "fed_savings_fn": lambda s: s.get("_loss_value", 0) * 0.60,
        "state_savings_fn": lambda s: s.get("_loss_value", 0) * 0.025,
        "speed_days": 30,
        "complexity": 20,
        "audit_friction": 8,
        "plain_english": (
            "A C-Corporation with a current-year net operating loss may carry the NOL forward "
            "indefinitely to offset future taxable income under IRC §172 (80% of taxable income "
            "limit per year). Proper NOL tracking, election planning, and documentation ensures "
            "full utilization of the tax benefit in future profitable years."
        ),
        "prerequisites": [
            "Document current-year NOL amount on Form 1120",
            "Establish NOL tracking schedule for carryforward utilization",
            "Consider §382 limitation analysis if ownership changes are anticipated",
        ],
    },
    {
        "id": "DTTS-234-704d-partner-basis",
        "name": "IRC §704(d) Partner Basis Limitation Review",
        "irc": "IRC §704(d)",
        "category": "Entity Structure",
        "overlap_group": "Loss Strategies",
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",
        "eligibility_logic": lambda s: (
            s.get("SIG_704D_BASIS_REVIEW", False)
            and s.get("_planning_mode") == "LOSS"
            and s.get("_entity_has_partnership", False)
        ),
        "materiality_fn": lambda s: (
            85 if s.get("_loss_value", 0) > 40_000
            else 65 if s.get("_loss_value", 0) > 15_000
            else 45
        ),
        "fed_savings_fn": lambda s: s.get("_loss_value", 0) * 0.45,
        "state_savings_fn": lambda s: s.get("_loss_value", 0) * 0.04,
        "speed_days": 30,
        "complexity": 35,
        "audit_friction": 15,
        "plain_english": (
            "Partnership losses allocated to a partner are deductible only to the extent of "
            "the partner's adjusted basis in the partnership interest under IRC §704(d). "
            "Reviewing and documenting basis — including increases from partner loans and "
            "capital contributions — can maximize the currently deductible portion of allocated losses."
        ),
        "prerequisites": [
            "Obtain partner basis schedule (outside basis)",
            "Document any partner loans to the partnership",
            "Review Schedule K-1 Box 1 loss allocation vs. basis",
        ],
    },
]
