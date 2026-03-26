from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-083-prepaid-expenses-via-management-company",
        "name": "Prepaid Expenses via Management Company",
        "irc": "IRC §461, §461(h), §461(h)(3)(A), §482, §162, Treas. Reg. §1.263(a)-4(f)",
        "category": "Entity & Structuring",
        "overlap_group": "Management Company",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_MULTI_ENTITY", False)
        and s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False),
        "materiality_fn": lambda s: (
            45
            if s.get("SIG_MULTI_ENTITY", False)
            and s.get("SIG_HIGH_TAX_LIABILITY", False)
            else 25
        ),
        "fed_savings_fn": lambda s: s.get("Q_MGMT_CO_REVENUE", 0)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("Q_MGMT_CO_REVENUE", 0)
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 14,
        "complexity": 20,
        "audit_friction": 15,
        "plain_english": "A dentist with a management company structure can prepay management fees before year-end and deduct them in the current tax year under the 12-month rule — as long as the benefit period does not extend beyond 12 months from the first date of benefit and does not cross into the second tax year following payment. This accelerates the deduction by 12 months, reducing current-year taxable income at the cost of a smaller deduction next year. The management company (typically on the cash method) recognizes the fee as income when received — but if the management company has its own deductible expenses or lower effective tax rate, there may be a combined tax benefit. The management fee must reflect actual arm's-length value of services provided — the IRS can reallocate income under §482 if the fee is set arbitrarily to shift income between related entities.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-131-management-company-set-up-as-a-c-corporation",
        "name": "Management Company Set up as a C-corporation",
        "irc": "IRC §482, Treas. Reg. §301.7701-3, IRC §11, §162, §351",
        "category": "Entity & Structuring",
        "overlap_group": "Management Company",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HAS_S_CORP_VERIFIED", False)
        and s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False),
        "materiality_fn": lambda s: (
            60
            if s.get("SIG_VERY_HIGH_INCOME", False)
            and s.get("SIG_HAS_S_CORP_VERIFIED", False)
            else 35
        ),
        "fed_savings_fn": lambda s: s.get("Q_MGMT_CO_REVENUE", 0)
        * max(0, s.get("_fed_marginal_rate", 0) - 0.21),
        "state_savings_fn": lambda s: s.get("Q_MGMT_CO_REVENUE", 0)
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 60,
        "complexity": 45,
        "audit_friction": 20,
        "plain_english": "A C-corporation management company allows a dental practice to split income between the operating practice (usually an S-Corp) and a separately owned C-Corporation that provides genuine management, administrative, and support services. The dental practice pays arm's-length management fees to the C-Corp — these fees are deductible to the practice, reducing the income that flows through to the dentist at 37%. The C-Corp retains those management fees at the flat 21% corporate tax rate, a significant rate differential. The retained earnings inside the C-Corp can then be used to fund executive life insurance, non-qualified deferred compensation plans, or other corporate benefits. The critical risk is double taxation: money retained in the C-Corp and eventually distributed as dividends is taxed again at 20% — so the long-term exit strategy must be planned carefully. The management fees must also be genuinely arm's-length and supportable under §482, not inflated amounts designed purely to shift income.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-175-family-management-company",
        "name": "Family Management Company",
        "irc": "IRC §162",
        "category": "Entity & Income Structuring",
        "overlap_group": "Management Company",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_DEPENDENTS_PRESENT", False),
        "materiality_fn": lambda s: (
            90
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 75 if s.get("SIG_HIGH_INCOME") else 60
        ),
        "fed_savings_fn": lambda s: s.get("Q_C_CORP_RETAINED_EARNINGS", 40000)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 40000
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 90,
        "complexity": 40,
        "audit_friction": 20,
        "plain_english": "A family management company can centralize administrative services for multiple related businesses and allow income shifting among family members when structured properly.",
        "prerequisites": ["Multiple related business entities"],
    },
    {
        "id": "DTTS-176-management-company",
        "name": "Management Company Structure",
        "irc": "IRC §162",
        "category": "Entity & Income Structuring",
        "overlap_group": "Management Company",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and (s.get("SIG_MULTI_ENTITY", False) or s.get("Q_MGMT_CO_REVENUE", 0) > 0),
        "materiality_fn": lambda s: (
            85
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 70 if s.get("SIG_HIGH_INCOME") else 55
        ),
        "fed_savings_fn": lambda s: s.get("Q_MGMT_CO_REVENUE", 30000)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 30000
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 60,
        "complexity": 35,
        "audit_friction": 15,
        "plain_english": "A management company can provide administrative and operational services to operating entities, allowing centralized expense management and potential tax planning opportunities.",
        "prerequisites": ["Operating business entity"],
    }
]