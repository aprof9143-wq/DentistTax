from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-004-maximizing-qbi-via-entity-restructure",
        "name": "Maximizing QBI via Entity Restructure",
        "irc": "IRC §199A, §199A(b)(2), §199A(b)(3), §199A(d)(2), §199A(d)(3), §199A(e)(4)",
        "category": "Entity & Structuring",
        "overlap_group": "QBI Optimization",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HAS_S_CORP_VERIFIED", False)
        and s.get("SIG_MULTI_ENTITY", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and (s.get("Q_MGMT_CO_REVENUE", 0) > 0),
        "materiality_fn": lambda s: (
            80
            if s.get("SIG_VERY_HIGH_INCOME", False)
            and s.get("SIG_HAS_S_CORP_VERIFIED", False)
            else 60
        ),
        "fed_savings_fn": lambda s: s.get(
            "Q_QBI_RESTRUCTURE_DEDUCTION", s.get("_obi", 0) * 0.04
        )
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 0,
        "speed_days": 45,
        "complexity": 35,
        "audit_friction": 15,
        "plain_english": "The §199A QBI deduction gives pass-through business owners up to a 20% deduction on qualified business income. If the practice is an SSTB, the deduction phases out above $483,900 of taxable income for married filers. Entity restructuring — separating the clinical practice from a non-clinical management company or real estate entity — can carve out non-SSTB income eligible for the full deduction. Maximizing W-2 wages paid by the S-Corp also unlocks more of the deduction within the phase-out range.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-024-qbi-deduction-optimization",
        "name": "QBI Deduction Optimization",
        "irc": "IRC §199A, §199A(b)(2), §199A(b)(3), §199A(d)(3), §199A(e)(4)",
        "category": "General Planning",
        "overlap_group": "QBI Optimization",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HAS_S_CORP_VERIFIED", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and (not s.get("SIG_SSTB_ABOVE_PHASEOUT", False))
        and s.get("SIG_QBI_MISSING", False),
        "materiality_fn": lambda s: (
            82
            if s.get("SIG_VERY_HIGH_INCOME", False)
            and s.get("SIG_HAS_S_CORP_VERIFIED", False)
            else 65
        ),
        "fed_savings_fn": lambda s: s.get(
            "Q_QBI_RESTRUCTURE_DEDUCTION", s.get("_obi", 0) * 0.05
        )
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 0,
        "speed_days": 21,
        "complexity": 25,
        "audit_friction": 10,
        "plain_english": "The §199A QBI deduction allows pass-through business owners to deduct up to 20% of qualified business income. Service businesses are subject to a phase-out above $483,900 for married filers. QBI optimization focuses on maximizing the deduction: setting the right W-2 salary level, tracking qualified property basis, and using retirement contributions to reduce taxable income below the phase-out threshold.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-028-qbi",
        "name": "Qualified Business Income (QBI) Deduction — §199A",
        "irc": "IRC §199A",
        "category": "Deduction & Reimbursement",
        "overlap_group": "QBI Optimization",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_QBI_MISSING", False)
        and (not s.get("SIG_HAS_C_CORP", False))
        and (s.get("_obi", 0) > 0)
        and (s.get("_agi", 0) < _LIM["qbi_sstb_phaseout_mfj"]),
        "materiality_fn": lambda s: 85 if s.get("SIG_QBI_MISSING", False) else 50,
        "fed_savings_fn": lambda s: max(s.get("_obi", 0), s.get("_wages", 0))
        * 0.2
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 0,
        "speed_days": 7,
        "complexity": 15,
        "audit_friction": 10,
        "plain_english": "The §199A deduction allows pass-through business owners to deduct up to 20% of qualified business income. Proper wage and income planning can maximize this deduction.",
        "prerequisites": ["Pass-through entity or self-employment income"],
    }
]