from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-051-non-qualified-deferred-compensation-nqdc-plan",
        "name": "Non-Qualified Deferred Compensation (NQDC) Plan",
        "irc": "IRC §409A, §409A(a), §409A(a)(2), §409A(a)(4), §457(f), §83",
        "category": "Compensation & Benefits",
        "overlap_group": "Deferred Compensation",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and s.get("SIG_W2_PRESENT", False),
        "materiality_fn": lambda s: (
            60
            if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("SIG_W2_PRESENT", False)
            else 40
        ),
        "fed_savings_fn": lambda s: s.get("_obi", 0)
        * 0.1
        * max(0, s.get("_fed_marginal_rate", 0) - 0.22),
        "state_savings_fn": lambda s: 0,
        "speed_days": 45,
        "complexity": 35,
        "audit_friction": 20,
        "plain_english": "A Non-Qualified Deferred Compensation (NQDC) plan allows a high-income dentist to defer a portion of current compensation to future years — paying tax when the money is received in retirement rather than when it is earned today. For a dentist currently in the 37% bracket who expects to be in the 22% bracket in retirement, deferring $100,000 of salary saves $15,000 in federal tax on that amount alone. The plan must comply strictly with §409A — elections must be made before December 31 of the year before the compensation is earned, and distributions are limited to specific triggering events like separation from service or a fixed payment schedule. Unlike qualified retirement plans, NQDC balances are unsecured obligations of the practice — the dentist is a general creditor. Violations of §409A trigger immediate income inclusion plus a 20% excise tax and interest, so plan design must be precise.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-054-457-b-non-governmental-deferred-comp-plan",
        "name": "457(b) Non-Governmental Deferred Comp Plan",
        "irc": "IRC §457, §457(b), §457(b)(2), §457(b)(3), §457(e)(12)",
        "category": "General Planning",
        "overlap_group": "Deferred Compensation",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and s.get("SIG_W2_PRESENT", False),
        "materiality_fn": lambda s: (
            50
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else (
                30
                if s.get("SIG_HIGH_INCOME") or s.get("SIG_HIGH_TAX_LIABILITY")
                else 20
            )
        ),
        "fed_savings_fn": lambda s: min(
            _LIM["elective_deferral_limit"], s.get("_wages", 0) * 0.1
        )
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: min(
            _LIM["elective_deferral_limit"], s.get("_wages", 0) * 0.1
        )
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 21,
        "complexity": 20,
        "audit_friction": 10,
        "plain_english": "Dentists employed by tax-exempt organizations — dental schools, hospital-affiliated practices, or federally qualified health centers — may have access to a §457(b) deferred compensation plan in addition to their 401(k) or 403(b). The key advantage: §457(b) contributions are completely separate from and do not reduce contributions to a 401(k) or 403(b) plan — meaning a dentist in this situation can defer an additional $23,000 (or $30,500 if age 50+) on top of their other retirement plan contributions. The deferred amounts are excluded from gross income until distributed. The non-governmental version differs from the governmental version in that assets remain general assets of the employer — the participant is an unsecured creditor. A special three-year catch-up provision allows up to double the annual limit in the final three years before normal retirement age for participants who under-deferred in prior years.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    }
]