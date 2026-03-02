"""
Dentists' Tax & Business Architecture System™
FastAPI Web Server
=====================================================
Endpoints:
  POST /analyze/pdf          Upload a PDF tax return
  POST /analyze/text         Submit pre-extracted text
  POST /analyze/return       Submit TaxReturnJSON directly
  GET  /health               Health check
  GET  /strategies           List all 52 strategies

Run:
    pip install fastapi uvicorn python-multipart
    uvicorn api:app --reload --port 8000
"""

try:
    from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("⚠ FastAPI not installed. Run: pip install fastapi uvicorn python-multipart")

import os
import json
import time
import tempfile
from pathlib import Path

from engine import (
    DentistTaxEngine, EngineConfig, TaxReturnJSON, FederalNumbers,
    StateNumbers, EntityRecord, DepreciationSummary, STRATEGY_LIBRARY
)


# ── Config & Engine ────────────────────────────────────────────────────────────
config = EngineConfig.from_env()
engine = DentistTaxEngine(config)


# ── Pydantic Models ────────────────────────────────────────────────────────────

class FederalInput(BaseModel):
    filing_status: str = "MFJ"
    agi: float = 0
    taxable_income: float = 0
    total_tax: float = 0
    w2_wages: float = 0
    self_employment_tax: float = 0
    niit: float = 0
    amt: float = 0
    qbi_deduction: float = 0
    itemized_deductions: float = 0
    salt_deduction_claimed: float = 0
    charitable_contributions: float = 0

class StateInput(BaseModel):
    state_taxable_income: float = 0
    state_total_tax: float = 0

class EntityInput(BaseModel):
    entity_id: str = "E1"
    entity_name: str = ""
    entity_type: str = "1120S"
    gross_receipts: float = 0
    ordinary_business_income: float = 0
    owner_wages: float = 0
    distributions: float = 0
    officer_compensation: float = 0
    rent_paid: float = 0
    retirement_plan_expense: float = 0
    depreciation_total: float = 0
    professional_fees: float = 0
    auto_truck: float = 0
    travel: float = 0
    health_insurance_expense: float = 0
    tax_planning_fees_detected: bool = False

class ReturnInput(BaseModel):
    client_id: str = "CLIENT_001"
    tax_year: int = 2024
    return_types: list[str] = Field(default_factory=lambda: ["1040"])
    state_returns_present: list[str] = Field(default_factory=list)
    primary_state: str = ""
    ptet_election_detected: bool = False
    dentist_indicator: str = "UNKNOWN"
    dependents_present: bool = False
    schedule_c_present: bool = False
    schedule_e_present: bool = False
    real_estate_activity_present: bool = False
    federal: FederalInput = Field(default_factory=FederalInput)
    states: dict[str, StateInput] = Field(default_factory=dict)
    entities: list[EntityInput] = Field(default_factory=list)

class TextInput(BaseModel):
    text: str
    client_id: str = "CLIENT_001"
    tax_year: int = 2024


