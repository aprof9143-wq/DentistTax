from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-165-vacation-home-tax-strategy",
        "name": "Vacation / Second Home Business Strategy",
        "irc": "IRC §280A",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Real Estate — Vacation Home",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("Q_OWNS_SECONDARY_HOME", False)
        or (
            s.get("SIG_REAL_ESTATE_ACTIVITY", False)
            and (
                s.get("SIG_REAL_ESTATE_DEPRECIATION", False)
                or s.get("Q_HAS_RENTAL_PROPERTIES", False)
            )
        ),
        "materiality_fn": lambda s: (
            85
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 70 if s.get("SIG_HIGH_INCOME") else 55
        ),
        "fed_savings_fn": lambda s: s.get("Q_COST_SEG_INCREMENTAL_DEDUCTION", 60000)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 60000
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 60,
        "complexity": 30,
        "audit_friction": 25,
        "plain_english": "If you own a vacation or second home used for rental or business, it may qualify for tax deductions with proper documentation.",
        "prerequisites": ["Vacation property with rental or business use"],
        "prerequisite_signals_any": ["SIG_SECOND_HOME_USAGE", "Q_OWNS_SECONDARY_HOME"],
    }
]