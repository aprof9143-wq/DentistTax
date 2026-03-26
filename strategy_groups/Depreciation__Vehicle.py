from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-069-section-280f-luxury-auto-depreciation-cap",
        "name": "Section 280F — Luxury Auto Depreciation Cap",
        "irc": "IRC §274, §280F, §280F(a), §280F(d)(5), §280F(d)(6), §168(k), §179(b)(5)",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Depreciation — Vehicle",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_AUTO_TRUCK_PRESENT", False)
        and s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False),
        "materiality_fn": lambda s: (
            50
            if s.get("SIG_AUTO_TRUCK_PRESENT", False)
            and s.get("SIG_HIGH_TAX_LIABILITY", False)
            else 30
        ),
        "fed_savings_fn": lambda s: s.get("Q_179_INCREMENTAL_DEDUCTION", 0)
        * 0.6
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("Q_179_INCREMENTAL_DEDUCTION", 0)
        * 0.6
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 14,
        "complexity": 15,
        "audit_friction": 20,
        "plain_english": "The IRS caps annual depreciation on passenger automobiles — no matter how expensive — at $20,400 in year one (2024, with bonus depreciation). A dentist buying a $100,000 luxury sedan is limited to the same first-year deduction as someone buying a $50,000 car. The planning strategy is to purchase a vehicle with a gross vehicle weight rating (GVWR) above 6,000 pounds — large SUVs like the Suburban, Expedition, or Tahoe, or work trucks like the F-250. These vehicles are exempt from the luxury auto caps, allowing 60% bonus depreciation in year one (2024 rate). Section 179 for heavy SUVs is limited to $30,500, but bonus depreciation is not capped. A $70,000 heavy SUV used 100% for business can generate a $42,000 first-year deduction — more than double what the luxury auto cap would allow on a comparable car. Mileage logs and business use documentation are required.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],
    }
]