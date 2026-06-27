"""
Dentists' Tax & Business Architecture System™
A professional tax analysis platform for high-income dental practice owners.

Run:
    pip install streamlit pdfplumber requests python-dotenv
    streamlit run app.py
"""

import os
import re
import time
import tempfile
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import streamlit as st

# ═══════════════════════════════════════════════════════════════════
#  PAGE CONFIG (must be first Streamlit call)
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Dentists' Tax Architecture System™",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════
#  ENVIRONMENT SETUP
# ═══════════════════════════════════════════════════════════════════
def load_env(path=".env"):
    """Load environment variables from .env file."""
    if Path(path).exists():
        for line in Path(path).read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env()

# ═══════════════════════════════════════════════════════════════════
#  OPTIONAL DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════
try:
    import pdfplumber
    PDF_OK = True
except ImportError:
    PDF_OK = False

# ═══════════════════════════════════════════════════════════════════
#  SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════
for k, v in [("report_done", False), ("ai_result", ""), ("upload_name", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════════════════════
#  DESIGN TOKENS & THEME
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --navy:    #09192F;
  --navy-lt: #122040;
  --gold:    #BFA05A;
  --gold-lt: #D4B978;
  --cream:   #F7F3EC;
  --white:   #FFFFFF;
  --ink:     #1A1F2E;
  --slate:   #3D4555;
  --muted:   #7A8099;
  --border:  #DDD8CE;
  --b2:      #EAE6DC;
  --ok:      #0E7A62;
  --ok-lt:   #E6F7F3;
  --ok-bdr:  #74C5AE;
  --warn:    #B07010;
  --warn-lt: #FEF9ED;
  --warn-bdr:#E0C060;
  --bad:     #A82818;
  --bad-lt:  #FEF3F2;
  --bad-bdr: #F2B8B0;
}

html, body, [class*="css"] {
  font-family: 'Inter', sans-serif;
  background: var(--cream);
  color: var(--ink);
}
.stApp { background: var(--cream); }
.block-container { padding-top: 0 !important; max-width: 100% !important; }

section[data-testid="stSidebar"] {
  background: var(--navy) !important;
  border-right: 2px solid var(--gold);
}
section[data-testid="stSidebar"] * { color: #C0CCDC !important; }
section[data-testid="stSidebar"] h3 {
  color: var(--gold) !important;
  font-family: 'Cormorant Garamond', serif !important;
  font-size: 1rem !important;
  letter-spacing: .04em;
  margin-bottom: .45rem !important;
}
section[data-testid="stSidebar"] .stTextInput label {
  color: #7080A0 !important;
  font-size: .6rem !important;
  text-transform: uppercase;
  letter-spacing: .14em;
  font-weight: 600;
}
section[data-testid="stSidebar"] input {
  background: rgba(255,255,255,.05) !important;
  border-color: rgba(191,160,90,.25) !important;
  color: #EBF0FA !important;
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: .75rem !important;
}

.phdr {
  background: var(--navy);
  padding: 1.75rem 2.4rem 1.5rem;
  margin: -1rem -1rem 0 -1rem;
  border-bottom: 2px solid var(--gold);
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}
.phdr-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.9rem;
  font-weight: 700;
  color: #FFF;
  letter-spacing: -.01em;
  line-height: 1.1;
}
.phdr-sub {
  font-size: .58rem;
  text-transform: uppercase;
  letter-spacing: .24em;
  color: var(--gold);
  margin-top: .3rem;
  font-weight: 500;
}
.phdr-meta {
  font-family: 'IBM Plex Mono', monospace;
  font-size: .5rem;
  color: rgba(255,255,255,.2);
  text-align: right;
  line-height: 2;
}

.col-hdr {
  font-size: .56rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .24em;
  color: var(--muted);
  padding-bottom: .4rem;
  border-bottom: 1px solid var(--b2);
  margin-bottom: .9rem;
}

.upwell {
  background: var(--white);
  border: 1.5px dashed var(--border);
  border-radius: 12px;
  padding: 2.2rem 1.5rem;
  text-align: center;
  margin-bottom: .75rem;
}
.upwell-icon  { font-size: 2rem; display: block; margin-bottom: .55rem; }
.upwell-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--navy);
  margin-bottom: .25rem;
}
.upwell-hint  { font-size: .72rem; color: var(--muted); line-height: 1.6; }

