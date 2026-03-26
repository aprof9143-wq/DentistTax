from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-COMBO-salary-retirement-restructure",
        "name": "Salary + Retirement Plan Restructure",
        "irc": "IRC §162, §401(a), §412, §415(c), §3121",
        "category": "Retirement & Benefits",
        "overlap_group": "Salary Retirement Combo",
        "phase_1_eligible": True,
        "estimate_confidence": "MODERATE",
        "eligibility_logic": lambda s: s.get("SIG_HAS_S_CORP_VERIFIED", False)
        and s.get("SIG_LOW_OWNER_WAGES", False)
        and s.get("SIG_NO_RETIREMENT_PLAN", False)
        and s.get("SIG_RETIREMENT_W2_CONSTRAINED", False)
        and (s.get("_obi", 0) > 200000),
        "materiality_fn": lambda s: (
            95 if s.get("_obi", 0) > 400000 else 85 if s.get("_obi", 0) > 250000 else 70
        ),
        "fed_savings_fn": lambda s: (
            lambda target, wages, marg: min(target * 0.6 + 23000, 143000) * marg
            - (
                min(target, 168600) * 0.153
                + max(0, target - 168600) * 0.029
                - (min(wages, 168600) * 0.153 + max(0, wages - 168600) * 0.029)
            )
            * (1 - 0.5 * marg)
        )(
            min(s.get("_obi", 0) * 0.4, 200000),
            s.get("_wages", 0),
            s.get("_fed_marginal_rate", 0),
        ),
        # Fix: replaced hardcoded 9.3% CA rate with dynamic state rate from signals.
        "state_savings_fn": lambda s: min(
            min(s.get("_obi", 0) * 0.4, 200000) * 0.6 + 23000, 143000
        )
        * s.get("Q_STATE_MARGINAL_RATE",
                s.get("_state_tax", 0) / s.get("_agi", 1) if s.get("_agi", 0) else 0.05),
        "speed_days": 60,
        "complexity": 35,
        "audit_friction": 15,
        "plain_english": "This is the highest-impact restructuring for an S-Corp dentist with low W-2 wages and no retirement plan. Step 1: Raise your S-Corp salary to a defensible level (~40% of practice income, documented with ADA/MGMA surveys). Step 2: Implement a Cash Balance Plan (or Solo 401(k) + DB combo) and contribute the maximum allowable amount — typically $100K–$140K+ per year depending on age. The retirement contributions create large tax deductions that far exceed the additional FICA cost of raising your salary. Net federal savings of $20K–$30K per year after FICA cost, plus $10K–$13K in state savings. This single restructuring captures more value than all other strategies combined.",
        "prerequisites": [
            "S-Corp entity in place",
            "Reasonable compensation study completed",
            "Retirement plan selected and adopted",
        ],
    }
]