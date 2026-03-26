from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-007-c-corp-dividends-planning",
        "name": "C-Corp Dividends Planning",
        "irc": "IRC §§301–316, §1(h)(11), §11, §531",
        "category": "Entity & Structuring",
        "overlap_group": "C-Corp Planning",
        "phase_1_eligible": False,
        "applicable_surfaces": ["1120", "1040", "MIXED"],
        "eligibility_logic": lambda s: s.get("SIG_HAS_C_CORP", False)
        and (
            (s.get("SIG_VERY_HIGH_INCOME", False) and s.get("SIG_HIGH_TAX_LIABILITY", False))
            or (
                s.get("_context_mode") == "ENTITY_ONLY"
                and s.get("SIG_ENTITY_VERY_HIGH_OBI", False)
                and s.get("SIG_ENTITY_HIGH_C_CORP_TAX", False)
            )
        ),
        "materiality_fn": lambda s: (
            65
            if s.get("SIG_HAS_C_CORP", False)
            and (
                s.get("SIG_VERY_HIGH_INCOME", False)
                or (
                    s.get("_context_mode") == "ENTITY_ONLY"
                    and s.get("SIG_ENTITY_VERY_HIGH_OBI", False)
                )
            )
            else 40
        ),
        "fed_savings_fn": lambda s: 200000
        * max(0, s.get("_fed_marginal_rate", 0) - 0.21)
        * 0.3,
        "state_savings_fn": lambda s: 200000
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
        * 0.2,
        "speed_days": 45,
        "complexity": 30,
        "audit_friction": 15,
        "plain_english": "A C-Corporation pays a flat 21% federal income tax rate on its earnings. When those earnings are distributed to shareholders as qualified dividends, they are taxed at the preferential 20% capital gains rate — plus 3.8% NIIT for high earners. The combined effective rate is often comparable to S-Corp pass-through rates at top brackets. The real advantage is the C-Corp's ability to retain earnings at 21% and redeploy them inside the entity — buying equipment, funding benefits, or accumulating for a future sale — before any shareholder-level tax is triggered. This deferral creates compounding value over time. Excessive accumulation beyond reasonable business needs risks the §531 accumulated earnings tax at 20%.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    }
]