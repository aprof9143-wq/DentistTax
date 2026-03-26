from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-093-s-corp-reasonable-compensation-planning",
        "name": "S-Corp Reasonable Compensation Planning",
        "irc": "IRC §162, §1366, §3121, §3121(a), §61, §1402(a)(2), Rev. Rul. 74-44",
        "category": "Entity & Structuring",
        "overlap_group": "S-Corp Compensation",
        "phase_1_eligible": True,
        "applicable_surfaces": ["1120S", "1040", "MIXED"],
        "eligibility_logic": lambda s: s.get("SIG_HAS_S_CORP_VERIFIED", False)
        and (s.get("SIG_HIGH_INCOME", False) or s.get("SIG_ENTITY_HIGH_OBI", False))
        and (s.get("_distributions", 0) > 0)
        and (
            s.get("SIG_LOW_OWNER_WAGES", False)
            or s.get("SIG_HIGH_DISTRIBUTIONS_VS_WAGES", False)
        ),
        "materiality_fn": lambda s: (
            75
            if s.get("SIG_LOW_OWNER_WAGES", False) and s.get("SIG_HIGH_INCOME", False)
            else (
                55
                if s.get("SIG_HAS_S_CORP_VERIFIED", False)
                and s.get("SIG_HIGH_INCOME", False)
                else 35
            )
        ),
        # Fix: formula was inverted — it only produced savings when wages EXCEEDED target,
        # but this strategy applies when wages are TOO LOW vs OBI.
        # The "savings" here represents FICA leakage recovered by raising salary to defensible level
        # (IRS will reclassify distributions → SE tax due). Quantify as future audit exposure.
        "fed_savings_fn": lambda s: max(
            0,
            (s.get("_obi", 0) * 0.4 - s.get("_wages", 0)) * 0.153 * 0.9235
            if s.get("_obi", 0) * 0.4 > s.get("_wages", 0) > 0 else 0
        ),
        "state_savings_fn": lambda s: 0,
        "speed_days": 14,
        "complexity": 30,
        "audit_friction": 25,
        "plain_english": "AUDIT RISK: S-Corp owners must pay themselves reasonable compensation. If W-2 wages are below 30–40% of practice income, the IRS may reclassify distributions as wages on audit. Raise salary to a defensible level, documented with compensation surveys. This also unlocks retirement plan contributions.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
        "prerequisite_signals_any": ["SIG_K1_FROM_S_CORP", "SIG_HAS_S_CORP_VERIFIED"],
    }
]