# Dentists' Tax & Business Architecture System™
## Phase 1 — Tax Risk Assessment Engine

---

## Architecture Overview

```
PDF / Text / JSON
       │
       ▼
┌─────────────────┐
│  PDFExtractor   │  Regex + pdfplumber → raw text → structured JSON
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SignalEngine   │  TaxReturnJSON → flat signals dict  (<1ms)
└────────┬────────┘
         │
┌────────┼────────────────────────┐
│        │                        │
▼        ▼                        ▼
StrategyScorer  ExposureCalculator  DentistClassifier
│        │                        │
└────────┼────────────────────────┘
         │
         ▼
┌─────────────────┐
│ TavilyResearcher│  Live IRC/state conformity research (optional)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   LLMClient     │  OpenRouter (primary) + Groq (fallback)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ReportAssembler │  Final AssessmentReport
└─────────────────┘
```

### Phase Separation (per spec)
| Phase | Input | Output |
|-------|-------|--------|
| **Phase 1** (this engine) | Tax returns only (1040/1120S/1120/1065) | Risk score + ranked strategies + savings ranges |
| **Phase 2** (post-subscription) | Phase 1 + confidential questionnaire | Engineered plan + MSO/captive/7702 analysis |

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API keys
```bash
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY, GROQ_API_KEY, TAVILY_API_KEY
```

### 3. Run the demo
```bash
# Demo: high-income CA practice owner (S-Corp)
python run.py --demo

# Demo: NY associate dentist (W-2)
python run.py --demo2

# Analyze a real PDF
python run.py --pdf /path/to/return.pdf

# Save report to JSON
python run.py --demo --output report.json

# Skip AI (deterministic only, no API keys needed)
python run.py --demo --no-ai --no-search

# Use Groq instead of OpenRouter
python run.py --demo --provider groq
```

### 4. Start the API server
```bash
pip install fastapi uvicorn python-multipart
uvicorn api:app --reload --port 8000
```

API docs: http://localhost:8000/docs

---

## API Reference

### POST `/analyze/return`
Submit structured return data.

```json
{
  "client_id": "DR_SMITH_2024",
  "tax_year": 2024,
  "return_types": ["1040", "1120S"],
  "state_returns_present": ["CA"],
  "primary_state": "CA",
  "ptet_election_detected": false,
  "dentist_indicator": "CONFIRMED",
  "dependents_present": true,
  "federal": {
    "filing_status": "MFJ",
    "agi": 680000,
    "taxable_income": 610000,
    "total_tax": 192000,
    "w2_wages": 160000,
    "qbi_deduction": 0
  },
  "states": {
    "CA": {
      "state_taxable_income": 620000,
      "state_total_tax": 65000
    }
  },
  "entities": [
    {
      "entity_type": "1120S",
      "gross_receipts": 1850000,
      "ordinary_business_income": 460000,
      "owner_wages": 160000,
      "distributions": 300000,
      "retirement_plan_expense": 0,
      "depreciation_total": 18000
    }
  ]
}
```

### POST `/analyze/pdf`
Upload PDF file (multipart form).

### POST `/analyze/text`
Submit pre-extracted text.

### GET `/demo`
Run with built-in demo data.

### GET `/strategies`
List all strategy metadata.

---

## Scoring Algorithm

### Tax Bleed Score (0–100)
```
TaxBleedScore = 
    45% × LiabilityIntensity
  + 35% × StructuralInefficiency  
  + 20% × OpportunityDensity
```

**Bands:**
| Score | Band | Label |
|-------|------|-------|
| 0–24 | LOW | Low Bleed |
| 25–49 | MODERATE | Moderate Bleed |
| 50–74 | HIGH | High Bleed |
| 75–100 | SEVERE | Severe Bleed (Architectural Failure) |