.stButton > button[kind="primary"] {
  background: var(--navy) !important;
  color: var(--gold) !important;
  border: 1.5px solid var(--gold) !important;
  border-radius: 6px !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 700 !important;
  font-size: .76rem !important;
  text-transform: uppercase;
  letter-spacing: .12em;
  padding: .7rem 1.5rem !important;
  width: 100% !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--gold) !important;
  color: var(--navy) !important;
}
.stButton > button[kind="primary"]:disabled { opacity: .38 !important; }

.card-exp {
  background: var(--bad-lt);
  border: 1px solid var(--bad-bdr);
  border-left: 3px solid var(--bad);
  border-radius: 6px;
  padding: .85rem 1.05rem;
  margin-bottom: .45rem;
  font-size: .82rem; color: var(--slate); line-height: 1.72;
}
.card-rec {
  background: var(--white);
  border: 1px solid var(--border);
  border-left: 3px solid var(--gold);
  border-radius: 6px;
  padding: .85rem 1.05rem;
  margin-bottom: .45rem;
  font-size: .82rem; color: var(--slate); line-height: 1.72;
}

.rpt {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 6px 32px rgba(9,25,47,.09);
  margin-top: 1rem;
}
.rpt-head {
  background: var(--navy);
  padding: 1.6rem 2rem 1.4rem;
  border-bottom: 2px solid var(--gold);
}
.rpt-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.55rem;
  font-weight: 700;
  color: #FFF;
  margin: 0 0 .2rem;
  letter-spacing: -.01em;
}
.rpt-sub {
  font-size: .6rem;
  color: rgba(255,255,255,.35);
  text-transform: uppercase;
  letter-spacing: .14em;
}
.rpt-body { padding: 2rem; }

.sec-hdr {
  display: flex;
  align-items: center;
  gap: .65rem;
  margin: 2.1rem 0 .8rem;
  padding-bottom: .5rem;
  border-bottom: 1.5px solid var(--cream);
}
.sec-num {
  background: var(--navy);
  color: var(--gold);
  font-family: 'IBM Plex Mono', monospace;
  font-size: .6rem;
  font-weight: 600;
  width: 1.55rem;
  height: 1.55rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.sec-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1rem;
  font-weight: 700;
  color: var(--navy);
}

.welcome-card {
  background: var(--white);
  border: 1px solid var(--b2);
  border-radius: 12px;
  padding: 1.6rem 1.75rem 1.5rem;
  margin-bottom: 1rem;
}
.welcome-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--navy);
  margin-bottom: .45rem;
}
.welcome-body {
  font-size: .82rem;
  color: var(--slate);
  line-height: 1.68;
}

</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
#  PDF EXTRACTION
# ═══════════════════════════════════════════════════════════════════
def extract_pdf(path: str) -> str:
    """Extract text from PDF file."""
    if not PDF_OK:
        raise ImportError("Run: pip install pdfplumber")
    pages = []
    with pdfplumber.open(path) as f:
        for pg in f.pages:
            t = pg.extract_text()
            if t:
                pages.append(t)
    return "\n\n".join(pages)

