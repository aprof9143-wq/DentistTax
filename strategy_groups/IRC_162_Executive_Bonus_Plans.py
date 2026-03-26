from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-041-executive-bonus-plan-with-gross-up",
        "name": "Executive Bonus Plan (with Gross-Up)",
        "irc": "IRC §162, §61, §7702",
        "category": "Compensation & Benefits",
        "overlap_group": "IRC §162 Executive Bonus Plans",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and s.get("SIG_W2_PRESENT", False),
        "materiality_fn": lambda s: (
            60
            if s.get("SIG_HAS_S_CORP_VERIFIED", False)
            and s.get("SIG_HIGH_TAX_LIABILITY", False)
            else 40
        ),
        "fed_savings_fn": lambda s: s.get("Q_EXEC_BONUS_TOTAL_DEDUCTION", 0)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("Q_EXEC_BONUS_TOTAL_DEDUCTION", 0)
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 30,
        "complexity": 25,
        "audit_friction": 15,
        "plain_english": "An executive bonus plan — sometimes called a §162 bonus plan — allows a dental practice to pay a bonus to the owner-dentist that is used to fund a personally-owned life insurance policy. The practice deducts the bonus as ordinary compensation expense, and the policy is owned by the executive (not the business), so the cash value grows tax-deferred and the death benefit passes to heirs tax-free. The 'gross-up' layer adds a second bonus to cover the income tax on the first — so the executive ends up with the full premium going into the policy on a tax-neutral basis. The result is a practice deduction today plus tax-deferred wealth accumulation in a personally-owned policy with no corporate ownership complications.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    }
]