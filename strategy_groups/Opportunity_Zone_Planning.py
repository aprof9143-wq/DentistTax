from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-062-opportunity-zone-step-up-in-basis",
        "name": "Opportunity Zone Step-Up in Basis",
        "irc": "IRC §1400Z-1, §1400Z-2, §1400Z-2(a), §1400Z-2(b), §1400Z-2(c)",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Opportunity Zone Planning",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and (s.get("_capital_gains", 0) > 0),
        "event_trigger_logic": lambda s: s.get("SIG_ASSET_SALE_EVENT", False),
        "event_note": "No asset sale / capital gain event detected — §1400Z-2 requires a realized gain to defer",
        "readiness_if_prereq_fail": "REQUIRES_EVENT",
        "materiality_fn": lambda s: (
            80
            if s.get("_capital_gains", 0) > 500000
            else 65 if s.get("_capital_gains", 0) > 200000 else 50
        ),
        "fed_savings_fn": lambda s: max(0, s.get("_capital_gains", 0)) * 0.238 * 0.25,
        "state_savings_fn": lambda s: 0,
        "speed_days": 90,
        "complexity": 55,
        "audit_friction": 20,
        "plain_english": "Qualified Opportunity Zones allow a dentist who has recently sold an appreciated asset — real estate, a practice interest, or an investment portfolio — to defer the capital gains tax by reinvesting the gain into a Qualified Opportunity Fund within 180 days. The deferred gain is now fully taxable by December 31, 2026, but the real remaining benefit is the 10-year exclusion: if the QOF investment is held for at least 10 years, all appreciation on the investment above the original deferred amount is completely excluded from income. A dentist who reinvests $1 million of capital gain into a QOF that grows to $3 million over 10 years would owe tax on the original $1M gain but pay zero tax on the $2M of growth. This strategy requires commitment to a 10-year illiquid investment and careful selection of a qualifying opportunity fund.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],
    }
]