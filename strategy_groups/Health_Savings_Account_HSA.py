from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-017-health-savings-account-hsa-optimization",
        "name": "Health Savings Account (HSA) Optimization",
        "irc": "IRC §223, §223(b), §223(c)(1), §223(f)(1), §223(f)(4), §106(d)",
        "category": "General Planning",
        "overlap_group": "Health Savings Account (HSA)",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HEALTH_INS_EXPENSE", False)
        and (s.get("SIG_HIGH_INCOME", False) or s.get("SIG_VERY_HIGH_INCOME", False)),
        "materiality_fn": lambda s: 75 if s.get("SIG_VERY_HIGH_INCOME", False) else 62,
        "fed_savings_fn": lambda s: s.get("Q_HEALTH_PREMIUM", 0)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("Q_HEALTH_PREMIUM", 0)
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 5,
        "plain_english": "A Health Savings Account is the only savings vehicle in the tax code with a triple tax advantage: contributions are deductible, growth is tax-free, and withdrawals for medical expenses are tax-free. The optimization strategy is to invest your HSA in low-cost index funds rather than leaving it in a cash sweep, pay current medical expenses out-of-pocket, and save every receipt — there is no deadline to reimburse yourself. Years later, you can take a completely tax-free distribution by submitting those old receipts. After age 65, you can withdraw for any purpose at ordinary income rates, making the HSA function like a second traditional IRA.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    }
]