### Strategy Score (0–100)
```
TotalScore =
    35% × MaterialityScore
  + 20% × EligibilityScore
  + 15% × FederalImpactScore
  + 10% × StateImpactScore
  + 10% × SpeedToImplementScore
  -  10% × ComplexityPenalty
  -   5% × AuditFrictionPenalty
  -   5% × MissingPrerequisitePenalty
```

---

## Strategy Library (14 implemented, 52 in spec)

| # | Strategy | IRC | Category |
|---|----------|-----|----------|
| 1 | Owner's Salary Strategy | §3101, §1402 | Entity Structuring |
| 2 | QBI Deduction | §199A | Deductions |
| 3 | Cash Balance Plan | §401(a) | Retirement |
| 4 | Accountable Plan | §62(a)(2)(A) | Deductions |
| 5 | Home Administrative Office | §280A(c) | Deductions |
| 6 | Augusta Rule | §280A(g) | Deductions |
| 7 | Hiring Children | §73, §3111 | Income Shifting |
| 8 | Cost Segregation | §168, Rev.Proc. 87-56 | Depreciation |
| 9 | 100% Bonus Depreciation | §168(k) | Depreciation |
| 10 | 401(k) + Profit Sharing | §402(g), §415 | Retirement |
| 11 | Schedule C → S-Corp | §1361-1379 | Entity Structuring |
| 12 | PTET Election | §164(b)(6) | SALT Workaround |
| 13 | SE Health Insurance | §162(l) | Deductions |
| 14 | HSA | §223 | Retirement |

---

## Performance Target
| Step | Target | Notes |
|------|--------|-------|
| PDF extraction | <3s | pdfplumber + regex |
| Signal derivation | <5ms | Pure Python dict ops |
| Strategy scoring | <50ms | Deterministic, no AI |
| Tavily research | 2–5s | Optional, parallel |
| LLM synthesis | 3–8s | Groq is fastest (<3s) |
| **Total** | **<15s** | Per spec requirement |

---

## Extending the Strategy Library

Add any strategy to `STRATEGY_LIBRARY` in `engine.py` using this structure:

```python
{
    "id": "DTTS-XXX-strategy-name",
    "name": "Strategy Display Name",
    "irc": "IRC §XXX",
    "category": "Category Name",
    "phase_1_eligible": True,
    "eligibility_logic": lambda s: s["SIG_SOME_SIGNAL"],
    "materiality_fn": lambda s: 75,   # 0-100
    "fed_savings_fn":  lambda s: s["_agi"] * 0.05 * s["_fed_marginal_rate"],
    "state_savings_fn": lambda s: 0,
    "speed_days": 30,
    "complexity": 20,
    "audit_friction": 10,
    "plain_english": "Plain language explanation...",
    "documentation": ["Doc 1", "Doc 2"],
    "cpa_handoff": ["Step 1", "Step 2"],
    "prerequisites": ["Requirement 1"],
}
```

Available signals: See `SignalEngine.derive()` for the full list of `SIG_*` keys.

---

## File Structure
```
dentist_tax_engine/
├── engine.py          # Core engine (PDF extraction, signals, scoring, LLM)
├── run.py             # CLI runner + demo data
├── api.py             # FastAPI web server
├── requirements.txt   # Python dependencies
├── .env.example       # API key template
└── README.md          # This file
```

---

## API Keys

| Service | URL | Notes |
|---------|-----|-------|
| OpenRouter | https://openrouter.ai | Access to Claude, GPT-4, Llama, etc. |
| Groq | https://console.groq.com | Very fast inference, free tier available |
| Tavily | https://tavily.com | Live web search, tax law research |

---

## Phase 2 Extension Points

The engine is designed for Phase 2 expansion. After questionnaire collection:
- Captive insurance feasibility (`SIG_HIGH_INCOME + facts`)
- MSO/DSO layering strategies
- Family foundation analysis
- IRC §7702 life insurance strategies
- STR "active" exception (requires rental day count from questionnaire)
- Real estate professional status (requires time tracking data)

These are flagged in the strategy library as `"phase_1_eligible": False` and surfaced 
in Phase 2 after questionnaire completion.
