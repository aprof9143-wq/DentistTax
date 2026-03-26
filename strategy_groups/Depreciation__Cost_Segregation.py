from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-016-cost-segregation",
        "name": "Cost Segregation",
        "irc": "IRC §§167, 168, §168(k); Rev. Proc. 87-56; IRS Cost Segregation ATG",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Depreciation — Cost Segregation",
        "phase_1_eligible": True,
        # Fix: required Q_COST_SEG_INCREMENTAL_DEDUCTION > 0, so it never fired without
        # questionnaire. Now fires on real estate + depreciation signals; Q_ gate handles rest.
        "eligibility_logic": lambda s: (
            s.get("Q_OWNS_BUILDING", False) or s.get("SIG_REAL_ESTATE_ASSET", False)
        )
        and (
            s.get("SIG_HAS_DEPRECIATION", False) or s.get("SIG_LOW_DEPRECIATION", False)
        )
        # Cost segregation requires owning a building — not applicable when the
        # real estate signal comes purely from a sale (Form 4797 disposition event).
        # If only an asset-sale event and no ongoing real estate activity, suppress.
        and not (
            s.get("SIG_PROPERTY_SALE_EVENT", False)
            and not s.get("SIG_REAL_ESTATE_ACTIVITY", False)
            and not s.get("Q_OWNS_BUILDING", False)
        ),
        "questionnaire_gates": ["Q_OWNS_BUILDING"],
        "fallback_savings_estimate": 30000,
        "materiality_fn": lambda s: (
            88
            if s.get("SIG_REAL_ESTATE_ASSET", False)
            and s.get("SIG_LOW_DEPRECIATION", False)
            and not s.get("SIG_PROPERTY_SALE_EVENT", False)  # sale = disposed, can't seg
            else (
                72
                if s.get("SIG_REAL_ESTATE_ASSET", False)
                and not s.get("SIG_PROPERTY_SALE_EVENT", False)
                else 45  # low materiality when only sale event drove the real estate signal
            )
        ),
        # Fix: use depreciation as proxy when Q_ not available; Q_ gate handles readiness.
        "fed_savings_fn": lambda s: (
            s.get("Q_COST_SEG_INCREMENTAL_DEDUCTION",
                  s.get("_depreciation", 0) * 0.40) * s.get("_fed_marginal_rate", 0)
        ),
        "state_savings_fn": lambda s: (
            s.get("Q_COST_SEG_INCREMENTAL_DEDUCTION",
                  s.get("_depreciation", 0) * 0.40) * s.get("Q_STATE_MARGINAL_RATE", 0.05) * 0.8
        ),
        "speed_days": 45,
        "complexity": 35,
        "audit_friction": 20,
        "plain_english": "Cost segregation is an engineering study that breaks down a building into its component parts and reclassifies them from 39-year straight-line depreciation into shorter-lived categories of 5, 7, or 15 years. A dental office built or purchased for $1 million might have $300,000 in components — specialized plumbing, electrical for equipment, dental cabinetry, flooring, and parking lot — that qualify for accelerated depreciation or bonus depreciation. Instead of deducting $25,000 per year for 39 years, those components generate hundreds of thousands in deductions in the first few years. For existing buildings, a lookback study captures all missed depreciation in a single catch-up deduction without amending prior returns.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],
    }
]