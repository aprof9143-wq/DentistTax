from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-006-installment-sales-to-defer-capital-gains",
        "name": "Installment Sales to Defer Capital Gains",
        "irc": "IRC §453, §453(i), §453A, §453B",
        "category": "Exit & Sale",
        "overlap_group": "Practice Sale Exit",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("Q_PRACTICE_SALE_PLANNED", False)
        and (
            s.get("SIG_HAS_S_CORP_VERIFIED", False)
            or s.get("SIG_HAS_C_CORP", False)
            or s.get("SIG_REAL_ESTATE_ASSET", False)
        ),
        "materiality_fn": lambda s: (
            80
            if s.get("SIG_VERY_HIGH_INCOME", False)
            and s.get("SIG_REAL_ESTATE_ASSET", False)
            else 65
        ),
        "fed_savings_fn": lambda s: 38080 * 3.1,
        "state_savings_fn": lambda s: 800000
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
        * 0.2,
        "speed_days": 60,
        "complexity": 25,
        "audit_friction": 15,
        "plain_english": "An installment sale spreads the recognition of capital gains over multiple years as payments are received — instead of paying tax on the full gain in the year of sale. For a dental practice sold for $1 million, spreading gain over 5 years keeps each year's income lower, potentially avoiding the 3.8% Net Investment Income Tax and keeping the taxpayer in a lower bracket. Important: §1245 depreciation recapture is recognized fully in the year of sale regardless of the installment method — only the capital gain portion is deferred. The interest on the installment note is also taxable as ordinary income each year.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-039-section-453a-interest-charge-planning-large-installments",
        "name": "Section 453A Interest Charge Planning (Large Installments)",
        "irc": "IRC §453, §453(b), §453A, §453A(a), §453A(b), §453A(c), §1274",
        "category": "Exit & Sale",
        "overlap_group": "Practice Sale Exit",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and (s.get("_agi", 0) > 500000),
        "materiality_fn": lambda s: (
            55
            if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("_agi", 0) > 800000
            else 35
        ),
        "fed_savings_fn": lambda s: 50000 * 0.2,
        "state_savings_fn": lambda s: 0,
        "speed_days": 60,
        "complexity": 45,
        "audit_friction": 20,
        "plain_english": "When a dentist sells their practice and receives payments over multiple years through an installment sale, they generally only pay tax as payments arrive — spreading the gain and the tax bill. However, §453A imposes an annual interest charge when the total outstanding installment obligations exceed $5 million at year-end, effectively adding a cost to the deferral benefit on large sales. The planning goal is to structure installment notes so the outstanding balance stays below the $5 million threshold, or to evaluate whether the deferral benefit still exceeds the §453A interest cost. A critical trap to avoid: pledging the installment note as loan collateral triggers immediate gain recognition on the pledged amount — eliminating the deferral benefit entirely.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-071-partial-asset-sale-with-installment-1031",
        "name": "Partial Asset Sale with Installment + 1031",
        "irc": "IRC §453, §453(b), §453A, §1031, §1031(a), §1031(b), §453(f)(6)",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Practice Sale Exit",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_REAL_ESTATE_ACTIVITY", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("Q_PRACTICE_SALE_PLANNED", False),
        "event_trigger_logic": lambda s: s.get("SIG_PROPERTY_SALE_EVENT", False)
        or s.get("SIG_INSTALLMENT_SALE_EVENT", False)
        or s.get("Q_PRACTICE_SALE_PLANNED", False),
        "event_note": "No property sale or installment sale event detected in return data",
        "readiness_if_prereq_fail": "REQUIRES_EVENT",
        "materiality_fn": lambda s: (
            70
            if s.get("Q_PRACTICE_SALE_PLANNED") and s.get("SIG_VERY_HIGH_INCOME", False)
            else 30
        ),
        "fed_savings_fn": lambda s: (
            max(0, s.get("_capital_gains", 0)) * 0.2 * 0.5
            if s.get("Q_PRACTICE_SALE_PLANNED", False)
            else 0
        ),
        "state_savings_fn": lambda s: (
            max(0, s.get("_capital_gains", 0))
            * 0.2
            * 0.5
            * s.get("Q_STATE_MARGINAL_RATE", 0.04)
            if s.get("Q_PRACTICE_SALE_PLANNED", False)
            else 0
        ),
        "speed_days": 90,
        "complexity": 65,
        "audit_friction": 25,
        "plain_english": "A partial installment + 1031 strategy combines two powerful tax deferral tools on the same real estate sale. When a dentist sells an investment property, a portion of the proceeds is rolled into a like-kind replacement property via a §1031 exchange — deferring the capital gain on that portion entirely. The remaining cash proceeds are structured as an installment sale — spreading the taxable gain on that portion over multiple years and avoiding a large single-year tax spike. The combination can dramatically reduce the tax cost of an exit: for a $2M property with $1.6M of gain, the dentist might defer $1M of gain via the 1031 exchange and spread the remaining $600K over five years rather than recognizing it all at once. Depreciation recapture (§1250 unrecaptured gain at 25%) cannot be deferred and must be recognized first. Qualified intermediary coordination is essential when combining installment notes with a 1031 exchange.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],
    },
    {
        "id": "DTTS-128-reclassify-income-to-capital-gains",
        "name": "Reclassify Income to Capital Gains",
        "irc": "IRC §1221, §1231, §1(h), §1239, §1245, §1250",
        "category": "Exit & Sale",
        "overlap_group": "Practice Sale Exit",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and s.get("SIG_BUSINESS_PRESENT", False),
        "materiality_fn": lambda s: (
            55
            if s.get("SIG_HIGH_TAX_LIABILITY", False)
            and s.get("SIG_HAS_DEPRECIATION", False)
            else 30
        ),
        "fed_savings_fn": lambda s: s.get("_distributions", 0) * 0.2 * 0.17,
        "state_savings_fn": lambda s: s.get("_distributions", 0)
        * 0.2
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 30,
        "complexity": 25,
        "audit_friction": 15,
        "plain_english": "Reclassifying ordinary income as capital gains is one of the highest-leverage tax planning moves available to a dental practice owner, because the rate differential can be enormous: ordinary income is taxed up to 37% while long-term capital gains are taxed at a maximum 20% federal rate. The most common opportunity arises at practice sale: the way the purchase price is allocated among assets determines how much is ordinary income (equipment depreciation recapture, covenants not to compete) versus capital gains (goodwill, practice going concern value). Strategic allocation of more value to goodwill and less to ordinary income assets can save hundreds of thousands of dollars on a large practice sale. During ongoing operations, §1231 assets (dental equipment held more than one year) generate capital gain character when sold. The §1239 trap must be avoided: selling depreciable property to a related party (spouse, 80%-owned entity) converts all gain back to ordinary income.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-129-private-annuity-sale-to-children",
        "name": "Private Annuity Sale to Children",
        "irc": "IRC §7872, §453, §1274, §72, §2501, §2512(b); IRS Notice 2006-96",
        "category": "Exit & Sale",
        "overlap_group": "Practice Sale Exit",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and s.get("SIG_DEPENDENTS_PRESENT", False)
        and (s.get("_agi", 0) > 750000),
        "materiality_fn": lambda s: (
            35
            if s.get("SIG_VERY_HIGH_INCOME", False)
            and s.get("SIG_DEPENDENTS_PRESENT", False)
            else 15
        ),
        "fed_savings_fn": lambda s: 500000 * 0.3 * 0.4 * 0.25,
        "state_savings_fn": lambda s: 0,
        "speed_days": 90,
        "complexity": 50,
        "audit_friction": 25,
        "plain_english": "A private annuity sale to children was once a popular way for practice owners to transfer assets to the next generation and defer capital gains — the parent sold the practice or other assets to the children in exchange for annuity payments over the parent's lifetime, spreading the tax over many years. However, the IRS eliminated the gain deferral benefit in 2006 (Notice 2006-96): all gain is now recognized in the year of sale, making private annuities largely obsolete for capital gain deferral. The remaining estate planning value is narrow: because annuity payments stop at the parent's death, the transferred asset's future appreciation is removed from the parent's estate. But this must be weighed against the immediate income tax hit in the year of transfer. For most high-income dentists, an installment sale to an Intentionally Defective Grantor Trust (DTTS-077) or an intra-family loan (DTTS-076) will achieve superior results with better tax treatment.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires related-party role, compensation, and documentation review before implementation.",
        ],
    }
]