from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-018-hiring-spouse-in-the-business",
        "name": "Hiring Spouse in the Business",
        "irc": "IRC §162, §3121(b)(3), §3306(c)(5), §401(k), §106",
        "category": "General Planning",
        "overlap_group": "Family Employment",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and (
            s.get("_filing_status", "S")
            in ("MFJ", "MARRIED FILING JOINTLY", "MFS", "MARRIED FILING SEPARATELY")
        )
        and (
            s.get("Q_COMMUNITY_PROPERTY_APPLICABLE", False)
            or (s.get("_wages", 0) > 0 and s.get("SIG_HIGH_INCOME", False))
        ),
        "materiality_fn": lambda s: (
            65
            if s.get("SIG_HIGH_INCOME", False)
            and s.get("SIG_HAS_S_CORP_VERIFIED", False)
            else 50
        ),
        "fed_savings_fn": lambda s: min(s.get("_wages", 0) * 0.3, 60000)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: min(s.get("_wages", 0) * 0.3, 60000)
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 21,
        "complexity": 15,
        "audit_friction": 20,
        "plain_english": "If your spouse performs real work for the dental practice — managing the schedule, handling billing, running the front desk, or providing administrative support — they should be on the payroll as a W-2 employee. This creates multiple tax benefits: their wages are deductible to the business, they can participate in the 401(k) and profit sharing plans with their own contribution limits, and the practice can provide health insurance and other benefits at full deductibility. The spouse's role must be genuine with documented services and reasonable compensation — the IRS scrutinizes spousal employment arrangements carefully.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires related-party role, compensation, and documentation review before implementation.",
        ],
    },
    {
        "id": "DTTS-040-hire-children-under-18",
        "name": "Hire Children Under 18",
        "irc": "IRC §162, §3121(b)(3)(A), §3306(c)(5), §73, §1(g)",
        "category": "General Planning",
        "overlap_group": "Family Employment",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_DEPENDENTS_PRESENT", False)
        and s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False),
        "materiality_fn": lambda s: (
            65
            if s.get("SIG_SCHEDULE_C_PRESENT", False)
            and s.get("SIG_HIGH_TAX_LIABILITY", False)
            else (
                50
                if s.get("SIG_DEPENDENTS_PRESENT", False)
                and s.get("SIG_HIGH_INCOME", False)
                else 35
            )
        ),
        "fed_savings_fn": lambda s: s.get("Q_HIRING_CHILDREN_WAGES", 0)
        * s.get("_fed_marginal_rate", 0)
        + s.get("Q_FICA_SAVINGS_CHILDREN", 0),
        "state_savings_fn": lambda s: s.get("Q_HIRING_CHILDREN_WAGES", 0)
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 14,
        "complexity": 15,
        "audit_friction": 20,
        "plain_english": "A dentist who owns their practice can hire their own children to perform real, documented work — and deduct the wages as an ordinary business expense. The child pays tax at their own lower rate, and their standard deduction ($14,600 in 2024) shelters the first $14,600 of wages from income tax entirely — so the family keeps more of what the practice earns. If the practice is structured as a sole proprietorship or a partnership owned entirely by the parents, wages paid to children under 18 are also exempt from FICA and FUTA — saving an additional 15.3% in payroll taxes. S-Corporations do not get this FICA exemption. The work must be real and the pay must be reasonable — the IRS scrutinizes this closely, so documented job descriptions, timesheets, and actual payment records are essential. Bonus: the child's earned wages can fund a Roth IRA.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires related-party role, compensation, and documentation review before implementation.",
        ],
    }
]