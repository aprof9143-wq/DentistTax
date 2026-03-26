from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-155-short-term-rentals",
        "name": "Short-Term Rentals (Active Participation Strategy)",
        "irc": "Treas. Reg. §1.469-1T(e)(3)(ii)(A)",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Real Estate — Short-Term Rental",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_REAL_ESTATE_ACTIVITY", False)
        and (
            s.get("SIG_REAL_ESTATE_DEPRECIATION", False)
            or s.get("Q_HAS_RENTAL_PROPERTIES", False)
            or s.get("Q_OWNS_BUILDING", False)
        ),
        "materiality_fn": lambda s: (
            100
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 90 if s.get("SIG_HIGH_INCOME") else 75
        ),
        "fed_savings_fn": lambda s: s.get("Q_COST_SEG_INCREMENTAL_DEDUCTION", 120000)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 120000
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 90,
        "complexity": 35,
        "audit_friction": 20,
        "plain_english": "If you have short-term rental property (average stays under seven days), it may qualify as an active business rather than passive rental, allowing losses to offset other income.",
        "prerequisites": ["Short-term rental property ownership"],
        "prerequisite_signals_any": ["SIG_SHORT_TERM_RENTAL", "Q_SHORT_TERM_RENTAL"],
    }
]