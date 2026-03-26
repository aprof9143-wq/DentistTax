from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-072-entity-classification-election-check-the-box",
        "name": "Entity Classification Election (Check-the-Box)",
        "irc": "Treas. Reg. §301.7701-3, §301.7701-2, §301.7701-3(c), IRC §482",
        "category": "Entity & Structuring",
        "overlap_group": "Entity Conversion",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_MULTI_ENTITY", False)
        and s.get("SIG_HIGH_INCOME", False)
        and (s.get("SIG_HAS_PARTNERSHIP", False) or s["SIG_K1_PRESENT"]),
        "materiality_fn": lambda s: (
            55
            if s.get("SIG_MULTI_ENTITY", False) and s.get("SIG_HIGH_INCOME", False)
            else 30
        ),
        "fed_savings_fn": lambda s: s.get("_obi", 0) * 0.15 * 0.153 * 0.9235,
        "state_savings_fn": lambda s: 0,
        "speed_days": 30,
        "complexity": 35,
        "audit_friction": 15,
        "plain_english": "The check-the-box election allows an LLC or other eligible business entity to choose how it is taxed for federal purposes — as a sole proprietorship (disregarded), partnership, C-Corporation, or S-Corporation. For dentists with multi-entity structures, this is a powerful restructuring tool: a partnership can be converted to an S-Corporation to access payroll tax savings, or to a C-Corporation to enable QSBS planning or retained earnings at the 21% corporate rate. Single-member LLCs currently filing as disregarded entities can elect S-Corp treatment — combined with a reasonable salary — to shield a portion of practice income from self-employment taxes. The election is filed on Form 8832 and can be made retroactive up to 75 days, allowing prior-year fixes. Important: changing an entity's classification can trigger deemed tax events — full modeling required before filing.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-142-schedule-c-to-scorp",
        "name": "Schedule C → S-Corp Conversion (SE Tax Protection)",
        "irc": "IRC §1361-1362, §1402",
        "category": "Entity & Income Structuring",
        "overlap_group": "Entity Conversion",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_SCHEDULE_C_PRESENT", False)
        and s.get("_obi", 0) > 80000,
        "materiality_fn": lambda s: (
            100
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 85 if s.get("SIG_HIGH_INCOME") else 70
        ),
        "fed_savings_fn": lambda s: max(0, s.get("_obi", 0) * 0.6) * 0.153,
        "state_savings_fn": lambda s: 0,
        "speed_days": 60,
        "complexity": 30,
        "audit_friction": 10,
        "plain_english": "Operating as a Schedule C exposes all business profit to self-employment tax. Converting to an S-Corporation allows part of the profit to be taken as distributions instead of wages, reducing payroll tax exposure.",
        "prerequisites": [
            "Business income typically above $80K",
            "State licensing board approval may be required",
        ],
    },
    {
        "id": "DTTS-143-s-corp-to-c-corp-profit-protection",
        "name": "S-Corporation to C-Corp (Profit Protection Strategy)",
        "irc": "IRC §11, §301",
        "category": "Entity & Income Structuring",
        "overlap_group": "Entity Conversion",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and (not s.get("SIG_HAS_S_CORP_VERIFIED", False)),
        "materiality_fn": lambda s: (
            75
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 60 if s.get("SIG_HIGH_INCOME") else 45
        ),
        "fed_savings_fn": lambda s: s.get("Q_MGMT_CO_REVENUE", 40000)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 10000
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 90,
        "complexity": 40,
        "audit_friction": 15,
        "plain_english": "In some cases, converting an S-corporation to a C-corporation can allow profits to be retained at the corporate tax rate rather than flowing through to the owner's individual tax return.",
        "prerequisites": ["Significant retained earnings expected"],
    }
]