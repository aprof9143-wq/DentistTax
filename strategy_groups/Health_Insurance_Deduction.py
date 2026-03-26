from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-003-s-corp-2-shareholder-health-deduction",
        "name": "S-Corp 2% Shareholder Health Deduction",
        "irc": "IRC §162(l), §1372; Notice 2008-1",
        "category": "Entity & Structuring",
        "overlap_group": "Health Insurance Deduction",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HAS_S_CORP_VERIFIED", False)
        and s.get("SIG_HEALTH_INS_EXPENSE", False),
        "materiality_fn": lambda s: (
            68
            if s.get("SIG_HAS_S_CORP_VERIFIED", False)
            and s.get("SIG_HEALTH_INS_EXPENSE", False)
            else 45
        ),
        "fed_savings_fn": lambda s: s.get("Q_HEALTH_DEDUCTION_AVAILABLE", 0)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("Q_HEALTH_DEDUCTION_AVAILABLE", 0)
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 5,
        "plain_english": "An S-Corp owner who owns more than 2% of the company cannot receive health insurance as a tax-free employee fringe benefit. Instead, the S-Corp pays the premium, includes it in the owner's W-2 wages, and the owner deducts it above-the-line on Schedule 1 under §162(l). The net result is the same as a self-employed health insurance deduction — the premium reduces AGI without requiring itemization — but only if the procedure is followed exactly. If the premium is not run through payroll and included in the W-2, the deduction is lost entirely.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-050-group-health-insurance-via-c-corp",
        "name": "Group Health Insurance via C-Corp",
        "irc": "IRC §105, §105(b), §106, §162, §125",
        "category": "Entity & Structuring",
        "overlap_group": "Health Insurance Deduction",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HAS_C_CORP", False)
        and s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False),
        "materiality_fn": lambda s: (
            55
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HAS_C_CORP")
            else 35 if s.get("SIG_HIGH_INCOME") or s.get("SIG_HAS_C_CORP") else 25
        ),
        "fed_savings_fn": lambda s: s.get("Q_HEALTH_PREMIUM", 0)
        * 1.0765
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("Q_HEALTH_PREMIUM", 0)
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 30,
        "complexity": 25,
        "audit_friction": 10,
        "plain_english": "A C-Corporation can provide group health insurance to owner-employees with better tax treatment than any other entity structure. The corporation deducts 100% of premiums as a business expense, and the owner-employee excludes the premium value from their gross income entirely — no income tax, no FICA. This is more favorable than an S-Corporation, where shareholders owning more than 2% must include health premiums in their W-2 wages (even though the deduction is then available on the personal return). A C-Corp can also establish a Health Reimbursement Arrangement (HRA) to reimburse out-of-pocket medical expenses tax-free. For a dentist with a management company or holding entity structured as a C-Corporation, routing health insurance through that entity produces the cleanest tax result.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires policy design, underwriting/actuarial review, and compliance documentation before implementation.",
        ],
    },
    {
        "id": "DTTS-084-section-105-medical-reimbursement-plan-hra-flexibility-qsehra-ichra-etc",
        "name": "Section §105 Medical Reimbursement Plan HRA Flexibility (QSEHRA, ICHRA, etc.)",
        "irc": "IRC §105, §105(b), §105(h), §106, §9831(d), §213",
        "category": "Compensation & Benefits",
        "overlap_group": "Health Insurance Deduction",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_W2_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False)
        and (s.get("Q_HEALTH_PREMIUM", 0) > 0)
        and s.get("SIG_HEALTH_INS_EXPENSE", False),
        "materiality_fn": lambda s: (
            55
            if s.get("SIG_HEALTH_INS_EXPENSE", False) and s.get("SIG_HAS_C_CORP", False)
            else (
                40
                if s.get("SIG_HEALTH_INS_EXPENSE", False)
                and s.get("SIG_HIGH_INCOME", False)
                else 20
            )
        ),
        "fed_savings_fn": lambda s: s.get("Q_HEALTH_PREMIUM", 0)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("Q_HEALTH_PREMIUM", 0)
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 21,
        "complexity": 20,
        "audit_friction": 10,
        "plain_english": "A Health Reimbursement Arrangement (HRA) allows a dental practice to reimburse employees — including the owner-dentist — for health insurance premiums and qualified medical expenses tax-free. There are two main flavors: QSEHRA (for practices with fewer than 50 full-time employees) reimburses up to $12,450 per family annually with no income tax or FICA on the reimbursement; ICHRA (available to any size employer) has no dollar cap and allows reimbursement of individual plan premiums. Unlike individual medical expense deductions (which require exceeding 7.5% of AGI), HRA reimbursements are fully excluded from income from dollar one. Important nuance: S-Corporation shareholders owning more than 2% cannot participate in a §125 cafeteria plan — but can often still benefit from a properly designed ICHRA or have premiums treated as W-2 income and then deducted above-the-line. C-Corporation owners receive the full §105/106 benefit with no restrictions.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-124-s-corp-health-reimbursement-arrangement-qsehra",
        "name": "S-Corp Health Reimbursement Arrangement (QSEHRA)",
        "irc": "IRC §105, §105(b), §105(h), §106, §9831(d)",
        "category": "Entity & Structuring",
        "overlap_group": "Health Insurance Deduction",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HAS_S_CORP_VERIFIED", False)
        and s.get("SIG_W2_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False)
        and (s.get("Q_HEALTH_PREMIUM", 0) > 0)
        and s.get("SIG_HEALTH_INS_EXPENSE", False),
        "materiality_fn": lambda s: (
            50
            if s.get("SIG_HEALTH_INS_EXPENSE", False)
            and s.get("SIG_HAS_S_CORP_VERIFIED", False)
            else 25
        ),
        "fed_savings_fn": lambda s: s.get("Q_HEALTH_PREMIUM", 0)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("Q_HEALTH_PREMIUM", 0)
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 14,
        "complexity": 15,
        "audit_friction": 5,
        "plain_english": "A Qualified Small Employer Health Reimbursement Arrangement (QSEHRA) allows S-Corp dental practices with fewer than 50 employees — and no existing group health plan — to reimburse employees for individual health insurance premiums and qualified medical expenses tax-free. In 2024, the limits are $6,150 per year for self-only coverage and $12,450 for family coverage. For non-owner employees, reimbursements are fully excluded from income and FICA taxes. The situation for the dentist-owner is different: as a greater-than 2% S-Corp shareholder, reimbursements must be included in W-2 wages, but the dentist can then deduct health insurance premiums on the front page of the personal tax return under §162(l). The practical planning value is structuring these reimbursements correctly so the deduction is captured at the right level and FICA treatment is handled properly. For dental practices without a group plan, the ICHRA (Individual Coverage HRA) is often a more flexible alternative with no employer size limit.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-157-se-health-insurance",
        "name": "Self-Employed Health Insurance Premium Deduction",
        "irc": "IRC §162(l)",
        "category": "Deduction & Reimbursement",
        "overlap_group": "Health Insurance Deduction",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and (not s.get("SIG_HAS_C_CORP", False))
        and (not s.get("SIG_HEALTH_INS_EXPENSE", False))
        and (
            s.get("Q_HEALTH_PREMIUM", 0) > 0
            or s.get("Q_HEALTH_DEDUCTION_AVAILABLE", 0) > 0
        ),
        "materiality_fn": lambda s: (
            70
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 55 if s.get("SIG_HIGH_INCOME") else 40
        ),
        "fed_savings_fn": lambda s: s.get("Q_HEALTH_DEDUCTION_AVAILABLE", 25000)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 25000
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 7,
        "complexity": 5,
        "audit_friction": 5,
        "plain_english": "Self-employed taxpayers may deduct 100% of health insurance premiums for themselves and their family as an above-the-line deduction.",
        "prerequisites": [
            "Self-employed income",
            "No employer-sponsored health coverage",
        ],
    },
    {
        "id": "DTTS-160-solo-owner-health-strategy",
        "name": "Solo Owner Strategy (Health Care Planning)",
        "irc": "IRC §105, §106",
        "category": "Retirement & Benefits",
        "overlap_group": "Health Insurance Deduction",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_HEALTH_INS_EXPENSE", False)
        and (not s.get("SIG_HAS_S_CORP_VERIFIED", False)),
        "materiality_fn": lambda s: (
            75
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 60 if s.get("SIG_HIGH_INCOME") else 45
        ),
        "fed_savings_fn": lambda s: s.get("Q_HEALTH_PREMIUM", 15000)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 15000
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 30,
        "complexity": 20,
        "audit_friction": 10,
        "plain_english": "Practice owners may structure healthcare reimbursements and insurance payments through the business entity to create tax-deductible benefits.",
        "prerequisites": ["Practice ownership"],
    },
    {
        "id": "DTTS-162-small-business-health-credit",
        "name": "Small Business Health Insurance Tax Credit",
        "irc": "IRC §45R",
        "category": "Credits & Special Incentives",
        "overlap_group": "Health Insurance Deduction",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_W2_PRESENT", False)
        and s.get("SIG_HEALTH_INS_EXPENSE", False)
        and (not s.get("SIG_VERY_HIGH_INCOME", False)),
        "materiality_fn": lambda s: (
            75
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 60 if s.get("SIG_HIGH_INCOME") else 45
        ),
        "fed_savings_fn": lambda s: min(10000, s.get("_wages", 0) * 0.05),
        "state_savings_fn": lambda s: 0,
        "speed_days": 30,
        "complexity": 20,
        "audit_friction": 10,
        "plain_english": "Small businesses providing employee health insurance through the SHOP marketplace may qualify for a federal tax credit covering a portion of premium costs.",
        "prerequisites": ["Employer-provided health insurance"],
    }
]