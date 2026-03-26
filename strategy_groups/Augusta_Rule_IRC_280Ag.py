from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-031-section-280a-g-the-augusta-rule",
        "name": "Augusta Rule (IRC §280A(g))",
        "irc": "IRC §162, §280A, §280A(g)",
        "category": "General Planning",
        "overlap_group": "Augusta Rule (IRC §280A(g))",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and (s.get("Q_OWNS_SECONDARY_HOME", False) or s.get("Q_OWNS_BUILDING", False)),
        "materiality_fn": lambda s: (
            70
            if s.get("SIG_HAS_S_CORP_VERIFIED", False)
            and s.get("SIG_HIGH_TAX_LIABILITY", False)
            else 50
        ),
        "fed_savings_fn": lambda s: 28000 * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 28000 * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 14,
        "complexity": 15,
        "audit_friction": 25,
        "plain_english": "The Augusta Rule — named after the practice of Augusta, Georgia homeowners renting their homes during the Masters golf tournament — allows a homeowner to rent their personal residence to their own business for up to 14 days per year completely tax-free. The business gets a deduction for the rental payment as an ordinary business expense, but the owner pays zero income tax on the rental income received. For a high-income dentist, this means shifting up to $25,000–$30,000 out of the business as a deductible expense while the owner receives that same amount completely tax-free. The key requirements: the rental must be for legitimate business purposes (board meetings, team retreats), the rate must be at fair market value, and meeting records must be documented.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    }
]
