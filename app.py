"""
Dentists' Tax & Business Architecture System™
Run:  pip install streamlit pdfplumber requests
      streamlit run app.py
"""

import os, re, time, tempfile
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import streamlit as st

st.set_page_config(
    page_title="Dentists' Tax Architecture System™",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── .env loader ───────────────────────────────────────────────────────────────
def _env(p=".env"):
    if Path(p).exists():
        for ln in Path(p).read_text().splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
_env()

# ── optional deps ─────────────────────────────────────────────────────────────
try:    import pdfplumber;                   PDF_OK = True
except: PDF_OK = False
try:    from new_strategies import STRATEGY_LIBRARY; STRAT_OK = True
except: STRATEGY_LIBRARY = [];               STRAT_OK = False

# ── session defaults ──────────────────────────────────────────────────────────
for k, v in [("report_done", False), ("ai_result", ""), ("upload_name", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
#  DESIGN TOKENS & STYLES
# ══════════════════════════════════════════════════════════════════════════════
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

/* ── globals ── */
html, body, [class*="css"] {
  font-family: 'Inter', sans-serif;
  background: var(--cream);
  color: var(--ink);
}
.stApp { background: var(--cream); }
.block-container { padding-top: 0 !important; max-width: 100% !important; }

/* ── sidebar ── */
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

/* ── page header ── */
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

/* ── col header ── */
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

/* ── upload ── */
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
[data-testid="stFileUploader"] section {
  border: 1.5px dashed var(--border) !important;
  background: var(--white) !important;
  border-radius: 12px !important;
}
.file-ok {
  background: var(--ok-lt);
  border: 1px solid var(--ok-bdr);
  border-radius: 8px;
  padding: .6rem 1rem;
  font-size: .78rem;
  color: var(--ok);
  margin-bottom: .65rem;
  display: flex;
  align-items: center;
  gap: .5rem;
  font-weight: 500;
}

/* ── buttons ── */
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
  transition: all .15s !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--gold) !important;
  color: var(--navy) !important;
}
.stButton > button[kind="primary"]:disabled { opacity: .38 !important; }
.stButton > button[kind="secondary"] {
  background: var(--white) !important;
  color: var(--navy) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: 6px !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  font-size: .75rem !important;
  letter-spacing: .04em;
  padding: .65rem 1.5rem !important;
  width: 100% !important;
  transition: all .15s !important;
}
.stButton > button[kind="secondary"]:hover {
  border-color: var(--gold) !important;
  color: var(--gold) !important;
  background: rgba(191,160,90,.04) !important;
}

/* ── progress ── */
.stProgress > div > div { background: var(--gold) !important; }
.stAlert { border-radius: 8px !important; font-size: .8rem !important; }

/* ══════════════════════
   REPORT (left)
══════════════════════ */
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
.rpt-head-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: .8rem;
}
.rpt-badge {
  font-family: 'IBM Plex Mono', monospace;
  font-size: .5rem;
  letter-spacing: .28em;
  text-transform: uppercase;
  color: var(--gold);
  border: 1px solid rgba(191,160,90,.35);
  padding: .15rem .5rem;
  border-radius: 2px;
}
.rpt-meta {
  font-family: 'IBM Plex Mono', monospace;
  font-size: .5rem;
  color: rgba(255,255,255,.2);
  text-align: right;
  line-height: 1.9;
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
.sec-hdr:first-child { margin-top: 0; }
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
.sec-sub {
  font-size: .64rem;
  color: var(--muted);
  margin-left: auto;
  font-style: italic;
}

/* report section cards */
.card-exp {
  background: var(--bad-lt);
  border: 1px solid var(--bad-bdr);
  border-left: 3px solid var(--bad);
  border-radius: 6px;
  padding: .85rem 1.05rem;
  margin-bottom: .45rem;
  font-size: .82rem; color: var(--slate); line-height: 1.72;
}
.card-str {
  background: var(--warn-lt);
  border: 1px solid var(--warn-bdr);
  border-left: 3px solid var(--warn);
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
.card-sav {
  background: var(--ok-lt);
  border: 1px solid var(--ok-bdr);
  border-left: 3px solid var(--ok);
  border-radius: 6px;
  padding: .85rem 1.05rem;
  margin-bottom: .45rem;
  font-size: .82rem; color: var(--slate); line-height: 1.72;
}
.card-total {
  background: var(--navy);
  border-radius: 8px;
  padding: 1.2rem 1.6rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
  margin: .75rem 0;
}
.total-lbl {
  font-size: .56rem;
  text-transform: uppercase;
  letter-spacing: .18em;
  color: rgba(255,255,255,.38);
  margin-bottom: .22rem;
}
.total-amt {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.7rem;
  font-weight: 700;
  color: var(--gold);
}
.total-txt {
  font-size: .78rem;
  color: rgba(255,255,255,.5);
  line-height: 1.6;
  max-width: 55%;
}
.verdict-full    { background:#E8F7F2; border:1px solid #5DC5A0; border-left:4px solid var(--ok);   border-radius:6px; padding:1rem 1.2rem; margin-bottom:.45rem; }
.verdict-partial { background:var(--warn-lt); border:1px solid var(--warn-bdr); border-left:4px solid var(--warn); border-radius:6px; padding:1rem 1.2rem; margin-bottom:.45rem; }
.verdict-limited { background:var(--bad-lt); border:1px solid var(--bad-bdr); border-left:4px solid var(--bad);  border-radius:6px; padding:1rem 1.2rem; margin-bottom:.45rem; }
.verdict-tag     { font-family:'Cormorant Garamond',serif; font-size:.97rem; font-weight:700; margin-bottom:.38rem; }
.verdict-body    { font-size:.82rem; color:var(--slate); line-height:1.72; }
.disclaimer {
  background: #F2EFE8;
  border: 1px solid var(--b2);
  border-radius: 6px;
  padding: .95rem 1.15rem;
  margin-top: 1.6rem;
  display: flex;
  gap: .6rem;
  align-items: flex-start;
}
.disclaimer-txt { font-size: .73rem; color: var(--muted); line-height: 1.7; }
.disclaimer-txt strong { color: var(--slate); }

/* ══════════════════════════════════════════════════════════════════
   RIGHT PANEL — PRE-ANALYSIS WELCOME
══════════════════════════════════════════════════════════════════ */
.welcome-card {
  background: var(--white);
  border: 1px solid var(--b2);
  border-radius: 12px;
  padding: 1.6rem 1.75rem 1.5rem;
  margin-bottom: 1rem;
}
.welcome-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: .65rem;
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
.stat-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: .65rem;
  margin: 1.1rem 0 0;
}
.stat-box {
  background: var(--cream);
  border: 1px solid var(--b2);
  border-radius: 8px;
  padding: .8rem 1rem;
  text-align: center;
}
.stat-val {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--navy);
  line-height: 1;
  margin-bottom: .2rem;
}
.stat-lbl {
  font-size: .66rem;
  color: var(--muted);
  line-height: 1.4;
}

/* how-it-works */
.how-row {
  display: flex;
  gap: .75rem;
  margin: 1rem 0;
}
.how-step {
  flex: 1;
  background: var(--white);
  border: 1px solid var(--b2);
  border-radius: 10px;
  padding: .9rem .75rem;
  text-align: center;
}
.how-circle {
  width: 1.8rem; height: 1.8rem;
  background: var(--navy);
  color: var(--gold);
  border-radius: 50%;
  font-size: .68rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto .5rem;
  font-family: 'IBM Plex Mono', monospace;
}
.how-title { font-size: .75rem; font-weight: 700; color: var(--navy); margin-bottom: .18rem; }
.how-desc  { font-size: .67rem; color: var(--muted); line-height: 1.45; }

/* category mini-tags */
.cat-tag-row { display: flex; flex-wrap: wrap; gap: .35rem; margin-top: .8rem; }
.cat-tag {
  font-size: .62rem;
  font-weight: 500;
  padding: .2rem .55rem;
  border-radius: 20px;
  border: 1px solid var(--b2);
  background: var(--cream);
  color: var(--slate);
  display: flex;
  align-items: center;
  gap: .25rem;
  white-space: nowrap;
}

/* ══════════════════════════════════════════════════════════════════
   RIGHT PANEL — RECOMMENDED STRATEGIES (post-analysis)
══════════════════════════════════════════════════════════════════ */

/* summary bar across top of right panel */
.rec-summary {
  background: var(--navy);
  border-radius: 10px;
  padding: 1.1rem 1.4rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.1rem;
}
.rec-summary-left {
  flex: 1;
}
.rec-summary-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1rem;
  font-weight: 700;
  color: #FFF;
  margin-bottom: .15rem;
}
.rec-summary-sub {
  font-size: .65rem;
  color: rgba(255,255,255,.45);
  letter-spacing: .03em;
}
.rec-summary-count {
  background: rgba(191,160,90,.15);
  border: 1px solid rgba(191,160,90,.35);
  border-radius: 8px;
  padding: .55rem .85rem;
  text-align: center;
}
.rec-count-num {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--gold);
  line-height: 1;
}
.rec-count-lbl {
  font-size: .58rem;
  color: rgba(255,255,255,.4);
  text-transform: uppercase;
  letter-spacing: .1em;
  margin-top: .15rem;
}