# ═══════════════════════════════════════════════════════════════════
#  LLM INTEGRATION (OpenRouter + Claude Opus 4.8 Fast)
# ═══════════════════════════════════════════════════════════════════
def call_openrouter(api_key: str, user_prompt: str) -> str:
    """Call OpenRouter API with Claude Opus 4.8 Fast model."""
    import requests
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://dentist-tax-system.com",
        "X-Title": "Dentists Tax Architecture System",
    }
    
    payload = {
        "model": "anthropic/claude-opus-4.8-fast",
        "messages": [
            {
                "role": "system",
                "content": """You are a senior tax architect with two decades of experience advising 
high-income dental practice owners. You read tax returns and write concise client memoranda that 
reflect the specific numbers, forms, and entity structure. Be direct, precise, and evidence-based.
Never recommend strategies you cannot justify with data from the return."""
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "max_tokens": 3000,
        "temperature": 0.2,
    }
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# ═══════════════════════════════════════════════════════════════════
#  ANALYSIS ENGINE
# ═══════════════════════════════════════════════════════════════════
def build_analysis_prompt(return_data: str) -> str:
    """Build the prompt for tax analysis."""
    return f"""Analyze this dental practice tax return and provide a 5-section assessment:

TAX RETURN DATA:
{return_data[:8000]}

Please provide exactly 5 sections with these headers (in this order):

## SECTION I: TAX EXPOSURE ANALYSIS
Identify all active tax exposures: unshielded income flows, missing forms, excess self-employment tax, 
audit-risk patterns, and state compliance gaps. Reference actual line items.

## SECTION II: STRUCTURAL INEFFICIENCIES
Analyze the business architecture: entity type optimization, W-2 salary calibration, retirement funding 
gaps, expense categorization issues, and missing management company structures.

## SECTION III: RECOMMENDED STRATEGIES
Recommend specific IRS-approved strategies with direct evidentiary support from the return. 
Weave IRC citations naturally into explanations.

## SECTION IV: DOLLAR IMPACT ESTIMATES
For each strategy, provide specific federal savings estimates (conservative to optimistic range).
End with a combined total.

## SECTION V: TAX PROTECTION VERDICT
Provide a clear verdict: "Full Protection Achievable", "Partial Protection Achievable", or "Protection Limited".
Include the disclaimer that this is for professional review only, not finalized tax advice.

Keep explanations concise and professional."""

def run_analysis(raw_text: str, api_key: str) -> str:
    """Run the full tax analysis via OpenRouter."""
    prompt = build_analysis_prompt(raw_text)
    return call_openrouter(api_key, prompt)

# ═══════════════════════════════════════════════════════════════════
#  REPORT PARSING
# ═══════════════════════════════════════════════════════════════════
_SECTIONS = ["SECTION I", "SECTION II", "SECTION III", "SECTION IV", "SECTION V"]

def parse_sections(text: str) -> dict:
    """Parse AI response into sections."""
    out = {}
    for i, k in enumerate(_SECTIONS):
        idx = text.find(k)
        if idx == -1:
            idx = text.find(f"## {k}")
        if idx == -1:
            out[k] = ""
            continue
        
        nxt = len(text)
        if i < 4:
            for next_k in _SECTIONS[i+1:]:
                j = text.find(next_k, idx + 1)
                if j == -1:
                    j = text.find(f"## {next_k}", idx + 1)
                if j != -1 and j < nxt:
                    nxt = j
        
        chunk = text[idx:nxt]
        lines = []
        for ln in chunk.splitlines():
            s = ln.strip()
            if s.startswith("SECTION") or s.startswith("##"):
                continue
            if s and not s.startswith("═") and not s.startswith("─"):
                lines.append(ln)
        
        out[k] = "\n".join(lines).strip()
    return out

def parse_paragraphs(t: str):
    """Split text into paragraphs."""
    return [p.strip() for p in t.split("\n\n") if p.strip()]

# ═══════════════════════════════════════════════════════════════════
#  REPORT RENDERING
# ═══════════════════════════════════════════════════════════════════
def render_report(ai_text: str, fname: str = ""):
    """Render the full report."""
    now = datetime.utcnow()
    did = f"DTTS-{now.strftime('%Y%m%d-%H%M')}"
    secs = parse_sections(ai_text)

    st.markdown(f"""
<div class="rpt">
  <div class="rpt-head">
    <div class="rpt-title">Tax Architecture Assessment</div>
    <div class="rpt-sub">Dental Practice · Phase 1 · Return-Only Analysis</div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:.5rem;color:rgba(255,255,255,.2);margin-top:.5rem;">
      Doc: {did} · {now.strftime("%b %d, %Y · %H:%M UTC")} · File: {fname or 'Uploaded return'}
    </div>
  </div>
  <div class="rpt-body">
""", unsafe_allow_html=True)

    SECS = [
        ("SECTION I",   "I",   "Tax Exposure Analysis",      "Problems found in your return"),
        ("SECTION II",  "II",  "Structural Inefficiencies",  "Business architecture gaps"),
        ("SECTION III", "III", "Recommended Strategies",     "IRS-approved strategies for your situation"),
        ("SECTION IV",  "IV",  "Dollar Impact Estimates",    "How much you could save"),
        ("SECTION V",   "V",   "Tax Protection Verdict",     "What's achievable for you"),
    ]

    for k, num, title, sub in SECS:
        body = secs.get(k, "")
        ps = parse_paragraphs(body)

        st.markdown(f"""
<div class="sec-hdr">
  <div class="sec-num">{num}</div>
  <div class="sec-title">{title}</div>
</div>
""", unsafe_allow_html=True)

        if not ps:
            st.markdown('<p style="color:#9CA3AF;font-style:italic;font-size:.8rem;">No content extracted.</p>',
                        unsafe_allow_html=True)
            continue

        for para in ps:
            if "licensed tax architect" in para.lower() or "do not constitute" in para.lower():
                st.markdown(f'<div class="card-rec"><strong>⚖️ Professional Disclaimer:</strong> {para}</div>',
                            unsafe_allow_html=True)
            elif k == "SECTION IV" and any(x in para.lower() for x in ["total", "combined", "aggregate"]):
                st.markdown(f'<div style="background:var(--navy);border-radius:8px;padding:1.2rem;color:#FFF;margin:.75rem 0;"><div style="font-size:.56rem;text-transform:uppercase;letter-spacing:.18em;color:rgba(255,255,255,.38);">Combined Annual Savings Estimate</div><div style="font-family:Cormorant Garamond,serif;font-size:1.7rem;font-weight:700;color:var(--gold);margin-top:.5rem;">{para}</div></div>',
                        unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="card-rec">{para}</div>', unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        "⬇  Download Full Assessment (TXT)",
        data=ai_text,
        file_name=f"tax_assessment_{did}.txt",
        mime="text/plain",
    )

def render_welcome():
    """Render the welcome panel."""
    st.markdown(f"""
<div class="welcome-card">
  <span style="font-size:2rem;display:block;margin-bottom:.65rem;">🔍</span>
  <div class="welcome-title">Your Personal Tax Review Starts Here</div>
  <div class="welcome-body">
    Upload your tax return and this system will read it line by line — finding what you're 
    overpaying, what's missing, and which strategies apply to your exact situation.
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div style="font-size:.62rem;font-weight:700;text-transform:uppercase;letter-spacing:.18em;color:var(--muted);margin:.5rem 0 .45rem;">
  How it works
</div>
""", unsafe_allow_html=True)
    
    cols = st.columns(3)
    with cols[0]:
        st.markdown("**1️⃣ Upload**")
        st.caption("Drop in your PDF tax return")
    with cols[1]:
        st.markdown("**2️⃣ Analyze**")
        st.caption("AI analyzes your specific return")
    with cols[2]:
        st.markdown("**3️⃣ Review**")
        st.caption("Get a plain-English report with savings")

# ═══════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════
def render_sidebar() -> dict:
    """Render the sidebar configuration."""
    with st.sidebar:
        st.markdown("""
<div style="padding:1.4rem 0 1rem;">
  <div style="font-family:'Cormorant Garamond',serif;font-size:1.2rem;
              font-weight:700;color:#BFA05A;line-height:1.28;">
    Dentists' Tax<br>Architecture™
  </div>
  <div style="font-size:.55rem;text-transform:uppercase;letter-spacing:.22em;
              color:#404B60;margin-top:.35rem;font-weight:600;">
    Phase 1 &nbsp;·&nbsp; Return Analysis
  </div>
</div>
<hr style="border-color:rgba(191,160,90,.15);margin:0 0 1.1rem;">
""", unsafe_allow_html=True)

        st.markdown("### API Configuration")
        api_key = st.text_input(
            "OpenRouter API Key",
            value=os.getenv("OPENROUTER_API_KEY", ""),
            type="password",
            placeholder="sk-or-..."
        )

        st.markdown("---")
        st.markdown("### Status")
        dot = "🟢" if api_key else "🔴"
        st.markdown(
            f'<div style="font-size:.71rem;margin-bottom:.26rem;">{dot}&nbsp; '
            f'{"✓ OpenRouter Connected" if api_key else "⚠ No API Key"}</div>',
            unsafe_allow_html=True
        )
        pdf_dot = "🟢" if PDF_OK else "🔴"
        st.markdown(
            f'<div style="font-size:.71rem;margin-bottom:.26rem;">{pdf_dot}&nbsp; '
            f'{"✓ PDF Reader Ready" if PDF_OK else "⚠ PDF Reader Missing"}</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div style="font-size:.71rem;">ℹ️&nbsp; Using Claude Opus 4.8 Fast</div>',
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.markdown(
            '<div style="font-size:.58rem;color:#3D4B60;line-height:1.65;">'
            '<strong>Disclaimer:</strong> Analysis is for professional review only. '
            'Not finalized tax advice. Consult a licensed tax architect before implementation.'
            '</div>',
            unsafe_allow_html=True
        )

    return {"api_key": api_key}

# ═══════════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════════
def main():
    """Main application logic."""
    # Header
    st.markdown("""
<div class="phdr">
  <div>
    <div class="phdr-title">Dentists' Tax &amp; Business Architecture System™</div>
    <div class="phdr-sub">Phase 1 &nbsp;·&nbsp; Tax Risk Assessment &nbsp;·&nbsp; Return-Only Analysis</div>
  </div>
  <div class="phdr-meta">Version 2026.02<br>CONFIDENTIAL<br>Phase 1</div>
</div>
""", unsafe_allow_html=True)

    cfg = render_sidebar()
    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([11, 9], gap="large")

    # ═══════════════════════════════════════════
    # LEFT — Upload & Analysis
    # ═══════════════════════════════════════════
    with left:
        st.markdown('<div class="col-hdr">Upload &amp; Analyze</div>', unsafe_allow_html=True)

        uploaded = st.file_uploader(
            label="pdf_upload",
            type=["pdf"],
            label_visibility="collapsed",
            help="Upload Form 1040, 1120S, 1120, or 1065 as PDF",
        )

        if uploaded:
            st.success(
                f'✓ **{uploaded.name}** · {uploaded.size / 1024:.1f} KB — Ready to analyze'
            )
        else:
            st.markdown("""
<div class="upwell">
  <span class="upwell-icon">📄</span>
  <div class="upwell-title">Upload your tax return to begin</div>
  <div class="upwell-hint">
    Accepts Form 1040 · 1120S · 1120 · 1065 &nbsp;·&nbsp; PDF only<br>
    Your file is read locally — nothing is stored or shared
  </div>
</div>""", unsafe_allow_html=True)

        if not cfg["api_key"]:
            st.warning("⚠ Enter your OpenRouter API key in the sidebar to enable analysis.")

        st.markdown("<br>", unsafe_allow_html=True)

        analyze_btn = st.button(
            "⬡  Analyze My Return",
            type="primary",
            disabled=(not uploaded or not cfg["api_key"]),
        )

        # Run analysis
        if uploaded and cfg["api_key"] and analyze_btn:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(uploaded.read())
                tmp_path = tmp.name

            try:
                progress = st.progress(0, text="Reading your PDF…")
                raw = extract_pdf(tmp_path)
                progress.progress(30, text="PDF extracted…")

                if len(raw.strip()) < 80:
                    st.error("Could not read text from this PDF. It may be scanned. "
                             "Please try a text-based PDF.")
                    return

                progress.progress(60, text="Analyzing your return with Claude Opus 4.8 Fast…")
                ai_txt = run_analysis(raw, cfg["api_key"])

                progress.progress(90, text="Building your report…")
                time.sleep(0.2)
                progress.progress(100, text="Done.")
                progress.empty()

                st.session_state.ai_result = ai_txt
                st.session_state.report_done = True
                st.session_state.upload_name = uploaded.name

                st.success("✓ Analysis complete — your strategies are on the right →")
                render_report(ai_txt, fname=uploaded.name)

            except Exception as e:
                st.error(f"Something went wrong: {e}")
                with st.expander("Technical details"):
                    import traceback
                    st.code(traceback.format_exc())
            finally:
                Path(tmp_path).unlink(missing_ok=True)

        elif st.session_state.report_done:
            render_report(st.session_state.ai_result, fname=st.session_state.upload_name)

    # ═══════════════════════════════════════════
    # RIGHT — Preview & Information
    # ═══════════════════════════════════════════
    with right:
        st.markdown('<div class="col-hdr">What You\'ll Get</div>', unsafe_allow_html=True)
        
        if not st.session_state.report_done:
            render_welcome()
        else:
            st.markdown("### Your Assessment is Ready")
            st.markdown(
                "Review the full report on the left. Download the complete analysis as a text file."
            )


if __name__ == "__main__":
    main()
