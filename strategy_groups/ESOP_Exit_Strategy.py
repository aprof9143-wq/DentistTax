from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-047-1042-rollover-sale-to-esop",
        "name": "1042 Rollover (Sale to ESOP)",
        "irc": "IRC §1042, §1042(a), §1042(b), §1042(c), §1042(d), §4975(e)(7)",
        "category": "Exit & Sale",
        "overlap_group": "ESOP Exit Strategy",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_HAS_C_CORP", False)
        and s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False),
        "materiality_fn": lambda s: (
            80
            if s.get("SIG_HAS_C_CORP", False) and s.get("SIG_VERY_HIGH_INCOME", False)
            else 40
        ),
        "fed_savings_fn": lambda s: 2800000 * 0.238 * 0.2,
        "state_savings_fn": lambda s: 0,
        "speed_days": 180,
        "complexity": 80,
        "audit_friction": 25,
        "plain_english": "The §1042 rollover allows a C-Corporation owner to sell stock to an Employee Stock Ownership Plan (ESOP) and defer all capital gains taxes — potentially indefinitely. The seller reinvests the proceeds into stocks or bonds of other domestic operating companies (qualified replacement property), and the gain is deferred until those replacement investments are sold. The ESOP must own at least 30% of the company's stock after the sale, and the seller must have held the stock for at least three years. This is one of the most powerful exit planning strategies available — a dental practice owner selling a $3M C-Corp interest could defer over $600,000 in capital gains taxes. The strategy requires the practice to be structured as a C-Corporation and involves significant ESOP administration and legal complexity.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-078-esop-employee-stock-ownership-plan-setup",
        "name": "ESOP (Employee Stock Ownership Plan) Setup",
        "irc": "IRC §4975(e)(7), §1042, §401(a), §404(a)(9), §404(k), §1368, §409(p)",
        "category": "Compensation & Benefits",
        "overlap_group": "ESOP Exit Strategy",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: (
            s.get("SIG_HAS_C_CORP", False) or s.get("SIG_HAS_S_CORP_VERIFIED", False)
        )
        and s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False),
        "materiality_fn": lambda s: (
            80
            if s.get("SIG_HAS_S_CORP_VERIFIED", False)
            and s.get("SIG_VERY_HIGH_INCOME", False)
            else (
                60
                if s.get("SIG_HAS_C_CORP", False)
                and s.get("SIG_VERY_HIGH_INCOME", False)
                else 30
            )
        ),
        "fed_savings_fn": lambda s: (
            min(s.get("_obi", 0), 500000) * s.get("_fed_marginal_rate", 0) * 0.15
            if s.get("SIG_HAS_S_CORP_VERIFIED", False)
            else 125000 * 0.21 * 0.15
        ),
        "state_savings_fn": lambda s: 0,
        "speed_days": 365,
        "complexity": 85,
        "audit_friction": 30,
        "plain_english": "An Employee Stock Ownership Plan (ESOP) is a qualified retirement plan that holds employer stock and offers some of the most powerful tax benefits available to dental practice owners. For an S-Corporation that becomes 100% ESOP-owned, all corporate income flows to the ESOP trust — which is tax-exempt — meaning the corporation effectively pays no federal income tax. This is the single most powerful ongoing income tax elimination strategy available in the tax code. For C-Corporation owners, the §1042 rollover allows deferral of all capital gains on the sale to the ESOP (see DTTS-047). The corporation can also deduct contributions to the ESOP of up to 25% of covered payroll annually. Important caveat for dentists: state dental practice laws may restrict who can own a dental professional corporation — ESOP feasibility requires a professional corporation law analysis in the practice state before proceeding.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-090-installment-sale-to-esop-with-1042-rollover",
        "name": "Installment Sale to ESOP with §1042 Rollover",
        "irc": "IRC §1042, §1042(a), §1042(b), §1042(c), §1042(d), §453, §4975(e)(7)",
        "category": "Exit & Sale",
        "overlap_group": "ESOP Exit Strategy",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_HAS_C_CORP", False)
        and s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False),
        "materiality_fn": lambda s: (
            85
            if s.get("SIG_HAS_C_CORP", False) and s.get("SIG_VERY_HIGH_INCOME", False)
            else 30
        ),
        "fed_savings_fn": lambda s: 2700000 * 0.238 * 0.25,
        "state_savings_fn": lambda s: 2700000
        * s.get("Q_STATE_MARGINAL_RATE", 0.05)
        * 0.15,
        "speed_days": 365,
        "complexity": 85,
        "audit_friction": 25,
        "plain_english": "When a C-Corporation dental practice owner sells at least 30% of their stock to an ESOP, they can elect under §1042 to defer — and potentially eliminate — all capital gains on the sale. The seller takes the proceeds and reinvests them in 'Qualified Replacement Property' (QRP) — typically floating-rate bonds or private operating company stock. The gain is deferred as long as the QRP is held. If the seller holds the QRP until death, heirs receive a stepped-up basis and the original deferred gain disappears entirely — a permanent tax elimination. Combining §1042 with an installment note from the ESOP creates additional flexibility: the seller receives payments over time and can manage QRP reinvestment timing. Critical requirements: the entity must be a C-Corporation (not S-Corp), the ESOP must own ≥30% after the sale, and the stock must have been held at least three years. State dental licensing laws may limit ESOP ownership of professional dental corporations.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    }
]