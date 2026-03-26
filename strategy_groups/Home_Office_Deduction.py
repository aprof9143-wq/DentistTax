from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-073-business-use-of-home-by-partner",
        "name": "Business Use of Home by Partner",
        "irc": "IRC §162, §280A, §280A(c)(1), §280A(c)(6), §167, §168",
        "category": "General Planning",
        "overlap_group": "Home Office Deduction",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HAS_PARTNERSHIP", False)
        and s["SIG_K1_PRESENT"]
        and s.get("SIG_HIGH_INCOME", False),
        "materiality_fn": lambda s: (
            40
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HAS_PARTNERSHIP")
            else 20 if s.get("SIG_HIGH_INCOME") or s.get("SIG_HAS_PARTNERSHIP") else 15
        ),
        "fed_savings_fn": lambda s: s.get("_agi", 0)
        * 0.005
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("_agi", 0)
        * 0.005
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 20,
        "plain_english": "A partner can deduct business use of home as an unreimbursed partner expense on Schedule E. The deduction covers a proportionate share of home expenses based on square footage used exclusively for partnership business. The partnership agreement should reflect the expectation of a home office.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
        "prerequisite_signals_any": ["SIG_K1_FROM_PARTNERSHIP", "SIG_HAS_PARTNERSHIP"],
    }
]