"""
Dentists' Tax & Business Architecture System™
Streamlit Dashboard — Phase 1 Assessment Interface
=====================================================
Run:
    pip install streamlit plotly
    streamlit run app.py
"""

import os
import sys
import json
import time
import tempfile
from pathlib import Path

import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Dentists' Tax Architecture System™",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load .env ─────────────────────────────────────────────────────────────────
def load_dotenv(path=".env"):
    if Path(path).exists():
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_dotenv()

# ── Engine imports ────────────────────────────────────────────────────────────
try:
    from engine import (
        DentistTaxEngine, EngineConfig, TaxReturnJSON, FederalNumbers,
        StateNumbers, EntityRecord, DepreciationSummary, STRATEGY_LIBRARY,
        AssessmentReport,
    )
    ENGINE_AVAILABLE = True
except ImportError as e:
    ENGINE_AVAILABLE = False
    ENGINE_ERROR = str(e)

# ── Plotly ────────────────────────────────────────────────────────────────────
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# ══════════════════════════════════════════════════════════════════════════════
#  THEME & STYLES
# ══════════════════════════════════════════════════════════════════════════════

STYLES = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

  /* ── Root variables ── */
  :root {
    --navy:     #0A1628;
    --ink:      #111827;
    --gold:     #C9A84C;
    --gold-lt:  #E8C96A;
    --cream:    #F5F0E8;
    --slate:    #374151;
    --muted:    #6B7280;
    --success:  #10B981;
    --warn:     #F59E0B;
    --danger:   #EF4444;
    --severe:   #DC2626;
    --border:   #E5E0D5;
    --card-bg:  #FAFAF7;
  }

  /* ── Global ── */
  html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    color: var(--ink);
    background: var(--cream);
  }
  .stApp { background: var(--cream); }

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] {
    background: var(--navy) !important;
    border-right: 2px solid var(--gold);
  }
  section[data-testid="stSidebar"] * {
    color: #E5E7EB !important;
  }
  section[data-testid="stSidebar"] .stSelectbox label,
  section[data-testid="stSidebar"] .stTextInput label,
  section[data-testid="stSidebar"] .stNumberInput label,
  section[data-testid="stSidebar"] .stCheckbox label {
    color: #9CA3AF !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }
  section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
    color: var(--gold) !important;
    font-family: 'Playfair Display', serif !important;
  }
  section[data-testid="stSidebar"] input,
  section[data-testid="stSidebar"] select {
    background: rgba(255,255,255,0.05) !important;
    border-color: rgba(201,168,76,0.3) !important;
    color: #F3F4F6 !important;
  }
  section[data-testid="stSidebar"] .stButton button {
    background: var(--gold) !important;
    color: var(--navy) !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 3px !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    font-size: 0.8rem !important;
  }
  section[data-testid="stSidebar"] .stButton button:hover {
    background: var(--gold-lt) !important;
  }

  /* ── Headers ── */
  h1 { font-family: 'Playfair Display', serif !important; color: var(--navy) !important; }
  h2 { font-family: 'Playfair Display', serif !important; color: var(--navy) !important; font-size: 1.5rem !important; }
  h3 { font-family: 'IBM Plex Sans', sans-serif !important; color: var(--slate) !important; font-size: 1rem !important; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600 !important; }

  /* ── Metric cards ── */
  [data-testid="metric-container"] {
    background: white;
    border: 1px solid var(--border);
    border-left: 4px solid var(--gold);
    border-radius: 4px;
    padding: 1rem 1.25rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  }
  [data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted) !important;
    font-weight: 600;
  }
  [data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.6rem !important;
    color: var(--navy) !important;
    font-weight: 500 !important;
  }

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {
    background: white;
    border-bottom: 2px solid var(--border);
    gap: 0;
  }
  .stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    font-weight: 600 !important;
    color: var(--muted) !important;
    padding: 0.75rem 1.5rem !important;
    border-bottom: 2px solid transparent !important;
  }
  .stTabs [aria-selected="true"] {
    color: var(--navy) !important;
    border-bottom: 2px solid var(--gold) !important;
    background: transparent !important;
  }

  /* ── Cards ── */
  .arch-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  }
  .arch-card-gold {
    background: white;
    border: 1px solid var(--border);
    border-top: 4px solid var(--gold);
    border-radius: 4px;
    padding: 1.5rem;
    margin-bottom: 1rem;
  }
  .arch-card-danger {
    background: #FFF5F5;
    border: 1px solid #FECACA;
    border-left: 4px solid var(--danger);
    border-radius: 4px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
  }
  .arch-card-warn {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-left: 4px solid var(--warn);
    border-radius: 4px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
  }
  .arch-card-success {
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-left: 4px solid var(--success);
    border-radius: 4px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
  }

  /* ── Strategy row ── */
  .strategy-row {
    background: white;
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.6rem;
    display: flex;
    gap: 1rem;
    align-items: flex-start;
  }
  .strategy-rank {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    color: var(--gold);
    line-height: 1;
    min-width: 2rem;
    text-align: center;
  }
  .strategy-name {
    font-weight: 600;
    color: var(--navy);
    font-size: 0.95rem;
    margin-bottom: 0.2rem;
  }
  .strategy-irc {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: var(--muted);
    margin-bottom: 0.4rem;
  }
  .strategy-meta {
    font-size: 0.78rem;
    color: var(--slate);
  }
  .score-badge {
    background: var(--navy);
    color: var(--gold);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    font-weight: 500;
    padding: 0.2rem 0.6rem;
    border-radius: 3px;
    white-space: nowrap;
  }
  .savings-range {
    font-family: 'IBM Plex Mono', monospace;
    color: var(--success);
    font-size: 0.88rem;
    font-weight: 600;
  }
  .risk-critical { color: var(--severe); font-weight: 700; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; }
  .risk-high     { color: var(--warn);   font-weight: 700; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; }
  .risk-medium   { color: var(--muted);  font-weight: 700; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; }

  /* ── Bleed score gauge ── */
  .bleed-score-wrap {
    text-align: center;
    padding: 1rem 0;
  }
  .bleed-score-number {
    font-family: 'Playfair Display', serif;
    font-size: 4.5rem;
    line-height: 1;
    font-weight: 900;
  }
  .bleed-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-top: 0.3rem;
    font-weight: 700;
  }

  /* ── Memo block ── */
  .memo-block {
    background: #FAFAF7;
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 2rem;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.9rem;
    line-height: 1.7;
    color: var(--ink);
    white-space: pre-wrap;
  }
  .memo-stamp {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--muted);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.75rem;
    margin-bottom: 1.25rem;
  }

  /* ── Section divider ── */
  .section-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
  }

  /* ── Pill badges ── */
  .pill {
    display: inline-block;
    padding: 0.15rem 0.6rem;
    border-radius: 20px;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-right: 0.3rem;
  }
  .pill-gold   { background: #FEF3C7; color: #92400E; }
  .pill-blue   { background: #EFF6FF; color: #1E40AF; }
  .pill-green  { background: #F0FDF4; color: #166534; }
  .pill-red    { background: #FEF2F2; color: #991B1B; }
  .pill-gray   { background: #F3F4F6; color: #374151; }

  /* ── Header banner ── */
  .header-banner {
    background: var(--navy);
    color: white;
    padding: 1.75rem 2rem;
    margin: -1rem -1rem 2rem -1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 3px solid var(--gold);
  }
  .header-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.01em;
  }
  .header-sub {
    font-size: 0.72rem;
    color: var(--gold);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-top: 0.2rem;
  }
  .header-badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: rgba(255,255,255,0.45);
    text-align: right;
  }

  /* ── Upload zone ── */
  [data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important;
    border-radius: 4px !important;
    background: white !important;
  }

  /* ── Expander ── */
  .streamlit-expanderHeader {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--slate) !important;
    background: var(--card-bg) !important;
    border: 1px solid var(--border) !important;
  }

  /* ── Info / warning boxes ── */
  .stInfo, .stWarning, .stSuccess, .stError {
    border-radius: 4px !important;
    font-size: 0.85rem !important;
  }

  /* ── Scrollable strategy list ── */
  .strategy-list-scroll {
    max-height: 600px;
    overflow-y: auto;
    padding-right: 0.5rem;
  }

  /* ── Evidence tag ── */
  .evidence-tag {
    background: #EFF6FF;
    color: #1E40AF;
    font-size: 0.72rem;
    padding: 0.2rem 0.5rem;
    border-radius: 3px;
    margin: 0.15rem 0.15rem 0 0;
    display: inline-block;
  }
</style>
"""

st.markdown(STYLES, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def fmt_dollars(v: float) -> str:
    if abs(v) >= 1_000_000:
        return f"${v/1_000_000:.2f}M"
    if abs(v) >= 1_000:
        return f"${v:,.0f}"
    return f"${v:.0f}"

def fmt_range(lo: float, hi: float) -> str:
    return f"{fmt_dollars(lo)} – {fmt_dollars(hi)}"

def bleed_color(score: float) -> str:
    if score < 25:   return "#10B981"
    if score < 50:   return "#F59E0B"
    if score < 75:   return "#EF4444"
    return "#DC2626"

def complexity_label(v: int) -> str:
    if v <= 15:  return "Low"
    if v <= 30:  return "Medium"
    return "High"

def audit_label(v: int) -> str:
    if v <= 10:  return "Low"
    if v <= 20:  return "Medium"
    return "High"

def risk_tier(days: int, score: float) -> tuple[str, str]:
    """Return (tier_label, css_class) based on implementation speed & score."""
    if days <= 30 and score >= 75:   return ("CRITICAL", "risk-critical")
    if days <= 90 and score >= 60:   return ("HIGH",     "risk-high")
    return ("MEDIUM", "risk-medium")


# ══════════════════════════════════════════════════════════════════════════════
#  ENGINE INIT
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def get_engine(openrouter_key: str, groq_key: str, tavily_key: str,
               provider: str, model: str, live_research: bool) -> "DentistTaxEngine":
    cfg = EngineConfig(
        openrouter_api_key=openrouter_key,
        groq_api_key=groq_key,
        tavily_api_key=tavily_key,
        primary_provider=provider,
        openrouter_model=model,
        enable_live_research=live_research,
        max_strategies=12,
        min_materiality_score=50,
    )
    return DentistTaxEngine(cfg)


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR — Configuration
# ══════════════════════════════════════════════════════════════════════════════

def render_sidebar() -> dict:
    with st.sidebar:
        st.markdown("""
        <div style="padding: 1.25rem 0 1rem;">
          <div style="font-family:'Playfair Display',serif; font-size:1.35rem; color:#C9A84C; font-weight:700; line-height:1.2;">
            Dentists' Tax<br>Architecture™
          </div>
          <div style="font-size:0.65rem; text-transform:uppercase; letter-spacing:0.15em; color:#6B7280; margin-top:0.4rem;">
            Phase 1 · Return Analysis
          </div>
        </div>
        <hr style="border-color:rgba(201,168,76,0.2); margin-bottom:1.25rem;">
        """, unsafe_allow_html=True)

        st.markdown("### API Configuration")

        openrouter_key = st.text_input(
            "OpenRouter API Key",
            value=os.getenv("OPENROUTER_API_KEY", ""),
            type="password",
            placeholder="sk-or-...",
        )
        groq_key = st.text_input(
            "Groq API Key",
            value=os.getenv("GROQ_API_KEY", ""),
            type="password",
            placeholder="gsk_...",
        )
        tavily_key = st.text_input(
            "Tavily API Key",
            value=os.getenv("TAVILY_API_KEY", ""),
            type="password",
            placeholder="tvly-...",
        )

        st.markdown("---")
        st.markdown("### Engine Settings")

        provider = st.selectbox(
            "Primary LLM Provider",
            ["openrouter", "groq"],
            index=0,
        )
        model = st.text_input(
            "OpenRouter Model",
            value=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
        )
        live_research = st.checkbox(
            "Enable Live Tax Research (Tavily)",
            value=bool(tavily_key),
            disabled=not bool(tavily_key),
        )

        st.markdown("---")

        # Status indicators
        st.markdown("### API Status")
        def status_dot(active: bool, label: str):
            dot = "🟢" if active else "🔴"
            st.markdown(
                f"<div style='font-size:0.78rem; margin-bottom:0.3rem;'>{dot} {label}</div>",
                unsafe_allow_html=True
            )
        status_dot(bool(openrouter_key), "OpenRouter")
        status_dot(bool(groq_key), "Groq (fallback)")
        status_dot(bool(tavily_key) and live_research, "Tavily Research")

        st.markdown("---")
        st.markdown(
            "<div style='font-size:0.65rem; color:#4B5563; line-height:1.5;'>"
            "All analysis is for professional review only. Not legal or tax advice. "
            "Consult a licensed CPA before implementation."
            "</div>",
            unsafe_allow_html=True
        )

    return {
        "openrouter_key": openrouter_key,
        "groq_key": groq_key,
        "tavily_key": tavily_key,
        "provider": provider,
        "model": model,
        "live_research": live_research,
    }


# ══════════════════════════════════════════════════════════════════════════════
#  REPORT RENDERING
# ══════════════════════════════════════════════════════════════════════════════

def render_exposure_gauge(report: "AssessmentReport"):
    """Render the Tax Bleed Score as a Plotly gauge or fallback."""
    exp = report.exposure_score
    score = exp.raw_score
    color = bleed_color(score)

    if PLOTLY_AVAILABLE:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            number={"font": {"size": 52, "family": "Playfair Display", "color": color}, "suffix": ""},
            title={"text": f"<b>{exp.band_label}</b><br><span style='font-size:0.8em;color:#6B7280'>"
                           f"Tax Bleed Score</span>",
                   "font": {"size": 14, "family": "IBM Plex Sans"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#E5E0D5",
                         "nticks": 5},
                "bar": {"color": color, "thickness": 0.25},
                "bgcolor": "white",
                "borderwidth": 0,
                "steps": [
                    {"range": [0,  25],  "color": "#F0FDF4"},
                    {"range": [25, 50],  "color": "#FFFBEB"},
                    {"range": [50, 75],  "color": "#FEF2F2"},
                    {"range": [75, 100], "color": "#FFF1F2"},
                ],
                "threshold": {
                    "line": {"color": color, "width": 4},
                    "thickness": 0.75,
                    "value": score,
                },
            }
        ))
        fig.update_layout(
            height=240,
            margin=dict(t=40, b=20, l=20, r=20),
            paper_bgcolor="white",
            font={"family": "IBM Plex Sans"},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown(
            f'<div class="bleed-score-wrap">'
            f'<div class="bleed-score-number" style="color:{color};">{score:.0f}</div>'
            f'<div class="bleed-label" style="color:{color};">{exp.band_label}</div>'
            f'</div>',
            unsafe_allow_html=True
        )


def render_exposure_breakdown(report: "AssessmentReport"):
    exp = report.exposure_score
    if PLOTLY_AVAILABLE:
        categories = ["Liability Intensity", "Structural Inefficiency", "Opportunity Density"]
        values     = [exp.liability_intensity, exp.structural_inefficiency, exp.opportunity_density]
        colors     = [bleed_color(v) for v in values]

        fig = go.Figure()
        for cat, val, col in zip(categories, values, colors):
            fig.add_trace(go.Bar(
                x=[val], y=[cat], orientation="h",
                name=cat, marker_color=col,
                text=[f"{val:.0f}"], textposition="inside",
                insidetextfont={"color": "white", "size": 11, "family": "IBM Plex Mono"},
                showlegend=False,
                width=0.45,
            ))
        fig.add_shape(type="line", x0=50, x1=50, y0=-0.5, y1=2.5,
                      line=dict(color="#E5E0D5", width=1.5, dash="dot"))
        fig.update_layout(
            xaxis=dict(range=[0, 100], showgrid=False, zeroline=False,
                       tickfont=dict(size=10, family="IBM Plex Mono")),
            yaxis=dict(showgrid=False, tickfont=dict(size=11, family="IBM Plex Sans")),
            height=160,
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="white",
            plot_bgcolor="white",
            barmode="overlay",
        )
        st.plotly_chart(fig, use_container_width=True)


def render_savings_chart(report: "AssessmentReport"):
    if not PLOTLY_AVAILABLE or not report.top_strategies:
        return
    strats = report.top_strategies[:8]
    names  = [s.strategy_name[:32] + ("…" if len(s.strategy_name) > 32 else "")
              for s in strats]
    lows   = [s.federal_savings_low  for s in strats]
    highs  = [s.federal_savings_high for s in strats]
    mids   = [(l + h) / 2 for l, h in zip(lows, highs)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=names[::-1], x=mids[::-1],
        orientation="h",
        marker_color="#C9A84C",
        marker_line_width=0,
        name="Est. Federal Savings",
        text=[fmt_dollars(v) for v in mids[::-1]],
        textposition="outside",
        textfont=dict(size=10, family="IBM Plex Mono", color="#374151"),
        width=0.55,
    ))
    fig.add_trace(go.Bar(
        y=names[::-1], x=[h - l for l, h in zip(lows[::-1], highs[::-1])],
        base=lows[::-1],
        orientation="h",
        marker_color="rgba(201,168,76,0.2)",
        marker_line_width=0,
        name="Range",
        width=0.55,
        showlegend=False,
    ))
    fig.update_layout(
        xaxis=dict(
            tickformat="$,.0f",
            showgrid=True, gridcolor="#F3F4F6",
            zeroline=True, zerolinecolor="#E5E0D5",
            tickfont=dict(size=10, family="IBM Plex Mono"),
        ),
        yaxis=dict(tickfont=dict(size=10, family="IBM Plex Sans"), showgrid=False),
        height=max(280, len(strats) * 44),
        margin=dict(t=10, b=30, l=10, r=80),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=10)),
        barmode="overlay",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_summary_metrics(report: "AssessmentReport"):
    exp   = report.exposure_score
    color = bleed_color(exp.raw_score)
    combined_tax = (
        report.exposure_score.raw_score  # approximate via score
    )
    # Pull from report directly
    fed_low  = report.total_federal_savings_low
    fed_high = report.total_federal_savings_high
    st_low   = report.total_state_savings_low
    st_high  = report.total_state_savings_high

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Tax Bleed Score", f"{exp.raw_score:.0f} / 100",
                  delta=exp.band_label, delta_color="off")
    with c2:
        st.metric("Federal Savings Range", fmt_range(fed_low, fed_high))
    with c3:
        st.metric("State Savings Range", fmt_range(st_low, st_high))
    with c4:
        total_lo = fed_low  + st_low
        total_hi = fed_high + st_high
        st.metric("Total Opportunity", fmt_range(total_lo, total_hi))
    with c5:
        st.metric("Strategies Identified", str(len(report.top_strategies)))


def render_strategy_cards(report: "AssessmentReport"):
    strats = report.top_strategies
    if not strats:
        st.info("No strategies above threshold were identified for this return.")
        return

    for i, s in enumerate(strats, 1):
        tier, tier_cls = risk_tier(s.time_to_implement_days, s.total_score)
        complexity_lbl = complexity_label(s.complexity)
        audit_lbl      = audit_label(s.audit_friction)

        # Category pill color
        cat_lower = s.category.lower()
        if "retirement" in cat_lower:   pill_cls = "pill-gold"
        elif "real estate" in cat_lower or "depreciation" in cat_lower: pill_cls = "pill-blue"
        elif "entity" in cat_lower or "structuring" in cat_lower: pill_cls = "pill-red"
        else: pill_cls = "pill-green"

        with st.expander(
            f"#{i}  {s.strategy_name}  ·  {fmt_range(s.federal_savings_low, s.federal_savings_high)} federal",
            expanded=(i <= 3),
        ):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(
                    f'<span class="pill {pill_cls}">{s.category}</span>'
                    f'<span class="pill pill-gray">{s.irc_authority}</span>',
                    unsafe_allow_html=True
                )
                st.markdown(f"*{s.plain_english}*")

                if s.evidence_basis:
                    st.markdown("**Evidence from return:**")
                    ev_html = "".join(
                        f'<span class="evidence-tag">✓ {e}</span>'
                        for e in s.evidence_basis
                    )
                    st.markdown(ev_html, unsafe_allow_html=True)

            with col_b:
                st.markdown(
                    f'<div style="text-align:right;">'
                    f'<div class="score-badge">Score {s.total_score:.0f}</div><br>'
                    f'<div class="{tier_cls}" style="margin-top:0.5rem;">{tier}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    f'<div style="font-family:IBM Plex Mono,monospace; font-size:0.78rem; '
                    f'text-align:right; margin-top:0.5rem;">'
                    f'<span style="color:#10B981;">Fed: {fmt_range(s.federal_savings_low, s.federal_savings_high)}</span><br>'
                    f'<span style="color:#6B7280;">State: {fmt_range(s.state_savings_low, s.state_savings_high)}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**⏱ Timeline:** {s.time_to_implement_days} days")
                st.markdown(f"**⚙ Complexity:** {complexity_lbl}")
            with col2:
                st.markdown(f"**🔍 Audit Risk:** {audit_lbl}")
            with col3:
                pass

            if s.documentation_checklist:
                with st.container():
                    st.markdown("**📋 Documentation Required (IRC §6001):**")
                    for doc in s.documentation_checklist:
                        st.markdown(f"• {doc}")

            if s.cpa_handoff:
                with st.container():
                    st.markdown("**👤 CPA Handoff Actions:**")
                    for action in s.cpa_handoff:
                        st.markdown(f"→ {action}")

            if s.prerequisites:
                st.warning("**Prerequisites:** " + " · ".join(s.prerequisites))


def render_ai_memo(report: "AssessmentReport"):
    ai_text = report.ai_synthesis or ""
    if not ai_text or ai_text.startswith("[AI synthesis"):
        st.warning("AI synthesis unavailable — no API key configured or LLM call failed. "
                   "The deterministic analysis above is still complete.")
        return

    st.markdown(
        f'<div class="memo-block">'
        f'<div class="memo-stamp">CONFIDENTIAL · TAX ARCHITECTURE MEMORANDUM · '
        f'CLIENT {report.client_id} · {report.generated_at}</div>'
        f'{ai_text}'
        f'</div>',
        unsafe_allow_html=True
    )


def render_return_profile(report: "AssessmentReport"):
    """Render return metadata and profile flags."""
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Return Details**")
        st.markdown(f"- Client ID: `{report.client_id}`")
        st.markdown(f"- Tax Year: **{report.tax_year}**")
        st.markdown(f"- Return Types: `{', '.join(report.return_types)}`")
        st.markdown(f"- Primary State: `{report.primary_state or 'N/A'}`")
        st.markdown(f"- Dentist Profile: `{report.dentist_profile}`")
        st.markdown(f"- Confidence: `{report.dentist_confidence:.0%}`")
    with col2:
        st.markdown("**Exposure Drivers**")
        for d in report.exposure_score.top_drivers:
            st.markdown(f"⚠ {d}")

    if report.research_notes:
        st.markdown("**Live Research Context (Tavily)**")
        for note in report.research_notes:
            st.markdown(f"• {note}")


def render_full_report(report: "AssessmentReport"):
    """Master render function — assembles all sections into tabs."""

    render_summary_metrics(report)
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊  Exposure Analysis",
        "🏆  Strategy Ranking",
        "📈  Savings Chart",
        "📄  AI Memorandum",
        "🗂  Return Profile",
    ])

    with tab1:
        col_gauge, col_break = st.columns([1, 1])
        with col_gauge:
            st.markdown("#### Tax Bleed Score")
            render_exposure_gauge(report)
        with col_break:
            st.markdown("#### Score Breakdown")
            render_exposure_breakdown(report)

        st.markdown("#### Exposure Drivers")
        exp = report.exposure_score
        drivers = exp.top_drivers
        if drivers:
            for d in drivers:
                score_hint = exp.raw_score
                if score_hint >= 75:   card_cls = "arch-card-danger"
                elif score_hint >= 50: card_cls = "arch-card-warn"
                else:                  card_cls = "arch-card-success"
                st.markdown(f'<div class="{card_cls}">⚠ {d}</div>', unsafe_allow_html=True)
        else:
            st.success("No major structural inefficiencies detected.")

    with tab2:
        st.markdown("#### Ranked Tax Strategies")
        render_strategy_cards(report)

    with tab3:
        st.markdown("#### Federal Savings by Strategy (Estimated Annual)")
        render_savings_chart(report)

        st.markdown("---")
        # Summary table
        if report.top_strategies:
            import pandas as pd
            rows = []
            for s in report.top_strategies:
                rows.append({
                    "Strategy": s.strategy_name,
                    "IRC": s.irc_authority,
                    "Category": s.category,
                    "Score": f"{s.total_score:.0f}",
                    "Fed. Low": fmt_dollars(s.federal_savings_low),
                    "Fed. High": fmt_dollars(s.federal_savings_high),
                    "Days": s.time_to_implement_days,
                })
            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True,
            )

    with tab4:
        st.markdown("#### AI Architecture Memorandum")
        render_ai_memo(report)

    with tab5:
        st.markdown("#### Return Profile & Metadata")
        render_return_profile(report)

        st.markdown("---")
        with st.expander("📥 Download Full JSON Report"):
            st.download_button(
                label="Download report.json",
                data=report.to_json(indent=2),
                file_name=f"tax_report_{report.client_id}_{report.tax_year}.json",
                mime="application/json",
            )


# ══════════════════════════════════════════════════════════════════════════════
#  INPUT MODES
# ══════════════════════════════════════════════════════════════════════════════

def build_demo_return() -> "TaxReturnJSON":
    """High-income CA S-Corp dentist demo."""
    return TaxReturnJSON(
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
            self_employment_tax=0,
            niit=11_400,
            amt=0,
            qbi_deduction=0,
            itemized_deductions=42_000,
            standard_deduction_used=False,
            salt_deduction_claimed=10_000,
            charitable_contributions=8_000,
            w2_wages=160_000,
            marginal_rate_estimate=0.37,
        ),
        states={"CA": StateNumbers(
            state_taxable_income=620_000,
            state_total_tax=65_000,
            state_withholding=40_000,
            state_estimated_payments=20_000,
            effective_rate_estimate=0.105,
        )},
        entities=[EntityRecord(
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
            employee_count_estimated=8,
            health_insurance_expense=18_000,
            retirement_plan_expense=0,
            section_179=12_000,
            bonus_depreciation=0,
            depreciation_total=18_000,
            meals_entertainment=4_200,
            travel=8_500,
            auto_truck=9_800,
            professional_fees=22_000,
            tax_planning_fees_detected=False,
            state_tax_expense=800,
        )],
        depreciation=DepreciationSummary(
            has_depreciation=True,
            section_179_claimed=12_000,
            bonus_depreciation_claimed=0,
            total_depreciation=18_000,
            cost_segregation_detected=False,
            assets_detected={"equipment": True, "vehicles": True, "real_estate": False},
        ),
        retirement_contributions=0,
        confidence=0.95,
    )


def build_demo_associate() -> "TaxReturnJSON":
    """NY associate dentist (W-2) demo."""
    return TaxReturnJSON(
        client_id="DR_JONES_2024",
        tax_year=2024,
        return_types=["1040"],
        state_returns_present=["NY"],
        primary_state="NY",
        dentist_indicator="CONFIRMED",
        high_income=True,
        meaningful_tax_liability=True,
        w2_present=True,
        k1_present=False,
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
        states={"NY": StateNumbers(
            state_taxable_income=310_000,
            state_total_tax=28_000,
            state_withholding=28_000,
            effective_rate_estimate=0.09,
        )},
        entities=[],
        confidence=0.90,
    )


def render_manual_input_form() -> "TaxReturnJSON | None":
    """Render a manual data entry form and return TaxReturnJSON on submit."""
    st.markdown("### Manual Return Entry")
    st.caption("Enter key figures from the tax return. All fields are optional — leave at 0 if not present.")

    with st.form("manual_entry"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Client Info**")
            client_id  = st.text_input("Client ID", value="CLIENT_001")
            tax_year   = st.number_input("Tax Year", value=2024, min_value=2018, max_value=2025, step=1)
            filing_status = st.selectbox("Filing Status", ["MFJ", "S", "MFS", "HH"])
            dentist    = st.selectbox("Dentist Indicator", ["UNKNOWN", "LIKELY", "CONFIRMED"])
            primary_state = st.text_input("Primary State (2-letter)", value="CA", max_chars=2).upper()

        with col2:
            st.markdown("**Federal Numbers**")
            agi          = st.number_input("AGI ($)", value=0, step=1000, format="%d")
            taxable_inc  = st.number_input("Taxable Income ($)", value=0, step=1000, format="%d")
            total_tax    = st.number_input("Total Federal Tax ($)", value=0, step=1000, format="%d")
            w2_wages     = st.number_input("W-2 Wages ($)", value=0, step=1000, format="%d")
            se_tax       = st.number_input("Self-Employment Tax ($)", value=0, step=100, format="%d")
            niit         = st.number_input("NIIT ($)", value=0, step=100, format="%d")
            qbi          = st.number_input("QBI Deduction ($)", value=0, step=1000, format="%d")
            salt         = st.number_input("SALT Deduction ($)", value=0, step=500, format="%d")

        with col3:
            st.markdown("**Entity / Practice**")
            entity_type  = st.selectbox("Entity Type", ["None", "1120S", "1120", "1065"])
            gross_rec    = st.number_input("Gross Receipts ($)", value=0, step=10000, format="%d")
            obi          = st.number_input("Ordinary Business Income ($)", value=0, step=1000, format="%d")
            owner_wages  = st.number_input("Owner/Officer Wages ($)", value=0, step=1000, format="%d")
            distributions= st.number_input("Distributions ($)", value=0, step=1000, format="%d")
            retirement   = st.number_input("Retirement Plan Expense ($)", value=0, step=1000, format="%d")
            depreciation = st.number_input("Total Depreciation ($)", value=0, step=1000, format="%d")

        st.markdown("---")
        col_a, col_b = st.columns(2)
        with col_a:
            state_tax_total = st.number_input("State Total Tax ($)", value=0, step=500, format="%d")
            ptet = st.checkbox("PTET Election Detected")
            dependents = st.checkbox("Dependents Present")
            real_estate = st.checkbox("Real Estate / Schedule E Activity")
            schedule_c = st.checkbox("Schedule C Present")
        with col_b:
            no_planning_fees = st.checkbox("No Tax Planning Fees Detected", value=True)

        submitted = st.form_submit_button("▶  Run Analysis", use_container_width=True)

    if not submitted:
        return None

    # Build TaxReturnJSON from form inputs
    return_types = ["1040"]
    entities = []
    if entity_type != "None":
        return_types.append(entity_type)
        entities.append(EntityRecord(
            entity_id="E1",
            entity_name="Practice Entity",
            entity_type=entity_type,
            gross_receipts=float(gross_rec),
            ordinary_business_income=float(obi),
            owner_wages=float(owner_wages),
            distributions=float(distributions),
            officer_compensation=float(owner_wages),
            retirement_plan_expense=float(retirement),
            depreciation_total=float(depreciation),
            tax_planning_fees_detected=not no_planning_fees,
        ))

    states = {}
    if primary_state and state_tax_total > 0:
        states[primary_state] = StateNumbers(
            state_taxable_income=float(taxable_inc),
            state_total_tax=float(state_tax_total),
        )

    ti = float(taxable_inc)
    if ti > 731200:       marginal = 0.37
    elif ti > 487450:     marginal = 0.35
    elif ti > 231250:     marginal = 0.32
    elif ti > 100525:     marginal = 0.24
    elif ti > 47150:      marginal = 0.22
    else:                  marginal = 0.12

    return TaxReturnJSON(
        client_id=client_id,
        tax_year=int(tax_year),
        return_types=return_types,
        state_returns_present=list(states.keys()),
        primary_state=primary_state,
        ptet_election_detected=ptet,
        dentist_indicator=dentist,
        high_income=float(agi) > 300_000,
        meaningful_tax_liability=float(total_tax) > 70_000,
        w2_present=float(w2_wages) > 0,
        k1_present=len(entities) > 0,
        schedule_c_present=schedule_c,
        real_estate_activity_present=real_estate,
        dependents_present=dependents,
        federal=FederalNumbers(
            filing_status=filing_status,
            agi=float(agi),
            taxable_income=float(taxable_inc),
            total_tax=float(total_tax),
            w2_wages=float(w2_wages),
            self_employment_tax=float(se_tax),
            niit=float(niit),
            qbi_deduction=float(qbi),
            salt_deduction_claimed=float(salt),
            marginal_rate_estimate=marginal,
        ),
        states=states,
        entities=entities,
        depreciation=DepreciationSummary(
            has_depreciation=float(depreciation) > 0,
            total_depreciation=float(depreciation),
        ),
        confidence=0.80,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # Header
    st.markdown(
        '<div class="header-banner">'
        '<div>'
        '<div class="header-title">Dentists\' Tax & Business Architecture System™</div>'
        '<div class="header-sub">Phase 1 · Tax Risk Assessment Engine · Return-Only Analysis</div>'
        '</div>'
        '<div class="header-badge">Version 2026.02<br>CONFIDENTIAL</div>'
        '</div>',
        unsafe_allow_html=True
    )

    if not ENGINE_AVAILABLE:
        st.error(
            f"❌ Engine not available: `{ENGINE_ERROR}`\n\n"
            "Make sure `engine.py` is in the same directory and dependencies are installed:\n"
            "```bash\npip install -r requirements.txt\n```"
        )
        st.stop()

    # Sidebar config
    cfg = render_sidebar()

    # ── Input mode selection ───────────────────────────────────────────────
    st.markdown("### Select Input Mode")
    input_mode = st.radio(
        "How would you like to provide the tax return?",
        ["🎯  Run Demo (CA Practice Owner)", "👤  Run Demo (NY Associate)", "📄  Upload PDF", "✏️  Manual Entry"],
        horizontal=True,
        label_visibility="collapsed",
    )
    st.markdown("---")

    ret = None
    run_analysis = False

    if input_mode == "🎯  Run Demo (CA Practice Owner)":
        st.markdown(
            '<div class="arch-card-gold">'
            '<strong>Demo Scenario:</strong> Dr. Smith — California dental practice owner (S-Corp, 1120S). '
            'AGI $680K · Federal tax $192K · CA tax $65K · No retirement plan · '
            'S-Corp distributions 1.9× wages · No PTET election.'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("▶  Run Demo Analysis", type="primary", use_container_width=False):
            ret = build_demo_return()
            run_analysis = True

    elif input_mode == "👤  Run Demo (NY Associate)":
        st.markdown(
            '<div class="arch-card-gold">'
            '<strong>Demo Scenario:</strong> Dr. Jones — New York associate dentist (W-2). '
            'AGI $340K · Federal tax $84K · NY tax $28K · Single filer · Dependents present.'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("▶  Run Associate Demo", type="primary", use_container_width=False):
            ret = build_demo_associate()
            run_analysis = True

    elif input_mode == "📄  Upload PDF":
        st.markdown(
            '<div class="arch-card">'
            'Upload a PDF tax return (1040, 1120S, 1120, or 1065). '
            'Text will be extracted via pdfplumber, then sent to OpenRouter (Gemini 2.0) for structured AI parsing.'
            '</div>',
            unsafe_allow_html=True
        )
        if not cfg["openrouter_key"]:
            st.warning("⚠ OpenRouter API key required for PDF extraction. Configure it in the sidebar.")
        uploaded = st.file_uploader("Upload PDF Tax Return", type=["pdf"])
        client_id_pdf = st.text_input("Client ID", value="CLIENT_001", key="pdf_client")
        tax_year_pdf  = st.number_input("Tax Year", value=2024, min_value=2018, max_value=2025, step=1, key="pdf_year")

        if uploaded and st.button("▶  Analyze PDF", type="primary"):
            with st.spinner("Extracting text from PDF…"):
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    tmp.write(uploaded.read())
                    tmp_path = tmp.name
            try:
                engine = get_engine(**cfg)
                with st.spinner("Running AI structured extraction and analysis…"):
                    t0 = time.time()
                    report = engine.analyze_pdf(tmp_path, client_id_pdf, int(tax_year_pdf))
                    elapsed = round((time.time() - t0) * 1000)
                Path(tmp_path).unlink(missing_ok=True)
                st.success(f"✅ Analysis complete in {elapsed}ms")
                render_full_report(report)
            except Exception as e:
                Path(tmp_path).unlink(missing_ok=True)
                st.error(f"❌ Analysis failed: {e}")
            return

    elif input_mode == "✏️  Manual Entry":
        manual_ret = render_manual_input_form()
        if manual_ret is not None:
            ret = manual_ret
            run_analysis = True

    # ── Execute analysis ───────────────────────────────────────────────────
    if run_analysis and ret is not None:
        try:
            engine = get_engine(**cfg)
            progress = st.progress(0, text="Initialising engine…")
            time.sleep(0.1)
            progress.progress(15, text="Deriving signals…")

            t0 = time.time()
            with st.spinner("Running full tax architecture analysis…"):
                # Run in steps so progress bar feels real
                sigs   = engine.signals.derive(ret)
                progress.progress(35, text="Scoring strategies…")
                strats = engine.scorer.score_all(sigs, engine.config)
                progress.progress(55, text="Calculating exposure score…")
                exp    = engine.exposure.calculate(ret, sigs)
                progress.progress(70, text="Classifying practice profile…")
                profile, confidence = engine.classifier.classify(ret)
                progress.progress(80, text="Running AI synthesis…")
                report = engine._run_analysis(ret)
                progress.progress(100, text="Complete.")
            elapsed = round((time.time() - t0) * 1000)
            progress.empty()

            st.success(f"✅ Analysis complete in {elapsed}ms — {len(report.top_strategies)} strategies identified.")
            render_full_report(report)

        except Exception as e:
            st.error(f"❌ Analysis error: {e}")
            if st.checkbox("Show traceback"):
                import traceback
                st.code(traceback.format_exc())

    elif not run_analysis:
        # Placeholder / welcome state
        st.markdown(
            '<div class="arch-card" style="text-align:center; padding: 3rem 2rem;">'
            '<div style="font-family:Playfair Display,serif; font-size:1.3rem; color:#0A1628; margin-bottom:0.75rem;">'
            'Select an input mode above to begin analysis.'
            '</div>'
            '<div style="color:#6B7280; font-size:0.9rem; max-width:520px; margin:0 auto;">'
            'Upload a PDF return, enter data manually, or run one of the built-in demos to '
            'generate a full Tax Architecture Risk Memorandum with ranked strategies and savings estimates.'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

        # Strategy library preview
        st.markdown("---")
        st.markdown("### Strategy Library — Phase 1 Eligible")
        cols = st.columns(3)
        phase1 = [s for s in STRATEGY_LIBRARY if s.get("phase_1_eligible", True)]
        for i, s in enumerate(phase1):
            with cols[i % 3]:
                cat_lower = s["category"].lower()
                if "retirement" in cat_lower:        dot = "🟡"
                elif "real estate" in cat_lower:     dot = "🔵"
                elif "entity" in cat_lower:          dot = "🔴"
                else:                                dot = "🟢"
                st.markdown(
                    f'<div class="arch-card" style="padding:0.9rem 1rem; margin-bottom:0.5rem;">'
                    f'<div style="font-weight:600; font-size:0.82rem; color:#111827;">{dot} {s["name"]}</div>'
                    f'<div style="font-family:IBM Plex Mono,monospace; font-size:0.68rem; color:#6B7280; margin-top:0.2rem;">'
                    f'{s["irc"]} · {s.get("speed_days", "?")}d</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )


if __name__ == "__main__":
    main()
