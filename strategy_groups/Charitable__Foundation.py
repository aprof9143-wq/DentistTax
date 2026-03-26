from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-174-private-family-foundation",
        "name": "Private Family Foundation",
        "irc": "IRC §501(c)(3)",
        "category": "Charitable & Community",
        "phase_1_eligible": False,
        "blocked_in_entity_only": True,
        "applicable_surfaces": ["1040", "MIXED"],
        "eligibility_logic": lambda s: s.get("SIG_HIGH_INCOME", False)
        and (
            s.get("Q_GOAL_LEGACY", False) or s.get("Q_HAS_INVESTMENT_PORTFOLIO", False)
        ),
        "materiality_fn": lambda s: (
            100
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 85 if s.get("SIG_HIGH_INCOME") else 70
        ),
        "fed_savings_fn": lambda s: min(
            s.get("Q_INVESTMENT_PORTFOLIO", 200000), s.get("_agi", 0) * 0.3
        )
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: min(200000, s.get("_agi", 0) * 0.3)
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 120,
        "complexity": 50,
        "audit_friction": 20,
        "plain_english": "A private family foundation allows individuals to donate assets, receive charitable deductions, and control how charitable funds are distributed over time.",
        "prerequisites": ["High income and charitable planning goals"],
        "overlap_group": "Charitable — Foundation",
    }
]