def return_input_to_json(inp: ReturnInput) -> TaxReturnJSON:
    """Convert Pydantic input model to internal TaxReturnJSON."""
    fed_data = inp.federal.dict()
    fed = FederalNumbers(**{k: v for k, v in fed_data.items()
                           if k in FederalNumbers.__dataclass_fields__})
    # Estimate marginal rate
    ti = fed.taxable_income
    if ti > 731200:   fed.marginal_rate_estimate = 0.37
    elif ti > 487450: fed.marginal_rate_estimate = 0.35
    elif ti > 231250: fed.marginal_rate_estimate = 0.32
    elif ti > 100525: fed.marginal_rate_estimate = 0.24
    else:              fed.marginal_rate_estimate = 0.22

    states = {}
    for state_code, state_data in inp.states.items():
        states[state_code] = StateNumbers(
            state_taxable_income=state_data.state_taxable_income,
            state_total_tax=state_data.state_total_tax,
        )

    entities = []
    for i, e in enumerate(inp.entities):
        entities.append(EntityRecord(
            entity_id=e.entity_id or f"E{i+1}",
            entity_name=e.entity_name,
            entity_type=e.entity_type,
            gross_receipts=e.gross_receipts,
            ordinary_business_income=e.ordinary_business_income,
            owner_wages=e.owner_wages,
            distributions=e.distributions,
            officer_compensation=e.officer_compensation,
            rent_paid=e.rent_paid,
            retirement_plan_expense=e.retirement_plan_expense,
            depreciation_total=e.depreciation_total,
            professional_fees=e.professional_fees,
            auto_truck=e.auto_truck,
            travel=e.travel,
            health_insurance_expense=e.health_insurance_expense,
            tax_planning_fees_detected=e.tax_planning_fees_detected,
        ))

    ret = TaxReturnJSON(
        client_id=inp.client_id,
        tax_year=inp.tax_year,
        return_types=inp.return_types,
        state_returns_present=inp.state_returns_present,
        primary_state=inp.primary_state,
        ptet_election_detected=inp.ptet_election_detected,
        dentist_indicator=inp.dentist_indicator,
        dependents_present=inp.dependents_present,
        schedule_c_present=inp.schedule_c_present,
        schedule_e_present=inp.schedule_e_present,
        real_estate_activity_present=inp.real_estate_activity_present,
        federal=fed,
        states=states,
        entities=entities,
        high_income=fed.agi > 300_000,
        meaningful_tax_liability=fed.total_tax > 70_000,
        w2_present=bool(fed.w2_wages),
        k1_present=len(entities) > 0,
        depreciation=DepreciationSummary(
            has_depreciation=any(e.depreciation_total > 0 for e in entities),
            total_depreciation=sum(e.depreciation_total for e in entities),
        ),
    )
    return ret


if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="Dentists' Tax & Business Architecture Engine",
        description="Phase 1 Tax Risk Assessment — Return-Only Analysis",
        version="2026.02",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Endpoints ──────────────────────────────────────────────────────────────

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "version": "2026.02",
            "providers": {
                "openrouter": bool(config.openrouter_api_key),
                "groq": bool(config.groq_api_key),
                "tavily": bool(config.tavily_api_key),
            }
        }

    @app.get("/strategies")
    def list_strategies():
        """Return the full strategy library (metadata only, no lambda functions)."""
        return [
            {
                "id": s["id"],
                "name": s["name"],
                "irc": s["irc"],
                "category": s["category"],
                "phase_1_eligible": s.get("phase_1_eligible", True),
                "speed_days": s.get("speed_days", 60),
                "complexity": s.get("complexity", 20),
                "audit_friction": s.get("audit_friction", 10),
            }
            for s in STRATEGY_LIBRARY
        ]

    @app.post("/analyze/return")
    async def analyze_return(inp: ReturnInput):
        """Submit structured return data for analysis."""
        t0 = time.time()
        try:
            ret = return_input_to_json(inp)
            report = engine.analyze_return(ret)
            elapsed = round((time.time() - t0) * 1000)
            result = report.to_dict()
            result["processing_ms"] = elapsed
            return JSONResponse(content=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/analyze/text")
    async def analyze_text(inp: TextInput):
        """Submit pre-extracted PDF text for analysis."""
        t0 = time.time()
        try:
            report = engine.analyze_text(inp.text, inp.client_id, inp.tax_year)
            elapsed = round((time.time() - t0) * 1000)
            result = report.to_dict()
            result["processing_ms"] = elapsed
            return JSONResponse(content=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/analyze/pdf")
    async def analyze_pdf(
        file: UploadFile = File(...),
        client_id: str = "CLIENT_001",
        tax_year: int = 2024,
    ):
        """Upload a PDF tax return for analysis."""
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        t0 = time.time()
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(await file.read())
                tmp_path = tmp.name
            try:
                report = engine.analyze_pdf(tmp_path, client_id, tax_year)
            finally:
                Path(tmp_path).unlink(missing_ok=True)
            elapsed = round((time.time() - t0) * 1000)
            result = report.to_dict()
            result["processing_ms"] = elapsed
            return JSONResponse(content=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/demo")
    async def run_demo():
        """Run analysis with built-in demo data (CA practice owner)."""
        from run import build_demo_return
        t0 = time.time()
        ret = build_demo_return()
        report = engine.analyze_return(ret)
        elapsed = round((time.time() - t0) * 1000)
        result = report.to_dict()
        result["processing_ms"] = elapsed
        return JSONResponse(content=result)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not FASTAPI_AVAILABLE:
        print("Install FastAPI: pip install fastapi uvicorn python-multipart")
    else:
        uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
