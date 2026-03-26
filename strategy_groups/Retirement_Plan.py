from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-002-401-h-plan-add-on-to-db-plan",
        "name": "401(h) Plan Add-on to DB Plan",
        "irc": "IRC §401(h)",
        "category": "Retirement Plans",
        "overlap_group": "Retirement Plan — DB",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HAS_RETIREMENT_PLAN", False)
        and s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HEALTH_INS_EXPENSE", False),
        "materiality_fn": lambda s: (
            72
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HAS_RETIREMENT_PLAN")
            else (
                60
                if s.get("SIG_HIGH_INCOME") and s.get("SIG_HAS_RETIREMENT_PLAN")
                else (
                    55
                    if s.get("SIG_VERY_HIGH_INCOME")
                    else 40 if s.get("SIG_HIGH_INCOME") else 25
                )
            )
        ),
        "fed_savings_fn": lambda s: 50000 * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 50000
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 60,
        "complexity": 35,
        "audit_friction": 10,
        "plain_english": "A §401(h) account is a medical benefit sub-account attached to an existing defined benefit or cash balance plan. Contributions are tax-deductible to the employer and grow tax-free, funding post-retirement medical expenses for the owner and spouse. The §401(h) account can receive up to 25% of the total DB plan contributions in any year — on top of regular retirement contributions. Withdrawals used for qualified medical expenses are completely tax-free. For a dentist already running a cash balance plan, adding a §401(h) sub-account via plan amendment converts future medical costs into a fully deductible, tax-free benefit.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],
    },
    {
        "id": "DTTS-011-double-up-401-k-contributions-for-spouses",
        "name": "Double-Up 401(k) Contributions for Spouses",
        "irc": "IRC §401(k), §415, §402(g)",
        "category": "Retirement Plans",
        "overlap_group": "Retirement Plan — DC",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HAS_RETIREMENT_PLAN", False)
        and (s.get("SIG_HAS_S_CORP_VERIFIED", False) or s.get("SIG_HAS_C_CORP", False))
        and s.get("SIG_HIGH_INCOME", False),
        "materiality_fn": lambda s: (
            72
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HAS_RETIREMENT_PLAN")
            else 60 if s.get("SIG_HIGH_INCOME") else 40
        ),
        "fed_savings_fn": lambda s: 69000 * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 69000
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 21,
        "complexity": 20,
        "audit_friction": 15,
        "plain_english": "If your spouse performs real work for the dental practice and receives a W-2, they can participate in the 401(k) plan as a regular employee. This means the practice can contribute up to $69,000 to the spouse's 401(k) account in 2024 — on top of the owner's own contributions. A couple running a dental practice together can shelter up to $138,000 per year in combined retirement contributions. The spouse's role must be genuine with reasonable compensation for actual services — a paper arrangement without real work will not withstand IRS scrutiny.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
            "Requires related-party role, compensation, and documentation review before implementation.",
        ],
    },
    {
        "id": "DTTS-012-401k",
        "name": "Solo 401(k) / Traditional 401(k) + Profit Sharing",
        "irc": "IRC §402(g), §415",
        "category": "Retirement & Benefits",
        "overlap_group": "Retirement Plan — DC",
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",
        "eligibility_logic": lambda s: s.get("SIG_NO_RETIREMENT_PLAN", False)
        or s.get("SIG_RETIREMENT_UNDERFUNDED", False),
        "materiality_fn": lambda s: (
            100
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_NO_RETIREMENT_PLAN")
            else (
                80
                if s.get("SIG_HIGH_INCOME") and s.get("SIG_NO_RETIREMENT_PLAN")
                else (
                    70
                    if s.get("SIG_NO_RETIREMENT_PLAN")
                    else (
                        65
                        if s.get("SIG_VERY_HIGH_INCOME")
                        and s.get("SIG_RETIREMENT_UNDERFUNDED")
                        else 55 if s.get("SIG_HIGH_INCOME") else 40
                    )
                )
            )
        ),
        "fed_savings_fn": lambda s: min(
            min(
                get_lim(s)["defined_contribution_limit"],  # §415 DC limit ($69K/70K)
                s.get(
                    "Q_CASH_BALANCE_INCREMENTAL",
                    min(
                        get_lim(s)["defined_contribution_limit"],
                        # Employer contribution = 25% of comp; employee deferral on top.
                        # Use _obi_positive (NOL-safe) + wages as income base.
                        max(s.get("_obi_positive", 0), s.get("_wages", 0)) * 0.25
                        + get_lim(s)["elective_deferral_limit"],
                    ),
                ),
            ),
            s.get("_max_retirement_at_current_w2", 69_000),
        )
        * s.get("_fed_marginal_rate", 0.37),
        "state_savings_fn": lambda s: min(
            get_lim(s)["defined_contribution_limit"],
            max(s.get("_obi_positive", 0), s.get("_wages", 0)) * 0.25,
        )
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 30,
        "complexity": 15,
        "audit_friction": 5,
        "plain_english": "A 401(k) with profit sharing allows business owners to make large tax-deductible retirement contributions.",
        "prerequisites": [],
        "prerequisite_signals": ["SIG_BUSINESS_PRESENT"],
        "prerequisite_signals_any": ["SIG_SELF_EMPLOYED", "SIG_HAS_S_CORP_VERIFIED", "SIG_HAS_C_CORP"],
    },
    {
        "id": "DTTS-026-separate-property-election-in-community-states",
        "name": "Separate Property Election in Community Property States",
        "irc": "IRC §66, §66(a), §66(b), §66(c)",
        "category": "International & State",
        "overlap_group": "Retirement Plan",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_STATE_RETURN_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False)
        and (
            s.get("_primary_state", "")
            in ("AZ", "CA", "ID", "LA", "NV", "NM", "TX", "WA", "WI")
        ),
        "materiality_fn": lambda s: (
            55
            if s.get("SIG_SCHEDULE_C_PRESENT", False)
            or s.get("SIG_HAS_S_CORP_VERIFIED", False)
            else 35
        ),
        # Fix: Q_COMMUNITY_PROPERTY_PROBABILITY defaults to 0, silently zeroing savings.
        # Add questionnaire_gate + fallback_savings_estimate.
        "questionnaire_gates": ["Q_COMMUNITY_PROPERTY_PROBABILITY"],
        "fallback_savings_estimate": 12000,
        "fed_savings_fn": lambda s: min(s.get("_agi", 0) * 0.15, 21000)
        * s.get("Q_COMMUNITY_PROPERTY_PROBABILITY", 0.5),
        "state_savings_fn": lambda s: 0,
        "speed_days": 30,
        "complexity": 30,
        "audit_friction": 20,
        "plain_english": "In the nine community property states, income earned during marriage is generally owned equally by both spouses. The non-practicing spouse may be subject to self-employment tax on their 50% share. A separate property election or careful filing strategy can eliminate this SE tax exposure. Requires confirming state rules before implementation.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],
    },
    {
        "id": "DTTS-064-qualified-longevity-annuity-contract-qlac",
        "name": "Qualified Longevity Annuity Contract (QLAC)",
        "irc": "Treas. Reg. §1.401(a)(9)-6, IRC §401(a)(9), §408(b)",
        "category": "Retirement Plans",
        "overlap_group": "Retirement Plan",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HAS_RETIREMENT_PLAN", False)
        and s.get("SIG_HIGH_INCOME", False)
        and (s.get("_retirement", 0) > 200000),
        "materiality_fn": lambda s: (
            50
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_RETIREMENT_UNDERFUNDED")
            else (
                30
                if s.get("SIG_HIGH_INCOME") or s.get("SIG_RETIREMENT_UNDERFUNDED")
                else 20
            )
        ),
        "fed_savings_fn": lambda s: 8000 * s.get("_fed_marginal_rate", 0) + 3000,
        "state_savings_fn": lambda s: 8000 * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 30,
        "complexity": 20,
        "audit_friction": 5,
        "plain_english": "A Qualified Longevity Annuity Contract (QLAC) is an insurance product purchased inside an IRA or 401(k) that converts up to $200,000 of retirement savings into guaranteed lifetime income starting at age 80 or 85. The premium used to purchase the QLAC is excluded from the IRA balance for required minimum distribution calculations — reducing mandatory withdrawals for up to 12 years. For a dentist with a large IRA balance approaching age 73 and not needing all the RMD income, a QLAC reduces taxable withdrawals, potentially lowers Medicare premium surcharges (IRMAA), and reduces the percentage of Social Security benefits subject to income tax. The trade-off is illiquidity — the premium cannot be surrendered, and if the dentist dies before income payments begin, the premium is forfeited unless a return-of-premium rider is purchased.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],
    },
    {
        "id": "DTTS-091-defined-benefit-plan",
        "name": "Defined Benefit Plan",
        "irc": "IRC §401(a), §412, §415(b), §404(a)(1), §430, §436, §411, §416",
        "category": "Retirement Plans",
        "overlap_group": "Retirement Plan — DB",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and (
            s.get("SIG_NO_RETIREMENT_PLAN", False)
            or s.get("SIG_RETIREMENT_UNDERFUNDED", False)
        )
        and (
            # W-2 wages or officer compensation — both represent earned income
            # eligible for defined benefit plan contributions under IRC §404(a)(1)
            s.get("SIG_W2_PRESENT", False)
            or s.get("SIG_OFFICER_COMPENSATION", False)
            or s.get("SIG_HAS_C_CORP", False)
        )
        and (
            s.get("SIG_HAS_S_CORP_VERIFIED", False)
            or s.get("SIG_SELF_EMPLOYED", False)
            or s.get("SIG_BUSINESS_PRESENT", False)
            or s.get("SIG_HAS_C_CORP", False)
        ),
        "materiality_fn": lambda s: (
            85
            if s.get("SIG_VERY_HIGH_INCOME", False)
            and s.get("SIG_NO_RETIREMENT_PLAN", False)
            else (
                70
                if s.get("SIG_HIGH_INCOME", False)
                and s.get("SIG_NO_RETIREMENT_PLAN", False)
                else 50
            )
        ),
        "fed_savings_fn": lambda s: min(
            s.get("Q_CASH_BALANCE_INCREMENTAL", s.get("_max_db_contribution", 175000)),
            275000,
        )
        * s.get("_fed_marginal_rate", 0.37),
        "state_savings_fn": lambda s: min(
            s.get("Q_CASH_BALANCE_INCREMENTAL", s.get("_max_db_contribution", 175000)),
            275000,
        )
        * (s.get("_state_tax", 0) / s.get("_agi", 1) if s.get("_agi", 0) else 0.05),
        "speed_days": 60,
        "complexity": 45,
        "audit_friction": 15,
        "plain_english": "A defined benefit (DB) pension plan allows a practice to make far larger tax-deductible contributions than a standard 401(k). A DB contribution is actuarially determined based on the promised benefit, age, and years to retirement. Can be combined with a 401(k) for larger total contributions. Requires minimum funding yearly and actuary certification.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],
        "prerequisite_signals": ["SIG_BUSINESS_PRESENT"],
        "prerequisite_signals_any": ["SIG_SELF_EMPLOYED", "SIG_HAS_S_CORP_VERIFIED", "SIG_HAS_C_CORP"],
    },
    {
        "id": "DTTS-096-self-directed-ira-solo-401-k-for-re-notes",
        "name": "Self-Directed IRA / Solo 401(k) for RE & Notes",
        "irc": "IRC §408, §408(a), §408(e)(1), §4975, §4975(c), §511, §512, §401",
        "category": "Retirement Plans",
        "overlap_group": "Retirement Plan — DC",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HIGH_INCOME", False)
        and (
            s.get("SIG_HAS_RETIREMENT_PLAN", False)
            or s.get("SIG_REAL_ESTATE_ACTIVITY", False)
        ),
        "materiality_fn": lambda s: (
            65
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_REAL_ESTATE_ACTIVITY")
            else (
                45
                if s.get("SIG_REAL_ESTATE_ACTIVITY")
                and s.get("SIG_HAS_RETIREMENT_PLAN")
                else 35 if s.get("SIG_HIGH_INCOME") else 20
            )
        ),
        # Fix: Q_CASH_BALANCE_INCREMENTAL is 0 without questionnaire → use IRA limit as fallback.
        "questionnaire_gates": ["Q_CASH_BALANCE_INCREMENTAL"],
        "fallback_savings_estimate": 7000,
        "fed_savings_fn": lambda s: s.get("Q_CASH_BALANCE_INCREMENTAL",
            min(7000, s.get("_max_sep_contribution", 7000)))
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("Q_CASH_BALANCE_INCREMENTAL",
            min(7000, s.get("_max_sep_contribution", 7000)))
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 30,
        "complexity": 25,
        "audit_friction": 15,
        "plain_english": "A self-directed IRA or solo 401(k) allows a dentist to invest retirement funds in alternative assets — real estate, promissory notes, private equity, or even interests in other dental practices — with all income and gains sheltered from current taxes inside the account. Unlike standard IRAs that only hold stocks and mutual funds, a self-directed account can hold virtually any investment the IRS doesn't specifically prohibit. The most important rule is the prohibited transaction restriction: the dentist cannot buy property they already own, lend the IRA money to themselves or family members, or personally benefit from IRA investments — any prohibited transaction disqualifies the entire account, making all funds immediately taxable. If the IRA uses debt financing (mortgage) to buy real estate, the leveraged portion generates Unrelated Business Taxable Income (UBTI) — the IRA pays taxes on that at trust rates. A Roth solo 401(k) avoids this issue for qualified plan investors.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],
    },
    {
        "id": "DTTS-100-net-unrealized-appreciation-nua-tax-planning",
        "name": "Net Unrealized Appreciation (NUA) Tax Planning",
        "irc": "IRC §402(e)(4), §402(e)(4)(A), §402(e)(4)(D), §402(a), §1(h)",
        "category": "General Planning",
        "overlap_group": "Retirement Plan",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HAS_RETIREMENT_PLAN", False)
        and (s.get("SIG_HAS_S_CORP_VERIFIED", False) or s.get("SIG_HAS_C_CORP", False))
        and s.get("SIG_HIGH_INCOME", False)
        and (s.get("_retirement", 0) > 200000),
        "materiality_fn": lambda s: (
            50
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HAS_RETIREMENT_PLAN")
            else (
                30
                if s.get("SIG_HIGH_INCOME") or s.get("SIG_HAS_RETIREMENT_PLAN")
                else 20
            )
        ),
        "fed_savings_fn": lambda s: min(s.get("_retirement", 0) * 0.75, 1500000)
        * (s.get("_fed_marginal_rate", 0) - 0.2)
        * 0.2,
        "state_savings_fn": lambda s: 0,
        "speed_days": 30,
        "complexity": 25,
        "audit_friction": 10,
        "plain_english": "If a dentist's 401(k) or ESOP holds employer stock that has appreciated significantly inside the plan, the Net Unrealized Appreciation (NUA) rules offer a powerful tax break. Instead of rolling all plan assets to an IRA (which would make all future distributions taxable as ordinary income), the dentist takes the employer stock out in kind as part of a lump-sum distribution. The cost basis of the stock is taxed as ordinary income immediately — but the appreciation (NUA) is not taxed until the stock is sold, and then only at favorable long-term capital gains rates (0%, 15%, or 20%) — regardless of how long the dentist holds the shares after distribution. For employer stock that has grown from $500,000 to $2 million inside the plan, converting $1.5 million of NUA from 37% ordinary income rates to 20% capital gains rates saves over $250,000 in taxes. All other plan assets (non-employer securities) should be rolled to an IRA normally.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-118-backdoor-roth-ira",
        "name": "Backdoor Roth IRA",
        "irc": "IRC §408A, §408A(c)(3)(B), §408(o), §408A(d)(3), §408(d)(2)",
        "category": "Retirement Plans",
        # Fixed: removed duplicate overlap_group key (Python uses last value; was silently "Roth Conversion Strategy")
        "overlap_group": "Roth Conversion Strategy",
        "phase_1_eligible": True,
        # IRC-8 fix: use filing-status-aware threshold (MFJ $240K, Single $161K)
        "eligibility_logic": lambda s: s.get("SIG_HIGH_INCOME", False)
        and s.get("_agi", 0) > (240_000 if (s.get("_filing_status", "MFJ") or "").upper().startswith("M") else 161_000),
        "materiality_fn": lambda s: (
            45 if s.get("_agi", 0) > 240000 and s.get("SIG_W2_PRESENT", False) else 25
        ),
        "fed_savings_fn": lambda s: min(8000, s.get("_wages", 0) * 0.02) * 0.238,
        "state_savings_fn": lambda s: 0,
        "speed_days": 7,
        "complexity": 10,
        "audit_friction": 5,
        "plain_english": "High-income dentists are barred from contributing directly to a Roth IRA — the income limit phases out completely at $240,000 for married filers in 2024. The backdoor Roth IRA is a legal workaround: the dentist first makes a nondeductible contribution of $7,000 ($8,000 if age 50 or older) to a traditional IRA — there is no income limit for this step. Then, the dentist converts the traditional IRA to a Roth IRA. Because the contribution was after-tax (nondeductible), there is no additional tax on the conversion, and the money is now in a Roth account growing tax-free forever. The critical trap is the pro-rata rule: if the dentist has other pre-tax IRA funds (like a rollover IRA from a prior 401(k)), the IRS aggregates all IRA balances when calculating the taxable portion of the conversion — making much of the conversion taxable. The fix is to first roll pre-tax IRA funds back into the current employer's 401(k) plan, then execute the backdoor conversion with a clean slate.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],
    },
    {
        "id": "DTTS-119-employer-401-k-match",
        "name": "Employer 401(k) Match",
        "irc": "IRC §401(a), §401(k), §401(m), §415(c), §404(a)(3), §416, §411",
        "category": "Retirement Plans",
        "overlap_group": "Retirement Plan — DC",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_W2_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False)
        and (
            s.get("SIG_HAS_RETIREMENT_PLAN", False)
            or s.get("SIG_NO_RETIREMENT_PLAN", False)
        ),
        "materiality_fn": lambda s: (
            60
            if s.get("SIG_NO_RETIREMENT_PLAN", False)
            and s.get("SIG_HIGH_INCOME", False)
            else (
                40
                if s.get("SIG_HAS_RETIREMENT_PLAN", False)
                and s.get("SIG_W2_PRESENT", False)
                else 20
            )
        ),
        "fed_savings_fn": lambda s: s.get("_wages", 0)
        * 0.03
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("_wages", 0)
        * 0.03
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 30,
        "complexity": 20,
        "audit_friction": 5,
        "plain_english": "For dental practice owners, setting up or optimizing the employer 401(k) match is one of the most direct ways to maximize retirement contributions and reduce current taxes. Without a match or safe harbor election, the IRS requires annual non-discrimination testing (the ADP test) — if the non-owner employees don't contribute enough to the plan, the dentist's own contributions are limited and excess amounts must be refunded. By adopting a Safe Harbor 401(k) — committing to match 100% on the first 3% plus 50% on the next 2% of employee compensation, or a flat 3% employer contribution for all eligible employees — the practice permanently eliminates ADP/ACP testing. The owner can then maximize contributions up to the $69,000 annual IRS limit for 2024 ($76,500 if age 50 or older) regardless of how much staff contributes. The employer match cost itself is a fully deductible business expense, and the owner's contributions grow tax-deferred inside the plan.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires plan-level eligibility, contribution-limit, and payroll/adoption review before implementation.",
        ],
    },
    {
        "id": "DTTS-144-profit-sharing-plan",
        "name": "Profit-Sharing Retirement Plan",
        "irc": "IRC §401(a)",
        "category": "Retirement & Benefits",
        "overlap_group": "Retirement Plan — DC",
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_NO_RETIREMENT_PLAN", False)
        and (not s.get("SIG_W2_ONLY", False)),
        "materiality_fn": lambda s: (
            90
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 75 if s.get("SIG_HIGH_INCOME") else 60
        ),
        "fed_savings_fn": lambda s: min(
            min(
                get_lim(s)["defined_contribution_limit"],
                s.get(
                    "Q_CASH_BALANCE_INCREMENTAL",
                    # Use _obi_positive (NOL-safe) + wages; avoids negative-OBI collapse
                    min(
                        get_lim(s)["defined_contribution_limit"],
                        max(s.get("_obi_positive", 0), s.get("_wages", 0)) * 0.25,
                    ),
                ),
            ),
            s.get("_max_retirement_at_current_w2", 69_000),
        )
        * s.get("_fed_marginal_rate", 0.37),
        "state_savings_fn": lambda s: min(
            get_lim(s)["defined_contribution_limit"],
            max(s.get("_obi_positive", 0), s.get("_wages", 0)) * 0.25,
        )
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 30,
        "complexity": 20,
        "audit_friction": 5,
        "plain_english": "A profit-sharing retirement plan allows businesses to contribute a portion of profits to retirement accounts while receiving tax deductions for the contributions.",
        "prerequisites": [],
    },
    {
        "id": "DTTS-145-cash-balance",
        "name": "Cash Balance Plan — IRC §401(a)",
        "irc": "IRC §401(a), §412",
        "category": "Retirement & Benefits",
        "overlap_group": "Retirement Plan — DB",
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",
        "eligibility_logic": lambda s: s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_NO_RETIREMENT_PLAN", False),
        # Materiality: use entity_book_income / wages as proxy when AGI is unavailable
        "materiality_fn": lambda s: (
            95 if max(s.get("_agi", 0), s.get("_wages", 0), s.get("_entity_book_income", 0)) > 600_000
            else 80
        ),
        "fed_savings_fn": lambda s: min(
            s.get(
                "Q_CASH_BALANCE_INCREMENTAL",
                # Cash Balance plan: base is earned income (wages) or positive OBI.
                # §415(b) DB benefit limit (~$275K) exceeds DC limit — use _max_db_contribution.
                min(
                    s.get("_max_db_contribution", 175_000),
                    max(s.get("_obi_positive", 0), s.get("_wages", 0)) * 0.40,
                ),
            ),
            s.get("_max_db_contribution", 175_000),
        )
        * s.get("_fed_marginal_rate", 0.37),
        "state_savings_fn": lambda s: min(
            s.get("_max_db_contribution", 175_000),
            max(s.get("_obi_positive", 0), s.get("_wages", 0)) * 0.40,
        )
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 90,
        "complexity": 40,
        "audit_friction": 10,
        "plain_english": "A Cash Balance Plan allows high-income dentists to contribute large tax-deductible retirement contributions each year, often exceeding $100,000 annually depending on age and income.",
        "prerequisites": ["Consistent business income", "Actuarial firm engaged"],
    },
    {
        "id": "DTTS-146-self-directed-retirement-plan",
        "name": "Self-Directed Traditional Retirement Plan",
        "irc": "IRC §408",
        "category": "Retirement & Benefits",
        "overlap_group": "Retirement Plan",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HIGH_INCOME", False),
        "materiality_fn": lambda s: (
            65
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 50 if s.get("SIG_HIGH_INCOME") else 35
        ),
        "fed_savings_fn": lambda s: min(
            7000,
            s.get("Q_CASH_BALANCE_INCREMENTAL", 7000),
            s.get("_max_retirement_at_current_w2", 69000),
        )
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 7500
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 14,
        "complexity": 15,
        "audit_friction": 5,
        "plain_english": "Self-directed IRAs allow investments in real estate, private equity, and other alternative assets while maintaining normal IRA tax advantages.",
        "prerequisites": ["Self-directed IRA custodian"],
    },
    {
        "id": "DTTS-147-412e3-plan",
        "name": "412(e)(3) Plans",
        "irc": "IRC §412(e)(3)",
        "category": "Retirement & Benefits",
        "overlap_group": "Retirement Plan — DB",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_NO_RETIREMENT_PLAN", False),
        "materiality_fn": lambda s: (
            100
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 85 if s.get("SIG_HIGH_INCOME") else 70
        ),
        "fed_savings_fn": lambda s: min(
            min(
                s.get("_max_db_contribution", 175_000),
                s.get(
                    "Q_CASH_BALANCE_INCREMENTAL",
                    # 412(e)(3): fully-insured DB, funded via annuity/insurance contracts.
                    # Income base = wages or positive OBI; never use negative OBI.
                    min(
                        s.get("_max_db_contribution", 175_000),
                        max(s.get("_obi_positive", 0), s.get("_wages", 0)) * 0.40,
                    ),
                ),
            ),
            s.get("_max_db_contribution", 175_000),
        )
        * s.get("_fed_marginal_rate", 0.37),
        "state_savings_fn": lambda s: min(
            s.get("_max_db_contribution", 175_000),
            max(s.get("_obi_positive", 0), s.get("_wages", 0)) * 0.40,
        )
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 90,
        "complexity": 40,
        "audit_friction": 10,
        "plain_english": "A 412(e)(3) plan is a fully insured defined benefit plan allowing large tax-deductible contributions funded through insurance or annuity contracts.",
        "prerequisites": ["High consistent income"],
    },
    {
        "id": "DTTS-149-sep-ira",
        "name": "SEP IRA",
        "irc": "IRC §408(k)",
        "category": "Retirement & Benefits",
        "overlap_group": "Retirement Plan — DC",
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and (not s.get("SIG_W2_ONLY", False))
        and (
            s.get("SIG_SELF_EMPLOYED", False)
            or s.get("SIG_HAS_S_CORP_VERIFIED", False)
            or s.get("SIG_HAS_PARTNERSHIP", False)
            or s.get("SIG_SCHEDULE_C_PRESENT", False)
            # C-Corp employers can fund SEP IRAs for shareholder-employees — IRC §408(k)
            or s.get("SIG_HAS_C_CORP", False)
        ),
        "materiality_fn": lambda s: (
            85
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 70 if s.get("SIG_HIGH_INCOME") else 55
        ),
        "fed_savings_fn": lambda s: min(
            s.get(
                "_max_sep_contribution",
                min(
                    get_lim(s)["defined_contribution_limit"],
                    max(s.get("_obi_positive", 0), s.get("_wages", 0)) * 0.25,
                ),
            ),
            get_lim(s)["defined_contribution_limit"],
        )
        * s.get("_fed_marginal_rate", 0.37),
        "state_savings_fn": lambda s: min(
            s.get(
                "_max_sep_contribution",
                min(
                    get_lim(s)["defined_contribution_limit"],
                    max(s.get("_obi_positive", 0), s.get("_wages", 0)) * 0.25,
                ),
            ),
            get_lim(s)["defined_contribution_limit"],
        )
        * (s.get("_state_tax", 0) / s.get("_agi", 1) if s.get("_agi", 0) else 0),
        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 5,
        "plain_english": "A SEP-IRA allows business owners to contribute up to 25% of compensation toward retirement with minimal administrative complexity.",
        "prerequisites": ["Self-employment or business income"],
    },
    {
        "id": "DTTS-150-solo-401k",
        "name": "Solo 401(k)",
        "irc": "IRC §402(g), §415",
        "category": "Retirement & Benefits",
        "overlap_group": "Retirement Plan — DC",
        "phase_1_eligible": True,
        "estimate_confidence": "HIGH",
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_NO_RETIREMENT_PLAN", False)
        and (not s.get("SIG_W2_ONLY", False))
        and (
            s.get("SIG_SELF_EMPLOYED", False)
            or s.get("SIG_HAS_S_CORP_VERIFIED", False)
            or s.get("SIG_HAS_PARTNERSHIP", False)
            or s.get("SIG_SCHEDULE_C_PRESENT", False)
            # C-Corp owner-employees qualify for 401(k) plans funded by the corporation
            or s.get("SIG_HAS_C_CORP", False)
        ),
        "materiality_fn": lambda s: (
            95
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 80 if s.get("SIG_HIGH_INCOME") else 65
        ),
        "fed_savings_fn": lambda s: min(
            s.get(
                "_max_solo401k_total",
                min(
                    get_lim(s)["defined_contribution_limit"],
                    get_lim(s)["elective_deferral_limit"]
                    + max(s.get("_obi_positive", 0), s.get("_wages", 0)) * 0.25,
                ),
            ),
            get_lim(s)["defined_contribution_limit"],
        )
        * s.get("_fed_marginal_rate", 0.37),
        "state_savings_fn": lambda s: min(
            s.get(
                "_max_solo401k_total",
                min(
                    get_lim(s)["defined_contribution_limit"],
                    get_lim(s)["elective_deferral_limit"]
                    + max(s.get("_obi_positive", 0), s.get("_wages", 0)) * 0.25,
                ),
            ),
            get_lim(s)["defined_contribution_limit"],
        )
        * (s.get("_state_tax", 0) / s.get("_agi", 1) if s.get("_agi", 0) else 0),
        "speed_days": 21,
        "complexity": 15,
        "audit_friction": 5,
        "plain_english": "A Solo 401(k) allows self-employed professionals with no full-time employees to make both employee and employer contributions.",
        "prerequisites": ["No full-time non-owner employees"],
    },
    {
        "id": "DTTS-151-simple-ira",
        "name": "SIMPLE IRA",
        "irc": "IRC §408(p)",
        "category": "Retirement & Benefits",
        "overlap_group": "Retirement Plan — DC",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and (
            s.get("SIG_NO_RETIREMENT_PLAN", False)
            or s.get("SIG_RETIREMENT_UNDERFUNDED", False)
        )
        and s.get("SIG_W2_PRESENT", False),
        "materiality_fn": lambda s: (
            70
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 55 if s.get("SIG_HIGH_INCOME") else 40
        ),
        "fed_savings_fn": lambda s: min(
            min(
                16000,
                s.get(
                    "Q_CASH_BALANCE_INCREMENTAL",
                    min(
                        16000,
                        s.get("_wages", 0) * 0.5 if s.get("_wages", 0) > 0 else 5000,
                    ),
                ),
            ),
            s.get("_max_retirement_at_current_w2", 69000),
        )
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 15500
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 21,
        "complexity": 10,
        "audit_friction": 5,
        "plain_english": "A SIMPLE IRA is a retirement plan designed for small businesses. It allows employees to defer salary while the employer provides a matching contribution.",
        "prerequisites": ["Small business with ≤100 employees"],
    }
]