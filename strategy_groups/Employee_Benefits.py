from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-033-tax-free-gifts-to-employees",
        "name": "Tax-Free Gifts to Employees",
        "irc": "IRC §102, §102(c), §132, §132(e), §274(j)",
        "category": "Compensation & Benefits",
        "overlap_group": "Employee Benefits",
        "phase_1_eligible": True,
        "estimate_confidence": "MODERATE",
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_W2_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False),
        "materiality_fn": lambda s: (
            35
            if s.get("SIG_BUSINESS_PRESENT", False) and s.get("SIG_W2_PRESENT", False)
            else 20
        ),
        "fed_savings_fn": lambda s: s.get("Q_EDUCATIONAL_ASSISTANCE_DEDUCTION", 0)
        * 0.06
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("Q_EDUCATIONAL_ASSISTANCE_DEDUCTION", 0)
        * 0.06
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 10,
        "plain_english": "The IRS allows dental practices to give employees certain non-cash gifts and awards completely tax-free — the practice gets a deduction, and the employee pays no income or payroll tax on the benefit. De minimis fringe benefits like a holiday gift basket, flowers, or occasional event tickets are excluded from employee income when their value is small enough that tracking them would be unreasonable. Employee achievement awards for length of service or safety — given as tangible non-cash property — are deductible up to $1,600 per employee under a qualified written plan. The critical rule: cash bonuses and gift cards never qualify and are always taxable wages. This is a low-complexity strategy best used to replace cash bonuses with qualifying non-cash recognition programs.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-061-reimbursement-of-educational-assistance",
        "name": "Reimbursement of Educational Assistance",
        "irc": "IRC §127, §127(a), §127(b), §127(c), §132(d), §162",
        "category": "Compensation & Benefits",
        "overlap_group": "Employee Benefits",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_W2_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False),
        "materiality_fn": lambda s: (
            35
            if s.get("SIG_PROFESSIONAL_FEES_PRESENT", False)
            and s.get("SIG_W2_PRESENT", False)
            else 20
        ),
        "fed_savings_fn": lambda s: s.get("Q_EDUCATIONAL_ASSISTANCE_DEDUCTION", 0)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("Q_EDUCATIONAL_ASSISTANCE_DEDUCTION", 0)
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 5,
        "plain_english": "A dental practice can reimburse employees up to $5,250 per year for educational expenses — tuition, fees, books, and supplies — completely tax-free to the employee and fully deductible by the practice. The practice must have a written educational assistance plan under §127, and the benefit must be available to employees broadly (not just owners). For a practice with five employees taking CE courses, dental hygiene programs, or business management training, this creates over $26,000 in deductible expenses with zero income or payroll tax to the employees. Owner-dentists in S-Corporations cannot use the §127 exclusion for themselves, but CE credits and specialty training that maintain current dental skills may qualify as working condition fringe benefits under §132(d) — deductible by the practice and excluded from the owner's income without a dollar limit.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-121-fringe-benefits-commuter-transportation",
        "name": "Fringe Benefits: Commuter/Transportation",
        "irc": "IRC §132(f), §132(f)(1), §125, §274(a)(4)",
        "category": "Compensation & Benefits",
        "overlap_group": "Employee Benefits",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_W2_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False),
        "materiality_fn": lambda s: (
            30
            if s.get("SIG_W2_PRESENT", False) and s.get("SIG_HIGH_INCOME", False)
            else 15
        ),
        "fed_savings_fn": lambda s: s.get("Q_EDUCATIONAL_ASSISTANCE_DEDUCTION", 0)
        * 0.12
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("Q_EDUCATIONAL_ASSISTANCE_DEDUCTION", 0)
        * 0.12
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 14,
        "complexity": 5,
        "audit_friction": 2,
        "plain_english": "Dental practices can provide employees (including the dentist-owner if on W-2) with up to $315 per month in tax-free transit or vanpool benefits and up to $315 per month in tax-free qualified parking — for a total of $7,560 per year that is completely excluded from the employee's gross income and exempt from FICA payroll taxes. These amounts are adjusted for inflation annually. The benefit can be funded either by the employer directly or through a pre-tax payroll reduction via a §125 cafeteria plan (where the employee redirects salary to pay for the commuter benefit pre-tax). A notable TCJA change: the employer no longer gets a tax deduction for providing these benefits (§274 eliminated the deduction for 2018 onward) — but the employee income exclusion and FICA savings remain fully intact. For a dental practice with multiple employees commuting to the office or using employer-provided parking, formalizing a commuter benefit program creates measurable FICA savings for the practice and income exclusions for employees at minimal cost.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-133-cafeteria-plan",
        "name": "Cafeteria Plan",
        "irc": "IRC §125, §125(d), §125(f), §125(i), §106, §79, §21(b)(2)",
        "category": "Compensation & Benefits",
        "overlap_group": "Employee Benefits",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_W2_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False),
        "materiality_fn": lambda s: (
            45
            if s.get("SIG_HEALTH_INS_EXPENSE", False) and s.get("SIG_W2_PRESENT", False)
            else (
                30
                if s.get("SIG_DEPENDENTS_PRESENT", False)
                and s.get("SIG_W2_PRESENT", False)
                else 20
            )
        ),
        "fed_savings_fn": lambda s: s.get("Q_EDUCATIONAL_ASSISTANCE_DEDUCTION", 0)
        * 1.8
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("Q_EDUCATIONAL_ASSISTANCE_DEDUCTION", 0)
        * 1.8
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 5,
        "plain_english": "A §125 Cafeteria Plan is one of the most cost-effective employee benefits a dental practice can offer. It allows employees to redirect a portion of their salary — before taxes — to pay for health insurance premiums, Flexible Spending Accounts (FSAs) for medical expenses (up to $3,300 in 2024), and Dependent Care FSAs for childcare (up to $5,000 in 2024). These amounts are excluded from federal income tax and FICA payroll taxes, saving both the employee and the employer money. The employer saves 7.65% in FICA taxes on every dollar redirected pre-tax, which on a staff of five can amount to thousands of dollars annually. The plan must be documented in writing, and annual elections must be made before the plan year begins. One important restriction: S-Corp shareholders owning more than 2% of the company cannot participate in the cafeteria plan — the dentist-owner must address health insurance through a different mechanism, specifically the §162(l) self-employed health insurance deduction.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    }
]