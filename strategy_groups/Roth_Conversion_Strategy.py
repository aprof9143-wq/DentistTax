from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-014-in-kind-roth-conversion-of-appreciated-assets",
        "name": "In-Kind Roth Conversion of Appreciated Assets",
        "irc": "IRC §402A, §408A, §408A(d)(3), §72",
        "category": "Retirement Plans",
        "overlap_group": "Roth Conversion Strategy",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_HAS_RETIREMENT_PLAN", False)
        and s.get("SIG_HIGH_INCOME", False),
        "materiality_fn": lambda s: (
            68
            if s.get("SIG_VERY_HIGH_INCOME", False)
            and s.get("SIG_HAS_RETIREMENT_PLAN", False)
            else 50
        ),
        "fed_savings_fn": lambda s: 100000
        * 0.07
        * s.get("_fed_marginal_rate", 0)
        * 0.2,
        "state_savings_fn": lambda s: 100000
        * 0.07
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
        * 0.2,
        "speed_days": 14,
        "complexity": 20,
        "audit_friction": 5,
        "plain_english": "A Roth conversion moves money from a traditional IRA to a Roth IRA — you pay tax now on the converted amount, but all future growth is tax-free and there are no required minimum distributions during your lifetime. An in-kind conversion means transferring the actual investments rather than selling first — particularly valuable when assets are temporarily down in value, since you pay tax on the lower current value and capture all future recovery tax-free inside the Roth. The best time to convert is in a low-income year — a practice transition year, a year with a large depreciation deduction, or before RMDs begin.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],
    },
    {
        "id": "DTTS-022-roth-conversion-ladder",
        "name": "Roth Conversion Ladder",
        "irc": "IRC §402A, §408A, §408A(d)(3), §408A(d)(3)(F), §401(a)(9)",
        "category": "Retirement Plans",
        "overlap_group": "Roth Conversion Strategy",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_HAS_RETIREMENT_PLAN", False)
        and s.get("SIG_HIGH_INCOME", False),
        "materiality_fn": lambda s: (
            70
            if s.get("SIG_VERY_HIGH_INCOME", False)
            and s.get("SIG_HAS_RETIREMENT_PLAN", False)
            else 52
        ),
        "fed_savings_fn": lambda s: 50000
        * max(0, s.get("_fed_marginal_rate", 0) - 0.24),
        "state_savings_fn": lambda s: 50000
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
        * 0.3,
        "speed_days": 14,
        "complexity": 20,
        "audit_friction": 5,
        "plain_english": "A Roth conversion ladder converts a portion of your traditional IRA to Roth every year — systematically, in controlled amounts — instead of all at once. The goal is to convert while your tax rate is lower than it will be in retirement when Required Minimum Distributions force large taxable withdrawals. Each year, you calculate how much you can convert while staying within a favorable tax bracket — typically to the top of the 22% or 24% bracket. Over 10-15 years, this can eliminate the entire traditional IRA balance at favorable rates, permanently reducing future RMDs and leaving a tax-free Roth estate for heirs.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],
    },
    {
        "id": "DTTS-044-in-plan-roth-rollover",
        "name": "In-Plan Roth Rollover",
        "irc": "IRC §402A, §402A(c)(4), §408A, §408A(d)(3)",
        "category": "Retirement Plans",
        "overlap_group": "Roth Conversion Strategy",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HAS_RETIREMENT_PLAN", False)
        and s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False),
        "materiality_fn": lambda s: (
            60
            if s.get("SIG_HAS_S_CORP") and s.get("SIG_HAS_RETIREMENT_PLAN")
            else (
                50
                if s.get("SIG_VERY_HIGH_INCOME")
                else 35 if s.get("SIG_HIGH_INCOME") else 25
            )
        ),
        "fed_savings_fn": lambda s: max(
            200000 * (s.get("_fed_marginal_rate", 0) - 0.22), 0
        ),
        "state_savings_fn": lambda s: 0,
        "speed_days": 21,
        "complexity": 20,
        "audit_friction": 10,
        "plain_english": "An in-plan Roth rollover allows a dentist to convert pre-tax retirement plan balances — 401(k), profit-sharing — into a designated Roth account within the same plan. The converted amount is taxable as ordinary income in the year of conversion, but all future growth and qualified distributions are completely tax-free. Under SECURE 2.0 (effective 2024), Roth 401(k) accounts no longer have required minimum distributions — allowing the balance to compound tax-free indefinitely. The strategy is most powerful when done in a year with lower than usual income or when large deductions (like cash balance contributions or bonus depreciation) are available to offset the conversion income. The mega backdoor Roth variant — converting after-tax 401(k) contributions — can add up to $43,500 of additional Roth funding annually beyond the standard contribution limit.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],
    },
    {
        "id": "DTTS-057-roth-conversions-during-low-income-years",
        "name": "Roth Conversions During Low-Income Years",
        "irc": "IRC §408A, §408A(d)(3), §402A, §72(t)",
        "category": "Retirement Plans",
        "overlap_group": "Roth Conversion Strategy",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HAS_RETIREMENT_PLAN", False)
        and s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False),
        "materiality_fn": lambda s: (
            65
            if s.get("SIG_RETIREMENT_UNDERFUNDED", False)
            and s.get("SIG_HIGH_TAX_LIABILITY", False)
            else 45 if s.get("SIG_HAS_RETIREMENT_PLAN", False) else 25
        ),
        "fed_savings_fn": lambda s: max(
            150000 * (s.get("_fed_marginal_rate", 0) - 0.22), 0
        ),
        "state_savings_fn": lambda s: 0,
        "speed_days": 14,
        "complexity": 15,
        "audit_friction": 5,
        "plain_english": "A Roth conversion moves pre-tax retirement savings into a Roth IRA — paying ordinary income tax on the converted amount now, in exchange for tax-free growth and distributions forever. The strategy is most powerful when done during low-income years: a year with a large business loss, significant bonus depreciation deductions, or a gap between leaving practice and starting required minimum distributions. The key technique is bracket filling — converting only enough to reach the top of the current tax bracket without crossing into the next. A dentist who normally pays 37% but has a year at 22% can convert $150,000 and save $22,500 in lifetime taxes on that amount. No income limit applies to conversions, there is no 10% penalty on conversion amounts, and Roth IRAs have no required minimum distributions — making them ideal for estate planning as well.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],
    },
    {
        "id": "DTTS-085-roth-401-k-and-mega-backdoor-roth",
        "name": "Roth 401(k) and Mega Backdoor Roth",
        "irc": "IRC §402A, §402A(b), §401(m), §408A, §402(c), §401(k)(2)(B)",
        "category": "Retirement Plans",
        "overlap_group": "Roth Conversion Strategy",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_W2_PRESENT", False)
        and s.get("SIG_HAS_RETIREMENT_PLAN", False),
        "materiality_fn": lambda s: (
            75
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HAS_RETIREMENT_PLAN")
            else (
                60
                if s.get("SIG_HIGH_INCOME") and s.get("SIG_HAS_RETIREMENT_PLAN")
                else 45 if s.get("SIG_HIGH_INCOME") else 30
            )
        ),
        "fed_savings_fn": lambda s: 23000 * (1.07**15 - 1) * 0.238 * 0.15,
        "state_savings_fn": lambda s: 0,
        "speed_days": 21,
        "complexity": 20,
        "audit_friction": 5,
        "plain_english": "High-income dentists cannot contribute directly to a Roth IRA (income limits phase out at $240,000 for married filers in 2024) — but the Roth 401(k) and mega backdoor Roth bypass that restriction entirely. A Roth 401(k) simply means designating regular elective deferrals (up to $23,000 in 2024, plus $7,500 catch-up if 50+) as Roth — after-tax today, tax-free forever. The mega backdoor Roth goes further: if the dental practice's 401(k) plan allows after-tax (non-Roth) contributions AND in-service withdrawals, the dentist can contribute up to $46,000 more in after-tax dollars, then immediately roll them to a Roth IRA. This creates up to $69,000 per year in total Roth-eligible contributions — dramatically accelerating tax-free retirement wealth. The key requirements: the plan document must explicitly permit after-tax contributions and in-service distributions — most off-the-shelf plan documents do not; a custom plan amendment is needed.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],
    },
    {
        "id": "DTTS-200-backdoor-roth-ira",
        "name": "Backdoor Roth IRA for High-Income W-2 Employees",
        "irc": "IRC §408A, §408A(c)(3)(B)",
        "category": "Retirement Plans",
        "overlap_group": "Roth Conversion Strategy",
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",
        "eligibility_logic": lambda s: s.get("SIG_W2_ONLY", False)
        and s.get("_agi", 0) > 240000
        and (not s.get("SIG_HAS_RETIREMENT_PLAN", False)),
        "materiality_fn": lambda s: 70 if s.get("_agi", 0) > 300000 else 50,
        "fed_savings_fn": lambda s: 7000 * s.get("_fed_marginal_rate", 0.32),
        "state_savings_fn": lambda s: 0,
        "speed_days": 7,
        "complexity": 10,
        "audit_friction": 5,
        "plain_english": "High-income W-2 employees cannot contribute directly to a Roth IRA due to income limits. The Backdoor Roth IRA is a legal workaround: make a non-deductible Traditional IRA contribution ($7,000 for 2024, or $8,000 if age 50+) and immediately convert it to Roth. This allows tax-free growth and withdrawals in retirement, even for high earners.",
        "prerequisites": [
            "No existing Traditional IRA, SEP IRA, or SIMPLE IRA balances",
            "W-2 income sufficient to make IRA contribution",
        ],
    }
]