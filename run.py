"""
Dentists' Tax & Business Architecture System™
CLI Runner + Demo Harness
=====================================================
Usage:
    python run.py --demo                          # Run with synthetic demo data
    python run.py --pdf path/to/return.pdf        # Analyze a real PDF
    python run.py --text path/to/extracted.txt    # Analyze pre-extracted text
    python run.py --json path/to/return.json      # Use pre-built TaxReturnJSON
    python run.py --demo --output report.json     # Save report to file

Environment variables (or create .env file):
    OPENROUTER_API_KEY=sk-or-...
    GROQ_API_KEY=gsk_...
    TAVILY_API_KEY=tvly-...
    PRIMARY_PROVIDER=openrouter   (or groq)
    OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Load .env if present
def load_dotenv(path=".env"):
    if Path(path).exists():
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_dotenv()

from engine import (
    DentistTaxEngine, EngineConfig, TaxReturnJSON, FederalNumbers,
    StateNumbers, EntityRecord, DepreciationSummary, print_report
)


# ═══════════════════════════════════════════════════════════════════════════════
#  DEMO DATA  — realistic high-income California dentist
# ═══════════════════════════════════════════════════════════════════════════════

def build_demo_return() -> TaxReturnJSON:
    """
    Realistic scenario:
    - California dental practice owner (S-Corp)
    - AGI: $680,000 | Federal Tax: $192,000 | CA Tax: $65,000
    - No retirement plan
    - Low depreciation
    - Dependents present (two kids)
    - S-Corp distributions >> wages (salary $160K vs distributions $300K)
    - No PTET election
    """
    ret = TaxReturnJSON(
        client_id="DR_SMITH_2024",
        tax_year=2024,
        return_types=["1040", "1120S"],
        state_returns_present=["CA"],
        primary_state="CA",
        ptet_election_detected=False,
        dentist_indicator="CONFIRMED",
        high_income=True,
        meaningful_tax_liability=True,
        w2_present=True,
        k1_present=True,
        schedule_c_present=False,
        schedule_e_present=True,
        real_estate_activity_present=True,
        dependents_present=True,
        federal=FederalNumbers(
            filing_status="MFJ",
            agi=680_000,
            taxable_income=610_000,
            total_tax=192_000,
            federal_withholding=100_000,
            estimated_payments=60_000,
            self_employment_tax=0,       # S-Corp so no SE
            niit=11_400,                 # 3.8% NIIT on investment income
            amt=0,
            qbi_deduction=0,             # MISSED — income too high without W-2 planning
            itemized_deductions=42_000,
            standard_deduction_used=False,
            salt_deduction_claimed=10_000,  # Capped at SALT limit
            charitable_contributions=8_000,
            w2_wages=160_000,
            marginal_rate_estimate=0.37,
        ),
        states={
            "CA": StateNumbers(
                state_taxable_income=620_000,
                state_total_tax=65_000,
                state_withholding=40_000,
                state_estimated_payments=20_000,
                effective_rate_estimate=0.105,
            )
        },
        entities=[
            EntityRecord(
                entity_id="E1",
                entity_name="Smile Bright Dental, Inc.",
                entity_type="1120S",
                state_of_incorporation="CA",
                fiscal_year_end="12-31",
                gross_receipts=1_850_000,
                ordinary_business_income=460_000,
                owner_wages=160_000,
                distributions=300_000,
                officer_compensation=160_000,
                rent_paid=72_000,
                rent_received=0,
                employee_count_estimated=8,
                health_insurance_expense=18_000,
                retirement_plan_expense=0,       # NO RETIREMENT PLAN
                section_179=12_000,
                bonus_depreciation=0,
                depreciation_total=18_000,       # Very low for $1.85M practice
                meals_entertainment=4_200,
                travel=8_500,
                auto_truck=9_800,
                professional_fees=22_000,
                tax_planning_fees_detected=False, # Red flag
                state_tax_expense=800,
            )
        ],
        depreciation=DepreciationSummary(
            has_depreciation=True,
            section_179_claimed=12_000,
            bonus_depreciation_claimed=0,
            total_depreciation=18_000,
            cost_segregation_detected=False,
            assets_detected={"equipment": True, "vehicles": True, "real_estate": False},
        ),
        schedule_e_properties=[],
        retirement_contributions=0,
        confidence=0.95,
    )
    return ret


def build_demo_return_associate() -> TaxReturnJSON:
    """
    Associate dentist (W-2) — simple scenario showing different strategy set.
    """
    ret = TaxReturnJSON(
        client_id="DR_JONES_ASSOCIATE_2024",
        tax_year=2024,
        return_types=["1040"],
        state_returns_present=["NY"],
        primary_state="NY",
        dentist_indicator="CONFIRMED",
        high_income=True,
        meaningful_tax_liability=True,
        w2_present=True,
        k1_present=False,
        schedule_c_present=False,
        schedule_e_present=False,
        real_estate_activity_present=False,
        dependents_present=True,
        federal=FederalNumbers(
            filing_status="S",
            agi=340_000,
            taxable_income=295_000,
            total_tax=84_000,
            federal_withholding=84_000,
            w2_wages=340_000,
            marginal_rate_estimate=0.35,
        ),
        states={
            "NY": StateNumbers(
                state_taxable_income=310_000,
                state_total_tax=28_000,
                state_withholding=28_000,
                effective_rate_estimate=0.09,
            )
        },
        entities=[],
        confidence=0.90,
    )
    return ret


# ═══════════════════════════════════════════════════════════════════════════════
#  CLI MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Dentists' Tax & Business Architecture Risk Assessment Engine"
    )
    parser.add_argument("--demo",       action="store_true", help="Run with synthetic practice-owner demo data")
    parser.add_argument("--demo2",      action="store_true", help="Run with synthetic associate-dentist demo data")
    parser.add_argument("--pdf",        type=str,            help="Path to PDF tax return")
    parser.add_argument("--text",       type=str,            help="Path to pre-extracted text file")
    parser.add_argument("--json-input", type=str,            help="Path to pre-built TaxReturnJSON file")
    parser.add_argument("--output",     type=str,            help="Save JSON report to file")
    parser.add_argument("--no-ai",      action="store_true", help="Skip LLM synthesis (deterministic only)")
    parser.add_argument("--no-search",  action="store_true", help="Skip Tavily live research")
    parser.add_argument("--provider",   type=str,            default=None,
                        choices=["openrouter", "groq"],      help="Override LLM provider")
    parser.add_argument("--max-strats", type=int,            default=12, help="Max strategies to surface")
    parser.add_argument("--client-id",  type=str,            default="CLIENT_001")
    parser.add_argument("--year",       type=int,            default=2024)
    args = parser.parse_args()

    # Build config
    config = EngineConfig.from_env()
    config.max_strategies = args.max_strats
    if args.provider:
        config.primary_provider = args.provider
    if args.no_search:
        config.enable_live_research = False
    if args.no_ai:
        # Disable both providers
        config.openrouter_api_key = ""
        config.groq_api_key = ""

    engine = DentistTaxEngine(config)

    # Determine input source
    if args.demo:
        print("\n▶ Running DEMO: High-Income CA Practice Owner (S-Corp)")
        ret = build_demo_return()
        report = engine.analyze_return(ret)

    elif args.demo2:
        print("\n▶ Running DEMO: Associate Dentist (W-2, NY)")
        ret = build_demo_return_associate()
        report = engine.analyze_return(ret)

    elif args.pdf:
        if not Path(args.pdf).exists():
            print(f"❌ PDF not found: {args.pdf}")
            sys.exit(1)
        print(f"\n▶ Analyzing PDF: {args.pdf}")
        report = engine.analyze_pdf(args.pdf, args.client_id, args.year)

    elif args.text:
        if not Path(args.text).exists():
            print(f"❌ Text file not found: {args.text}")
            sys.exit(1)
        print(f"\n▶ Analyzing text: {args.text}")
        raw_text = Path(args.text).read_text()
        report = engine.analyze_text(raw_text, args.client_id, args.year)

    elif args.json_input:
        if not Path(args.json_input).exists():
            print(f"❌ JSON file not found: {args.json_input}")
            sys.exit(1)
        print(f"\n▶ Loading TaxReturnJSON: {args.json_input}")
        # Simple approach: load JSON dict and pass to a mock TaxReturnJSON
        with open(args.json_input) as f:
            data = json.load(f)
        # Build from dict
        fed_data = data.get("federal", {})
        fed = FederalNumbers(**{k: v for k, v in fed_data.items()
                               if k in FederalNumbers.__dataclass_fields__})
        ret = TaxReturnJSON(
            client_id=data.get("client_id", args.client_id),
            tax_year=data.get("tax_year", args.year),
            federal=fed,
        )
        report = engine.analyze_return(ret)

    else:
        parser.print_help()
        print("\n💡 Quick start: python run.py --demo")
        sys.exit(0)

    # Print report
    print_report(report)

    # Save output if requested
    if args.output:
        out_path = Path(args.output)
        with open(out_path, "w") as f:
            f.write(report.to_json())
        print(f"\n✅ Report saved to: {out_path}")


if __name__ == "__main__":
    main()
