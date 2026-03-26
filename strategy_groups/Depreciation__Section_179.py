from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-167-section-179-equipment",
        "name": "Section 179 Equipment Deduction",
        "irc": "IRC §179",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Depreciation — Section 179",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("Q_179_INCREMENTAL_DEDUCTION", 0) > 0,
        "materiality_fn": lambda s: (
            95
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 80 if s.get("SIG_HIGH_INCOME") else 65
        ),
        "fed_savings_fn": lambda s: s.get("Q_INVESTMENT_PORTFOLIO", 100000)
        * 0.2
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 100000
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 14,
        "complexity": 15,
        "audit_friction": 5,
        "plain_english": "Section 179 allows immediate expensing of qualifying equipment purchases instead of depreciating them over several years.",
        "prerequisites": ["Business equipment purchases"],
    }
]