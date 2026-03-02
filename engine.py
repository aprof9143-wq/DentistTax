"""
Dentists' Tax & Business Architecture System™
Tax Risk Assessment Engine — Phase 1
=====================================================
Architecture:
  1. PDF → JSON extraction (pdfplumber)
  2. JSON → Signal derivation (deterministic, fast)
  3. Signals → Strategy scoring (weighted algorithm)
  4. Live research via Tavily (optional enrichment)
  5. AI reasoning via OpenRouter or Groq (configurable)
  6. Structured report output

APIs used:
  - OpenRouter  (primary LLM, any model)
  - Groq        (fallback / fast inference)
  - Tavily      (live tax law / strategy research)
"""

import os
import json
import re
import time
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path

import requests

# ── optional PDF parsing ──────────────────────────────────────────────────────
try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ── optional rich console ─────────────────────────────────────────────────────
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    console = Console()
    RICH = True
except ImportError:
    RICH = False
    class Console:
        def print(self, *a, **kw): print(*a)
    console = Console()

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("DentistTaxEngine")


# ═══════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class EngineConfig:
    # API keys (load from env or pass directly)
    openrouter_api_key: str = ""
    groq_api_key: str = ""
    tavily_api_key: str = ""

    # Model selection
    openrouter_model: str = "anthropic/claude-3.5-sonnet"   # any OpenRouter model
    groq_model: str = "llama-3.3-70b-versatile"             # Groq fast model
    primary_provider: str = "openrouter"                     # "openrouter" | "groq"

    # Behavior
    max_strategies: int = 12          # top-N strategies to surface
    min_materiality_score: int = 50   # exclude low-impact strategies
    enable_live_research: bool = True  # Tavily research enrichment
    phase: int = 1                     # 1 = return-only, 2 = + questionnaire

    @classmethod
    def from_env(cls) -> "EngineConfig":
        return cls(
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
            groq_api_key=os.getenv("GROQ_API_KEY", ""),
            tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
            openrouter_model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
            groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            primary_provider=os.getenv("PRIMARY_PROVIDER", "openrouter"),
        )


# ═══════════════════════════════════════════════════════════════════════════════
#  DATA MODELS  (mirrors JSON schema in the spec)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FederalNumbers:
    filing_status: str = "UNKNOWN"
    agi: float = 0
    taxable_income: float = 0
    total_tax: float = 0
    federal_withholding: float = 0
    estimated_payments: float = 0
    self_employment_tax: float = 0
    niit: float = 0
    amt: float = 0
    qbi_deduction: float = 0
    itemized_deductions: float = 0
    standard_deduction_used: bool = False
    salt_deduction_claimed: float = 0
    charitable_contributions: float = 0
    w2_wages: float = 0
    marginal_rate_estimate: float = 0.0   # derived

@dataclass
class StateNumbers:
    state_taxable_income: float = 0
    state_total_tax: float = 0
    state_withholding: float = 0
    state_estimated_payments: float = 0
    effective_rate_estimate: float = 0.0  # derived

@dataclass
class EntityRecord:
    entity_id: str = "E1"
    entity_name: str = ""
    entity_type: str = ""          # 1120S | 1120 | 1065
    state_of_incorporation: str = ""
    fiscal_year_end: str = "12-31"
    gross_receipts: float = 0
    ordinary_business_income: float = 0
    owner_wages: float = 0
    distributions: float = 0
    officer_compensation: float = 0
    rent_paid: float = 0
    rent_received: float = 0
    employee_count_estimated: int = 0
    health_insurance_expense: float = 0
    retirement_plan_expense: float = 0
    section_179: float = 0
    bonus_depreciation: float = 0
    depreciation_total: float = 0
    meals_entertainment: float = 0
    travel: float = 0
    auto_truck: float = 0
    professional_fees: float = 0
    tax_planning_fees_detected: bool = False
    state_tax_expense: float = 0

@dataclass
class DepreciationSummary:
    has_depreciation: bool = False
    section_179_claimed: float = 0
    bonus_depreciation_claimed: float = 0
    total_depreciation: float = 0
    cost_segregation_detected: bool = False
    assets_detected: dict = field(default_factory=lambda: {
        "equipment": False, "vehicles": False, "real_estate": False
    })

@dataclass
class ScheduleEProperty:
    property_id: str = "RE1"
    type: str = "RESIDENTIAL"
    use: str = "LONG_TERM_RENTAL"
    income: float = 0
    expenses: float = 0
    depreciation: float = 0
    net: float = 0

@dataclass
class TaxReturnJSON:
    """Normalized representation of all uploaded tax returns."""
    schema_version: str = "1.0"
    analysis_phase: str = "PHASE_1_RETURN_ONLY"
    client_id: str = ""
    tax_year: int = 2024
    return_types: list = field(default_factory=list)
    state_returns_present: list = field(default_factory=list)
    primary_state: str = ""
    ptet_election_detected: bool = False

    # Profile flags
    dentist_indicator: str = "UNKNOWN"
    high_income: bool = False
    meaningful_tax_liability: bool = False
    w2_present: bool = False
    k1_present: bool = False
    schedule_c_present: bool = False
    schedule_e_present: bool = False
    real_estate_activity_present: bool = False
    dependents_present: bool = False

    # Core numbers
    federal: FederalNumbers = field(default_factory=FederalNumbers)
    states: dict = field(default_factory=dict)          # state_code → StateNumbers
    entities: list = field(default_factory=list)        # list of EntityRecord
    depreciation: DepreciationSummary = field(default_factory=DepreciationSummary)
    schedule_e_properties: list = field(default_factory=list)
    schedule_c_net_profit: float = 0
    retirement_contributions: float = 0

    # Derived signals (populated by SignalEngine)
    signals: dict = field(default_factory=dict)
    confidence: float = 0.0


# ═══════════════════════════════════════════════════════════════════════════════
#  PDF EXTRACTOR
# ═══════════════════════════════════════════════════════════════════════════════

