from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-029-conservation-easement-with-mineral-rights-retained",
        "name": "Conservation Easement with Mineral Rights Retained",
        "irc": "IRC §170(h), §170(h)(1), §170(h)(4), §170(h)(5), §170(f)(11)",
        "category": "Charitable & Foundations",
        "overlap_group": "Conservation Easement Strategies",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and (
            s.get("SIG_REAL_ESTATE_ACTIVITY", False)
            or s.get("SIG_SCHEDULE_E_PRESENT", False)
        ),
        "materiality_fn": lambda s: 60 if s.get("_agi", 0) > 750000 else 40,
        "fed_savings_fn": lambda s: min(166667, s.get("_agi", 0) * 0.5)
        * s.get("_fed_marginal_rate", 0)
        * 0.3,
        "state_savings_fn": lambda s: 0,
        "speed_days": 180,
        "complexity": 70,
        "audit_friction": 40,
        "plain_english": "A conservation easement allows a landowner to donate a permanent restriction on how their land can be developed to a qualified land trust or government organization — and take a charitable deduction for the reduction in property value caused by that restriction. When mineral rights are retained, the owner keeps the right to extract any oil, gas, or minerals beneath the surface while still receiving the deduction for the surface development restriction. The deduction is based on a qualified appraisal and can be substantial — but this strategy carries high IRS scrutiny, particularly for syndicated arrangements. Only legitimate, owner-driven easements with genuine conservation purpose and proper appraisals should be considered.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    }
]