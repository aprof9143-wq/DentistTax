from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-005-key-person-insurance-deduction",
        "name": "Key-Person Insurance Deduction",
        "irc": "IRC §162, §264(a)(1), §101(a), §101(j)",
        "category": "Insurance & Risk",
        "overlap_group": "Life Insurance Planning",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and (s.get("SIG_HAS_S_CORP_VERIFIED", False) or s.get("SIG_HAS_C_CORP", False))
        and s.get("SIG_HIGH_INCOME", False),
        "materiality_fn": lambda s: (
            55
            if s.get("SIG_HIGH_INCOME", False)
            and s.get("SIG_HAS_S_CORP_VERIFIED", False)
            else 35
        ),
        "fed_savings_fn": lambda s: 8000 * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 8000
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 30,
        "complexity": 20,
        "audit_friction": 15,
        "plain_english": "Key-person insurance protects the business if its most critical person — typically the owner-dentist — dies or becomes disabled. The tax treatment depends entirely on the type of policy: premiums on key-person term life insurance are NOT deductible under §264, and the death benefit is tax-free. Key-person disability insurance premiums ARE deductible to the business, but any disability benefits received are then taxable as ordinary income. The owner can choose to forgo the premium deduction and receive disability benefits tax-free instead. For C-Corps holding life insurance on employees, the §101(j) COLI notice and consent must be executed annually.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires policy design, underwriting/actuarial review, and compliance documentation before implementation.",
        ],
    },
    {
        "id": "DTTS-010-buy-sell-stock-redemption-with-life-insurance",
        "name": "Buy-Sell Stock Redemption with Life Insurance",
        "irc": "IRC §101(a), §302, §302(b)(3), §303, §264(a)(1)",
        "category": "Insurance & Risk",
        "overlap_group": "Life Insurance Planning",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and (s.get("SIG_HAS_S_CORP_VERIFIED", False) or s.get("SIG_HAS_C_CORP", False))
        and s.get("SIG_HIGH_INCOME", False)
        and (s.get("SIG_MULTI_ENTITY", False) or s.get("SIG_HAS_PARTNERSHIP", False)),
        "materiality_fn": lambda s: (
            60
            if s.get("SIG_HAS_S_CORP_VERIFIED", False)
            and s.get("SIG_HIGH_INCOME", False)
            else 40
        ),
        "fed_savings_fn": lambda s: 100000 * 0.238 * 0.3,
        "state_savings_fn": lambda s: 0,
        "speed_days": 60,
        "complexity": 35,
        "audit_friction": 10,
        "plain_english": "A buy-sell agreement funded with life insurance ensures that if one owner dies, the remaining owners can buy out the deceased owner's share at a pre-agreed price — without a fire sale or forced partnership with the deceased's heirs. In an entity redemption structure, the business owns and is beneficiary of the life insurance, receives the tax-free death benefit, and redeems the deceased's stock. In a cross-purchase structure, each owner individually owns policies on the other owners — this gives the surviving owner a stepped-up basis in the acquired interest, which reduces future capital gain on eventual sale. Premiums are not deductible in either structure.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires policy design, underwriting/actuarial review, and compliance documentation before implementation.",
        ],
    },
    {
        "id": "DTTS-021-life-insurance-death-benefit-estate-exclusion",
        "name": "Life Insurance Death Benefit Estate Exclusion",
        "irc": "IRC §101(a), §2042, §2042(2), §2035(a), §2503(b)",
        "category": "Insurance & Risk",
        "overlap_group": "Life Insurance Planning",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_DEPENDENTS_PRESENT", False),
        "materiality_fn": lambda s: 65 if s.get("_agi", 0) > 1000000 else 45,
        "fed_savings_fn": lambda s: 2000000 * 0.4 * 0.4,
        "state_savings_fn": lambda s: 0,
        "speed_days": 60,
        "complexity": 40,
        "audit_friction": 10,
        "plain_english": "Life insurance death benefits are income-tax-free to beneficiaries under §101(a). However, if you own the policy at death, the entire death benefit is included in your taxable estate under §2042 — subject to 40% estate tax. An Irrevocable Life Insurance Trust (ILIT) solves this: the trust owns the policy, you give up all incidents of ownership, and the death benefit passes to your beneficiaries completely outside your estate. You fund the trust each year with gifts to pay the premiums, using the $18,000 per-beneficiary annual gift tax exclusion. Crummey notices must be sent to beneficiaries annually to preserve the gift tax exclusion.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires policy design, underwriting/actuarial review, and compliance documentation before implementation.",
        ],
    },
    {
        "id": "DTTS-025-employer-provided-life-insurance",
        "name": "Employer-Provided Life Insurance",
        "irc": "IRC §§79, 105, 106, 125, 132",
        "category": "Insurance & Risk",
        "overlap_group": "Life Insurance Planning",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False),
        "materiality_fn": lambda s: (
            45 if s.get("SIG_HAS_S_CORP_VERIFIED", False) else 30
        ),
        "fed_savings_fn": lambda s: s.get("Q_EXEC_BONUS_TOTAL_DEDUCTION", 0)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("Q_EXEC_BONUS_TOTAL_DEDUCTION", 0)
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 30,
        "complexity": 20,
        "audit_friction": 10,
        "plain_english": "A dental practice can deduct life insurance premiums as a business expense when coverage is provided as an employee fringe benefit. The first $50,000 of group-term life insurance is excludable from the employee's taxable income under IRC §79. For S-Corp owner-dentists who own more than 2% of the practice, premiums are included in W-2 wages but are then deductible on the personal return — creating a net benefit through proper payroll structuring. This is a low-complexity strategy that works best when the practice already runs payroll and wants to add tax-efficient benefits for the owner and staff.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires policy design, underwriting/actuarial review, and compliance documentation before implementation.",
        ],
    },
    {
        "id": "DTTS-030-irrevocable-life-insurance-trust-ilit",
        "name": "Irrevocable Life Insurance Trust (ILIT)",
        "irc": "IRC §101, §101(a), §2042, §2035, §2503(b), §2503(c), §677",
        "category": "Insurance & Risk",
        "overlap_group": "Life Insurance Planning",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and s.get("SIG_DEPENDENTS_PRESENT", False),
        "materiality_fn": lambda s: 60 if s.get("_agi", 0) > 1000000 else 40,
        "fed_savings_fn": lambda s: 2000000 * 0.4 * 0.35,
        "state_savings_fn": lambda s: 0,
        "speed_days": 90,
        "complexity": 60,
        "audit_friction": 15,
        "plain_english": "An Irrevocable Life Insurance Trust (ILIT) is a trust that owns a life insurance policy on the dentist's life — keeping the death benefit completely outside the taxable estate. Without an ILIT, life insurance owned by the insured is included in the taxable estate and can trigger a 40% federal estate tax on the proceeds. With an ILIT, the trust owns the policy; the dentist makes annual gifts to the trust to pay premiums (using the annual gift tax exclusion of $18,000 per beneficiary); and at death, proceeds pass to heirs free of both income and estate tax. The ILIT can also lend money to the estate to cover any estate taxes without increasing the taxable estate.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
            "Requires policy design, underwriting/actuarial review, and compliance documentation before implementation.",
        ],
    },
    {
        "id": "DTTS-034-c-corporation-owned-life-insurance-eoli",
        "name": "C-Corporation-Owned Life Insurance (COLI/EOLI)",
        "irc": "IRC §101(a), §101(j), §264(a)(1), §264(f), §7702",
        "category": "Entity & Structuring",
        "overlap_group": "Life Insurance Planning",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_HAS_C_CORP", False)
        and s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False),
        "materiality_fn": lambda s: (
            55
            if s.get("SIG_HAS_C_CORP", False) and s.get("SIG_VERY_HIGH_INCOME", False)
            else 30
        ),
        "fed_savings_fn": lambda s: 20000 * 0.21,
        "state_savings_fn": lambda s: 0,
        "speed_days": 90,
        "complexity": 55,
        "audit_friction": 20,
        "plain_english": "A C-Corporation can own life insurance on a key employee or owner-dentist — a strategy known as Corporate-Owned Life Insurance (COLI) or Employer-Owned Life Insurance (EOLI). While the premiums are not deductible, the cash value inside the policy grows tax-deferred on the corporation's balance sheet, and the death benefit is received tax-free by the corporation — provided the IRS notice and consent requirements under §101(j) are satisfied. The insured employee must be notified and provide written consent before the policy is issued, and the corporation must file Form 8925 annually. Common uses include funding buy-sell agreements, replacing key person income, and providing liquidity for deferred compensation obligations.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires policy design, underwriting/actuarial review, and compliance documentation before implementation.",
        ],
    },
    {
        "id": "DTTS-099-insurance-dedicated-fund-idf-within-ppli",
        "name": "Insurance-Dedicated Fund (IDF) within PPLI",
        "irc": "IRC §7702, §7702(a), §817(h), §817(h)(1), §101(a), §72",
        "category": "Insurance & Risk",
        "overlap_group": "Life Insurance Planning",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and (s.get("_agi", 0) > 1000000),
        "materiality_fn": lambda s: 65 if s.get("_agi", 0) > 1500000 else 40,
        "fed_savings_fn": lambda s: (200000 * 0.238 - 20000) * 0.2,
        "state_savings_fn": lambda s: 200000 * 0.05 * 0.2,
        "speed_days": 180,
        "complexity": 75,
        "audit_friction": 25,
        "plain_english": "Private Placement Life Insurance (PPLI) with an Insurance-Dedicated Fund (IDF) allows a high-net-worth dentist to invest large sums in hedge funds or private equity strategies inside a life insurance wrapper — sheltering all investment returns from current income tax. Instead of paying tax on dividends, interest, and capital gains each year, the dentist's investments grow tax-deferred inside the policy, and can ultimately be accessed through tax-free policy loans or passed as an income-tax-free death benefit. The IDF is a special fund created exclusively for PPLI policies — the same strategy used by certain hedge funds is not available to direct investors but is accessible inside the insurance wrapper. Critical compliance requirements: the policyholder cannot direct specific investments (investor control doctrine); the IDF must be sufficiently diversified under §817(h); and the insurance charges (typically 0.5%–1.5% per year) must be justified by the tax savings. Minimum investments typically start at $1 million to $5 million.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires policy design, underwriting/actuarial review, and compliance documentation before implementation.",
        ],
    },
    {
        "id": "DTTS-107-private-placement-life-insurance-ppli",
        "name": "Private Placement Life Insurance (PPLI)",
        "irc": "IRC §7702, §7702A, §817(h), §101(a), §72, §264(a)(1)",
        "category": "Insurance & Risk",
        "overlap_group": "Life Insurance Planning",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and (s.get("_agi", 0) > 1000000),
        "materiality_fn": lambda s: 70 if s.get("_agi", 0) > 2000000 else 45,
        "fed_savings_fn": lambda s: (300000 * 0.238 - 30000) * 0.2,
        "state_savings_fn": lambda s: 300000 * 0.05 * 0.2,
        "speed_days": 180,
        "complexity": 80,
        "audit_friction": 25,
        "plain_english": "Private Placement Life Insurance (PPLI) is a customized life insurance policy designed for high-net-worth dentists that wraps an investment portfolio inside a life insurance contract — converting taxable investment returns into tax-deferred or tax-free wealth. The dentist funds the policy with $1 million or more, and the policy's sub-accounts invest in hedge funds, private equity, or other alternative strategies. All investment returns grow inside the policy without current income tax. The death benefit passes to beneficiaries income-tax-free under §101(a), and the dentist can access policy cash value through tax-free loans during life. PPLI is distinct from DTTS-099 (IDF within PPLI) in that DTTS-107 covers the full PPLI wrapper strategy including premium financing and estate planning integration through an ILIT. Key risks: (1) over-funding the policy beyond IRS limits converts it to a Modified Endowment Contract (MEC), making withdrawals taxable; (2) the investor control doctrine requires that policy management be independent; and (3) insurance charges must be justified by tax savings.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires policy design, underwriting/actuarial review, and compliance documentation before implementation.",
        ],
    }
]