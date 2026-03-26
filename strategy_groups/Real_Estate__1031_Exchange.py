from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-153-1031-exchange",
        "name": "§1031 Exchange",
        "irc": "IRC §1031",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Real Estate — 1031 Exchange",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_REAL_ESTATE_ASSET", False)
        and s.get("SIG_CAPITAL_GAIN_REALIZED", False)
        and (
            s.get("SIG_REAL_ESTATE_DEPRECIATION", False)
            or s.get("Q_HAS_RENTAL_PROPERTIES", False)
            or s.get("Q_OWNS_BUILDING", False)
        ),
        "materiality_fn": lambda s: (
            100
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("_capital_gains", 0) > 200000
            else 85 if s.get("_capital_gains", 0) > 100000 else 70
        ),
        "fed_savings_fn": lambda s: max(0, s.get("_capital_gains", 0)) * 0.2,
        "state_savings_fn": lambda s: max(0, s.get("_capital_gains", 0))
        * 0.2
        * (s.get("_state_tax", 0) / s.get("_agi", 1) if s.get("_agi", 0) else 0),
        "speed_days": 120,
        "complexity": 35,
        "audit_friction": 10,
        "plain_english": "A §1031 exchange allows taxpayers to defer capital gains tax when selling investment real estate and reinvesting in another qualifying property.",
        "prerequisites": [
            "Sale of investment or business real estate with realized capital gain"
        ],
    }
]