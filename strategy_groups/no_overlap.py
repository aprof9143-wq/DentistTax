from strategy_tax_limits import TAX_YEAR_LIMITS, get_lim
_LIM = TAX_YEAR_LIMITS[2024]  # use get_lim(s) in lambdas for tax-year-aware limits
STRATEGY_LIBRARY = [
    {
        "id": "DTTS-008-ic-disc-export-income-deduction",
        "name": "IC-DISC Export Income Deduction",
        "irc": "IRC §§991–997",
        "category": "General Planning",
        "overlap_group": None,
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HAS_C_CORP", False),
        "materiality_fn": lambda s: 20,
        "fed_savings_fn": lambda s: 0,
        "state_savings_fn": lambda s: 0,
        "speed_days": 90,
        "complexity": 50,
        "audit_friction": 25,
        "plain_english": "An IC-DISC converts ordinary business income from export sales into qualified dividend income taxed at the preferential 20% rate. The operating company pays a commission to the IC-DISC — deductible at ordinary rates — and the IC-DISC distributes it as a qualified dividend to the shareholder at 20%. The rate arbitrage between 37% ordinary income and 20% qualified dividends is the savings. For dental practices, this strategy requires meaningful export revenue — dental products, training, or intellectual property licensed internationally. Most dental practices will not qualify. Flag for questionnaire confirmation before recommending.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires qualified export receipts — dental product sales, IP licensing, or training internationally.",
        ],
    },
    {
        "id": "DTTS-009-100-meals-deduction-for-company-parties",
        "name": "100% Meals Deduction for Company Parties",
        "irc": "IRC §162, §274(e)(4), §274(n)(2)(B)",
        "category": "General Planning",
        "overlap_group": None,
        "phase_1_eligible": True,
        "estimate_confidence": "MODERATE",
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and (
            s.get("SIG_HAS_S_CORP_VERIFIED", False)
            or s.get("SIG_HAS_C_CORP", False)
            or s.get("SIG_SCHEDULE_C_PRESENT", False)
        ),
        "materiality_fn": lambda s: (
            60
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 45 if s.get("SIG_HIGH_INCOME") else 30
        ),
        "fed_savings_fn": lambda s: s.get("_obi", 0)
        * 0.005
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("_obi", 0)
        * 0.005
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 7,
        "complexity": 5,
        "audit_friction": 5,
        "plain_english": "Most business meals are only 50% deductible after the 2018 tax law changes. But there is an important exception: recreational and social activities primarily for the benefit of all employees — like a holiday party, summer picnic, or team lunch open to every staff member — are 100% deductible. The key requirements are that the event must be open to all employees (not just the owner or executives) and must be a social/recreational event rather than a working business meal. A dental office holiday party with food, beverages, and entertainment for the entire team qualifies for the full deduction.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-015-pre-ipo-stock-options-amt-planning",
        "name": "Pre-IPO Stock Options & AMT Planning",
        "irc": "IRC §422, §422(b), §56(b)(3), §55, §53",
        "category": "Exit & Sale",
        "overlap_group": None,
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and s.get("SIG_HAS_C_CORP", False),
        "materiality_fn": lambda s: (
            55
            if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("SIG_HAS_C_CORP", False)
            else 30
        ),
        "fed_savings_fn": lambda s: 200000 * (0.28 - 0.2) * 0.4,
        "state_savings_fn": lambda s: 200000
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0)
        * 0.2,
        "speed_days": 30,
        "complexity": 40,
        "audit_friction": 15,
        "plain_english": "Incentive Stock Options (ISOs) receive special tax treatment — no regular income tax when you exercise them. The catch is the Alternative Minimum Tax: the difference between the option's fair market value and your exercise price counts as an AMT preference item, potentially triggering AMT even though no regular tax is owed. The planning strategy is to exercise ISOs in calculated tranches — enough each year to stay below the AMT trigger point. AMT paid in prior years creates a credit that reduces future regular tax when you eventually sell the shares and your tax situation normalizes.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-032-energy-efficient-home-credit-builders",
        "name": "Energy Efficient Home Credit (Builders)",
        "irc": "IRC §45L, §45L(a), §45L(b), §45L(c), §45L(e)",
        "category": "Credits & Incentives",
        "overlap_group": None,
        "phase_1_eligible": True,
        "estimate_confidence": "MODERATE",
        "eligibility_logic": lambda s: s.get("SIG_REAL_ESTATE_ACTIVITY", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and s.get("SIG_BUSINESS_PRESENT", False),
        "materiality_fn": lambda s: (
            50
            if s.get("SIG_SCHEDULE_E_PRESENT", False)
            and s.get("SIG_HIGH_TAX_LIABILITY", False)
            else 30
        ),
        "fed_savings_fn": lambda s: min(12500, s.get("_obi", 0) * 0.02),
        "state_savings_fn": lambda s: 0,
        "speed_days": 60,
        "complexity": 25,
        "audit_friction": 15,
        "plain_english": "The §45L Energy Efficient Home Credit gives a dollar-for-dollar federal tax credit to builders and contractors who construct new homes that meet Energy Star or DOE Zero Energy Ready standards. The credit is $2,500 per unit for Energy Star certified homes and $5,000 per unit for Zero Energy Ready homes. This strategy applies to dentists who have a real estate development or construction business on the side — not to homebuyers. A dentist building even a small number of qualifying units can generate meaningful dollar-for-dollar tax credits. Third-party energy certification is required for each unit, and the credit reduces the basis of the dwelling unit built.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-035-electing-out-of-partnership-treatment",
        "name": "Electing Out of Partnership Treatment",
        "irc": "IRC §761(a), §1361, §1362",
        "category": "Entity & Structuring",
        "overlap_group": None,
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HAS_PARTNERSHIP", False)
        and s["SIG_K1_PRESENT"]
        and s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False),
        "materiality_fn": lambda s: (
            60
            if s.get("SIG_MULTI_ENTITY", False) and s.get("SIG_HIGH_INCOME", False)
            else 40
        ),
        "fed_savings_fn": lambda s: s.get("_obi", 0) * 0.3 * 0.153 * 0.9235,
        "state_savings_fn": lambda s: 0,
        "speed_days": 60,
        "complexity": 35,
        "audit_friction": 15,
        "plain_english": "When two or more owners co-own a business without incorporating, the IRS treats it as a partnership — requiring Form 1065, K-1s, and self-employment tax on profits. Two planning paths: elect out of partnership treatment (for passive co-ownerships), or convert to S-Corporation to eliminate SE tax on profits above reasonable salary. Both require careful analysis of the partnership agreement and state rules.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
        "prerequisite_signals_any": ["SIG_K1_FROM_PARTNERSHIP", "SIG_HAS_PARTNERSHIP"],
    },
    {
        "id": "DTTS-037-1033-involuntary-conversion-deferral",
        "name": "1033 Involuntary Conversion Deferral",
        "irc": "IRC §1033, §1033(a)(1), §1033(a)(2), §1033(b), §1033(g), §1231",
        "category": "Real Estate & Depreciation",
        "overlap_group": None,
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_REAL_ESTATE_ACTIVITY", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and s.get("SIG_HAS_DEPRECIATION", False),
        "materiality_fn": lambda s: (
            55
            if s.get("SIG_REAL_ESTATE_ACTIVITY", False)
            and s.get("SIG_HIGH_TAX_LIABILITY", False)
            else 30
        ),
        "fed_savings_fn": lambda s: 250000 * 0.238 * 0.2,
        "state_savings_fn": lambda s: 0,
        "speed_days": 45,
        "complexity": 35,
        "audit_friction": 20,
        "plain_english": "If a dentist's business or investment property is destroyed by fire, condemned by a government authority, or subject to another involuntary conversion, the resulting insurance or condemnation proceeds can create a large taxable gain. Section 1033 allows that gain to be deferred — not forgiven — if the proceeds are reinvested in similar replacement property within the replacement period. For real property, that window is three years from the end of the tax year in which the gain occurred. The election must be made on the tax return, and the replacement property must be similar or related in service or use to the converted property. This is a situational strategy — it applies only when an involuntary conversion event has actually occurred.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],
    },
    {
        "id": "DTTS-038-domestic-production-deduction-for-film-tv",
        "name": "Domestic Production Deduction for Film/TV",
        "irc": "IRC §181, §181(a), §181(d), §181(f)",
        "category": "General Planning",
        "overlap_group": None,
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and (s.get("_agi", 0) > 500000),
        "materiality_fn": lambda s: 40 if s.get("SIG_VERY_HIGH_INCOME", False) else 20,
        "fed_savings_fn": lambda s: 500000 * s.get("_fed_marginal_rate", 0) * 0.1,
        "state_savings_fn": lambda s: 0,
        "speed_days": 60,
        "complexity": 40,
        "audit_friction": 30,
        "plain_english": "IRC §181 allows investors in qualifying domestic film, television, or live theatrical productions to immediately deduct their full production cost investment in the year it is paid — instead of capitalizing and amortizing the cost over the life of the project. For a high-income dentist who invests in a qualifying production where at least 75% of compensation goes to US workers, this election can create a substantial first-year deduction. The strategy is subject to at-risk rules — the investor must have genuine economic exposure — and passive activity rules may limit the deduction if the dentist does not materially participate. This is a niche strategy that applies only when there is an actual qualifying film or TV investment in place.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-042-deducting-start-up-costs",
        "name": "Deducting Start-Up Costs",
        "irc": "IRC §195, §195(a), §195(b), §195(c), §248, §709",
        "category": "General Planning",
        "overlap_group": None,
        "phase_1_eligible": True,
        "estimate_confidence": "MODERATE",
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False),
        "materiality_fn": lambda s: (
            45
            if s.get("SIG_HAS_S_CORP_VERIFIED", False)
            or s.get("SIG_SCHEDULE_C_PRESENT", False)
            else 25
        ),
        "fed_savings_fn": lambda s: min(5000, s.get("_agi", 0) * 0.005)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: min(5000, s.get("_agi", 0) * 0.005)
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 5,
        "plain_english": "When a dentist opens or acquires a new practice, the costs incurred before the business officially opens — market research, training, advertising, professional fees for the acquisition — are start-up costs that must be capitalized under §195. However, the tax code allows an election to immediately deduct up to $5,000 of those costs in the first year the business begins, with the remainder amortized over 15 years. The $5,000 immediate deduction phases out dollar-for-dollar when total start-up costs exceed $50,000. This is a frequently missed election — practitioners often capitalize these costs and never make the §195 election, delaying deductions unnecessarily. Organization costs for forming the entity (§248 for corporations, §709 for partnerships) receive the same treatment and should be tracked separately.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-045-business-credit-card-optimization",
        "name": "Business Credit Card Optimization",
        "irc": "IRC §162, §274, §274(d)",
        "category": "Credits & Incentives",
        "overlap_group": None,
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False)
        and (
            s.get("SIG_PROFESSIONAL_FEES_PRESENT", False)
            or s.get("SIG_TRAVEL_PRESENT", False)
            or s.get("SIG_AUTO_TRUCK_PRESENT", False)
        ),
        "materiality_fn": lambda s: (
            40
            if s.get("SIG_TRAVEL_PRESENT", False)
            and s.get("SIG_PROFESSIONAL_FEES_PRESENT", False)
            else 25
        ),
        "fed_savings_fn": lambda s: s.get("_obi", 0)
        * 0.03
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("_obi", 0)
        * 0.03
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 7,
        "complexity": 5,
        "audit_friction": 5,
        "plain_english": "Using a dedicated business credit card for all practice expenses is a low-complexity strategy that creates real tax and cash flow benefits. Business expenses are deductible when charged — not when the bill is paid — so charging large deductible items in December pulls those deductions into the current tax year even if payment doesn't happen until January. A dedicated card also creates a clean documentation trail for IRS substantiation purposes, eliminating mixed-use issues. Business rewards programs return 1.5–3% on spending as cash back or points that the IRS treats as a purchase price reduction — not taxable income. For a practice spending $150,000–$300,000 annually on deductible business expenses, this strategy generates meaningful timing benefits and non-taxable rewards with virtually no implementation complexity.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-049-oil-gas-intangible-drilling-costs-idc",
        "name": "Oil & Gas Intangible Drilling Costs (IDC)",
        "irc": "IRC §263(c), §469(c)(3), §613A, §57(a)(2)",
        "category": "General Planning",
        "overlap_group": None,
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and (s.get("_agi", 0) > 500000),
        "materiality_fn": lambda s: (
            60
            if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("_total_tax", 0) > 150000
            else 40
        ),
        "fed_savings_fn": lambda s: 140000 * s.get("_fed_marginal_rate", 0) * 0.2,
        "state_savings_fn": lambda s: 0,
        "speed_days": 60,
        "complexity": 45,
        "audit_friction": 25,
        "plain_english": "When a dentist invests in an oil and gas working interest, approximately 65–80% of the investment qualifies as intangible drilling costs (IDC) — deductible in full in the year the well is drilled under IRC §263(c). For a high-income dentist facing a $200,000 federal tax bill, a $200,000 oil and gas investment could generate roughly $140,000 in first-year deductions. The critical planning point is the working interest exception under §469(c)(3): unlike most investments, oil and gas working interests held directly (not through an LLC or limited partnership) are exempt from the passive activity rules — meaning IDC losses can offset ordinary dental practice income directly. The remaining tangible costs depreciate over seven years, and future production income benefits from percentage depletion. AMT exposure should be confirmed before implementation.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-052-754-basis-adjustment-election-for-partnerships",
        "name": "754 Basis Adjustment Election for Partnerships",
        "irc": "IRC §754, §743(b), §734(b), §755, §732",
        "category": "Entity & Structuring",
        "overlap_group": None,
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HAS_PARTNERSHIP", False)
        and s["SIG_K1_PRESENT"]
        and s.get("SIG_HIGH_INCOME", False),
        "materiality_fn": lambda s: (
            55
            if s.get("SIG_MULTI_ENTITY", False) and s.get("SIG_HAS_DEPRECIATION", False)
            else 35
        ),
        "fed_savings_fn": lambda s: s.get("_depreciation", 0)
        * 0.3
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("_depreciation", 0)
        * 0.3
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 30,
        "complexity": 35,
        "audit_friction": 15,
        "plain_english": "When a partner buys into a partnership, they typically pay FMV — but partnership assets reflect historical book values. A §754 election adjusts inside basis to match what the new partner paid, eliminating pre-entry built-in gains. Same applies when a partner dies with stepped-up outside basis. Once made, the election is permanent.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
        "prerequisite_signals_any": ["SIG_K1_FROM_PARTNERSHIP", "SIG_HAS_PARTNERSHIP"],
    },
    {
        "id": "DTTS-055-offshore-trust-with-u-s-reporting-compliance",
        "name": "Offshore Trust with U.S. Reporting Compliance",
        "irc": "IRC §679, §6048, §6048(a), §6048(b), §6048(c), §6677",
        "category": "Trusts & Estate",
        "overlap_group": None,
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and (s.get("_agi", 0) > 1000000),
        "materiality_fn": lambda s: (
            50
            if s.get("SIG_VERY_HIGH_INCOME", False) and s.get("_agi", 0) > 1500000
            else 30
        ),
        "fed_savings_fn": lambda s: 2000000 * 0.4 * 0.25,
        "state_savings_fn": lambda s: 0,
        "speed_days": 180,
        "complexity": 80,
        "audit_friction": 35,
        "plain_english": "A properly structured offshore trust with full US reporting compliance is primarily an asset protection and estate planning tool — not an income tax reduction strategy. Under US tax law, a US person who creates a foreign trust with US beneficiaries is treated as the trust's grantor and pays tax on all trust income at their normal US rates. The benefit comes from the strong creditor protection that foreign trust law provides and the potential to remove assets from the taxable estate. This strategy carries the most demanding compliance obligations of any structure discussed — Form 3520 and Form 3520-A must be filed annually, FBAR and FATCA reporting apply, and failure to comply can trigger penalties of 35% of the trust's gross assets. This is exclusively for dentists with very high net worth, genuine asset protection objectives, and top-tier international tax counsel.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],
    },
    {
        "id": "DTTS-058-section-1244-stock-loss-deduction",
        "name": "Section 1244 Stock Loss Deduction",
        "irc": "IRC §1244, §1244(a), §1244(c), §1244(d), §1211, §1212",
        "category": "General Planning",
        "overlap_group": None,
        "phase_1_eligible": True,
        "estimate_confidence": "LOW",
        "eligibility_logic": lambda s: s.get("SIG_HAS_C_CORP", False)
        and s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False),
        "materiality_fn": lambda s: (
            45
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HAS_C_CORP")
            else 25 if s.get("SIG_HIGH_INCOME") or s.get("SIG_HAS_C_CORP") else 15
        ),
        "fed_savings_fn": lambda s: s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.1 * 0.17,
        "state_savings_fn": lambda s: 0,
        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 10,
        "plain_english": "Section 1244 is a simple but powerful planning tool for dentists who invest in or start C-Corporation ventures. When qualifying §1244 stock becomes worthless or is sold at a loss, the loss is treated as an ordinary loss — not a capital loss. This matters enormously: without §1244, a $100,000 loss on a failed investment can only offset $3,000 of ordinary income per year, with the rest carried forward indefinitely. With §1244, that same $100,000 loss for a married couple is fully deductible against dental practice income in the year of the loss. The qualifying requirements are simple: the stock must be C-Corporation stock issued directly to the taxpayer for money or property, and the corporation's total capitalization must have been $1 million or less at issuance. There is no special filing or election needed — just confirm the qualifying facts when the investment is made.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-059-installment-lease-for-high-ticket-equipment",
        "name": "Installment Lease for High-Ticket Equipment",
        "irc": "IRC §162, §168, §168(k), §179, §7701(e)",
        "category": "Exit & Sale",
        "overlap_group": None,
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False),
        "materiality_fn": lambda s: (
            40
            if s.get("SIG_HAS_DEPRECIATION", False)
            and s.get("SIG_HIGH_TAX_LIABILITY", False)
            else 25
        ),
        "fed_savings_fn": lambda s: s.get("Q_ANNUAL_LEASE_PAYMENTS", 0)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("Q_ANNUAL_LEASE_PAYMENTS", 0)
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 10,
        "plain_english": "Leasing high-ticket dental equipment — CBCT machines, laser systems, CAD/CAM units — rather than purchasing allows the practice to deduct 100% of lease payments as ordinary business expenses in each payment period, with no capitalization required. This contrasts with purchasing, where bonus depreciation (60% in 2024) front-loads the deduction but the remaining 40% is spread over seven years. For practices that prefer level, predictable deductions or that lack the cash to purchase outright, leasing provides full deductibility with simplified tax treatment. The lease must be structured as a true lease — not a disguised purchase — to receive this treatment. In low-income years or years when §179 has already been maximized, leasing may produce a better after-tax outcome than purchasing with delayed depreciation.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-065-529-college-savings-plan",
        "name": "529 College Savings Plan",
        "irc": "IRC §529, §529(a), §529(b), §529(c)(3), §529(c)(2)(B)",
        "category": "General Planning",
        "overlap_group": None,
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_DEPENDENTS_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False),
        "materiality_fn": lambda s: (
            45
            if s.get("SIG_DEPENDENTS_PRESENT", False)
            and s.get("SIG_STATE_RETURN_PRESENT", False)
            else 30
        ),
        "fed_savings_fn": lambda s: s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.1 * 0.238,
        "state_savings_fn": lambda s: s.get("Q_INVESTMENT_PORTFOLIO", 0)
        * 0.1
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 7,
        "complexity": 5,
        "audit_friction": 2,
        "plain_english": "A 529 college savings plan allows a dentist to invest money for a child's education with tax-free growth and tax-free withdrawals for qualified education expenses. While contributions are not federally deductible, most states offer a deduction for contributions to the in-state plan. The superfunding provision allows a dentist to contribute up to $90,000 per child in a single year ($180,000 for a couple) and spread it over five years for gift tax purposes — removing a large amount from the taxable estate while using only the annual gift tax exclusion. Under SECURE 2.0, unused 529 balances (after 15 years) can be rolled over to a Roth IRA for the beneficiary — up to $35,000 lifetime — eliminating the concern about over-funding. This is a low-complexity, high-impact strategy for any dentist with children and education funding goals.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-067-net-operating-loss-nol-carryforward",
        "name": "Net Operating Loss (NOL) Carryforward",
        "irc": "IRC §172, §172(a), §172(b), §172(f), §167, §168, §469",
        "category": "Real Estate & Depreciation",
        "overlap_group": "Loss Strategies",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: (
            s.get("_obi", 0) < 0 or s.get("SIG_NOL_CARRYOVER_CONFIRMED", False)
        )
        and (
            s.get("SIG_HAS_DEPRECIATION", False)
            or s.get("SIG_REAL_ESTATE_ACTIVITY", False)
            or s.get("SIG_BUSINESS_PRESENT", False)
        ),
        "prerequisites_logic": lambda s: s.get("_obi", 0) < 0
        or s.get("SIG_NOL_CARRYOVER_CONFIRMED", False),
        "readiness_if_prereq_fail": "REQUIRES_EVENT",
        "readiness_note": "NOL strategy requires a confirmed net operating loss — no loss detected in current return",
        "materiality_fn": lambda s: (
            65
            if s.get("SIG_NOL_CARRYOVER_CONFIRMED") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 50 if s.get("_obi", 0) < 0 else 30
        ),
        "fed_savings_fn": lambda s: (
            abs(min(0, s.get("_obi", 0))) * 0.8 * s.get("_fed_marginal_rate", 0.37)
            if s.get("_obi", 0) < 0
            else s.get("_nol_amount", 0) * 0.8 * s.get("_fed_marginal_rate", 0.37)
        ),
        "state_savings_fn": lambda s: abs(min(0, s.get("_obi", 0)))
        * 0.8
        * (s.get("_state_tax", 0) / s.get("_agi", 1) if s.get("_agi", 0) else 0.05),
        "speed_days": 14,
        "complexity": 20,
        "audit_friction": 10,
        "plain_english": "A Net Operating Loss occurs when a business or investment activity generates deductions that exceed income in a given year — most commonly through large depreciation deductions from bonus depreciation, cost segregation, or §179 expensing. Under current law, NOLs can be carried forward indefinitely and applied against up to 80% of taxable income in future years. For a dentist who generates a large depreciation deduction in a year with high income, the excess deduction becomes an NOL that reduces taxes in subsequent high-income years. The strategy is most relevant when depreciation-heavy investments or real estate activities produce losses that exceed current-year income, or when a dentist deliberately accelerates depreciation to create an NOL that will shield future practice income. State NOL rules vary significantly and should be modeled separately.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],
    },
    {
        "id": "DTTS-068-business-interest-deduction-optimization",
        "name": "Business Interest Deduction Optimization",
        "irc": "IRC §163(j), §163(j)(1), §163(j)(2), §163(j)(3), §163(j)(7)",
        "category": "General Planning",
        "overlap_group": None,
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False),
        "materiality_fn": lambda s: (
            50
            if s.get("SIG_HAS_S_CORP_VERIFIED", False)
            and s.get("SIG_HAS_DEPRECIATION", False)
            else 30
        ),
        "fed_savings_fn": lambda s: s.get("_obi", 0)
        * 0.05
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("_obi", 0)
        * 0.05
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 21,
        "complexity": 25,
        "audit_friction": 10,
        "plain_english": "Section 163(j) limits the deduction for business interest expense to 30% of a practice's adjusted taxable income — meaning a dentist with significant business debt may be unable to deduct all their interest in a given year. The most important planning point is the small business exemption: practices with average gross receipts of $29 million or less over the prior three years are completely exempt from §163(j) and can deduct all business interest without limitation. For larger practices or those above the threshold, optimization involves maximizing adjusted taxable income to increase the 30% deduction cap — which requires coordinating depreciation elections with interest deductibility. Disallowed interest carries forward indefinitely, so tracking and planning for future utilization is critical. Real estate businesses can elect out of §163(j) entirely in exchange for using the slower ADS depreciation method.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-079-tax-efficient-entity-merger",
        "name": "Tax-Efficient Entity Merger",
        "irc": "IRC §368, §368(a)(1)(A), §381, §382, §482, §708, §708(b), §704(c)",
        "category": "Entity & Structuring",
        "overlap_group": None,
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_MULTI_ENTITY", False)
        and s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False),
        "materiality_fn": lambda s: (
            55
            if s.get("SIG_MULTI_ENTITY", False)
            and s.get("SIG_HIGH_TAX_LIABILITY", False)
            else 30
        ),
        "fed_savings_fn": lambda s: s.get("Q_MGMT_CO_REVENUE", 0)
        * 0.15
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("Q_MGMT_CO_REVENUE", 0)
        * 0.15
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 90,
        "complexity": 50,
        "audit_friction": 20,
        "plain_english": "A tax-efficient entity merger consolidates multiple dental entities — practice entities, management companies, or multiple location LLCs — into a simpler structure. For dentists who have accumulated several entities over time, consolidation reduces compliance costs (multiple returns, accounting fees, payroll setups) and simplifies income allocation. Corporate mergers under §368 can be done tax-free when properly structured. Partnership mergers under §708 consolidate the entities with built-in gain tracking. The simplest approach for LLC-heavy structures is using check-the-box elections to convert entities to disregarded status — effectively merging them for tax purposes without a formal legal merger transaction. Key risks: if any entity has NOL carryforwards, §382 ownership change rules may limit future NOL utilization after merger; and built-in gains in contributed property must be tracked under §704(c).",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-081-section-754-election-after-partner-death",
        "name": "Section 754 Election after Partner Death",
        "irc": "IRC §754, §743(b), §1014, §734(b), §743(d)",
        "category": "General Planning",
        "overlap_group": None,
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HAS_PARTNERSHIP", False)
        and s["SIG_K1_PRESENT"]
        and s.get("SIG_HIGH_INCOME", False),
        "materiality_fn": lambda s: (
            50
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HAS_PARTNERSHIP")
            else 30 if s.get("SIG_HIGH_INCOME") or s.get("SIG_HAS_PARTNERSHIP") else 20
        ),
        "fed_savings_fn": lambda s: s.get("Q_INVESTMENT_PORTFOLIO", 0)
        * 0.1
        * s.get("_fed_marginal_rate", 0)
        * 5,
        "state_savings_fn": lambda s: s.get("Q_INVESTMENT_PORTFOLIO", 0)
        * 0.1
        * s.get("Q_STATE_MARGINAL_RATE", 0.05)
        * 5,
        "speed_days": 30,
        "complexity": 25,
        "audit_friction": 10,
        "plain_english": "When a dental partner dies, their heirs inherit the partnership interest at a stepped-up basis equal to the fair market value at death — but the partnership's internal asset basis stays at its historical cost. Without a §754 election, the heir would be taxed on income that economically represents appreciation that occurred before they even owned the interest. A §754 election instructs the partnership to adjust the heir's share of inside basis up to FMV — eliminating this phantom income going forward. The adjustment is made under §743(b) and reduces the heir's future taxable income from the partnership by the amount of the step-up, amortized over the applicable recovery periods. The election must be made on a timely filed Form 1065 for the year of death and is permanent once made. For partnerships with significantly appreciated assets, the §754 election after a partner's death is almost always beneficial to the successor.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-089-qualified-disability-trust-qdt-deduction",
        "name": "Qualified Disability Trust (QDT) Deduction",
        "irc": "IRC §642(b)(2)(C), §642(b)(3), §661, §662, §1(e)",
        "category": "Trusts & Estate",
        "overlap_group": None,
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_DEPENDENTS_PRESENT", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False),
        "materiality_fn": lambda s: (
            40
            if s.get("SIG_VERY_HIGH_INCOME", False)
            and s.get("SIG_DEPENDENTS_PRESENT", False)
            else 20
        ),
        "fed_savings_fn": lambda s: 7500 + 1757,
        "state_savings_fn": lambda s: 50000 * s.get("Q_STATE_MARGINAL_RATE", 0.03),
        "speed_days": 90,
        "complexity": 50,
        "audit_friction": 15,
        "plain_english": "A Qualified Disability Trust (QDT) is an irrevocable trust established for the sole benefit of a disabled individual who meets the Social Security Administration's disability definition. Unlike a standard complex trust — which is entitled to only a $300 exemption and hits the top 37% tax bracket at just $15,200 of income — a QDT gets the full individual personal exemption ($5,050 in 2024) and can distribute income to the disabled beneficiary who is taxed at their own typically lower rates. For a dentist with a disabled child, sibling, or spouse, a QDT (often structured as a Special Needs Trust to protect government benefit eligibility) allows the practice to fund a trust that provides lifelong financial support — while keeping the beneficiary eligible for SSI and Medicaid. The trust must be established before the beneficiary turns 65, and the disability must meet the SSA §1614(a)(3) standard.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires estate-planning counsel and trust drafting before implementation.",
        ],
    },
    {
        "id": "DTTS-095-net-investment-income-tax-niit-avoidance",
        "name": "Net Investment Income Tax (NIIT) Avoidance",
        "irc": "IRC §1411, §1411(c), §1411(c)(4), §469, §1411(c)(2)",
        "category": "Real Estate & Depreciation",
        "overlap_group": None,
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HIGH_INCOME", False)
        and (
            s.get("SIG_REAL_ESTATE_ACTIVITY", False)
            or s.get("SIG_SCHEDULE_E_PRESENT", False)
        )
        and (s.get("_agi", 0) > 250000),
        "materiality_fn": lambda s: (
            55
            if s.get("SIG_REAL_ESTATE_ACTIVITY", False)
            and s.get("SIG_VERY_HIGH_INCOME", False)
            else 35
        ),
        "fed_savings_fn": lambda s: (
            s.get("_niit", 0)
            if s.get("_niit", 0) > 0
            else s.get("_agi", 0) * 0.038 * 0.1
        ),
        "state_savings_fn": lambda s: 0,
        "speed_days": 30,
        "complexity": 25,
        "audit_friction": 20,
        "plain_english": "The Net Investment Income Tax (NIIT) adds a 3.8% surcharge on investment income — interest, dividends, rents, royalties, and passive business gains — for dentists with MAGI above $250,000 (married) or $200,000 (single). Practice income from an active S-Corporation is already exempt. The main exposure for dentists is rental income from investment properties (passive by default) and capital gains on investment real estate. Avoidance strategies include converting passive rental income to active by materially participating in the rental activity (e.g., short-term rentals where the average stay is 7 days or fewer and the dentist materially participates), using the §469 grouping election to aggregate activities, or restructuring entities so the dentist has active involvement. Installment sales can spread gain across multiple years, reducing the NIIT base in any single year. For dentists with substantial rental portfolios, the 3.8% savings can be material — $500,000 of reclassified passive income = $19,000 saved.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],
    },
    {
        "id": "DTTS-103-deductible-advisory-planning-fees",
        "name": "Deductible Advisory/Planning Fees",
        "irc": "IRC §162, §162(a), §212",
        "category": "General Planning",
        "overlap_group": None,
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False)
        and (
            s.get("SIG_NO_TAX_PLANNING_FEES", False)
            or s.get("SIG_PROFESSIONAL_FEES_PRESENT", False)
        ),
        "materiality_fn": lambda s: (
            55
            if s.get("SIG_NO_TAX_PLANNING_FEES", False)
            and s.get("SIG_HIGH_TAX_LIABILITY", False)
            else 30
        ),
        "fed_savings_fn": lambda s: s.get("_obi", 0)
        * 0.03
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: s.get("_obi", 0)
        * 0.03
        * s.get("Q_STATE_MARGINAL_RATE", 0.05),
        "speed_days": 7,
        "complexity": 5,
        "audit_friction": 5,
        "plain_english": "Tax planning, CPA, and advisory fees paid in connection with the dental practice are fully deductible as ordinary and necessary business expenses under §162. This includes fees for tax return preparation, tax planning engagements, legal advice on business structure, and financial advisory services related to the practice. The critical distinction: fees routed through the business entity (S-Corp, partnership, or Schedule C) are fully deductible under §162 with no floor or limitation. In contrast, personal investment advisory fees (managing a brokerage portfolio) fall under §212 — which was suspended by the 2017 Tax Cuts and Jobs Act and is not deductible on individual returns through at least 2025. The planning opportunity is to ensure that all advisory and planning fees with a business nexus are invoiced to and paid by the business entity, not personally. For a dentist paying $30,000/year in advisory fees and in the 37% bracket, routing fees through the entity saves approximately $11,100 in federal taxes.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-110-domestic-production-activities-deduction",
        "name": "Domestic Production Activities Deduction",
        "irc": "IRC §199 [REPEALED 2018]; see §199A (QBI deduction) as current replacement",
        "category": "General Planning",
        "overlap_group": None,
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_MULTI_ENTITY", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and (s.get("Q_MGMT_CO_REVENUE", 0) > 0),
        "materiality_fn": lambda s: (
            50
            if s.get("SIG_QBI_MISSING", False) and s.get("SIG_HIGH_INCOME", False)
            else 10
        ),
        "fed_savings_fn": lambda s: max(s.get("_obi", 0), s.get("_wages", 0))
        * 0.2
        * s.get("_fed_marginal_rate", 0)
        * 0.3,
        "state_savings_fn": lambda s: 0,
        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 5,
        "plain_english": "The Domestic Production Activities Deduction (§199 DPAD) was a deduction of up to 9% of qualified domestic production income — but it was fully repealed by the Tax Cuts and Jobs Act effective for tax years beginning after December 31, 2017. Dental practices cannot use §199 DPAD for current tax years. The replacement benefit for dental practice owners is the §199A Qualified Business Income (QBI) deduction — a 20% deduction on pass-through business income available to eligible dentists. If a dental practice is showing no QBI deduction on the return despite having business income, that represents a potentially missed opportunity worth investigating. Note that dental practices are classified as Specified Service Trades or Businesses (SSTBs) under §199A, which limits or eliminates the QBI deduction for high-income dentists above the income thresholds ($383,900 MFJ in 2024).",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-111-foreign-tax-credit",
        "name": "Foreign Tax Credit",
        "irc": "IRC §901, §904, §904(d), §27, §905",
        "category": "Credits & Incentives",
        "overlap_group": None,
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_SCHEDULE_E_PRESENT", False),
        "materiality_fn": lambda s: (
            35
            if s.get("SIG_HIGH_INCOME", False)
            and s.get("SIG_SCHEDULE_E_PRESENT", False)
            else 15
        ),
        "fed_savings_fn": lambda s: s.get("Q_INVESTMENT_PORTFOLIO", 0) * 0.01,
        "state_savings_fn": lambda s: 0,
        "speed_days": 7,
        "complexity": 10,
        "audit_friction": 5,
        "plain_english": "If a dentist's investment portfolio includes international funds, ADRs, or foreign ETFs, the fund company often withholds foreign income taxes on dividends before they are paid. These foreign taxes show up in Box 7 of the Form 1099-DIV and can be claimed as a dollar-for-dollar credit against U.S. income tax — significantly more valuable than taking them as a deduction. The Foreign Tax Credit (FTC) under §901 directly reduces the U.S. tax owed rather than reducing taxable income. For a dentist in the 37% bracket who paid $5,000 in foreign withholding taxes, the FTC saves $5,000 versus $1,850 as a deduction. The credit is limited to the U.S. tax allocable to foreign-source income under §904 and excess credits carry forward 10 years. For small amounts ($300 or less for single filers; $600 or less for married), the credit can be claimed directly on Form 1040 without filing Form 1116.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-112-rental-loss-offset-for-active-participation",
        "name": "Rental Loss Offset for Active Participation",
        "irc": "IRC §469, §469(c), §469(i), §469(i)(2), §469(i)(3), §469(g), §469(c)(7)",
        "category": "Real Estate & Depreciation",
        "overlap_group": None,
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_REAL_ESTATE_ACTIVITY", False)
        and s.get("SIG_SCHEDULE_E_PRESENT", False)
        and s.get("SIG_HAS_DEPRECIATION", False),
        "materiality_fn": lambda s: (
            50
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_REAL_ESTATE_ACTIVITY")
            else (
                30
                if s.get("SIG_HIGH_INCOME") or s.get("SIG_REAL_ESTATE_ACTIVITY")
                else 20
            )
        ),
        "fed_savings_fn": lambda s: min(s.get("_depreciation", 0), 25000)
        * s.get("_fed_marginal_rate", 0)
        * 0.1,
        "state_savings_fn": lambda s: 0,
        "speed_days": 14,
        "complexity": 15,
        "audit_friction": 15,
        "plain_english": "Rental property losses are normally 'passive' under the tax code and can only offset passive income — not the dentist's practice income. There is one exception: if the dentist 'actively participates' in the rental (approving tenants, setting rents, approving repairs — even through a property manager), up to $25,000 of rental losses can be deducted against ordinary income each year. However, this $25,000 special allowance phases out completely once adjusted gross income exceeds $150,000 — meaning most practicing dentists above that threshold receive zero current benefit. The practical value for high-income dentists is different: unused rental losses are 'suspended' and accumulate each year. When the property is eventually sold, all accumulated suspended losses are released in full against any income — creating a potentially large tax deduction at the time of sale. Tracking and documenting these suspended losses every year on Form 8582 is essential to capture the full future benefit.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
            "Requires asset/property-level support, basis records, and timing review before implementation.",
        ],
    },
    {
        "id": "DTTS-122-home-equity-loan-interest-deduction-biz",
        "name": "Home Equity Loan Interest Deduction (Biz)",
        "irc": "IRC §163(h), §163(h)(3)(C), §163(a), Temp. Reg. §1.163-8T",
        "category": "General Planning",
        "overlap_group": None,
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False),
        "materiality_fn": lambda s: (
            35
            if s.get("SIG_BUSINESS_PRESENT", False)
            and s.get("SIG_HIGH_TAX_LIABILITY", False)
            else 15
        ),
        "fed_savings_fn": lambda s: s.get("_obi", 0)
        * 0.05
        * 0.07
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 0,
        "speed_days": 7,
        "complexity": 10,
        "audit_friction": 10,
        "plain_english": "The Tax Cuts and Jobs Act (2017) eliminated the deduction for home equity loan interest when the loan is used for purposes other than buying or improving the home. However, there is a powerful planning opportunity using the IRS interest tracing rules: if a dentist takes a home equity loan and uses the proceeds to fund the dental practice or purchase business equipment, the interest on that loan is classified as business interest — fully deductible as an ordinary business expense under §162, not limited by the mortgage interest rules. The key is meticulous documentation: the dentist must trace the loan proceeds directly to business use (bank transfers showing funds going from home equity loan to business account) and maintain those records. The interest deduction follows the use of the money, not the collateral. A dentist borrowing $200,000 at 7% and using it for practice equipment saves approximately $5,180 per year in federal taxes at the 37% rate — on top of any equipment depreciation deductions available.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-126-corporate-aircraft-deduction",
        "name": "Corporate Aircraft Deduction",
        "irc": "IRC §162, §274, §274(a), §274(e)(2), §280F, §168(k)",
        "category": "General Planning",
        "overlap_group": None,
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_VERY_HIGH_INCOME", False)
        and s.get("SIG_HIGH_TAX_LIABILITY", False)
        and s.get("SIG_TRAVEL_PRESENT", False)
        and (s.get("_agi", 0) > 750000),
        "materiality_fn": lambda s: (
            55
            if s.get("SIG_VERY_HIGH_INCOME", False)
            and s.get("SIG_TRAVEL_PRESENT", False)
            else 25
        ),
        "fed_savings_fn": lambda s: (480000 + 120000)
        * s.get("_fed_marginal_rate", 0)
        * 0.15,
        "state_savings_fn": lambda s: (480000 + 120000) * 0.05 * 0.15,
        "speed_days": 60,
        "complexity": 40,
        "audit_friction": 30,
        "plain_english": "Dentists who own or are considering owning an aircraft for business travel can deduct a significant portion of the costs against dental practice income. The aircraft purchase itself can be eligible for bonus depreciation (60% in 2024) — meaning a $1 million aircraft used 80% for business could generate $480,000 in first-year depreciation deductions. Annual operating costs — fuel, maintenance, hangar, crew, insurance — are deductible in proportion to business use. The key compliance requirement is maintaining detailed flight logs documenting every flight's business purpose, passengers, and destination. When the aircraft is used for personal travel, the owner must recognize imputed income calculated using the IRS's Standard Industry Fare Level (SIFL) formula — which is typically far less than the actual aircraft cost — and this is added to the owner's W-2. Entertainment use (flying clients to sporting events) has been non-deductible since 2018. This strategy only makes sense for practices with genuine multi-location or regional travel needs and AGI well above $750,000.",
        "prerequisites": [
            "Confirm facts in tax return before recommending.",
            "If required entity/plan/account does not exist, flag as 'Prerequisite Build' instead of 'Implement Now'.",
        ],
    },
    {
        "id": "DTTS-134-home-office",
        "name": "Home Office / Administrative Office Deduction",
        "irc": "IRC §280A(c)",
        "category": "Deduction & Reimbursement",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: not s.get("SIG_W2_ONLY", False)
        and (not s.get("SIG_HAS_S_CORP_VERIFIED", False))
        and (
            s.get("SIG_SCHEDULE_C_PRESENT", False)
            or s.get("SIG_HAS_PARTNERSHIP", False)
            or (
                s.get("SIG_SELF_EMPLOYED", False)
                and s.get("SIG_BUSINESS_PRESENT", False)
            )
        ),
        "materiality_fn": lambda s: (
            70
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 55 if s.get("SIG_HIGH_INCOME") else 40
        ),
        "fed_savings_fn": lambda s: s.get("Q_HEALTH_PREMIUM", 5000)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 5000
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 15,
        "plain_english": "A home administrative office used exclusively for management and administrative work may qualify as a deductible business expense.",
        "prerequisites": [],
    },
    {
        "id": "DTTS-135-business-travel",
        "name": "Business Travel Expenses",
        "irc": "IRC §162(a)(2)",
        "category": "Deduction & Reimbursement",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and s.get("SIG_TRAVEL_PRESENT", False),
        "materiality_fn": lambda s: (
            70
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 55 if s.get("SIG_HIGH_INCOME") else 40
        ),
        "fed_savings_fn": lambda s: s.get("Q_HEALTH_PREMIUM", 8000)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 8000
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 7,
        "complexity": 10,
        "audit_friction": 20,
        "plain_english": "Travel expenses are deductible when the primary purpose of the trip is business, such as attending conferences, training, or meetings.",
        "prerequisites": ["Documented business purpose for travel"],
    },
    {
        "id": "DTTS-139-c-corp-fringe-benefits",
        "name": "Fringe Benefits (For C-corporations)",
        "irc": "IRC §132, §105, §106",
        "category": "Deduction & Reimbursement",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_HAS_C_CORP", False),
        "materiality_fn": lambda s: (
            80
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 65 if s.get("SIG_HIGH_INCOME") else 50
        ),
        "fed_savings_fn": lambda s: s.get("Q_HEALTH_PREMIUM", 20000)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 20000
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 30,
        "complexity": 25,
        "audit_friction": 10,
        "plain_english": "C-corporations can provide owner-employees with tax-deductible fringe benefits such as health insurance or medical reimbursement plans that are not taxable to the owner.",
        "prerequisites": ["Operating C-Corporation"],
    },
    {
        "id": "DTTS-140-accountable-plan",
        "name": "Accountable Plan (Reimbursement Plan)",
        "irc": "IRC §62(a)(2)(A), Reg §1.62-2",
        "category": "Deduction & Reimbursement",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False)
        and (
            s.get("SIG_RENT_EXPENSE_PRESENT", False)
            or s.get("SIG_AUTO_TRUCK_PRESENT", False)
            or s.get("SIG_TRAVEL_PRESENT", False)
            or s.get("SIG_PROFESSIONAL_FEES_PRESENT", False)
        ),
        "materiality_fn": lambda s: (
            65
            if s.get("SIG_AUTO_TRUCK_PRESENT", False)
            or s.get("SIG_TRAVEL_PRESENT", False)
            else 50
        ),
        "fed_savings_fn": lambda s: s.get("Q_HEALTH_DEDUCTION_AVAILABLE", 15000)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 15000
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 5,
        "plain_english": "An accountable plan allows your practice to reimburse you tax-free for legitimate business expenses you paid personally, such as mileage, continuing education, and supplies.",
        "prerequisites": ["Operating business entity"],
    },
    {
        "id": "DTTS-164-business-use-vehicle",
        "name": "Business Use of Personal Vehicle Deduction",
        "irc": "IRC §162, §274(d)",
        "category": "Deduction & Reimbursement",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s.get("SIG_BUSINESS_PRESENT", False),
        "materiality_fn": lambda s: (
            65
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 50 if s.get("SIG_HIGH_INCOME") else 35
        ),
        "fed_savings_fn": lambda s: s.get("Q_HEALTH_PREMIUM", 7500)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 7500
        * (s.get("_state_tax", 0) / s.get("_agi", 0) if s.get("_agi", 0) else 0),
        "speed_days": 7,
        "complexity": 5,
        "audit_friction": 10,
        "plain_english": "Dentists who use a personal vehicle for business purposes can deduct mileage or actual vehicle expenses related to practice activities.",
        "prerequisites": ["Vehicle used for business activities"],
    },
    {
        "id": "DTTS-171-film-production-credit",
        "name": "Film & Media Production Tax Incentives",
        "irc": "IRC §181",
        "category": "Credits & Special Incentives",
        "phase_1_eligible": False,
        "eligibility_logic": lambda s: s.get("SIG_HIGH_INCOME", False)
        and s.get("Q_INVESTMENT_PORTFOLIO", 0) > 100000,
        "materiality_fn": lambda s: (
            85
            if s.get("SIG_VERY_HIGH_INCOME") and s.get("SIG_HIGH_TAX_LIABILITY")
            else 70 if s.get("SIG_HIGH_INCOME") else 55
        ),
        "fed_savings_fn": lambda s: s.get("Q_INVESTMENT_PORTFOLIO", 75000)
        * s.get("_fed_marginal_rate", 0),
        "state_savings_fn": lambda s: 0,
        "speed_days": 90,
        "complexity": 45,
        "audit_friction": 15,
        "plain_english": "Certain investments in film, television, and media production may qualify for accelerated deductions or state tax incentives.",
        "prerequisites": ["Investment in qualifying production project"],
    }
]