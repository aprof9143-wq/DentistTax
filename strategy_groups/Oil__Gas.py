from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-043-oil-gas-idc",
        "name": "Oil & Gas Intangible Drilling Cost Deduction",
        "irc": "IRC §263(c)",
        "category": "Alternative Investments",
        "overlap_group": "Oil & Gas",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_HIGH_INCOME", False)
        and s.get("Q_INVESTMENT_PORTFOLIO", 0) > 100000,
        "materiality_fn": lambda s: (
            100
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 85 if s.get("SIG_HIGH_INCOME") else 70
        ),
        "fed_savings_fn": lambda s: s.get("Q_INVESTMENT_PORTFOLIO", 100000)
        * 0.7
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 100000
        * 0.7
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 60,
        "complexity": 40,
        "audit_friction": 15,
        "plain_english": "Oil and gas partnerships allow investors to deduct a large portion of intangible drilling costs immediately.",
        "prerequisites": ["Investment in oil and gas drilling partnership"],
    }
]