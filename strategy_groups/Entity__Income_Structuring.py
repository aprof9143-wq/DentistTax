from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-172-entity-structuring-layering",
        "name": "Entity Structuring & Layering (Income Shifting)",
        "irc": "IRC §162, §482",
        "category": "Entity & Income Structuring",
        "overlap_group": "Entity & Income Structuring",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False)
        and (s.get("SIG_MULTI_ENTITY", False) or s.get("SIG_VERY_HIGH_INCOME", False)),
        "materiality_fn": lambda s: (
            95
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 80 if s.get("SIG_HIGH_INCOME") else 65
        ),
        "fed_savings_fn": lambda s: s.get("Q_NON_SSTB_INCOME", 50000)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 50000
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 90,
        "complexity": 45,
        "audit_friction": 20,
        "plain_english": "Advanced tax planning sometimes uses multiple entities to separate operations, management, and real estate ownership.",
        "prerequisites": ["Multiple related business entities"],
    }
]