class PDFExtractor:
    """
    Extracts raw text from uploaded PDF tax returns.
    Returns page-by-page text dict for downstream parsing.
    """

    DOLLAR_PATTERN = re.compile(r'\$?([\d,]+(?:\.\d{2})?)')
    LINE_PATTERNS = {
        # 1040 key lines
        "agi":             re.compile(r'adjusted gross income.*?\$([\d,]+)', re.I),
        "taxable_income":  re.compile(r'taxable income.*?\$([\d,]+)', re.I),
        "total_tax":       re.compile(r'total tax.*?\$([\d,]+)', re.I),
        "se_tax":          re.compile(r'self.employment tax.*?\$([\d,]+)', re.I),
        "niit":            re.compile(r'net investment income tax.*?\$([\d,]+)', re.I),
        "amt":             re.compile(r'alternative minimum tax.*?\$([\d,]+)', re.I),
        "qbi":             re.compile(r'qualified business income.*?\$([\d,]+)', re.I),
        "salt":            re.compile(r'state and local taxes.*?\$([\d,]+)', re.I),
        "w2_wages":        re.compile(r'wages.*?salaries.*?\$([\d,]+)', re.I),
        # Entity
        "gross_receipts":  re.compile(r'gross receipts.*?\$([\d,]+)', re.I),
        "obi":             re.compile(r'ordinary business income.*?\$([\d,]+)', re.I),
        "officer_comp":    re.compile(r'officer compensation.*?\$([\d,]+)', re.I),
    }

    def extract_from_pdf(self, pdf_path: str) -> dict:
        """Return {page: text, 'all': combined_text, 'raw_lines': [...]}"""
        if not PDF_AVAILABLE:
            raise ImportError("pdfplumber not installed. Run: pip install pdfplumber")
        pages = {}
        all_text = []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                pages[i + 1] = text
                all_text.append(text)
        combined = "\n".join(all_text)
        return {"pages": pages, "all": combined, "raw_lines": combined.splitlines()}

    def parse_dollar(self, text: str) -> float:
        """Extract first dollar amount from text string."""
        m = self.DOLLAR_PATTERN.search(text)
        return float(m.group(1).replace(",", "")) if m else 0.0

    def quick_extract(self, raw_text: str) -> dict:
        """Fast regex pass over raw text → dict of key financial values."""
        results = {}
        for key, pattern in self.LINE_PATTERNS.items():
            m = pattern.search(raw_text)
            if m:
                results[key] = float(m.group(1).replace(",", ""))
            else:
                results[key] = 0.0
        return results

    def detect_return_types(self, raw_text: str) -> list:
        types = []
        if re.search(r'form\s*1040', raw_text, re.I):
            types.append("1040")
        if re.search(r'form\s*1120-?s', raw_text, re.I):
            types.append("1120S")
        if re.search(r'form\s*1120\b', raw_text, re.I):
            if "1120S" not in types:
                types.append("1120")
        if re.search(r'form\s*1065', raw_text, re.I):
            types.append("1065")
        return types or ["1040"]

    def detect_states(self, raw_text: str) -> list:
        state_forms = re.findall(r'\b([A-Z]{2})\s+(?:form|return|schedule|income tax)', raw_text, re.I)
        return list(set(s.upper() for s in state_forms)) if state_forms else []

    def build_return_json(self, pdf_path: str, client_id: str = "CLIENT_001",
                          tax_year: int = 2024) -> TaxReturnJSON:
        """Full pipeline: PDF → TaxReturnJSON."""
        raw = self.extract_from_pdf(pdf_path)
        return self._text_to_json(raw["all"], client_id, tax_year)

    def build_return_json_from_text(self, raw_text: str, client_id: str = "CLIENT_001",
                                     tax_year: int = 2024) -> TaxReturnJSON:
        return self._text_to_json(raw_text, client_id, tax_year)

    def _text_to_json(self, raw_text: str, client_id: str, tax_year: int) -> TaxReturnJSON:
        extracted = self.quick_extract(raw_text)
        return_types = self.detect_return_types(raw_text)
        states = self.detect_states(raw_text)

        fed = FederalNumbers(
            agi=extracted["agi"],
            taxable_income=extracted["taxable_income"],
            total_tax=extracted["total_tax"],
            self_employment_tax=extracted["se_tax"],
            niit=extracted["niit"],
            amt=extracted["amt"],
            qbi_deduction=extracted["qbi"],
            salt_deduction_claimed=extracted["salt"],
            w2_wages=extracted["w2_wages"],
            itemized_deductions=extracted["salt"] * 3 if extracted["salt"] else 0,
        )

        # Estimate marginal rate
        if fed.taxable_income > 731200:
            fed.marginal_rate_estimate = 0.37
        elif fed.taxable_income > 487450:
            fed.marginal_rate_estimate = 0.35
        elif fed.taxable_income > 231250:
            fed.marginal_rate_estimate = 0.32
        elif fed.taxable_income > 100525:
            fed.marginal_rate_estimate = 0.24
        elif fed.taxable_income > 47150:
            fed.marginal_rate_estimate = 0.22
        else:
            fed.marginal_rate_estimate = 0.12

        # Entity detection
        entities = []
        if "1120S" in return_types or "1120" in return_types or "1065" in return_types:
            ent = EntityRecord(
                entity_id="E1",
                entity_name=self._guess_entity_name(raw_text),
                entity_type=next((t for t in ["1120S","1120","1065"] if t in return_types), "1120S"),
                gross_receipts=extracted["gross_receipts"],
                ordinary_business_income=extracted["obi"],
                officer_compensation=extracted["officer_comp"],
            )
            entities.append(ent)

        state_numbers = {}
        for state in states:
            state_numbers[state] = StateNumbers()

        ret = TaxReturnJSON(
            client_id=client_id,
            tax_year=tax_year,
            return_types=return_types,
            state_returns_present=states,
            primary_state=states[0] if states else "",
            federal=fed,
            states=state_numbers,
            entities=entities,
            high_income=fed.agi > 300_000,
            meaningful_tax_liability=fed.total_tax > 70_000,
            w2_present=bool(extracted["w2_wages"]),
            k1_present=len(entities) > 0,
            schedule_c_present=bool(extracted.get("schedule_c", 0)),
            real_estate_activity_present="schedule_e" in raw_text.lower(),
            dependents_present=bool(re.search(r'dependent', raw_text, re.I)),
            confidence=0.75,
        )

        # Detect dentist indicator
        dental_keywords = ["dental", "dds", "dmd", "orthodont", "periodon", "endodon",
                           "oral", "prosthodon"]
        if any(kw in raw_text.lower() for kw in dental_keywords):
            ret.dentist_indicator = "CONFIRMED"
        return ret

    def _guess_entity_name(self, raw_text: str) -> str:
        m = re.search(r'(?:name of corporation|business name)[:\s]+([A-Za-z0-9 ,\.]+)', raw_text, re.I)
        return m.group(1).strip() if m else "Practice Entity"


# ═══════════════════════════════════════════════════════════════════════════════
#  SIGNAL ENGINE  (deterministic, < 10ms)
# ═══════════════════════════════════════════════════════════════════════════════

class SignalEngine:
    """
    Converts TaxReturnJSON → flat signals dict.
    Signals power the scoring engine without re-parsing JSON repeatedly.
    """

    def derive(self, ret: TaxReturnJSON) -> dict:
        fed = ret.federal
        entities = ret.entities
        total_entity_retirement = sum(e.retirement_plan_expense for e in entities)
        total_entity_wages = sum(e.owner_wages or e.officer_compensation for e in entities)
        total_entity_obi = sum(e.ordinary_business_income for e in entities)
        total_entity_distributions = sum(e.distributions for e in entities)

        combined_tax = fed.total_tax + sum(
            s.state_total_tax for s in ret.states.values()
        )
        combined_effective_rate = (combined_tax / fed.agi) if fed.agi > 0 else 0

        signals = {
            # Income & tax
            "SIG_HIGH_INCOME":               fed.agi > 300_000,
            "SIG_VERY_HIGH_INCOME":          fed.agi > 600_000,
            "SIG_HIGH_TAX_LIABILITY":        fed.total_tax > 70_000,
            "SIG_VERY_HIGH_TAX_LIABILITY":   fed.total_tax > 150_000,
            "SIG_COMBINED_EFFECTIVE_RATE":   combined_effective_rate,
            "SIG_MARGINAL_RATE":             fed.marginal_rate_estimate,

            # Entity structure
            "SIG_BUSINESS_PRESENT":          len(entities) > 0,
            "SIG_MULTI_ENTITY":              len(entities) > 1,
            "SIG_HAS_S_CORP":               any(e.entity_type == "1120S" for e in entities),
            "SIG_HAS_C_CORP":               any(e.entity_type == "1120" for e in entities),
            "SIG_HAS_PARTNERSHIP":          any(e.entity_type == "1065" for e in entities),
            "SIG_SCHEDULE_C_PRESENT":        ret.schedule_c_present,

            # Wages & compensation
            "SIG_W2_PRESENT":                ret.w2_present or fed.w2_wages > 0,
            "SIG_K1_PRESENT":                ret.k1_present,
            "SIG_LOW_OWNER_WAGES":          (
                total_entity_obi > 0 and total_entity_wages > 0 and
                (total_entity_wages / total_entity_obi < 0.4)
            ),
            "SIG_HIGH_DISTRIBUTIONS_VS_WAGES": (
                total_entity_wages > 0 and total_entity_distributions > total_entity_wages
            ),

            # Retirement
            "SIG_NO_RETIREMENT_PLAN":        total_entity_retirement == 0 and fed.agi > 200_000,
            "SIG_HAS_RETIREMENT_PLAN":       total_entity_retirement > 0,
            "SIG_RETIREMENT_UNDERFUNDED":    (
                total_entity_retirement < 50_000 and fed.agi > 400_000
            ),

            # Real estate & depreciation
            "SIG_SCHEDULE_E_PRESENT":        ret.schedule_e_present,
            "SIG_REAL_ESTATE_ACTIVITY":      ret.real_estate_activity_present,
            "SIG_HAS_DEPRECIATION":          ret.depreciation.has_depreciation,
            "SIG_NO_DEPRECIATION":           not ret.depreciation.has_depreciation and len(entities) > 0,
            "SIG_LOW_DEPRECIATION":          (
                ret.depreciation.total_depreciation < 20_000 and
                any(e.gross_receipts > 500_000 for e in entities)
            ),
            "SIG_COST_SEG_DETECTED":         ret.depreciation.cost_segregation_detected,
            "SIG_REAL_ESTATE_ASSET":         ret.depreciation.assets_detected.get("real_estate", False),

            # Deductions
            "SIG_QBI_CLAIMED":               fed.qbi_deduction > 0,
            "SIG_QBI_MISSING":               (
                fed.qbi_deduction == 0 and total_entity_obi > 100_000
            ),
            "SIG_HIGH_SALT":                 fed.salt_deduction_claimed > 10_000,
            "SIG_STATE_RETURN_PRESENT":      len(ret.state_returns_present) > 0,
            "SIG_PTET_DETECTED":             ret.ptet_election_detected,
            "SIG_PTET_OPPORTUNITY":          (
                len(ret.state_returns_present) > 0 and not ret.ptet_election_detected
            ),

            # Family / lifestyle
            "SIG_DEPENDENTS_PRESENT":        ret.dependents_present,
            "SIG_RENT_EXPENSE_PRESENT":      any(e.rent_paid > 0 for e in entities),
            "SIG_AUTO_TRUCK_PRESENT":        any(e.auto_truck > 0 for e in entities),
            "SIG_TRAVEL_PRESENT":            any(e.travel > 0 for e in entities),
            "SIG_PROFESSIONAL_FEES_PRESENT": any(e.professional_fees > 0 for e in entities),
            "SIG_NO_TAX_PLANNING_FEES":      not any(e.tax_planning_fees_detected for e in entities),
            "SIG_HEALTH_INS_EXPENSE":        any(e.health_insurance_expense > 0 for e in entities),

            # Dentist classification
            "SIG_DENTIST_CONFIRMED":         ret.dentist_indicator == "CONFIRMED",
            "SIG_DENTIST_LIKELY":            ret.dentist_indicator in ("CONFIRMED","LIKELY"),

            # Raw values (for savings calculations)
            "_agi":                          fed.agi,
            "_taxable_income":               fed.taxable_income,
            "_total_tax":                    fed.total_tax,
            "_obi":                          total_entity_obi,
            "_wages":                        fed.w2_wages or total_entity_wages,
            "_distributions":                total_entity_distributions,
            "_retirement":                   total_entity_retirement,
            "_depreciation":                 ret.depreciation.total_depreciation,
            "_state_tax":                    sum(s.state_total_tax for s in ret.states.values()),
            "_fed_marginal_rate":            fed.marginal_rate_estimate,
            "_primary_state":                ret.primary_state,
        }
        return signals


