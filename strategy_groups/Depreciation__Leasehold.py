from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-036-accelerated-depreciation-via-leasehold-improvements",
        "name": "Accelerated Depreciation via Leasehold Improvements",
        "irc": "IRC §168, §168(e)(6), §168(k), §179, §179D",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Depreciation — Leasehold",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and (
            s.get("SIG_NO_DEPRECIATION", False) or s.get("SIG_LOW_DEPRECIATION", False)
        ),
        "materiality_fn": lambda s: (
            70
            if s.get("SIG_NO_DEPRECIATION", False)
            and s.get("SIG_HIGH_TAX_LIABILITY", False)
            else 50 if s.get("SIG_LOW_DEPRECIATION", False) else 35
        ),
        "fed_savings_fn": lambda s: s.get("Q_COST_SEG_INCREMENTAL_DEDUCTION", 0)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("Q_COST_SEG_INCREMENTAL_DEDUCTION", 0)
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 30,
        "complexity": 30,
        "audit_friction": 15,
        "plain_english": "When a dentist builds out or renovates a leased office space, those leasehold improvements qualify as Qualified Improvement Property (QIP) — a 15-year asset class eligible for accelerated depreciation. Instead of writing off a $300,000 build-out over 39 years, the practice can deduct 60% in the first year through bonus depreciation (2024 rate), and elect to expense additional amounts under Section 179. Energy-efficient upgrades to lighting, HVAC, or building envelope may also qualify for the §179D commercial building deduction — up to $5.65 per square foot. A cost segregation study can identify additional personal property components in the build-out that depreciate even faster. This strategy is most powerful in the year improvements are placed in service.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],
    }
]