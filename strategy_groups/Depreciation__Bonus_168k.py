from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-074-bonus-depreciation-on-used-property",
        "name": "Bonus Depreciation on Used Property",
        "irc": "IRC §168(k), §168(k)(1), §168(k)(2)(A), §168(k)(2)(A)(ii), §168(k)(6)",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Depreciation — Bonus §168(k)",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and (
            s.get("SIG_HAS_DEPRECIATION", False) or s.get("SIG_LOW_DEPRECIATION", False)
        ),
        "materiality_fn": lambda s: (
            65
            if s.get("SIG_HIGH_TAX_LIABILITY", False)
            and s.get("SIG_LOW_DEPRECIATION", False)
            else 45
        ),
        "fed_savings_fn": lambda s: s.get("Q_179_INCREMENTAL_DEDUCTION", 0)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("Q_179_INCREMENTAL_DEDUCTION", 0)
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 21,
        "complexity": 25,
        "audit_friction": 15,
        "plain_english": "The Tax Cuts and Jobs Act of 2017 eliminated the 'original use' requirement for bonus depreciation — meaning used equipment and property acquired from an unrelated party now qualifies for first-year bonus depreciation just like new property. For dentists, this is particularly powerful when acquiring an existing dental practice: the purchase price allocated to equipment, furniture, and fixtures can receive 60% bonus depreciation in 2024 — creating a massive year-one deduction on the acquisition. A $500,000 allocation to qualifying used equipment generates a $300,000 deduction in the acquisition year. The used property must not have been previously used by the buyer, a related party, or a predecessor — so buying a second location's equipment from an unrelated seller qualifies; buying equipment from the dentist's own other practice does not.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],
    },
    {
        "id": "DTTS-173-bonus-depreciation",
        "name": "Bonus Depreciation Strategy — §168(k)",
        "irc": "IRC §168(k)",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Depreciation — Bonus §168(k)",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_LOW_DEPRECIATION", False),
        "materiality_fn": lambda s: 75 if s.get("SIG_LOW_DEPRECIATION", False) else 50,
        # Fix: removed fabricated $100K fallback — it fires when no actual assets are known.
        # Without known depreciation base, show as REQUIRES_QUESTIONNAIRE with fallback estimate.
        "questionnaire_gates": ["Q_179_INCREMENTAL_DEDUCTION"],
        "fallback_savings_estimate": 50000,
        "fed_savings_fn": lambda s: (
            s.get("_depreciation", 0) * 0.6 * s.get("_fed_marginal_rate", 0)
            if s.get("_depreciation", 0) > 0
            else s.get("Q_179_INCREMENTAL_DEDUCTION", 0) * s.get("_fed_marginal_rate", 0)
        ),
        "state_savings_fn": lambda s: 0,
        "speed_days": 30,
        "complexity": 20,
        "audit_friction": 10,
        "plain_english": "Bonus depreciation allows accelerated expensing of qualified equipment and improvements in the year placed in service.",
        "prerequisites": ["Assets placed in service during the tax year"],
    }
]