from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-063-family-limited-partnership-flp",
        "name": "Family Limited Partnership (FLP)",
        "irc": "IRC §2036, §2701, §2702, §2703, §2704, §704(e)",
        "category": "Entity & Structuring",
        "overlap_group": "Family Entity Planning",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and s.get("SIG_DEPENDENTS_PRESENT", False)
        and (s.get("_agi", 0) > 750000),
        "materiality_fn": lambda s: (
            70
            if s.get("SIG_VERY_HIGH_INCOME", False)
            and s.get("SIG_DEPENDENTS_PRESENT", False)
            and (s.get("_agi", 0) > 1000000)
            else 45
        ),
        "fed_savings_fn": lambda s: 300000 * 0.4 * 0.35,
        "state_savings_fn": lambda s: 0,
        "speed_days": 120,
        "complexity": 65,
        "audit_friction": 30,
        "plain_english": "A Family Limited Partnership (FLP) allows a dentist to transfer assets to family members at a discount for gift and estate tax purposes. The dentist contributes assets — real estate, investments, or a management company interest — to the FLP and retains control as the general partner. Limited partnership interests are then gifted to children or grandchildren. Because LP interests lack voting control and have no public market, they receive valuation discounts of 20–40% compared to the underlying asset value. This means a $1 million gift of LP interests might be valued at only $700,000 for gift tax purposes — stretching the lifetime exemption further. Future appreciation compounds outside the estate in the children's hands. The IRS scrutinizes FLPs closely under §2036, so the partnership must have genuine business purpose, proper formalities must be maintained, and personal and partnership assets must not be commingled.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
            "Requires related-party role, compensation, and documentation review before implementation.",
        ],
    },
    {
        "id": "DTTS-076-intra-family-loans-with-afr",
        "name": "Intra-Family Loans with AFR",
        "irc": "IRC §7872, §7872(a), §7872(c), §7872(d), §7872(f)(2), §1274",
        "category": "General Planning",
        "overlap_group": "Family Entity Planning",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and s.get("SIG_DEPENDENTS_PRESENT", False)
        and (s.get("Q_INVESTMENT_PORTFOLIO", 0) > 100000),
        "materiality_fn": lambda s: (
            50
            if s.get("SIG_VERY_HIGH_INCOME", False)
            and s.get("SIG_DEPENDENTS_PRESENT", False)
            else 30
        ),
        "fed_savings_fn": lambda s: s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.035,
        "state_savings_fn": lambda s: min(
            s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.035,
            s.get("Q_INVESTMENT_PORTFOLIO", 0)
            * s.get("Q_STATE_MARGINAL_RATE", 0.05)
            * 0.5,
        ),
        "speed_days": 21,
        "complexity": 20,
        "audit_friction": 15,
        "plain_english": "An intra-family loan allows a dentist to lend money to children, grandchildren, or a family trust at the IRS minimum interest rate (the Applicable Federal Rate, or AFR). As long as the loan charges at least the AFR, there is no gift tax element and no imputed income under §7872. The wealth transfer benefit comes from the spread: if the borrowed funds are invested and earn more than the AFR, the excess return accumulates in the child's hands — outside the dentist's taxable estate — without using any gift tax exemption. For example, lending $1 million at a 4.5% AFR while the child earns 8% on the funds transfers $35,000 per year in wealth to the next generation at no gift tax cost. The loan must be documented with a written promissory note, actual interest payments must be made, and the dentist reports the interest received as ordinary income.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires related-party role, compensation, and documentation review before implementation.",
        ],
    },
    {
        "id": "DTTS-082-gifting-appreciated-stock-to-family",
        "name": "Gifting Appreciated Stock to Family",
        "irc": "IRC §2501, §2503(b), §1015, §1(g), §2505",
        "category": "General Planning",
        "overlap_group": "Family Entity Planning",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_DEPENDENTS_PRESENT", False),
        "materiality_fn": lambda s: (
            50
            if s.get("SIG_VERY_HIGH_INCOME", False)
            and s.get("SIG_DEPENDENTS_PRESENT", False)
            else 30
        ),
        "fed_savings_fn": lambda s: s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.05 * 0.238,
        "state_savings_fn": lambda s: s.get("Q_INVESTMENT_PORTFOLIO", 0)
        * 0.05
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 7,
        "complexity": 10,
        "audit_friction": 5,
        "plain_english": "Gifting appreciated stock to family members can shift capital gains from the dentist's high tax bracket to a lower-bracket family member — or eliminate them entirely if the recipient is in the 0% long-term capital gains bracket. Each year, a dentist can gift up to $18,000 per recipient ($36,000 if married filing jointly) with no gift tax and no Form 709 required. The recipient inherits the dentist's original cost basis, not the current value — so the gain isn't eliminated, just shifted. If an adult child with little other income receives and sells the stock, they may owe zero capital gains tax on the appreciation. Two important traps: the 'kiddie tax' rules tax unearned income of children under 19 (or full-time students under 24) at the parent's rate, eliminating the benefit for young children. And gifting loses the step-up in basis that would occur at death — so if the dentist is not estate-tax exposed, holding appreciated stock until death may be better.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires related-party role, compensation, and documentation review before implementation.",
        ],
    }
]