/* individual recommended strategy card */
.strat-card {
  background: var(--white);
  border: 1px solid var(--b2);
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: .85rem;
  box-shadow: 0 2px 10px rgba(9,25,47,.05);
  transition: box-shadow .18s, transform .18s;
}
.strat-card:hover {
  box-shadow: 0 5px 20px rgba(9,25,47,.1);
  transform: translateY(-1px);
}
.strat-card-body { padding: 1rem 1.1rem .85rem; }
.strat-icon-row {
  display: flex;
  align-items: flex-start;
  gap: .7rem;
  margin-bottom: .5rem;
}
.strat-icon-bubble {
  width: 2.4rem; height: 2.4rem;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}
.strat-name {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.02rem;
  font-weight: 700;
  color: var(--navy);
  line-height: 1.2;
  margin-bottom: .12rem;
}
.strat-irc {
  font-family: 'IBM Plex Mono', monospace;
  font-size: .6rem;
  color: var(--muted);
}
.strat-savings-badge {
  margin-left: auto;
  background: var(--ok-lt);
  border: 1px solid var(--ok-bdr);
  border-radius: 6px;
  padding: .28rem .65rem;
  font-family: 'IBM Plex Mono', monospace;
  font-size: .68rem;
  font-weight: 600;
  color: var(--ok);
  white-space: nowrap;
  flex-shrink: 0;
}
.strat-desc {
  font-size: .8rem;
  color: var(--slate);
  line-height: 1.68;
  margin-bottom: .6rem;
}
.strat-footer {
  background: var(--cream);
  border-top: 1px solid var(--b2);
  padding: .55rem 1.1rem;
  display: flex;
  align-items: center;
  gap: .4rem;
  flex-wrap: wrap;
}
.tag {
  font-size: .6rem;
  font-weight: 600;
  padding: .15rem .5rem;
  border-radius: 20px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: .22rem;
}
.tag-cat  { background: #EEF1F8; color: #1A3A6B; }
.tag-time { background: var(--ok-lt); color: #0A5C44; }
.tag-ph   { background: var(--warn-lt); color: #7A5010; }

/* generic prose card for unmatched paragraphs */
.strat-card-plain {
  background: var(--white);
  border: 1px solid var(--b2);
  border-left: 3px solid var(--gold);
  border-radius: 10px;
  padding: 1rem 1.1rem;
  margin-bottom: .7rem;
  font-size: .82rem;
  color: var(--slate);
  line-height: 1.7;
}

/* ══════════════════════════════════════════════════════════════════
   LIBRARY DIALOG
══════════════════════════════════════════════════════════════════ */
.lib-intro {
  font-size: .78rem;
  color: var(--muted);
  line-height: 1.6;
  padding: .75rem 0 .25rem;
}
.lib-cat-title {
  display: flex;
  align-items: center;
  gap: .45rem;
  font-family: 'Cormorant Garamond', serif;
  font-size: .95rem;
  font-weight: 700;
  color: var(--navy);
  padding: .4rem 0 .3rem;
  border-bottom: 1px solid var(--b2);
  margin: 1rem 0 .5rem;
}
.lib-cat-title:first-of-type { margin-top: 0; }
.lib-cat-count { font-family: 'IBM Plex Mono', monospace; font-size: .6rem; color: var(--muted); font-weight: 400; }
.lib-item {
  display: flex;
  align-items: flex-start;
  gap: .55rem;
  background: var(--cream);
  border: 1px solid var(--b2);
  border-radius: 7px;
  padding: .6rem .8rem;
  margin-bottom: .32rem;
}
.lib-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; margin-top: .28rem; }
.lib-item-main { flex: 1; min-width: 0; }
.lib-item-name { font-size: .78rem; font-weight: 600; color: var(--navy); line-height: 1.3; margin-bottom: .18rem; }
.lib-item-desc { font-size: .7rem; color: var(--muted); line-height: 1.4; }
.lib-item-right { flex-shrink: 0; text-align: right; }
.lib-item-irc { font-family: 'IBM Plex Mono', monospace; font-size: .58rem; color: var(--muted); margin-bottom: .18rem; }
.lib-badge {
  font-size: .57rem;
  font-weight: 700;
  padding: .1rem .38rem;
  border-radius: 3px;
  text-transform: uppercase;
  letter-spacing: .05em;
  display: inline-block;
}
.lib-ph1 { background: #E4EEF8; color: #163870; }
.lib-ph2 { background: #F0EDE4; color: #6B5920; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  CATEGORY PALETTE
# ══════════════════════════════════════════════════════════════════════════════
_CAT = {
    "Entity & Income Structuring":  ("#B83020", "🏢", "#FDEEED"),
    "Retirement & Benefits":        ("#A07830", "🏦", "#FBF5E6"),
    "Deduction & Reimbursement":    ("#0E7A62", "📋", "#E6F5F0"),
    "Real Estate & Depreciation":   ("#1E50C0", "🏠", "#EBF0FB"),
    "Credits & Special Incentives": ("#6030B8", "⭐", "#F0E8FC"),
    "Alternative Investments":      ("#B86010", "📈", "#FDF3E5"),
    "Charitable & Community":       ("#B02070", "🤝", "#FCEAF4"),
    "SALT & State Planning":        ("#0878A0", "🗺️", "#E6F3F8"),
}
def _cc(c):  return _CAT.get(c, ("#6B7280", "•",  "#F3F4F6"))[0]
def _ci(c):  return _CAT.get(c, ("#6B7280", "•",  "#F3F4F6"))[1]
def _cbg(c): return _CAT.get(c, ("#6B7280", "•",  "#F3F4F6"))[2]


# ══════════════════════════════════════════════════════════════════════════════
#  STRATEGY LOOKUP
# ══════════════════════════════════════════════════════════════════════════════
_BY_NAME = {s["name"].lower(): s for s in STRATEGY_LIBRARY}

def _match_strategy(para: str):
    """Match a paragraph to a strategy by name or IRC citation."""
    tl = para.lower()
    for name, s in _BY_NAME.items():
        # Match on first 4 meaningful words
        words = [w for w in name.split() if len(w) > 2][:4]
        if len(words) >= 2 and all(w in tl for w in words):
            return s
    # Fall back to IRC
    for s in STRATEGY_LIBRARY:
        for part in re.split(r"[,;]", s["irc"]):
            part = part.strip()
            if len(part) > 5 and part.lower() in tl:
                return s
    return None


# ══════════════════════════════════════════════════════════════════════════════
#  PDF EXTRACTION
# ══════════════════════════════════════════════════════════════════════════════
def _extract(path: str) -> str:
    if not PDF_OK:
        raise ImportError("Run: pip install pdfplumber")
    pages = []
    with pdfplumber.open(path) as f:
        for pg in f.pages:
            t = pg.extract_text()
            if t: pages.append(t)
    return "\n\n".join(pages)


# ══════════════════════════════════════════════════════════════════════════════
#  PROMPTS
# ══════════════════════════════════════════════════════════════════════════════
_SYS = """You are a senior tax architect with two decades of practice advising high-income dental practice owners across the United States. You have personally reviewed thousands of returns. You know the patterns — what dental practice owners miss year after year, what general-practice CPAs overlook, and where the real money sits unclaimed.

You do not produce checklists. You read the specific return in front of you and write a private client memorandum that reflects exactly those numbers, those forms, that state, that entity structure.

Your voice is that of a trusted senior advisor: direct, precise, and occasionally blunt. You never use filler phrases like "it is important to note," "it is worth mentioning," or "you may wish to consider." You state findings as facts. You quantify everything that can be quantified. When something is wrong, you name it plainly and say what it costs. When an opportunity exists, you say how much it is worth.

Every dollar figure comes from the return or from a calculation you can defend. Every strategy you recommend has direct evidentiary support in the data. You never recommend what you cannot justify.

When strategies carry state-level nuance, you name the state and the specific issue. IRC citations are woven naturally into sentences rather than appended as tags.

OUTPUT FORMAT — STRICT:
Produce exactly five sections using the exact headers listed below. Inside each section write only in flowing prose paragraphs. Each finding or strategy is its own paragraph, separated by a blank line. No bullet points. No numbered lists. No tables. No sub-headers within sections. No markdown. Nothing before Section I. Nothing after the disclaimer in Section V."""


def _build_prompt(raw: str) -> str:
    strats = "\n".join(f"  • {s['name']}  ({s['irc']})" for s in STRATEGY_LIBRARY)
    return f"""Analyze the tax return data and produce a five-section Tax Architecture Assessment.
Only recommend strategies from the approved list where the return contains direct supporting evidence.

APPROVED STRATEGY UNIVERSE:
{strats}

────────────────────────────────────────────────
TAX RETURN DATA:
────────────────────────────────────────────────
{raw[:34000]}
────────────────────────────────────────────────

Use these exact headers. Prose paragraphs only — never lists, tables, or sub-headers.

SECTION I — TAX EXPOSURE ANALYSIS
Every active tax exposure: unshielded income flows, missing forms, excess SE tax, audit-risk patterns, state compliance gaps. Reference actual line items and dollar figures. Each problem is its own paragraph.

SECTION II — STRUCTURAL INEFFICIENCIES
Business architecture: entity type, W-2 salary calibration, retirement funding, expense categorization, missing management company or real estate separation. Each gap is its own paragraph with dollar context.

SECTION III — RECOMMENDED STRATEGIES
Only strategies from the list above with direct evidentiary support. For each: weave the IRC citation naturally into the opening sentence, explain plainly, cite the specific return data, and note state non-conformity by name. Each strategy is its own paragraph.

SECTION IV — DOLLAR IMPACT ESTIMATES
For each strategy in Section III: a specific conservative-to-optimistic federal savings range in prose. End with a summary paragraph stating the combined total as a dollar range and as a percentage of current federal liability.

SECTION V — TAX PROTECTION VERDICT
Clear verdict. Federal reduction potential, state conformity by strategy, classification — exactly one of: Full Protection Achievable, Partial Protection Achievable, or Protection Limited. State classification in one clear sentence. Then implementation steps. Close with this disclaimer word for word as its own paragraph:

"All findings in this assessment are prepared for review by a licensed tax architect and do not constitute finalized tax advice. Implementation of any strategy described here should be undertaken only with the guidance of a qualified tax professional who has reviewed the complete facts and circumstances of your situation." """


# ══════════════════════════════════════════════════════════════════════════════
#  LLM CALL
# ══════════════════════════════════════════════════════════════════════════════
def _call_ai(key: str, model: str, sys_p: str, usr_p: str) -> str:
    import requests as rq
    r = rq.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type":  "application/json",
            "HTTP-Referer":  "https://dentist-tax-system.com",
            "X-Title":       "Dentists Tax Architecture System",
        },
        json={
            "model":       model,
            "messages":    [{"role":"system","content":sys_p},{"role":"user","content":usr_p}],
            "max_tokens":  4200,
            "temperature": 0.13,
        },
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION PARSER
# ══════════════════════════════════════════════════════════════════════════════
_SK = ["SECTION I","SECTION II","SECTION III","SECTION IV","SECTION V"]

def _parse(txt: str) -> dict:
    out = {}
    for i, k in enumerate(_SK):
        idx = txt.find(k)
        if idx == -1: out[k] = ""; continue
        nxt = len(txt)
        if i < 4:
            j = txt.find(_SK[i+1], idx+1)
            if j != -1: nxt = j
        chunk = txt[idx:nxt]
        lines, skip = [], False
        for ln in chunk.splitlines():
            s = ln.strip()
            if s.startswith("═") or s.startswith("─"): continue
            if s.startswith(k): skip = True; continue
            if skip:
                if s == "": continue
                if s.startswith("(") and len(s) > 55: continue
                skip = False
            lines.append(ln)
        out[k] = "\n".join(lines).strip()
    return out

def _pp(t: str):
    return [p.strip() for p in t.split("\n\n") if p.strip()]


# ══════════════════════════════════════════════════════════════════════════════
#  FULL REPORT RENDERER (left panel)
# ══════════════════════════════════════════════════════════════════════════════
def render_report(ai: str, fname: str = ""):
    now = datetime.utcnow()
    did = f"DTTS-{now.strftime('%Y%m%d-%H%M')}"
    secs = _parse(ai)

    st.markdown(f"""
<div class="rpt">
  <div class="rpt-head">
    <div class="rpt-head-row">
      <span class="rpt-badge">Confidential</span>
      <div class="rpt-meta">
        Doc: {did}<br>
        {now.strftime("%b %d, %Y · %H:%M UTC")}<br>
        {"File: " + fname if fname else "Uploaded return"}
      </div>
    </div>
    <div class="rpt-title">Tax Architecture Assessment</div>
    <div class="rpt-sub">Dental Practice &nbsp;·&nbsp; Phase 1 &nbsp;·&nbsp; Return-Only</div>
  </div>
  <div class="rpt-body">
""", unsafe_allow_html=True)

    SECS = [
        ("SECTION I",   "I",   "Tax Exposure Analysis",      "Problems found in your return",             "card-exp"),
        ("SECTION II",  "II",  "Structural Inefficiencies",  "Business architecture gaps",                "card-str"),
        ("SECTION III", "III", "Recommended Strategies",     "IRS-approved strategies for your situation","card-rec"),
        ("SECTION IV",  "IV",  "Dollar Impact Estimates",    "How much you could save",                   "card-sav"),
        ("SECTION V",   "V",   "Tax Protection Verdict",     "What's achievable for you",                 "card-rec"),
    ]

    for k, num, title, sub, dfl in SECS:
        body = secs.get(k, "")
        ps   = _pp(body)

        st.markdown(f"""
<div class="sec-hdr">
  <div class="sec-num">{num}</div>
  <div class="sec-title">{title}</div>
  <div class="sec-sub">{sub}</div>
</div>
""", unsafe_allow_html=True)

        if not ps:
            st.markdown('<p style="color:#9CA3AF;font-style:italic;font-size:.8rem;">No content extracted.</p>',
                        unsafe_allow_html=True)
            continue

        for para in ps:

            # Section V — verdict + disclaimer
            if k == "SECTION V":
                is_disc = ("licensed tax architect" in para.lower()
                           or "do not constitute finalized" in para.lower())
                if is_disc:
                    st.markdown(f"""
<div class="disclaimer">
  <div style="font-size:.95rem;flex-shrink:0;margin-top:.05rem;">⚖️</div>
  <div class="disclaimer-txt"><strong>Professional Disclaimer — </strong>{para}</div>
</div>""", unsafe_allow_html=True)
                    continue
                if "Full Protection Achievable" in para:
                    vc, vt, vtc = "verdict-full",    "✓ Full Protection Achievable",    "#0A6050"
                elif "Partial Protection Achievable" in para:
                    vc, vt, vtc = "verdict-partial", "⚡ Partial Protection Achievable", "#8A5808"
                elif "Protection Limited" in para:
                    vc, vt, vtc = "verdict-limited", "⚠ Protection Limited",            "#8A1E14"
                else:
                    vc, vt, vtc = "verdict-partial", "", "#3D4555"
                tag = f'<div class="verdict-tag" style="color:{vtc};">{vt}</div>' if vt else ""
                st.markdown(f'<div class="{vc}">{tag}<div class="verdict-body">{para}</div></div>',
                            unsafe_allow_html=True)
                continue

            # Section IV — pull out totals line
            if k == "SECTION IV":
                is_tot = any(x in para.lower() for x in
                             ["across all","combined total","total annual","total savings",
                              "all strategies","in aggregate","overall savings"])
                if is_tot:
                    amts = re.findall(r'\$[\d,]+(?:\s*(?:to|–|-)\s*\$[\d,]+)?', para)
                    disp = amts[0] if amts else "See report"
                    st.markdown(f"""
<div class="card-total">
  <div>
    <div class="total-lbl">Combined Annual Savings Estimate</div>
    <div class="total-amt">{disp}</div>
  </div>
  <div class="total-txt">{para}</div>
</div>""", unsafe_allow_html=True)
                    continue

            st.markdown(f'<div class="{dfl}">{para}</div>', unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        "⬇  Download Full Assessment (PDF)",
        data=ai, file_name=f"tax_assessment_{did}.txt", mime="text/plain",
    )


# ══════════════════════════════════════════════════════════════════════════════
#  RIGHT PANEL — PRE-ANALYSIS WELCOME
# ══════════════════════════════════════════════════════════════════════════════
def render_welcome():
    cats = sorted(set(s.get("category","Other") for s in STRATEGY_LIBRARY))
    tags = "".join(
        f'<span class="cat-tag">{_ci(c)}&nbsp;{c}</span>'
        for c in cats
    )
    n_strats = len(STRATEGY_LIBRARY)

    st.markdown(f"""
<div class="welcome-card">
  <span class="welcome-icon">🔍</span>
  <div class="welcome-title">Your personal tax review starts here</div>
  <div class="welcome-body">
    Upload your tax return and this system will read it line by line —
    finding what you're overpaying, what's missing, and which of our
    <strong>{n_strats} dental-specific strategies</strong> apply to your exact situation.
    No accountant required to get started.
  </div>
  <div class="stat-row">
    <div class="stat-box">
      <div class="stat-val">{n_strats}</div>
      <div class="stat-lbl">Dental tax strategies in our library</div>
    </div>
    <div class="stat-box">
      <div class="stat-val">5</div>
      <div class="stat-lbl">Report sections covering every angle</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div style="font-size:.62rem;font-weight:700;text-transform:uppercase;
            letter-spacing:.18em;color:var(--muted);margin:.5rem 0 .45rem;">
  How it works
</div>
<div class="how-row">
  <div class="how-step">
    <div class="how-circle">1</div>
    <div class="how-title">Upload</div>
    <div class="how-desc">Drop in your PDF tax return — any standard form</div>
  </div>
  <div class="how-step">
    <div class="how-circle">2</div>
    <div class="how-title">Analyze</div>
    <div class="how-desc">AI matches your return against 50 proven strategies</div>
  </div>
  <div class="how-step">
    <div class="how-circle">3</div>
    <div class="how-title">Review</div>
    <div class="how-desc">Get a plain-English report with dollar savings estimates</div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown(f"""
<div style="font-size:.62rem;font-weight:700;text-transform:uppercase;
            letter-spacing:.18em;color:var(--muted);margin:.5rem 0 .4rem;">
  Strategies covered
</div>
<div class="cat-tag-row">{tags}</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  RIGHT PANEL — RECOMMENDED STRATEGIES (post-analysis)
# ══════════════════════════════════════════════════════════════════════════════
def render_recommended(ai: str):
    secs  = _parse(ai)
    ps    = _pp(secs.get("SECTION III", ""))
    count = len(ps)

    # ── Summary banner ──
    st.markdown(f"""
<div class="rec-summary">
  <div class="rec-summary-left">
    <div class="rec-summary-title">Your Recommended Strategies</div>
    <div class="rec-summary-sub">Based on your specific return — only what applies to you</div>
  </div>
  <div class="rec-summary-count">
    <div class="rec-count-num">{count}</div>
    <div class="rec-count-lbl">strategies found</div>
  </div>
</div>
""", unsafe_allow_html=True)

    if not ps:
        st.info("No strategy recommendations were extracted from this return.")
        return

    # ── Render each strategy ──
    for para in ps:
        s = _match_strategy(para)

        # Extract savings figure if present
        amts = re.findall(r'\$[\d,]+(?:\s*(?:to|–|-)\s*\$[\d,]+)?', para)
        savings_html = (
            f'<div class="strat-savings-badge">💰 {amts[0]}</div>' if amts else ""
        )

        if s:
            cat   = s.get("category", "Strategy")
            color = _cc(cat)
            icon  = _ci(cat)
            bg    = _cbg(cat)
            days  = s.get("speed_days", "?")
            ph1   = s.get("phase_1_eligible", True)
            ph_lbl= "Phase 1 — Can start now" if ph1 else "Phase 2 — Plan ahead"

            st.markdown(f"""
<div class="strat-card">
  <div class="strat-card-body">
    <div class="strat-icon-row">
      <div class="strat-icon-bubble" style="background:{bg};">
        <span>{icon}</span>
      </div>
      <div style="flex:1;min-width:0;">
        <div class="strat-name">{s['name']}</div>
        <div class="strat-irc">{s['irc']}</div>
      </div>
      {savings_html}
    </div>
    <div class="strat-desc">{para}</div>
  </div>
  <div class="strat-footer">
    <span class="tag tag-cat" style="background:{bg};color:{color};">{icon} {cat}</span>
    <span class="tag tag-time">⏱ {days} days to implement</span>
    <span class="tag tag-ph">{ph_lbl}</span>
  </div>
</div>
""", unsafe_allow_html=True)

        else:
            # Fallback for unmatched paragraphs
            st.markdown(f"""
<div class="strat-card">
  <div class="strat-card-body">
    <div class="strat-icon-row">
      <div class="strat-icon-bubble" style="background:#FBF5E6;">
        <span>📌</span>
      </div>
      <div style="flex:1;">
        <div class="strat-name">Additional Recommendation</div>
        <div class="strat-irc">See full report for IRC reference</div>
      </div>
      {savings_html}
    </div>
    <div class="strat-desc">{para}</div>
  </div>
  <div class="strat-footer">
    <span class="tag tag-cat">📋 Strategy</span>
    <span class="tag tag-time">⏱ Review with advisor</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  STRATEGY LIBRARY DIALOG
# ══════════════════════════════════════════════════════════════════════════════
@st.dialog("📚  Complete Strategy Library", width="large")
def open_library_dialog():
    if not STRAT_OK or not STRATEGY_LIBRARY:
        st.warning("Strategy library not loaded — ensure new_strategies.py is in the same folder.")
        return

    by_cat: dict = defaultdict(list)
    for s in STRATEGY_LIBRARY:
        by_cat[s.get("category","Other")].append(s)

    st.markdown(f"""
<div class="lib-intro">
  Our full library contains <strong>{len(STRATEGY_LIBRARY)} IRS-approved tax strategies</strong>
  built specifically for dental practice owners.
  After uploading your return, this system identifies which of these apply to your situation.
</div>
""", unsafe_allow_html=True)

    for cat in sorted(by_cat.keys()):
        strats = by_cat[cat]
        color  = _cc(cat)
        icon   = _ci(cat)

        st.markdown(f"""
<div class="lib-cat-title">
  <span style="color:{color};">{icon}</span>
  {cat}
  <span class="lib-cat-count">— {len(strats)} strategies</span>
</div>
""", unsafe_allow_html=True)

        for s in strats:
            ph1   = s.get("phase_1_eligible", True)
            desc  = s.get("plain_english", "")
            # Trim for display
            if len(desc) > 120:
                desc = desc[:117] + "…"

            st.markdown(f"""
<div class="lib-item">
  <div class="lib-dot" style="background:{color};"></div>
  <div class="lib-item-main">
    <div class="lib-item-name">{s['name']}</div>
    {f'<div class="lib-item-desc">{desc}</div>' if desc else ''}
  </div>
  <div class="lib-item-right">
    <div class="lib-item-irc">{s['irc']}</div>
    <span class="lib-badge {'lib-ph1' if ph1 else 'lib-ph2'}">{'Phase 1' if ph1 else 'Phase 2'}</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
def _sidebar() -> dict:
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

        st.markdown("### API Keys")
        api_key = st.text_input("OpenRouter API Key",
                                value=os.getenv("OPENROUTER_API_KEY",""),
                                type="password", placeholder="sk-or-...")
        model   = st.text_input("Model",
                                value=os.getenv("OPENROUTER_MODEL","anthropic/claude-3.5-sonnet"))

        st.markdown("---")
        st.markdown("### Status")
        def _dot(ok, lbl):
            c = "🟢" if ok else "🔴"
            st.markdown(f'<div style="font-size:.71rem;margin-bottom:.26rem;">{c}&nbsp; {lbl}</div>',
                        unsafe_allow_html=True)
        _dot(bool(api_key), "OpenRouter connected")
        _dot(PDF_OK,        "PDF reader ready")
        _dot(STRAT_OK,      f"{len(STRATEGY_LIBRARY)} strategies loaded")

        st.markdown("---")
        st.markdown(
            '<div style="font-size:.58rem;color:#3D4B60;line-height:1.65;">'
            'Analysis is for professional review only. Not finalized tax advice. '
            'Consult a licensed tax architect before implementation.'
            '</div>',
            unsafe_allow_html=True)

    return {"key": api_key, "model": model}


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    # ── Header ──
    st.markdown("""
<div class="phdr">
  <div>
    <div class="phdr-title">Dentists' Tax &amp; Business Architecture System™</div>
    <div class="phdr-sub">Phase 1 &nbsp;·&nbsp; Tax Risk Assessment &nbsp;·&nbsp; Return-Only Analysis</div>
  </div>
  <div class="phdr-meta">Version 2026.02<br>Confidential<br>Phase 1</div>
</div>
""", unsafe_allow_html=True)

    cfg = _sidebar()
    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([11, 9], gap="large")

    # ═══════════════════════════════════════════
    # LEFT — Upload + Full Report
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
            st.markdown(
                f'<div class="file-ok">✓ &nbsp;<strong>{uploaded.name}</strong>'
                f'&nbsp;·&nbsp; {uploaded.size / 1024:.1f} KB — ready to analyze</div>',
                unsafe_allow_html=True)
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

        if not cfg["key"]:
            st.warning("⚠  Enter your OpenRouter API key in the sidebar to enable analysis.")

        st.markdown("<br>", unsafe_allow_html=True)

        go = st.button(
            "⬡  Analyze My Return",
            type="primary",
            disabled=(not uploaded or not cfg["key"]),
        )

        # ── Run analysis ──
        if uploaded and cfg["key"] and go:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(uploaded.read())
                tmp_path = tmp.name

            try:
                prog = st.progress(0,  text="Reading your PDF…")
                raw  = _extract(tmp_path)
                prog.progress(20, text="PDF read successfully…")

                if len(raw.strip()) < 80:
                    st.error("Could not read text from this PDF. It may be scanned. "
                             "Please try a text-based PDF.")
                    Path(tmp_path).unlink(missing_ok=True)
                    return

                prog.progress(38, text="Analyzing your return — about 30 seconds…")
                ai_txt = _call_ai(cfg["key"], cfg["model"], _SYS, _build_prompt(raw))

                prog.progress(94, text="Building your report…")
                time.sleep(0.2)
                prog.progress(100, text="Done.")
                prog.empty()

                st.session_state.ai_result   = ai_txt
                st.session_state.report_done = True
                st.session_state.upload_name = uploaded.name

                st.success("✓  Analysis complete — your strategies are on the right →")
                render_report(ai_txt, fname=uploaded.name)

            except Exception as e:
                st.error(f"Something went wrong: {e}")
                with st.expander("Technical details"):
                    import traceback; st.code(traceback.format_exc())
            finally:
                Path(tmp_path).unlink(missing_ok=True)

        elif st.session_state.report_done and not go:
            render_report(st.session_state.ai_result, fname=st.session_state.upload_name)

    # ═══════════════════════════════════════════
    # RIGHT — Recommended Strategies + Library
    # ═══════════════════════════════════════════
    with right:
        if st.session_state.report_done:
            st.markdown('<div class="col-hdr">Your Recommended Strategies</div>',
                        unsafe_allow_html=True)
            render_recommended(st.session_state.ai_result)
        else:
            st.markdown('<div class="col-hdr">What You\'ll Get</div>',
                        unsafe_allow_html=True)
            render_welcome()

        # ── Explore Library button (always visible) ──
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📚  Explore Strategy Library", type="secondary",
                     key="lib_btn"):
            open_library_dialog()
        st.markdown(
            '<div style="font-size:.67rem;color:var(--muted);text-align:center;'
            'margin-top:.4rem;line-height:1.5;">'
            f'Browse all {len(STRATEGY_LIBRARY)} dental-specific strategies in our library'
            '</div>',
            unsafe_allow_html=True)


if __name__ == "__main__":
    main()
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
