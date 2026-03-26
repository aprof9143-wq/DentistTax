from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-066-self-rental-to-business",
        "name": "Self-Rental to Business",
        "irc": "IRC §469, §469(c), §469(l)(1), §162, §1231",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Real Estate — Self Rental",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_REAL_ESTATE_ACTIVITY", False)
        and s.get("SIG_HAS_S_CORP_VERIFIED", False)
        and s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_RENT_EXPENSE_PRESENT", False),
        "materiality_fn": lambda s: (
            65
            if s.get("SIG_HAS_S_CORP_VERIFIED", False)
            and s.get("SIG_REAL_ESTATE_ACTIVITY", False)
            and s.get("SIG_HIGH_INCOME", False)
            else 40
        ),
        "fed_savings_fn": lambda s: s.get("Q_MGMT_CO_REVENUE", 0) * 0.153 * 0.9235,
        "state_savings_fn": lambda s: 0,
        "speed_days": 30,
        "complexity": 30,
        "audit_friction": 20,
        "plain_english": "A self-rental arrangement allows a dentist who owns their office building or equipment to rent it to their own practice — shifting income from the practice (which may be subject to payroll taxes) to rental income (which is not subject to self-employment or FICA taxes). The practice deducts the rent as a business expense, and the owner receives rental income that can be partially sheltered by depreciation on the property. An important tax rule applies: under the self-rental recharacterization rule of §469, rental income from property rented to a business in which the owner materially participates is non-passive — it cannot be sheltered by passive losses from other rental properties. The primary planning benefit is the FICA/SE tax savings on income shifted to the rental channel, plus the ability to accelerate depreciation deductions on the property.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],
    },
    {
        "id": "DTTS-158-self-rental-grouping",
        "name": "Self-Rental Grouping Strategy",
        "irc": "IRC §469, Reg. §1.469-4",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Real Estate — Self Rental",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_REAL_ESTATE_ACTIVITY", False)
        and (
            s.get("SIG_HAS_S_CORP_VERIFIED", False)
            or s.get("SIG_BUSINESS_PRESENT", False)
        )
        and (
            s.get("Q_OWNS_BUILDING", False) or s.get("Q_OWNS_PRACTICE_BUILDING", False)
        ),
        "prerequisites_logic": lambda s: s.get("Q_OWNS_BUILDING", False)
        or s.get("Q_OWNS_PRACTICE_BUILDING", False),
        "readiness_if_prereq_fail": "PREREQUISITE_BUILD",
        "readiness_note": "Questionnaire needed — confirm practice building ownership before analysis",
        "materiality_fn": lambda s: (
            85
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 70 if s.get("SIG_HIGH_INCOME") else 50
        ),
        "fed_savings_fn": lambda s: (
            max(s.get("_schedule_e_depreciation", 0), s.get("_rental_net_loss", 0))
            * s.get("_fed_marginal_rate", 0.37)
            if s.get("_schedule_e_depreciation", 0) > 0
            or s.get("_rental_net_loss", 0) > 0
            else 0.0
        ),
        "state_savings_fn": lambda s: max(
            s.get("_schedule_e_depreciation", 0), s.get("_rental_net_loss", 0)
        )
        * (s.get("_state_tax", 0) / s.get("_agi", 1) if s.get("_agi", 0) else 0),
        "speed_days": 45,
        "complexity": 30,
        "audit_friction": 15,
        "plain_english": "When a dentist owns both the dental practice and the building used by the practice, the rental activity may sometimes be grouped with the business. This may allow depreciation losses from the building to offset practice income.",
        "prerequisites": [
            "Confirmed ownership of practice building (separate entity or direct ownership)",
            "Lease agreement between building entity and practice entity",
        ],
    }
]