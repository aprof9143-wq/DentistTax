from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-027-state-tax-deduction-workaround-salt-cap",
        "name": "State Tax Deduction Workaround (SALT Cap)",
        "irc": "IRC §164, §164(b)(6), §164(a)(3), §199A",
        "category": "International & State",
        "overlap_group": "SALT PTET Workaround",
        "phase_1_eligible": True,
        # Fix: Q_PTET_CONFIRMED in eligibility_logic silently excluded the strategy
        # when questionnaire not provided. Moved to questionnaire_gates so strategy
        # shows as REQUIRES_QUESTIONNAIRE and gives a savings estimate.
        # SIG_PTET_OPPORTUNITY already validates: state is PTET-eligible + entity present +
        # PTET not already elected. Do NOT require SIG_HIGH_SALT or SIG_STATE_RETURN_PRESENT —
        # clients often upload only the federal return, so state return presence cannot be a gate.
        "eligibility_logic": lambda s: s.get("SIG_PTET_OPPORTUNITY", False)
        and (
            s.get("SIG_HAS_S_CORP_VERIFIED", False)
            or s.get("SIG_HAS_PARTNERSHIP", False)
        ),
        "questionnaire_gates": ["Q_PTET_CONFIRMED"],
        "fallback_savings_estimate": 8000,
        "materiality_fn": lambda s: (
            75
            if s.get("SIG_HAS_S_CORP_VERIFIED", False)
            and s.get("SIG_HIGH_INCOME", False)
            else 50
        ),
        # Estimate PTET savings from OBI regardless of Q_PTET_CONFIRMED so the
        # REQUIRES_QUESTIONNAIRE path returns a real estimate (×0.60) instead of
        # falling back to the flat fallback_savings_estimate.
        # Q_PTET_CONFIRMED still controls readiness; it no longer silences the savings.
        "fed_savings_fn": lambda s: max(
            s.get("_obi", 0) * s.get("Q_STATE_MARGINAL_RATE", 0.05)
            - _LIM["salt_cap"],
            0,
        )
        * s.get("_fed_marginal_rate", 0.37),
        "state_savings_fn": lambda s: 0,
        "speed_days": 21,
        "complexity": 20,
        "audit_friction": 10,
        "plain_english": "The SALT cap limits the deduction for state and local taxes at $10,000 for individuals. The Pass-Through Entity Tax (PTET) election allows the S-Corp or partnership to pay state income tax at the entity level, where it is fully deductible. The owner receives a dollar-for-dollar credit on their personal state return. This election is available in most high-tax states and can recover significant lost federal deductions.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
        "prerequisite_signals_any": ["SIG_HAS_S_CORP_VERIFIED", "SIG_HAS_PARTNERSHIP"],
    }
]