from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-013-grantor-retained-income-trust-grit",
        "name": "Grantor Retained Income Trust (GRIT)",
        "irc": "IRC §2702, §2702(a)(2), §2036, §2501; Treas. Reg. §25.2702-1",
        "category": "Trusts & Estate",
        "overlap_group": "Grantor Trust Planning",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_DEPENDENTS_PRESENT", False)
        and (s.get("_agi", 0) > 1000000),
        "materiality_fn": lambda s: 55 if s.get("_agi", 0) > 1500000 else 35,
        "fed_savings_fn": lambda s: 1000000 * 0.2 * 0.4 * 0.4,
        "state_savings_fn": lambda s: 0,
        "speed_days": 120,
        "complexity": 65,
        "audit_friction": 15,
        "plain_english": "A Grantor Retained Income Trust (GRIT) allows a grantor to transfer assets into a trust while retaining the right to income from the trust for a set number of years. At the end of the term, the remaining assets pass to the beneficiaries at a reduced gift tax cost — because the value of the retained income stream reduces the taxable gift. However, the 1990 tax law changes largely eliminated the GRIT for transfers to family members — the retained income interest is valued at zero for gift tax purposes when family members are the remaindermen. For transfers to non-family beneficiaries (charities, non-family individuals), the GRIT still functions as designed. For family transfers, the modern GRAT (Grantor Retained Annuity Trust) is generally preferred and more favorable.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],
    },
    {
        "id": "DTTS-046-asset-sale-to-intentionally-defective-grantor-trust",
        "name": "Asset Sale to Intentionally Defective Grantor Trust (IDGT)",
        "irc": "IRC §§671–679, §2511, §2512",
        "category": "Trusts & Estate",
        "overlap_group": "Grantor Trust Planning",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and s.get("SIG_DEPENDENTS_PRESENT", False)
        and (s.get("_agi", 0) > 750000),
        "materiality_fn": lambda s: (
            70
            if s.get("_agi", 0) > 1000000 and s.get("SIG_DEPENDENTS_PRESENT", False)
            else 50
        ),
        "fed_savings_fn": lambda s: 2000000 * 0.4 * 0.35,
        "state_savings_fn": lambda s: 0,
        "speed_days": 120,
        "complexity": 70,
        "audit_friction": 20,
        "plain_english": "An Intentionally Defective Grantor Trust (IDGT) is one of the most powerful estate planning tools available for high-income dentists with appreciating assets. The trust is 'defective' on purpose — it is structured so that the grantor (the dentist) is treated as the owner for income tax purposes, but the assets inside the trust are completely outside the taxable estate. The dentist sells appreciating assets — practice equity, investment property, or a management company interest — to the trust in exchange for an installment note at the IRS minimum interest rate. Because the grantor is selling to their own grantor trust, no capital gains are recognized. All future appreciation on the sold assets compounds inside the trust and eventually passes to heirs free of estate tax. As an added benefit, when the grantor pays the trust's income tax each year, they are making additional tax-free transfers to the trust beneficiaries.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],
    },
    {
        "id": "DTTS-077-installment-sale-to-intentionally-defective-grantor-trust",
        "name": "Installment Sale to Intentionally Defective Grantor Trust",
        "irc": "IRC §453, §453(b), §671, §675, §§671–679, §1274",
        "category": "Trusts & Estate",
        "overlap_group": "Grantor Trust Planning",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and s.get("SIG_DEPENDENTS_PRESENT", False)
        and (s.get("_agi", 0) > 750000),
        "materiality_fn": lambda s: (
            70
            if s.get("_agi", 0) > 1000000 and s.get("SIG_DEPENDENTS_PRESENT", False)
            else 45
        ),
        "fed_savings_fn": lambda s: 3000000 * 0.4 * 0.3,
        "state_savings_fn": lambda s: 0,
        "speed_days": 120,
        "complexity": 75,
        "audit_friction": 20,
        "plain_english": "An installment sale to an Intentionally Defective Grantor Trust combines two powerful tax tools: the grantor trust rules (which make the sale non-taxable) and an installment note (which provides a structured payment stream). The dentist sells an appreciating asset — practice equity, a management company interest, or investment real estate — to an irrevocable trust in exchange for a promissory note bearing the AFR rate. Because the trust is a grantor trust, the sale is treated as the dentist selling to themselves — no capital gains are recognized. The asset appreciates inside the trust, while the dentist's estate contains only the declining note balance (as the trust makes principal payments). The interest payments the trust makes to the dentist are also non-taxable — a grantor trust paying interest to its own grantor. All appreciation above the note amount compounds in the trust and eventually passes to heirs estate-tax-free.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],
    },
    {
        "id": "DTTS-080-deferred-sales-trust-dst",
        "name": "Deferred Sales Trust (DST)",
        "irc": "IRC §453, §453(b), §671–679, §2501, §2511",
        "category": "Trusts & Estate",
        "overlap_group": "Grantor Trust Planning",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and (
            s.get("SIG_REAL_ESTATE_ACTIVITY", False)
            or s.get("SIG_SCHEDULE_E_PRESENT", False)
        )
        and (s.get("_agi", 0) > 500000),
        "materiality_fn": lambda s: (
            50
            if s.get("SIG_REAL_ESTATE_ACTIVITY", False)
            and s.get("SIG_VERY_HIGH_INCOME", False)
            else 25
        ),
        "fed_savings_fn": lambda s: 166600 * 0.25,
        "state_savings_fn": lambda s: 0,
        "speed_days": 90,
        "complexity": 75,
        "audit_friction": 40,
        "plain_english": "A Deferred Sales Trust (DST) is a marketed tax strategy that uses the installment sale rules (§453) to defer capital gains recognition when selling an appreciated asset. Instead of selling directly to a buyer, the owner sells to an independently managed trust in exchange for an installment note — the trust then sells to the actual buyer and invests the proceeds. The owner receives installment payments over time and recognizes gain proportionally as payments arrive. Unlike an IDGT (which eliminates gain entirely because the trust is treated as the seller themselves), a DST only defers gain via §453 — it is still fully taxable, just spread over multiple years. Important warning: the IRS has scrutinized DST structures aggressively. If the trust is found to be acting as the seller's agent, the entire gain is recognized in the year of sale. This strategy carries significant audit risk and should only be pursued after thorough review by independent tax counsel — not through a promoter.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],
    },
    {
        "id": "DTTS-097-tax-efficient-sale-via-grantor-retained-annuity-trust-grat",
        "name": "Tax-Efficient Sale via Grantor Retained Annuity Trust (GRAT)",
        "irc": "IRC §2702, §2702(b), §7520, §2036, §671–677, §2001",
        "category": "Trusts & Estate",
        "overlap_group": "Grantor Trust Planning",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and s.get("SIG_DEPENDENTS_PRESENT", False)
        and (s.get("_agi", 0) > 750000),
        "materiality_fn": lambda s: (
            65
            if s.get("_agi", 0) > 1000000 and s.get("SIG_DEPENDENTS_PRESENT", False)
            else 40
        ),
        "fed_savings_fn": lambda s: 1458000 * 0.4 * 0.3,
        "state_savings_fn": lambda s: 0,
        "speed_days": 90,
        "complexity": 60,
        "audit_friction": 20,
        "plain_english": "A Grantor Retained Annuity Trust (GRAT) allows a dentist to transfer appreciating assets to heirs with little or no gift tax. The dentist transfers an asset — practice equity, DSO stock, or an investment portfolio — to the GRAT and receives back a fixed annuity payment each year for the trust's term. The annuity is sized so the present value equals the asset's value at transfer, making the taxable gift approximately zero. If the asset grows faster than the IRS hurdle rate (currently around 5%), all appreciation above that rate passes to the remainder beneficiaries (children or a trust for them) free of estate and gift tax. If the asset doesn't beat the hurdle rate, the asset simply flows back to the dentist via annuity payments — no harm, no foul. The key risk: if the dentist dies during the GRAT term, the assets return to the estate. GRATs work best with short terms or rolling multi-year GRATs to minimize mortality risk.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],
    }
]