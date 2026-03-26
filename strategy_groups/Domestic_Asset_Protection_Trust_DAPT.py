from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-070-asset-protection-trust-structure-dapt",
        "name": "Asset Protection Trust Structure (DAPT)",
        "irc": "IRC §671, §677, §2036, §167, §168, §469",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Domestic Asset Protection Trust (DAPT)",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and (s.get("_agi", 0) > 750000),
        "materiality_fn": lambda s: (
            60
            if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("_agi", 0) > 1000000
            else 35
        ),
        "fed_savings_fn": lambda s: 2000000 * 0.4 * 0.2,
        "state_savings_fn": lambda s: 0,
        "speed_days": 120,
        "complexity": 70,
        "audit_friction": 25,
        "plain_english": "A Domestic Asset Protection Trust (DAPT) is a self-settled irrevocable trust established in a favorable state — Alaska, Nevada, South Dakota, Delaware, or Wyoming — that allows the dentist to be a discretionary beneficiary while shielding assets from future creditors. Unlike a traditional irrevocable trust, the grantor can receive distributions at the trustee's discretion, while future creditors (including malpractice plaintiffs) are barred from reaching trust assets after the applicable statute of limitations expires (typically 2–4 years). The trust is structured as a grantor trust for income tax — meaning the dentist still pays all income taxes on trust earnings, which itself constitutes an additional tax-free wealth transfer to the trust beneficiaries. Existing creditors are not protected, and federal bankruptcy law may limit DAPT effectiveness in some circumstances. This is primarily an asset protection and estate planning tool, not an income tax reduction strategy.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],
    }
]