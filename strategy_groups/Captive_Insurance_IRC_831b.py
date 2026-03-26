from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-120-captive-insurance-831-b",
        "name": "Captive Insurance (831(b))",
        "irc": "IRC §831(b), §162, §953(d), §7701(o)",
        "category": "Insurance & Risk",
        "overlap_group": "Captive Insurance (IRC §831(b))",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and (s.get("_total_tax", 0) > 100000),
        "materiality_fn": lambda s: (
            70
            if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("_total_tax", 0) > 150000
            else 40
        ),
        "fed_savings_fn": lambda s: 500000 * s.get("_fed_marginal_rate", 0) * 0.2,
        "state_savings_fn": lambda s: 500000
        * 0.05
        * s.get("Q_STATE_MARGINAL_RATE", 0.2),
        "speed_days": 180,
        "complexity": 75,
        "audit_friction": 45,
        "plain_english": "A captive insurance company is an insurance company that the dentist owns, which insures the dental practice against genuine business risks. Under IRC §831(b), small insurance companies with premiums up to $2.8 million per year pay no income tax on premium revenue — only on investment income. The dental practice deducts the premiums as a business expense, and the premiums accumulate inside the captive as a growing asset owned by the dentist. This strategy requires the captive to insure real risks that the practice genuinely faces — such as regulatory defense costs, cyber liability, business interruption, or other coverage gaps — with premiums set by an independent actuary at arm's-length rates. The IRS has aggressively audited captive arrangements since 2014 and has designated many as Listed Transactions requiring Form 8886 disclosure. Improperly structured captives — those with implausible risks, inflated premiums, or no real risk distribution — have been repeatedly invalidated in Tax Court. A properly structured captive with genuine risk, actuarial pricing, and risk distribution remains legally viable but requires expert insurance and tax counsel.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires policy design, underwriting/actuarial review, and compliance documentation before implementation.",
        ],
    }
]