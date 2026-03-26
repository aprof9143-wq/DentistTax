from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-019-deduction-bunching-with-donor-advised-fund",
        "name": "Deduction Bunching with Donor-Advised Fund",
        "irc": "IRC §170, §170(b)(1)(A), §170(b)(1)(C), §170(f)(8), §63(c)",
        "category": "General Planning",
        "overlap_group": "Charitable Giving",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HIGH_INCOME", False)
        or s.get("SIG_VERY_HIGH_INCOME", False),
        "materiality_fn": lambda s: 62 if s.get("SIG_VERY_HIGH_INCOME", False) else 48,
        "fed_savings_fn": lambda s: s.get("Q_INVESTMENT_PORTFOLIO", 0)
        * 0.08
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("Q_INVESTMENT_PORTFOLIO", 0)
        * 0.08
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 7,
        "complexity": 10,
        "audit_friction": 5,
        "plain_english": "The standard deduction ($29,200 for married couples in 2024) means that smaller annual charitable contributions produce no additional tax benefit — you take the standard deduction anyway. The bunching strategy concentrates two or three years of planned giving into a single year, pushing your itemized deductions well above the standard deduction threshold. A Donor-Advised Fund makes this practical: you get the full tax deduction in the bunching year, but distribute grants to your chosen charities over time at your own pace. Contributing appreciated stock instead of cash is even more powerful — you avoid capital gains tax entirely and still deduct the full fair market value.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-023-charitable-lead-annuity-trust-clat",
        "name": "Charitable Lead Annuity Trust (CLAT)",
        "irc": "IRC §170, §2055(e)(2)(B), §2522(c)(2)(B), §2702(a)(2)(B), §664",
        "category": "Charitable & Foundations",
        "overlap_group": "Charitable Giving",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_DEPENDENTS_PRESENT", False)
        and (s.get("_agi", 0) > 1000000),
        "materiality_fn": lambda s: 68 if s.get("_agi", 0) > 1500000 else 45,
        "fed_savings_fn": lambda s: 370000 * 0.4 * 0.4,
        "state_savings_fn": lambda s: 0,
        "speed_days": 120,
        "complexity": 65,
        "audit_friction": 15,
        "plain_english": "A Charitable Lead Annuity Trust (CLAT) pays a fixed annuity to charity for a set number of years — then the remaining assets pass to your children or grandchildren. The key tax advantage: the gift to your heirs is valued for gift tax purposes by subtracting the present value of the charity's annuity from the total assets transferred. If the trust is structured as a 'zeroed-out' CLAT — where the annuity value equals the full amount transferred at the IRS discount rate — the taxable gift to heirs is zero. Any investment return above the IRS hurdle rate passes to heirs completely free of gift and estate tax. This strategy requires genuine charitable intent and functions best in a high-interest-rate environment.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],
    },
    {
        "id": "DTTS-114-intentionally-delaying-qcd-recognition",
        "name": "Intentionally Delaying QCD Recognition",
        "irc": "IRC §408(d)(8), §170, §401(a)(9)",
        "category": "Charitable & Foundations",
        "overlap_group": "Charitable Giving",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HAS_RETIREMENT_PLAN", False)
        and s.get("SIG_HIGH_INCOME", False)
        and (s.get("_retirement", 0) > 100000),
        "materiality_fn": lambda s: (
            50
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else (
                30
                if s.get("SIG_HIGH_INCOME") or s.get("SIG_HIGH_TAX_LIABILITY")
                else 20
            )
        ),
        "fed_savings_fn": lambda s: min(105000, s.get("_retirement", 0) * 0.3)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: min(105000, s.get("_retirement", 0) * 0.3)
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 7,
        "complexity": 10,
        "audit_friction": 5,
        "plain_english": "A Qualified Charitable Distribution (QCD) allows IRA owners age 70½ and older to donate up to $105,000 per year directly from an IRA to a qualified charity — and the distribution is completely excluded from gross income. This is far more powerful than taking the IRA distribution as income and then deducting the charitable contribution. If the dentist takes $105,000 out of the IRA, that amount is taxable income; a separate charitable deduction might not offset it fully due to AGI percentage limits, standard deduction, and SALT cap interactions. With a QCD, the $105,000 never hits the tax return as income at all — directly reducing AGI and avoiding Medicare IRMAA surcharges and other income-based phase-outs. The 'intentional delay' angle means strategically timing QCDs to high-income years when the AGI reduction is most valuable — for example, the year a DSO transition or other large income event occurs, directing the IRA RMD as a QCD in that year maximizes the benefit.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-166-charitable-contributions",
        "name": "Charitable Contributions Strategy",
        "irc": "IRC §170",
        "category": "Charitable & Community",
        "overlap_group": "Charitable Giving",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("_agi", 0) > 100000
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and (s.get("Q_INVESTMENT_PORTFOLIO", 0) > 0),
        "materiality_fn": lambda s: (
            70
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 55 if s.get("SIG_HIGH_INCOME") else 40
        ),
        "fed_savings_fn": lambda s: s.get("Q_HEALTH_PREMIUM", 15000)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 15000
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 5,
        "plain_english": "Charitable donations to qualified organizations can provide tax deductions while supporting community initiatives and outreach.",
        "prerequisites": ["Donations made to qualified charities"],
    }
]