from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-154-real-estate-professional-status",
        "name": "Real Estate Professional Status (IRC §469)",
        "irc": "IRC §469",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Real Estate — Professional Status",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_REAL_ESTATE_ACTIVITY", False)
        and s.get("SIG_SCHEDULE_E_PRESENT", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and s.get("SIG_REAL_ESTATE_DEPRECIATION", False)
        and (
            s.get("SIG_RENTAL_NET_LOSS", False)
            or s.get("Q_HAS_RENTAL_PROPERTIES", False)
        ),
        "materiality_fn": lambda s: (
            100
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_RENTAL_NET_LOSS")
            else (
                85
                if s.get("SIG_HIGH_INCOME") and s.get("SIG_RENTAL_NET_LOSS")
                else 60 if s.get("Q_HAS_RENTAL_PROPERTIES") else 40
            )
        ),
        "fed_savings_fn": lambda s: (
            max(s.get("_rental_net_loss", 0), s.get("_schedule_e_depreciation", 0))
            * s.get("_fed_marginal_rate", 0.37)
            if s.get("_rental_net_loss", 0) > 0
            or s.get("_schedule_e_depreciation", 0) > 0
            else 0.0
        ),
        "state_savings_fn": lambda s: max(
            s.get("_rental_net_loss", 0), s.get("_schedule_e_depreciation", 0)
        )
        * (s.get("_state_tax", 0) / s.get("_agi", 1) if s.get("_agi", 0) else 0),
        "speed_days": 90,
        "complexity": 40,
        "audit_friction": 25,
        "plain_english": "Real Estate Professional Status allows qualifying taxpayers to use rental losses to offset active income such as professional earnings.",
        "prerequisites": [
            "Active rental properties with net losses suspended under §469"
        ],
    }
]