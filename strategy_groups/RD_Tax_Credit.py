from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-116-r-d-tax-credit",
        "name": "R&D Tax Credit",
        "irc": "IRC §41, §41(b), §41(d), §41(d)(4), §280C(c), §174",
        "category": "Credits & Incentives",
        "overlap_group": "R&D Tax Credit",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False),
        "materiality_fn": lambda s: (
            40
            if s.get("SIG_HIGH_TAX_LIABILITY", False)
            and s.get("SIG_BUSINESS_PRESENT", False)
            else 15
        ),
        "fed_savings_fn": lambda s: s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.02 * 0.14,
        "state_savings_fn": lambda s: s.get("Q_INVESTMENT_PORTFOLIO", 0)
        * 0.02
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 60,
        "complexity": 35,
        "audit_friction": 25,
        "plain_english": "The Research and Development Tax Credit (§41) provides a credit of up to 20% of qualified research expenditures — including wages paid to employees doing research and development, research supplies, and contract research costs. For dental practices, qualifying activities are narrow: developing novel treatment protocols, custom designing dental devices or digital prosthetics, building proprietary software for practice management or diagnostics, or conducting genuine experimental research into new dental techniques. Standard patient care, adapting existing procedures, and following established dental protocols do not qualify. Dentists who develop novel digital workflows (e.g., custom CAD/CAM implant designs, AI-assisted diagnostic tools, or proprietary practice management software) may have significant qualifying R&D wages and supplies. An important change: starting in 2022, R&D expenses must be capitalized and amortized over 5 years rather than expensed immediately — this interacts with the credit calculation under §280C. Many states also offer their own R&D credits that can be stacked.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-156-rd-tax-credit",
        "name": "Research & Development Tax Credit",
        "irc": "IRC §41",
        "category": "Credits & Special Incentives",
        "overlap_group": "R&D Tax Credit",
        "phase_1_eligible": False,
        "estimate_confidence": "LOW",
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_DENTIST_CONFIRMED", False)
        and (s.get("Q_MGMT_CO_REVENUE", 0) > 0),
        "materiality_fn": lambda s: (
            85
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 70 if s.get("SIG_HIGH_INCOME") else 55
        ),
        "fed_savings_fn": lambda s: s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.05 * 0.14,
        "state_savings_fn": lambda s: s.get("Q_INVESTMENT_PORTFOLIO", 0)
        * 0.05
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 60,
        "complexity": 30,
        "audit_friction": 20,
        "plain_english": "Businesses that develop new processes, technologies, or products may qualify for the federal research and development tax credit.",
        "prerequisites": ["Qualified research activity"],
    }
]