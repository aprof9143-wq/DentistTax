from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-101-delaware-incomplete-non-grantor-trust-ding",
        "name": "Delaware Incomplete Non-Grantor Trust (DING)",
        "irc": "IRC §2501, §2511, §§671–679, §641, §661, §662, §2036",
        "category": "Trusts & Estate",
        "overlap_group": "Estate Trust Planning",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and s.get("SIG_STATE_RETURN_PRESENT", False)
        and (s.get("_state_tax", 0) > 30000),
        "materiality_fn": lambda s: (
            65
            if s.get("_state_tax", 0) > 50000 and s.get("SIG_VERY_HIGH_INCOME", False)
            else 35
        ),
        "fed_savings_fn": lambda s: 500000 * 0.1 * 0.25,
        "state_savings_fn": lambda s: min(
            min(s.get("_agi", 0) * 0.2, 500000) * s.get("Q_STATE_MARGINAL_RATE", 0.08),
            500000 * 0.1 * 0.25,
        ),
        "speed_days": 120,
        "complexity": 70,
        "audit_friction": 30,
        "plain_english": "A Delaware Incomplete Non-Grantor Trust (DING) is an advanced estate and tax planning structure used by high-income dentists in high-tax states like California and New York. The dentist transfers investment assets to a trust sited in Delaware, Nevada, or another state with no income tax. The transfer is deliberately structured as an 'incomplete gift' — the dentist retains certain powers to change beneficiaries — so no gift tax is owed at funding. The trust is also designed as a non-grantor trust, meaning it files its own tax return and pays federal income tax itself. Because the trust is administered in a no-tax state and the grantor is not a beneficiary, the dentist's home state arguably cannot tax the trust's income. For a California dentist paying 13.3% state income tax on $500,000 of investment income, a successful DING saves $66,500 in state taxes annually. However, California and New York actively challenge these structures and may assert nexus based on the grantor's residency — this strategy requires specialized estate planning counsel and a current-law state nexus analysis.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],
    },
    {
        "id": "DTTS-104-credit-shelter-trust-bypass-trust",
        "name": "Credit Shelter Trust (Bypass Trust)",
        "irc": "IRC §2010, §2010(c)(2)(B), §2056, §2010(c)(5)(A), §2001, §1014",
        "category": "Trusts & Estate",
        "overlap_group": "Estate Trust Planning",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and s.get("SIG_DEPENDENTS_PRESENT", False)
        and (s.get("_agi", 0) > 750000),
        "materiality_fn": lambda s: (
            70
            if s.get("_agi", 0) > 1000000 and s.get("SIG_DEPENDENTS_PRESENT", False)
            else 40
        ),
        "fed_savings_fn": lambda s: 13610000 * 0.4 * 0.3,
        "state_savings_fn": lambda s: 0,
        "speed_days": 120,
        "complexity": 55,
        "audit_friction": 10,
        "plain_english": "A Credit Shelter Trust (also called a Bypass Trust or Family Trust) is a foundational estate planning tool for married dentists with significant wealth. When the first spouse dies, assets equal to the federal estate tax exemption ($13.61 million in 2024) are placed in an irrevocable trust for the benefit of children or other heirs. Because these assets bypass the surviving spouse's estate, they are not subject to estate tax when the surviving spouse later dies — effectively using both spouses' exemptions and potentially sheltering up to $27 million from estate tax. Portability (electing to carry over the deceased spouse's unused exemption) is simpler but doesn't protect future appreciation inside the trust from estate tax. Two critical timing issues: (1) this structure must be in place in the will or trust before death — it cannot be created retroactively; and (2) the TCJA estate tax exemption is scheduled to be cut roughly in half after 2025 — dentists with estates between $7 million and $27 million have a limited window before that sunset takes effect.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],
    },
    {
        "id": "DTTS-115-dynasty-trust-for-multi-gen-wealth-transfer",
        "name": "Dynasty Trust for Multi-Gen Wealth Transfer",
        "irc": "IRC §2501, §2511, §2631, §2642, §2613, §§671–679, §2036, §2041",
        "category": "Trusts & Estate",
        "overlap_group": "Estate Trust Planning",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and s.get("SIG_DEPENDENTS_PRESENT", False)
        and (s.get("_agi", 0) > 1000000),
        "materiality_fn": lambda s: (
            65
            if s.get("_agi", 0) > 2000000 and s.get("SIG_DEPENDENTS_PRESENT", False)
            else 35
        ),
        "fed_savings_fn": lambda s: 5000000 * (1.07**30 - 1) * 0.4 * 0.35,
        "state_savings_fn": lambda s: 0,
        "speed_days": 120,
        "complexity": 70,
        "audit_friction": 15,
        "plain_english": "A Dynasty Trust is an irrevocable trust designed to hold family wealth for multiple generations — potentially indefinitely — without ever paying estate tax or Generation-Skipping Transfer tax. The dentist funds the trust using the lifetime gift and GST exemptions ($13.61 million in 2024, per person), allocates the GST exemption to the trust, and then all future distributions to children, grandchildren, and great-grandchildren pass completely free of both estate tax and GST tax. The trust must be sited in a state that has abolished the Rule Against Perpetuities — Delaware, South Dakota, Nevada, and Wyoming are the most popular. The compounding effect is extraordinary: $5 million invested at 7% grows to $147 million over 50 years, all inside a structure that skips estate tax at every generation. Assets in the trust are also protected from the beneficiaries' creditors, divorce, and lawsuits. The TCJA estate tax exemption is scheduled to drop significantly after 2025 — creating urgency to fund dynasty trusts before the exemption reduction.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],
    }
]