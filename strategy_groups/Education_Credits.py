from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-086-lifetime-learning-credit",
        "name": "Lifetime Learning Credit",
        "irc": "IRC §25A, §25A(b), §25A(d), §25A(f), §25A(g)(2)",
        "category": "Credits & Incentives",
        "overlap_group": "Education Credits",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_DEPENDENTS_PRESENT", False)
        and s.get("_agi", 0) < _LIM["llc_phaseout_mfj"],
        "materiality_fn": lambda s: (
            40
            if s.get("_agi", 0) < 160000
            else 20 if s.get("_agi", 0) < _LIM["llc_phaseout_mfj"] else 15
        ),
        "fed_savings_fn": lambda s: max(
            2000
            * max(
                0,
                1
                - max(
                    0, (s.get("_agi", 0) - (_LIM["llc_phaseout_mfj"] - 20000)) / 20000
                ),
            ),
            0,
        ),
        "state_savings_fn": lambda s: 0,
        "speed_days": 7,
        "complexity": 5,
        "audit_friction": 5,
        "plain_english": "The Lifetime Learning Credit provides a tax credit of 20% of the first $10,000 paid for qualified tuition and related expenses — up to a maximum of $2,000 per tax return. Unlike the American Opportunity Credit (which is limited to the first four years of college), the LLC applies to any year of post-secondary education including graduate school, professional courses, and continuing education. However, the credit phases out completely at $180,000 AGI for married filers — meaning most practice-owner dentists above that threshold receive no benefit themselves. The credit is most valuable for associate dentists in early career, dental students, or dentist-owners whose dependent children are in college or graduate school. For higher-income dentists, the §127 employer educational assistance exclusion (up to $5,250 tax-free through the practice) often provides greater benefit than the LLC — the two cannot be stacked on the same expenses.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-123-american-opportunity-credit",
        "name": "American Opportunity Credit",
        "irc": "IRC §25A, §25A(b), §25A(d), §25A(f), §25A(g)(2)",
        "category": "Credits & Incentives",
        "overlap_group": "Education Credits",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_DEPENDENTS_PRESENT", False)
        and s.get("_agi", 0) < _LIM["llc_phaseout_mfj"],
        "materiality_fn": lambda s: (
            45
            if s.get("SIG_DEPENDENTS_PRESENT", False) and s.get("_agi", 0) < 160000
            else 20 if s.get("_agi", 0) < _LIM["llc_phaseout_mfj"] else 5
        ),
        "fed_savings_fn": lambda s: (
            max(
                2500
                * max(
                    0,
                    1
                    - max(
                        0,
                        (s.get("_agi", 0) - (_LIM["llc_phaseout_mfj"] - 20000)) / 20000,
                    ),
                ),
                0,
            )
            if s.get("_agi", 0) < _LIM["llc_phaseout_mfj"]
            else 0
        ),
        "state_savings_fn": lambda s: 0,
        "speed_days": 7,
        "complexity": 5,
        "audit_friction": 5,
        "plain_english": "The American Opportunity Tax Credit (AOTC) provides up to $2,500 per eligible student per year as a dollar-for-dollar credit against federal income tax for qualified college education expenses — tuition, fees, and required course materials. The credit covers the first four years of higher education only and requires the student to be enrolled at least half-time in a degree program. Unlike a deduction, a credit directly reduces the tax owed; up to $1,000 of the AOTC is even refundable, meaning it can produce a refund even if no tax is owed. However, the AOTC phases out completely once adjusted gross income exceeds $180,000 for married couples filing jointly — which means most actively practicing dentists receive no benefit. The planning opportunity applies in two scenarios: (1) associate dentists or new graduates with income below the threshold, and (2) dependents who file their own returns and can claim the credit independently if they are not claimed as dependents.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    }
]