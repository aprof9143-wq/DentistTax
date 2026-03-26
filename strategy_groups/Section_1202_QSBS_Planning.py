from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-048-1202-gain-exclusion-stacking-via-multiple-entities",
        "name": "1202 Gain Exclusion Stacking via Multiple Entities",
        "irc": "IRC §1202, §1202(a), §1202(b), §1202(c), §1202(e), §1202(h)",
        "category": "General Planning",
        "overlap_group": "Section 1202 (QSBS) Planning",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_HAS_C_CORP", False)
        and s.get("SIG_MULTI_ENTITY", False)
        and s.get("SIG_VERY_HIGH_INCOME", False),
        "materiality_fn": lambda s: (
            75
            if s.get("SIG_HAS_C_CORP", False)
            and s.get("SIG_MULTI_ENTITY", False)
            and s.get("SIG_VERY_HIGH_INCOME", False)
            else 40
        ),
        "fed_savings_fn": lambda s: 10000000 * 0.238 * 0.2,
        "state_savings_fn": lambda s: 0,
        "speed_days": 180,
        "complexity": 65,
        "audit_friction": 30,
        "plain_english": "Section 1202 allows investors in qualifying small business C-Corporation stock to exclude up to 100% of their capital gains from federal tax — up to $10 million per taxpayer per issuing company. The 'stacking' strategy multiplies this exclusion by transferring shares to a spouse, children, or trusts — each of whom gets their own $10 million exclusion limit for the same stock. For a dentist who structures a non-clinical management company or real estate entity as a C-Corporation and eventually sells it, this exclusion can eliminate millions in capital gains taxes entirely. The key requirements are that the stock must be originally issued (not purchased on the secondary market), the corporation's gross assets must be under $50 million at issuance, and the stock must be held for more than five years. Important caveat: dental practices as health service businesses may be excluded — non-clinical entities in the structure are more likely to qualify.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    }
]