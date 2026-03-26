from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-179-mineral-donations",
        "name": "Mineral Rights Charitable Donation",
        "irc": "IRC §170",
        "category": "Charitable & Community",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_HIGH_INCOME", False)
        and s.get("Q_INVESTMENT_PORTFOLIO", 0) > 100000
        and s.get("SIG_HIGH_TAX_LIABILITY", False),
        "materiality_fn": lambda s: (
            100
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 85 if s.get("SIG_HIGH_INCOME") else 70
        ),
        "fed_savings_fn": lambda s: min(
            s.get("Q_INVESTMENT_PORTFOLIO", 150000), s.get("_agi", 0) * 0.3
        )
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: min(150000, s.get("_agi", 0) * 0.3)
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 120,
        "complexity": 45,
        "audit_friction": 25,
        "plain_english": "Donating mineral rights to a qualified charity can generate a charitable deduction based on the appraised value of the asset.",
        "prerequisites": ["Ownership of mineral rights or energy assets"],
        "overlap_group": "Charitable — Mineral Rights",
    }
]