# ═══════════════════════════════════════════════════════════════════════════════
#  STRATEGY LIBRARY  (subset of the 52 — full scoring logic)
# ═══════════════════════════════════════════════════════════════════════════════

STRATEGY_LIBRARY = [
    {
        "id": "DTTS-029-owners-salary",
        "name": "Owner's Salary Strategy (S-Corp SE Tax Savings)",
        "irc": "IRC §3101, §1402",
        "category": "Entity & Income Structuring",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: (
            s["SIG_HAS_S_CORP"] and s["SIG_HIGH_DISTRIBUTIONS_VS_WAGES"]
        ),
        "materiality_fn": lambda s: min(100, int(
            (s["_distributions"] - s["_wages"]) * 0.1532 / 500  # SE tax savings
        )),
        "fed_savings_fn": lambda s: (
            max(0, s["_distributions"] - s["_wages"]) * 0.1532 * 0.5
        ),
        "state_savings_fn": lambda s: 0,
        "speed_days": 30,
        "complexity": 20,
        "audit_friction": 10,
        "plain_english": (
            "By optimizing your owner salary vs. distributions ratio in your S-Corp, "
            "you can significantly reduce self-employment (FICA) taxes. The IRS requires "
            "a 'reasonable salary,' but distributions above that avoid 15.3% SE tax."
        ),
        "documentation": [
            "Board minutes authorizing salary",
            "Comparable salary benchmarks",
            "Payroll records",
        ],
        "cpa_handoff": [
            "Confirm reasonable comp analysis on file",
            "Adjust W-2 and distributions per new salary structure",
        ],
        "prerequisites": ["Operating S-Corp entity required"],
    },
    {
        "id": "DTTS-028-qbi",
        "name": "Qualified Business Income (QBI) Deduction — §199A",
        "irc": "IRC §199A",
        "category": "Deduction & Reimbursement",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s["SIG_QBI_MISSING"] or s["SIG_BUSINESS_PRESENT"],
        "materiality_fn": lambda s: 85 if s["SIG_QBI_MISSING"] else 50,
        "fed_savings_fn": lambda s: (
            s["_obi"] * 0.20 * s["_fed_marginal_rate"] if s["SIG_QBI_MISSING"] else 0
        ),
        "state_savings_fn": lambda s: 0,  # QBI is federal only
        "speed_days": 7,
        "complexity": 15,
        "audit_friction": 10,
        "plain_english": (
            "The §199A deduction allows pass-through business owners to deduct up to 20% of "
            "qualified business income. For dentists, careful W-2 wage and capital analysis "
            "can unlock or maximize this deduction — especially if it was missed or under-claimed."
        ),
        "documentation": [
            "QBI worksheet (Form 8995 or 8995-A)",
            "Entity income documentation",
        ],
        "cpa_handoff": ["Recompute QBI deduction with all entity income", "File amended return if missed prior year"],
        "prerequisites": ["Pass-through entity or self-employment income"],
    },
    {
        "id": "DTTS-013-cash-balance",
        "name": "Cash Balance Plan — IRC §401(a)",
        "irc": "IRC §401(a), §412",
        "category": "Retirement & Benefits",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: (
            s["SIG_HIGH_INCOME"] and s["SIG_NO_RETIREMENT_PLAN"]
        ),
        "materiality_fn": lambda s: 95 if s["_agi"] > 600_000 else 80,
        "fed_savings_fn": lambda s: min(300_000, s["_agi"] * 0.25) * s["_fed_marginal_rate"],
        "state_savings_fn": lambda s: min(300_000, s["_agi"] * 0.25) * (s["_state_tax"] / s["_agi"] if s["_agi"] else 0),
        "speed_days": 90,
        "complexity": 40,
        "audit_friction": 10,
        "plain_english": (
            "A Cash Balance Plan (a type of defined benefit plan) allows high-income dentists "
            "to contribute $100,000–$300,000+ per year pre-tax. Combined with a 401(k)/profit-sharing, "
            "a 50-year-old dentist could shelter $400,000+ annually — creating massive deductions."
        ),
        "documentation": [
            "Actuarial certification",
            "Plan document",
            "Annual Form 5500",
            "Contribution calculation",
        ],
        "cpa_handoff": ["Engage actuary for contribution calculation", "Establish plan before year-end"],
        "prerequisites": ["Consistent business income (plan requires ongoing funding)", "Actuarial firm engaged"],
    },
    {
        "id": "DTTS-007-accountable-plan",
        "name": "Accountable Plan (Reimbursement Plan)",
        "irc": "IRC §62(a)(2)(A), Reg §1.62-2",
        "category": "Deduction & Reimbursement",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s["SIG_BUSINESS_PRESENT"],
        "materiality_fn": lambda s: 65 if s["SIG_AUTO_TRUCK_PRESENT"] or s["SIG_TRAVEL_PRESENT"] else 50,
        "fed_savings_fn": lambda s: (
            (s.get("_auto", 0) + s.get("_travel", 0)) * s["_fed_marginal_rate"]
            if s.get("_auto") else 15_000 * s["_fed_marginal_rate"]
        ),
        "state_savings_fn": lambda s: (
            15_000 * (s["_state_tax"] / s["_agi"] if s["_agi"] else 0)
        ),
        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 5,
        "plain_english": (
            "An accountable plan allows your practice to reimburse you (tax-free) for business "
            "expenses you pay personally — home office, mileage, phone, continuing education. "
            "The practice deducts the reimbursement; you pay no tax on it. Quick to set up, "
            "enormous long-term impact."
        ),
        "documentation": [
            "Written accountable plan document",
            "Expense reports with receipts",
            "Business purpose documentation",
        ],
        "cpa_handoff": ["Draft plan document", "Train staff on expense reporting"],
        "prerequisites": ["Operating business entity (S-Corp, C-Corp, or Partnership)"],
    },
    {
        "id": "DTTS-001-home-office",
        "name": "Home Office / Home Administrative Office Deduction",
        "irc": "IRC §280A(c), Rev. Rul. 99-7",
        "category": "Deduction & Reimbursement",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s["SIG_BUSINESS_PRESENT"],
        "materiality_fn": lambda s: 55,
        "fed_savings_fn": lambda s: 5_000 * s["_fed_marginal_rate"],
        "state_savings_fn": lambda s: 5_000 * (s["_state_tax"] / s["_agi"] if s["_agi"] else 0),
        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 15,
        "plain_english": (
            "The 'home administrative office' strategy positions your home office as the "
            "principal place of business for administrative and management activities — even "
            "if you see patients at your practice. This creates deductible rent between your "
            "home and your practice entity."
        ),
        "documentation": [
            "Square footage measurement",
            "Business use percentage documentation",
            "Rental agreement with entity (if applicable)",
        ],
        "cpa_handoff": ["Confirm principal place of business determination", "File Form 8829 or entity deduction"],
        "prerequisites": [],
    },
    {
        "id": "DTTS-021-augusta-rule",
        "name": "Augusta Rule — IRC §280A(g) Home Rental",
        "irc": "IRC §280A(g)",
        "category": "Deduction & Reimbursement",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s["SIG_BUSINESS_PRESENT"],
        "materiality_fn": lambda s: 60,
        "fed_savings_fn": lambda s: min(28_000, 14 * 2000) * s["_fed_marginal_rate"],
        "state_savings_fn": lambda s: min(28_000, 14 * 2000) * (s["_state_tax"] / s["_agi"] if s["_agi"] else 0),
        "speed_days": 14,
        "complexity": 10,
        "audit_friction": 20,
        "plain_english": (
            "Rent your home to your practice for up to 14 days per year for legitimate "
            "business meetings (board meetings, partner retreats, team planning). The practice "
            "deducts the rental — and under §280A(g), you pay zero income tax on the rental income. "
            "A $14,000–$28,000 tax-free payment to yourself each year."
        ),
        "documentation": [
            "Written rental agreement",
            "Rental comps (what the market charges)",
            "Meeting agendas and minutes",
            "Proof of payment from entity",
            "Calendar entries",
        ],
        "cpa_handoff": ["Confirm §280A(g) treatment", "Ensure rental expense on entity return"],
        "prerequisites": ["Business entity pays rent to you"],
    },
    {
        "id": "DTTS-003-hiring-children",
        "name": "Hiring Children (Income Shifting Strategy)",
        "irc": "IRC §73, §3111(a)(4), §3301(2)",
        "category": "Entity & Income Structuring",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: (
            s["SIG_DEPENDENTS_PRESENT"] and s["SIG_BUSINESS_PRESENT"]
        ),
        "materiality_fn": lambda s: 65,
        "fed_savings_fn": lambda s: min(14_600, 3 * 14_600) * (s["_fed_marginal_rate"] - 0.10),
        "state_savings_fn": lambda s: min(14_600, 3 * 14_600) * (s["_state_tax"] / s["_agi"] if s["_agi"] else 0),
        "speed_days": 30,
        "complexity": 20,
        "audit_friction": 15,
        "plain_english": (
            "Pay your children a reasonable wage for real work in your practice. Income shifts "
            "from your 37% bracket to their 0–10% bracket. Under 18 working in a parent-owned "
            "sole prop or single-member entity = no FICA taxes. Use earnings for Roth IRA, college, "
            "or living expenses."
        ),
        "documentation": [
            "Time records and job description",
            "Payroll records with reasonable wage",
            "W-2 issued to child",
            "Proof of actual work performed",
        ],
        "cpa_handoff": ["Set up payroll for child", "Confirm entity structure for FICA exemption"],
        "prerequisites": ["Dependent children ages 7-17", "Sole prop, SMLLC, or single-owner LLC"],
    },
    {
        "id": "DTTS-041-cost-segregation",
        "name": "Cost Segregation Analysis",
        "irc": "IRC §168, Rev. Proc. 87-56",
        "category": "Real Estate & Depreciation",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: (
            s["SIG_REAL_ESTATE_ACTIVITY"] or s["SIG_LOW_DEPRECIATION"]
        ),
        "materiality_fn": lambda s: 88 if s["SIG_REAL_ESTATE_ASSET"] else 65,
        "fed_savings_fn": lambda s: (
            s["_depreciation"] * 2.5 * s["_fed_marginal_rate"] if s["_depreciation"] else 50_000 * s["_fed_marginal_rate"]
        ),
        "state_savings_fn": lambda s: (
            s["_depreciation"] * 2.5 * (s["_state_tax"] / s["_agi"] if s["_agi"] else 0) if s["_depreciation"] else 0
        ),
        "speed_days": 60,
        "complexity": 35,
        "audit_friction": 15,
        "plain_english": (
            "A cost segregation study reclassifies components of your building from 39-year "
            "straight-line depreciation to 5-, 7-, or 15-year property — accelerating "
            "hundreds of thousands of dollars of deductions. Especially powerful when "
            "combined with bonus depreciation."
        ),
        "documentation": [
            "Cost segregation study from qualified engineer",
            "Building/improvement purchase records",
            "Form 3115 (if catchup depreciation)",
        ],
        "cpa_handoff": ["Engage cost seg firm", "File Form 3115 for catch-up if prior year property"],
        "prerequisites": ["Own commercial real estate or dental office building", "Cost seg engineer engagement"],
    },
    {
        "id": "DTTS-046-bonus-depreciation",
        "name": "100% Bonus Depreciation Strategy — §168(k)",
        "irc": "IRC §168(k)",
        "category": "Real Estate & Depreciation",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s["SIG_BUSINESS_PRESENT"] and s["SIG_LOW_DEPRECIATION"],
        "materiality_fn": lambda s: 75 if s["SIG_LOW_DEPRECIATION"] else 50,
        "fed_savings_fn": lambda s: 100_000 * s["_fed_marginal_rate"],
        "state_savings_fn": lambda s: 0,  # Many states decouple from bonus dep
        "speed_days": 30,
        "complexity": 20,
        "audit_friction": 10,
        "plain_english": (
            "Bonus depreciation allows immediate expensing of qualifying equipment, "
            "technology, and improvements. For dental practices, new chairs, imaging systems, "
            "and office buildouts can generate massive year-one deductions. "
            "Note: many states decouple from federal bonus depreciation — state savings vary."
        ),
        "documentation": [
            "Asset purchase records",
            "Placed-in-service date documentation",
            "Form 4562 bonus depreciation election",
        ],
        "cpa_handoff": ["Confirm asset qualifies under §168(k)", "Check state add-back requirements"],
        "prerequisites": ["Asset placed in service during tax year"],
    },
    {
        "id": "DTTS-012-401k",
        "name": "Solo 401(k) / Traditional 401(k) + Profit Sharing",
        "irc": "IRC §402(g), §415",
        "category": "Retirement & Benefits",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: (
            s["SIG_NO_RETIREMENT_PLAN"] or s["SIG_RETIREMENT_UNDERFUNDED"]
        ),
        "materiality_fn": lambda s: 80 if s["SIG_NO_RETIREMENT_PLAN"] else 60,
        "fed_savings_fn": lambda s: (
            min(69_000, s["_obi"] * 0.25) * s["_fed_marginal_rate"]
        ),
        "state_savings_fn": lambda s: (
            min(69_000, s["_obi"] * 0.25) * (s["_state_tax"] / s["_agi"] if s["_agi"] else 0)
        ),
        "speed_days": 30,
        "complexity": 15,
        "audit_friction": 5,
        "plain_english": (
            "A 401(k) with profit-sharing allows contributions up to $69,000/year (2024). "
            "Combined with employer match and profit-sharing, a solo dentist can shelter "
            "$69,000–$76,500 pre-tax annually. For married dentists both working, "
            "that's $138,000–$153,000 in retirement contributions alone."
        ),
        "documentation": [
            "Plan adoption agreement",
            "Contribution calculation",
            "IRS Form 5500-EZ (if plan assets > $250K)",
        ],
        "cpa_handoff": ["Establish plan before Dec 31", "Calculate maximum deductible contribution"],
        "prerequisites": [],
    },
    {
        "id": "DTTS-009-schedule-c-to-scorp",
        "name": "Schedule C → S-Corp Conversion (SE Tax Protection)",
        "irc": "IRC §1361-1379, §3111",
        "category": "Entity & Income Structuring",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: (
            s["SIG_SCHEDULE_C_PRESENT"] and s["_obi"] > 80_000
        ),
        "materiality_fn": lambda s: 85,
        "fed_savings_fn": lambda s: (
            max(0, s["_obi"] - min(s["_obi"] * 0.40, 180_000)) * 0.1532
        ),
        "state_savings_fn": lambda s: 0,
        "speed_days": 60,
        "complexity": 30,
        "audit_friction": 5,
        "plain_english": (
            "Operating as a Schedule C exposes 100% of profit to 15.3% self-employment tax. "
            "Converting to an S-Corp and paying yourself a reasonable salary means only the "
            "salary portion is subject to FICA — distributions are SE tax-free. For a dentist "
            "earning $300K net, this saves $15,000–$25,000 annually."
        ),
        "documentation": [
            "Articles of incorporation",
            "S-Corp election (Form 2553)",
            "Payroll setup",
            "Reasonable comp documentation",
        ],
        "cpa_handoff": ["File Form 2553 before deadline", "Establish payroll", "Transfer practice to entity"],
        "prerequisites": ["State licensing board approval may be required for professional corporations"],
    },
    {
        "id": "DTTS-ptet-election",
        "name": "Pass-Through Entity Tax (PTET) Election",
        "irc": "IRC §164(b)(6) SALT workaround — state-level election",
        "category": "Entity & Income Structuring",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s["SIG_PTET_OPPORTUNITY"] and s["SIG_BUSINESS_PRESENT"],
        "materiality_fn": lambda s: 80 if s["_state_tax"] > 20_000 else 55,
        "fed_savings_fn": lambda s: (
            s["_state_tax"] * s["_fed_marginal_rate"]  # SALT now deducted at entity level
        ),
        "state_savings_fn": lambda s: 0,
        "speed_days": 30,
        "complexity": 20,
        "audit_friction": 5,
        "plain_english": (
            "The PTET election allows your pass-through entity to pay state income tax at "
            "the entity level — circumventing the $10,000 SALT cap. The entity deducts "
            "the full state tax, reducing your federal taxable income dollar-for-dollar. "
            "For dentists in California, New York, and other high-tax states, this is "
            "worth $15,000–$50,000 in federal savings annually."
        ),
        "documentation": [
            "State PTET election filing",
            "Entity tax payment records",
            "K-1 with PTET credit",
        ],
        "cpa_handoff": ["Confirm state PTET election deadline", "Make estimated PTET payments"],
        "prerequisites": ["State must have PTET legislation (CA, NY, NJ, IL, TX, and 36+ others do)"],
    },
    {
        "id": "DTTS-026-se-health-insurance",
        "name": "Self-Employed Health Insurance Premium Deduction",
        "irc": "IRC §162(l)",
        "category": "Deduction & Reimbursement",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s["SIG_BUSINESS_PRESENT"] and not s["SIG_HAS_C_CORP"],
        "materiality_fn": lambda s: 55,
        "fed_savings_fn": lambda s: 25_000 * s["_fed_marginal_rate"],
        "state_savings_fn": lambda s: 25_000 * (s["_state_tax"] / s["_agi"] if s["_agi"] else 0),
        "speed_days": 7,
        "complexity": 5,
        "audit_friction": 5,
        "plain_english": (
            "Self-employed business owners can deduct 100% of health insurance premiums "
            "for themselves and family as an above-the-line deduction — reducing AGI without "
            "itemizing. For a family paying $25,000/year in premiums, this saves $7,000–$10,000 "
            "depending on your bracket."
        ),
        "documentation": [
            "Health insurance premium statements",
            "Proof of self-employed status",
        ],
        "cpa_handoff": ["Verify deduction taken on Schedule 1, Line 17", "Confirm not eligible for employer-sponsored plan"],
        "prerequisites": ["Not eligible for employer-sponsored health insurance"],
    },
    {
        "id": "DTTS-005-hsa",
        "name": "Health Savings Account (HSA) — Triple Tax Advantage",
        "irc": "IRC §223",
        "category": "Retirement & Benefits",
        "phase_1_eligible": True,
        "eligibility_logic": lambda s: s["SIG_HIGH_INCOME"],
        "materiality_fn": lambda s: 50,
        "fed_savings_fn": lambda s: 8_300 * s["_fed_marginal_rate"],
        "state_savings_fn": lambda s: 8_300 * (s["_state_tax"] / s["_agi"] if s["_agi"] else 0),
        "speed_days": 7,
        "complexity": 5,
        "audit_friction": 2,
        "plain_english": (
            "An HSA paired with an HDHP gives you triple tax benefits: contributions are "
            "pre-tax (deductible), growth is tax-free, and withdrawals for medical expenses "
            "are tax-free. Family contribution limit is $8,300 (2024). Often overlooked by "
            "high-income dentists who overpay for traditional health plans."
        ),
        "documentation": ["HSA account statements", "HDHP insurance policy"],
        "cpa_handoff": ["Confirm HDHP enrollment", "Deduct on Schedule 1"],
        "prerequisites": ["Enrolled in qualifying High-Deductible Health Plan (HDHP)"],
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
#  STRATEGY SCORER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ScoredStrategy:
    strategy_id: str
    strategy_name: str
    irc_authority: str
    category: str
    total_score: float
    eligibility_score: float
    materiality_score: float
    federal_savings_low: float
    federal_savings_high: float
    state_savings_low: float
    state_savings_high: float
    time_to_implement_days: int
    complexity: int
    audit_friction: int
    plain_english: str
    documentation_checklist: list
    cpa_handoff: list
    prerequisites: list
    evidence_basis: list = field(default_factory=list)


class StrategyScorer:
    """
    Scores all strategies against derived signals.
    Returns top-N ranked ScoredStrategy objects.
    """

    WEIGHT_MATERIALITY = 0.35
    WEIGHT_ELIGIBILITY = 0.20
    WEIGHT_FED_IMPACT  = 0.15
    WEIGHT_STATE       = 0.10
    WEIGHT_SPEED       = 0.10
    PENALTY_COMPLEXITY = 0.10
    PENALTY_AUDIT      = 0.05
    PENALTY_PREREQ     = 0.05

    def score_all(self, signals: dict, config: EngineConfig) -> list[ScoredStrategy]:
        scored = []
        for strat in STRATEGY_LIBRARY:
            result = self._score_one(strat, signals)
            if result and result.total_score >= config.min_materiality_score:
                scored.append(result)
        scored.sort(key=lambda x: x.total_score, reverse=True)
        return scored[:config.max_strategies]

    def _score_one(self, strat: dict, signals: dict) -> Optional[ScoredStrategy]:
        # Check eligibility
        try:
            eligible = strat["eligibility_logic"](signals)
        except Exception:
            eligible = False

        if not eligible:
            return None

        eligibility_score = 90 if eligible else 30

        # Materiality
        try:
            materiality_score = min(100, strat["materiality_fn"](signals))
        except Exception:
            materiality_score = 50

        # Savings estimates
        try:
            fed_save = max(0, strat["fed_savings_fn"](signals))
        except Exception:
            fed_save = 0
        try:
            state_save = max(0, strat["state_savings_fn"](signals))
        except Exception:
            state_save = 0

        # Convert to 0-100 impact scores
        fed_impact = min(100, int(fed_save / 1000))
        state_impact = min(100, int(state_save / 500))

        # Speed score (inverse of days)
        days = strat.get("speed_days", 60)
        speed_score = 100 if days <= 14 else (80 if days <= 30 else (60 if days <= 60 else 30))

        # Penalties
        complexity_penalty = strat.get("complexity", 20)
        audit_penalty = strat.get("audit_friction", 10)
        prereq_penalty = 10 if strat.get("prerequisites") else 0

        total = (
            materiality_score    * self.WEIGHT_MATERIALITY +
            eligibility_score    * self.WEIGHT_ELIGIBILITY +
            fed_impact           * self.WEIGHT_FED_IMPACT  +
            state_impact         * self.WEIGHT_STATE       +
            speed_score          * self.WEIGHT_SPEED       -
            complexity_penalty   * self.PENALTY_COMPLEXITY -
            audit_penalty        * self.PENALTY_AUDIT      -
            prereq_penalty       * self.PENALTY_PREREQ
        )

        # Build evidence basis from active signals
        evidence = []
        active_signal_map = {
            "SIG_LOW_OWNER_WAGES":          "S-Corp distributions substantially exceed owner wages",
            "SIG_QBI_MISSING":              "QBI deduction not claimed despite qualifying pass-through income",
            "SIG_NO_RETIREMENT_PLAN":       "No retirement plan contribution detected despite high income",
            "SIG_RETIREMENT_UNDERFUNDED":   "Retirement contributions appear below maximum allowable limits",
            "SIG_LOW_DEPRECIATION":         "Depreciation appears low relative to entity revenue",
            "SIG_SCHEDULE_C_PRESENT":       "Schedule C income subject to self-employment tax",
            "SIG_DEPENDENTS_PRESENT":       "Dependents present — income-shifting strategies applicable",
            "SIG_REAL_ESTATE_ACTIVITY":     "Real estate/rental activity detected on return",
            "SIG_PTET_OPPORTUNITY":         "State return present but PTET election not detected",
            "SIG_HIGH_SALT":                "SALT deduction exceeds $10K cap — PTET may recover federal benefit",
        }
        for sig_key, desc in active_signal_map.items():
            if signals.get(sig_key):
                evidence.append(desc)
        if not evidence:
            evidence.append("Business activity present — strategy applicable to entity structure")

        return ScoredStrategy(
            strategy_id=strat["id"],
            strategy_name=strat["name"],
            irc_authority=strat["irc"],
            category=strat["category"],
            total_score=round(total, 1),
            eligibility_score=eligibility_score,
            materiality_score=materiality_score,
            federal_savings_low=round(fed_save * 0.70, 0),
            federal_savings_high=round(fed_save * 1.30, 0),
            state_savings_low=round(state_save * 0.70, 0),
            state_savings_high=round(state_save * 1.30, 0),
            time_to_implement_days=days,
            complexity=strat.get("complexity", 20),
            audit_friction=strat.get("audit_friction", 10),
            plain_english=strat["plain_english"],
            documentation_checklist=strat.get("documentation", []),
            cpa_handoff=strat.get("cpa_handoff", []),
            prerequisites=strat.get("prerequisites", []),
            evidence_basis=evidence,
        )


# ═══════════════════════════════════════════════════════════════════════════════
#  EXPOSURE SCORE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ExposureScore:
    raw_score: float
    band: str
    band_label: str
    liability_intensity: float
    structural_inefficiency: float
    opportunity_density: float
    top_drivers: list


class ExposureCalculator:

    def calculate(self, ret: TaxReturnJSON, signals: dict) -> ExposureScore:
        fed = ret.federal
        combined_tax = fed.total_tax + sum(s.state_total_tax for s in ret.states.values())
        agi = fed.agi if fed.agi else 1

        # 1. Liability Intensity (0-100)
        rate = combined_tax / agi
        if rate < 0.15:   li = 10
        elif rate < 0.25: li = 35
        elif rate < 0.35: li = 65
        else:              li = min(100, 65 + (rate - 0.35) * 350)

        # 2. Structural Inefficiency (0-100)
        si = 0
        drivers = []
        if signals.get("SIG_LOW_OWNER_WAGES") or signals.get("SIG_HIGH_DISTRIBUTIONS_VS_WAGES"):
            si += 20
            drivers.append("S-Corp salary/distribution ratio is suboptimal")
        if signals.get("SIG_NO_RETIREMENT_PLAN"):
            si += 20
            drivers.append("No retirement plan — significant shielding opportunity missed")
        if signals.get("SIG_RETIREMENT_UNDERFUNDED"):
            si += 10
            drivers.append("Retirement contributions below maximum allowable")
        if signals.get("SIG_QBI_MISSING"):
            si += 15
            drivers.append("§199A QBI deduction not claimed")
        if signals.get("SIG_NO_DEPRECIATION"):
            si += 15
            drivers.append("No depreciation claimed on equipment-heavy practice")
        if signals.get("SIG_PTET_OPPORTUNITY"):
            si += 10
            drivers.append("PTET election could recover federal SALT benefit")
        if signals.get("SIG_NO_TAX_PLANNING_FEES"):
            si += 5
            drivers.append("No tax planning fees evident — architecture likely absent")
        si = min(100, si)

        # 3. Opportunity Density (0-100)
        od = 0
        if signals.get("SIG_DEPENDENTS_PRESENT"):   od += 20
        if signals.get("SIG_REAL_ESTATE_ACTIVITY"): od += 20
        if signals.get("SIG_AUTO_TRUCK_PRESENT"):   od += 10
        if signals.get("SIG_TRAVEL_PRESENT"):       od += 10
        if signals.get("SIG_PTET_OPPORTUNITY"):     od += 15
        if signals.get("SIG_NO_RETIREMENT_PLAN"):   od += 25
        od = min(100, od)

        raw = li * 0.45 + si * 0.35 + od * 0.20

        if raw < 25:   band, label = "LOW", "Low Bleed"
        elif raw < 50: band, label = "MODERATE", "Moderate Bleed"
        elif raw < 75: band, label = "HIGH", "High Bleed"
        else:           band, label = "SEVERE", "Severe Bleed (Architectural Failure)"

        return ExposureScore(
            raw_score=round(raw, 1),
            band=band,
            band_label=label,
            liability_intensity=round(li, 1),
            structural_inefficiency=round(si, 1),
            opportunity_density=round(od, 1),
            top_drivers=drivers[:5],
        )


# ═══════════════════════════════════════════════════════════════════════════════
#  DENTIST CLASSIFIER
# ═══════════════════════════════════════════════════════════════════════════════

class DentistClassifier:

    def classify(self, ret: TaxReturnJSON) -> tuple[str, float]:
        entities = ret.entities
        confidence = 0.0

        if ret.schedule_c_present and not entities:
            profile = "DENTIST_ASSOCIATE_1099"
            confidence = 0.55
        elif ret.w2_present and not entities:
            profile = "DENTIST_ASSOCIATE_W2"
            confidence = 0.55
        elif len(entities) >= 2:
            profile = "DENTIST_OWNER_MULTI_ENTITY"
            confidence = 0.75
        elif len(entities) == 1:
            profile = "DENTIST_OWNER_SINGLE_ENTITY"
            confidence = 0.70
        else:
            profile = "UNKNOWN"
            confidence = 0.30

        # Confidence boosters
        if ret.dentist_indicator == "CONFIRMED":
            confidence = min(1.0, confidence + 0.35)
        if ret.real_estate_activity_present and "OWNER" in profile:
            profile += "_WITH_RE"

        return profile, round(confidence, 2)


# ═══════════════════════════════════════════════════════════════════════════════
#  TAVILY RESEARCH CLIENT
# ═══════════════════════════════════════════════════════════════════════════════

class TavilyResearcher:
    """
    Calls Tavily Search API to enrich strategy recommendations
    with current IRS guidance, recent case law, and state conformity.
    """
    API_URL = "https://api.tavily.com/search"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def research_strategy(self, strategy_name: str, irc_section: str) -> dict:
        """Research a specific strategy for current IRS guidance."""
        query = f"{strategy_name} {irc_section} IRS 2024 tax planning dentist"
        return self._search(query, max_results=3)

    def research_state_conformity(self, state: str, strategy_name: str) -> dict:
        """Research state conformity for a specific strategy."""
        query = f"{state} state income tax conformity {strategy_name} 2024"
        return self._search(query, max_results=2)

    def research_ptet(self, state: str) -> dict:
        """Get current PTET rules for a state."""
        query = f"{state} pass-through entity tax PTET election 2024 rules deadline"
        return self._search(query, max_results=3)

    def _search(self, query: str, max_results: int = 3) -> dict:
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
            "include_answer": True,
        }
        try:
            resp = requests.post(self.API_URL, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return {
                "answer": data.get("answer", ""),
                "results": [
                    {"title": r.get("title", ""),
                     "url": r.get("url", ""),
                     "snippet": r.get("content", "")[:400]}
                    for r in data.get("results", [])
                ],
            }
        except requests.RequestException as e:
            logger.warning(f"Tavily search failed for '{query}': {e}")
            return {"answer": "", "results": []}


# ═══════════════════════════════════════════════════════════════════════════════
#  LLM CLIENT (OpenRouter + Groq)
# ═══════════════════════════════════════════════════════════════════════════════

class LLMClient:
    """
    Unified LLM client supporting OpenRouter and Groq.
    Falls back automatically between providers.
    """
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, config: EngineConfig):
        self.config = config

    def complete(self, system_prompt: str, user_prompt: str,
                 max_tokens: int = 2500, temperature: float = 0.1) -> str:
        """Run completion — tries primary, falls back to secondary."""
        if self.config.primary_provider == "openrouter":
            result = self._openrouter(system_prompt, user_prompt, max_tokens, temperature)
            if not result and self.config.groq_api_key:
                result = self._groq(system_prompt, user_prompt, max_tokens, temperature)
        else:
            result = self._groq(system_prompt, user_prompt, max_tokens, temperature)
            if not result and self.config.openrouter_api_key:
                result = self._openrouter(system_prompt, user_prompt, max_tokens, temperature)
        return result or "[AI synthesis unavailable — returning deterministic analysis only]"

    def _openrouter(self, system_prompt: str, user_prompt: str,
                    max_tokens: int, temperature: float) -> Optional[str]:
        if not self.config.openrouter_api_key:
            return None
        headers = {
            "Authorization": f"Bearer {self.config.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://dentist-tax-engine.local",
            "X-Title": "Dentists Tax Architecture Engine",
        }
        payload = {
            "model": self.config.openrouter_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        try:
            resp = requests.post(self.OPENROUTER_URL, headers=headers,
                                 json=payload, timeout=30)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except (requests.RequestException, KeyError, IndexError) as e:
            logger.warning(f"OpenRouter error: {e}")
            return None

    def _groq(self, system_prompt: str, user_prompt: str,
              max_tokens: int, temperature: float) -> Optional[str]:
        if not self.config.groq_api_key:
            return None
        headers = {
            "Authorization": f"Bearer {self.config.groq_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.config.groq_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        try:
            resp = requests.post(self.GROQ_URL, headers=headers,
                                 json=payload, timeout=20)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except (requests.RequestException, KeyError, IndexError) as e:
            logger.warning(f"Groq error: {e}")
            return None


# ═══════════════════════════════════════════════════════════════════════════════
#  REPORT ASSEMBLER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AssessmentReport:
    client_id: str
    tax_year: int
    generated_at: str
    dentist_profile: str
    dentist_confidence: float
    exposure_score: ExposureScore
    top_strategies: list[ScoredStrategy]
    total_federal_savings_low: float
    total_federal_savings_high: float
    total_state_savings_low: float
    total_state_savings_high: float
    ai_synthesis: str
    research_notes: list
    primary_state: str
    return_types: list
    phase: int = 1

    def to_dict(self) -> dict:
        d = asdict(self)
        # strategies are dataclasses — already handled by asdict
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


class ReportAssembler:

    def assemble(
        self,
        ret: TaxReturnJSON,
        exposure: ExposureScore,
        strategies: list[ScoredStrategy],
        ai_synthesis: str,
        profile: str,
        confidence: float,
        research_notes: list,
    ) -> AssessmentReport:

        fed_low  = sum(s.federal_savings_low  for s in strategies)
        fed_high = sum(s.federal_savings_high for s in strategies)
        st_low   = sum(s.state_savings_low    for s in strategies)
        st_high  = sum(s.state_savings_high   for s in strategies)

        # Avoid double-counting retirement strategies
        retirement_strats = [s for s in strategies if s.category == "Retirement & Benefits"]
        if len(retirement_strats) > 1:
            # Keep only the highest-scoring retirement strategy in totals
            for s in retirement_strats[1:]:
                fed_low  -= s.federal_savings_low
                fed_high -= s.federal_savings_high
                st_low   -= s.state_savings_low
                st_high  -= s.state_savings_high

        return AssessmentReport(
            client_id=ret.client_id,
            tax_year=ret.tax_year,
            generated_at=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            dentist_profile=profile,
            dentist_confidence=confidence,
            exposure_score=exposure,
            top_strategies=strategies,
            total_federal_savings_low=max(0, round(fed_low, 0)),
            total_federal_savings_high=max(0, round(fed_high, 0)),
            total_state_savings_low=max(0, round(st_low, 0)),
            total_state_savings_high=max(0, round(st_high, 0)),
            ai_synthesis=ai_synthesis,
            research_notes=research_notes,
            primary_state=ret.primary_state,
            return_types=ret.return_types,
        )


# ═══════════════════════════════════════════════════════════════════════════════
#  AI SYNTHESIS PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """You are the Dentists' Tax & Business Architecture Risk Assessment Engine.
You analyze tax returns ONLY (no questionnaire data in Phase 1).
Your job: produce a concise, specific, high-value risk summary for a licensed Tax & Business Architect.

Rules:
- Reference only what is evidenced in the return data provided
- Be specific about IRC sections and tax mechanics
- Rank concerns by dollar materiality
- Do NOT fabricate numbers — use the ranges provided
- Keep response under 400 words
- Tone: professional, direct, CPA-ready
- End with: "Phase 2 questionnaire will confirm: [3 key facts needed]"
"""

def build_synthesis_prompt(ret: TaxReturnJSON, exposure: ExposureScore,
                            strategies: list[ScoredStrategy],
                            research_notes: list) -> str:
    strat_summary = "\n".join(
        f"  {i+1}. {s.strategy_name} | Score: {s.total_score} | "
        f"Fed savings: ${s.federal_savings_low:,.0f}–${s.federal_savings_high:,.0f}"
        for i, s in enumerate(strategies[:6])
    )

    research_text = ""
    if research_notes:
        research_text = "\n\nLIVE RESEARCH CONTEXT:\n" + "\n".join(
            f"- {note}" for note in research_notes[:3]
        )

    return f"""RETURN ANALYSIS DATA:
Tax Year: {ret.tax_year}
Return Types: {', '.join(ret.return_types)}
Primary State: {ret.primary_state or 'Not detected'}

FINANCIAL SUMMARY:
AGI: ${ret.federal.agi:,.0f}
Federal Taxable Income: ${ret.federal.taxable_income:,.0f}
Federal Total Tax: ${ret.federal.total_tax:,.0f}
SE Tax: ${ret.federal.self_employment_tax:,.0f}
QBI Claimed: ${ret.federal.qbi_deduction:,.0f}
State Tax: ${sum(s.state_total_tax for s in ret.states.values()):,.0f}

EXPOSURE SCORE: {exposure.raw_score}/100 — {exposure.band_label}
Drivers: {'; '.join(exposure.top_drivers[:3])}

TOP RANKED STRATEGIES:
{strat_summary}
{research_text}

Provide a concise architectural risk assessment and synthesis."""


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN ENGINE ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════════

class DentistTaxEngine:
    """
    Main orchestrator. Call analyze_return() or analyze_pdf().
    """

    def __init__(self, config: Optional[EngineConfig] = None):
        self.config = config or EngineConfig.from_env()
        self.extractor  = PDFExtractor()
        self.signals    = SignalEngine()
        self.scorer     = StrategyScorer()
        self.exposure   = ExposureCalculator()
        self.classifier = DentistClassifier()
        self.llm        = LLMClient(self.config)
        self.researcher = TavilyResearcher(self.config.tavily_api_key) \
                          if self.config.tavily_api_key else None
        self.assembler  = ReportAssembler()

    def analyze_pdf(self, pdf_path: str, client_id: str = "CLIENT_001",
                    tax_year: int = 2024) -> AssessmentReport:
        """Full pipeline from PDF file."""
        ret = self.extractor.build_return_json(pdf_path, client_id, tax_year)
        return self._run_analysis(ret)

    def analyze_return(self, ret: TaxReturnJSON) -> AssessmentReport:
        """Full pipeline from pre-built TaxReturnJSON (useful for testing)."""
        return self._run_analysis(ret)

    def analyze_text(self, raw_text: str, client_id: str = "CLIENT_001",
                     tax_year: int = 2024) -> AssessmentReport:
        """Full pipeline from raw extracted PDF text string."""
        ret = self.extractor.build_return_json_from_text(raw_text, client_id, tax_year)
        return self._run_analysis(ret)

    def _run_analysis(self, ret: TaxReturnJSON) -> AssessmentReport:
        t0 = time.time()

        # Step 1: Derive signals
        sigs = self.signals.derive(ret)
        ret.signals = {k: v for k, v in sigs.items() if not k.startswith("_")}
        t1 = time.time()

        # Step 2: Score strategies
        strategies = self.scorer.score_all(sigs, self.config)
        t2 = time.time()

        # Step 3: Exposure score
        exposure = self.exposure.calculate(ret, sigs)
        t3 = time.time()

        # Step 4: Classify
        profile, confidence = self.classifier.classify(ret)

        # Step 5: Live research (optional)
        research_notes = []
        if self.researcher and self.config.enable_live_research and strategies:
            try:
                # Research top 2 strategies
                for strat in strategies[:2]:
                    result = self.researcher.research_strategy(
                        strat.strategy_name, strat.irc_authority
                    )
                    if result.get("answer"):
                        research_notes.append(
                            f"[{strat.strategy_name}] {result['answer'][:200]}"
                        )
                # Research state PTET if applicable
                if sigs.get("SIG_PTET_OPPORTUNITY") and ret.primary_state:
                    ptet = self.researcher.research_ptet(ret.primary_state)
                    if ptet.get("answer"):
                        research_notes.append(
                            f"[PTET {ret.primary_state}] {ptet['answer'][:200]}"
                        )
            except Exception as e:
                logger.warning(f"Research enrichment failed: {e}")
        t4 = time.time()

        # Step 6: AI synthesis
        user_prompt = build_synthesis_prompt(ret, exposure, strategies, research_notes)
        ai_text = self.llm.complete(SYSTEM_PROMPT, user_prompt)
        t5 = time.time()

        # Step 7: Assemble report
        report = self.assembler.assemble(
            ret, exposure, strategies, ai_text, profile, confidence, research_notes
        )

        total_ms = round((t5 - t0) * 1000)
        logger.info(
            f"Analysis complete in {total_ms}ms | "
            f"signals={round((t1-t0)*1000)}ms | "
            f"scoring={round((t2-t1)*1000)}ms | "
            f"exposure={round((t3-t2)*1000)}ms | "
            f"research={round((t4-t3)*1000)}ms | "
            f"llm={round((t5-t4)*1000)}ms"
        )
        return report


# ═══════════════════════════════════════════════════════════════════════════════
#  PRETTY PRINT CONSOLE OUTPUT
# ═══════════════════════════════════════════════════════════════════════════════

def print_report(report: AssessmentReport):
    """Terminal-friendly report output with rich formatting if available."""
    if RICH:
        _print_rich(report)
    else:
        _print_plain(report)


def _print_rich(report: AssessmentReport):
    exp = report.exposure_score
    band_colors = {"LOW": "green", "MODERATE": "yellow", "HIGH": "red", "SEVERE": "bold red"}
    color = band_colors.get(exp.band, "white")

    console.print()
    console.print(Panel.fit(
        f"[bold]DENTISTS' TAX RISK ASSESSMENT[/bold]\n"
        f"Client: {report.client_id}  |  Tax Year: {report.tax_year}  |  "
        f"Generated: {report.generated_at}\n"
        f"Profile: {report.dentist_profile} (confidence: {report.dentist_confidence:.0%})",
        border_style="blue"
    ))

    # Exposure score
    console.print(Panel(
        f"[{color}]TAX BLEED SCORE: {exp.raw_score}/100 — {exp.band_label}[/{color}]\n\n"
        f"Liability Intensity:     {exp.liability_intensity:.0f}/100\n"
        f"Structural Inefficiency: {exp.structural_inefficiency:.0f}/100\n"
        f"Opportunity Density:     {exp.opportunity_density:.0f}/100\n\n"
        f"[bold]Key Drivers:[/bold]\n" +
        "\n".join(f"  • {d}" for d in exp.top_drivers),
        title="TAX EXPOSURE ANALYSIS",
        border_style=color
    ))

    # Savings summary
    console.print(Panel(
        f"Total Estimated Federal Savings: [green]${report.total_federal_savings_low:,.0f} – "
        f"${report.total_federal_savings_high:,.0f}[/green]\n"
        f"Total Estimated State Savings:   [green]${report.total_state_savings_low:,.0f} – "
        f"${report.total_state_savings_high:,.0f}[/green]",
        title="ESTIMATED TOTAL SAVINGS OPPORTUNITY",
        border_style="green"
    ))

    # Strategy table
    table = Table(title=f"TOP {len(report.top_strategies)} RANKED STRATEGIES",
                  show_header=True, header_style="bold cyan")
    table.add_column("#",    width=3)
    table.add_column("Strategy",  width=35)
    table.add_column("Score",     width=6)
    table.add_column("Federal $", width=22)
    table.add_column("State $",   width=16)
    table.add_column("Days",      width=5)
    table.add_column("Category",  width=25)

    for i, s in enumerate(report.top_strategies, 1):
        table.add_row(
            str(i),
            s.strategy_name[:34],
            str(s.total_score),
            f"${s.federal_savings_low:,.0f}–${s.federal_savings_high:,.0f}",
            f"${s.state_savings_low:,.0f}–${s.state_savings_high:,.0f}",
            str(s.time_to_implement_days),
            s.category[:24],
        )
    console.print(table)

    # Strategy details
    for i, s in enumerate(report.top_strategies[:5], 1):
        console.print(Panel(
            f"[bold]{s.strategy_name}[/bold]\n"
            f"IRC Authority: {s.irc_authority}\n\n"
            f"[italic]{s.plain_english}[/italic]\n\n"
            f"[bold]Evidence from return:[/bold]\n" +
            "\n".join(f"  ✓ {e}" for e in s.evidence_basis[:3]) +
            f"\n\n[bold]Documentation (IRC §6001):[/bold]\n" +
            "\n".join(f"  • {d}" for d in s.documentation_checklist) +
            (f"\n\n[bold]Prerequisites:[/bold]\n" +
             "\n".join(f"  ⚠ {p}" for p in s.prerequisites)
             if s.prerequisites else ""),
            title=f"Strategy #{i} — Score: {s.total_score}",
            border_style="cyan"
        ))

    # AI synthesis
    if report.ai_synthesis and not report.ai_synthesis.startswith("[AI synthesis"):
        console.print(Panel(
            report.ai_synthesis,
            title="AI ARCHITECTURAL SYNTHESIS",
            border_style="magenta"
        ))

    # Research notes
    if report.research_notes:
        console.print(Panel(
            "\n".join(f"• {n}" for n in report.research_notes),
            title="LIVE RESEARCH CONTEXT (Tavily)",
            border_style="yellow"
        ))

    console.print()


def _print_plain(report: AssessmentReport):
    exp = report.exposure_score
    print("\n" + "="*70)
    print("DENTISTS' TAX RISK ASSESSMENT")
    print(f"Client: {report.client_id} | Year: {report.tax_year} | {report.generated_at}")
    print(f"Profile: {report.dentist_profile} ({report.dentist_confidence:.0%} confidence)")
    print("="*70)
    print(f"\nTAX BLEED SCORE: {exp.raw_score}/100 — {exp.band_label}")
    print(f"  Liability Intensity:     {exp.liability_intensity:.0f}/100")
    print(f"  Structural Inefficiency: {exp.structural_inefficiency:.0f}/100")
    print(f"  Opportunity Density:     {exp.opportunity_density:.0f}/100")
    if exp.top_drivers:
        print("  Drivers:")
        for d in exp.top_drivers:
            print(f"    • {d}")

    print(f"\nESTIMATED SAVINGS:")
    print(f"  Federal: ${report.total_federal_savings_low:,.0f} – ${report.total_federal_savings_high:,.0f}")
    print(f"  State:   ${report.total_state_savings_low:,.0f} – ${report.total_state_savings_high:,.0f}")

    print(f"\nTOP {len(report.top_strategies)} STRATEGIES:")
    for i, s in enumerate(report.top_strategies, 1):
        print(f"\n  {i}. {s.strategy_name}")
        print(f"     IRC: {s.irc_authority}")
        print(f"     Score: {s.total_score} | Federal: ${s.federal_savings_low:,.0f}–${s.federal_savings_high:,.0f}")
        print(f"     Time: {s.time_to_implement_days} days | Category: {s.category}")
        print(f"     {s.plain_english[:120]}...")

    if report.ai_synthesis and not report.ai_synthesis.startswith("["):
        print("\nAI SYNTHESIS:")
        print(report.ai_synthesis[:800])

    print("\n" + "="*70)
