"""
AgriYield — Ethiopian smallholder yield & income forecasting (Team 11).
Every number on screen comes from the production model or the cleaned competition tables.
"""

import base64
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

app_dir = Path(__file__).resolve().parent
project_dir = app_dir.parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

from predictor import CropYieldPredictor  # noqa: E402

st.set_page_config(
    page_title="AgriYield — Ethiopian Smallholder Yield Forecasts",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# DESIGN TOKENS
# -----------------------------------------------------------------------------
FIELD = "#0E3B2E"    # deep field green: ink, dark surfaces
CANOPY = "#1F6B4A"   # primary
SPROUT = "#5FB37A"   # accent
HARVEST = "#D9A441"  # highlight: "your plot", optimum
BRICK = "#B5523B"    # losses only
SAGE = "#F2F5F0"     # page background
LINE = "#DCE5DD"
MUTED = "#5D6F64"
GREENS = [FIELD, CANOPY, "#3E8E5E", SPROUT, "#A7D3A6"]


@st.cache_data(show_spinner=False)
def get_cached_hero_bg():
    p = app_dir / "assets" / "hero_bg.jpg"
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else ""


@st.cache_resource(show_spinner=False)
def get_predictor():
    # Loaded once per server process: model + lookup tables
    return CropYieldPredictor()


hero_bg_b64 = get_cached_hero_bg()
try:
    predictor = get_predictor()
except Exception as exc:
    st.error(
        f"The production model or its lookup tables could not be loaded: {exc}\n\n"
        "Run `python src/build_app_assets.py` from the repository root and restart the app."
    )
    st.stop()

hero_img = f", url('data:image/jpeg;base64,{hero_bg_b64}') center/cover no-repeat" if hero_bg_b64 else ""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Instrument+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {
  --field: __FIELD__; --canopy: __CANOPY__; --sprout: __SPROUT__; --harvest: __HARVEST__;
  --brick: __BRICK__; --sage: __SAGE__; --line: __LINE__; --muted: __MUTED__;
  --display: 'Bricolage Grotesque', 'Instrument Sans', sans-serif;
  --body: 'Instrument Sans', -apple-system, 'Segoe UI', sans-serif;
  --mono: 'IBM Plex Mono', ui-monospace, monospace;
}
html, body, [class*="css"], .stMarkdown, .stText, button, input, label, textarea, select {
  font-family: var(--body);
}
.stApp { background: var(--sage); color: #17261F; }
header[data-testid="stHeader"] { display: none !important; }
.block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 1280px !important; }
h1, h2, h3, h4 { font-family: var(--display) !important; color: var(--field) !important; letter-spacing: -0.015em; }
h3 { font-size: 1.35rem !important; font-weight: 700 !important; }
h4 { font-size: 1.02rem !important; font-weight: 700 !important; }
[data-testid="stCaptionContainer"] { color: var(--muted); }

/* ---------- top bar ---------- */
.topbar { display: flex; justify-content: space-between; align-items: center; gap: 12px;
  background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: 10px 18px; margin-bottom: 10px; }
.brand { display: flex; align-items: center; gap: 10px; font-family: var(--display); font-weight: 800;
  font-size: 1.2rem; color: var(--field); letter-spacing: -0.02em; }
.brand small { font-family: var(--body); font-weight: 600; font-size: 0.72rem; color: var(--muted);
  letter-spacing: 0.04em; text-transform: uppercase; }
.topbar-right { display: flex; align-items: center; gap: 14px; font-size: 0.75rem; color: var(--muted); }
.status { display: inline-flex; align-items: center; gap: 7px; background: #EAF5EC; color: var(--canopy);
  border: 1px solid #CFE6D4; padding: 4px 11px; border-radius: 999px; font-weight: 600; }
.status i { width: 7px; height: 7px; border-radius: 50%; background: var(--sprout); display: inline-block;
  box-shadow: 0 0 0 0 rgba(95,179,122,.6); animation: pulse 2.4s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(95,179,122,.55);} 70% { box-shadow: 0 0 0 7px rgba(95,179,122,0);} 100% { box-shadow: 0 0 0 0 rgba(95,179,122,0);} }
.mono { font-family: var(--mono); }

/* ---------- price strip ---------- */
.prices { display: grid; grid-template-columns: auto repeat(5, 1fr); align-items: center; gap: 4px;
  background: var(--field); border-radius: 14px; padding: 8px 14px; margin-bottom: 14px; }
.prices .lbl { color: #9FC3AC; font-size: 0.68rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; padding-right: 10px; line-height: 1.25; }
.price { border-left: 1px solid rgba(255,255,255,.10); padding: 2px 12px; }
.price .c { color: #9FC3AC; font-size: 0.7rem; text-transform: uppercase; letter-spacing: .06em; }
.price .v { color: #fff; font-family: var(--mono); font-weight: 600; font-size: 0.92rem; }
.price .d { font-family: var(--mono); font-size: 0.72rem; margin-left: 4px; }

/* ---------- hero (image + topographic contour signature) ---------- */
.hero { position: relative; overflow: hidden; border-radius: 20px; padding: 34px 34px 26px; color: #fff; margin-bottom: 18px;
  background: linear-gradient(115deg, rgba(8,36,27,.94) 0%, rgba(14,59,46,.82) 45%, rgba(14,59,46,.55) 100%)__HERO_IMG__; }
.hero:before { content: ""; position: absolute; inset: 0; pointer-events: none;
  background: repeating-radial-gradient(ellipse at 92% 8%, rgba(255,255,255,.07) 0 1px, transparent 1px 26px); }
.hero > * { position: relative; }
.eyebrow { font-size: .7rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: #A7D3A6; }
.hero h1 { font-family: var(--display) !important; color: #fff !important; font-size: clamp(1.8rem, 3.4vw, 2.55rem) !important;
  font-weight: 800 !important; line-height: 1.08 !important; margin: 6px 0 8px !important; padding: 0 !important; }
.hero p { color: #D5E6DA; font-size: .97rem; max-width: 640px; margin: 0 0 22px; }
.hero-stats { display: grid; grid-template-columns: repeat(4, 1fr); border-top: 1px solid rgba(255,255,255,.16); }
.hstat { padding: 14px 16px 2px 0; }
.hstat + .hstat { padding-left: 18px; border-left: 1px solid rgba(255,255,255,.12); }
.hstat .n { font-family: var(--display); font-weight: 700; font-size: 1.65rem; line-height: 1; }
.hstat .l { font-size: .72rem; color: #B9D3C1; margin-top: 5px; }

/* ---------- tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--line); background: transparent; }
.stTabs [data-baseweb="tab"] { padding: 10px 14px; font-weight: 600; color: var(--muted); background: transparent; }
.stTabs [aria-selected="true"] { color: var(--field) !important; }
.stTabs [data-baseweb="tab-highlight"] { background-color: var(--canopy) !important; height: 3px; border-radius: 3px; }
.stTabs [data-baseweb="tab-border"] { display: none; }

/* ---------- surfaces ---------- */
[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 16px; }
.st-key-plotcard { background: #fff; border-radius: 16px; }
.card-title { font-family: var(--display); font-weight: 700; font-size: 1rem; color: var(--field); margin-bottom: 2px; }
.card { background: #fff; border: 1px solid var(--line); border-radius: 16px; padding: 16px 18px; margin-bottom: 14px; }
.sub { color: var(--muted); font-size: .78rem; }

/* KPI tiles */
.kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 12px; }
.kpi { background: #fff; border: 1px solid var(--line); border-radius: 16px; padding: 14px 16px; min-height: 112px; }
.kpi .t { font-size: .72rem; font-weight: 700; letter-spacing: .07em; text-transform: uppercase; color: var(--muted); }
.kpi .n { font-family: var(--display); font-weight: 700; font-size: clamp(1.35rem, 2vw, 1.9rem); color: var(--field); white-space: nowrap; line-height: 1.15; margin-top: 4px; }
.kpi .n span { font-family: var(--body); font-size: .8rem; color: var(--muted); font-weight: 500; margin-left: 3px; }
.kpi .s { font-family: var(--mono); font-size: .74rem; color: var(--muted); margin-top: 4px; }
.kpi.hl { border-color: #CFE6D4; box-shadow: inset 0 3px 0 var(--sprout); }

/* field-row gauge (signature) */
.bench { display: grid; grid-template-columns: 1.35fr 1fr; gap: 22px; align-items: center; }
.gauge { position: relative; height: 22px; border-radius: 6px; margin: 12px 0 6px;
  background: repeating-linear-gradient(90deg, #E4ECE5 0 3px, #F4F8F4 3px 9px); }
.gauge .band { position: absolute; top: 0; bottom: 0; background: rgba(31,107,74,.22); border-left: 2px solid rgba(31,107,74,.45); border-right: 2px solid rgba(31,107,74,.45); }
.gauge .med { position: absolute; top: -3px; bottom: -3px; width: 2px; background: var(--canopy); }
.gauge .you { position: absolute; top: 50%; width: 16px; height: 16px; margin: -8px 0 0 -8px; border-radius: 50%;
  background: var(--harvest); border: 3px solid #fff; box-shadow: 0 1px 4px rgba(0,0,0,.25); }
.gauge-scale { display: flex; justify-content: space-between; font-family: var(--mono); font-size: .7rem; color: var(--muted); }
.legend { display: flex; gap: 14px; font-size: .74rem; color: var(--muted); margin-top: 6px; flex-wrap: wrap; }
.legend b { display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: 5px; vertical-align: -1px; }
.conds { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px 14px; }
.cond .l { font-size: .7rem; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); }
.cond .v { font-family: var(--mono); font-weight: 600; font-size: .95rem; color: var(--field); }

/* P&L + insights */
.row { display: flex; justify-content: space-between; align-items: baseline; padding: 7px 0; border-bottom: 1px solid #EEF2EE; font-size: .88rem; }
.row .v { font-family: var(--mono); }
.row.total { border-bottom: 0; border-top: 2px solid var(--field); margin-top: 4px; padding-top: 10px; font-weight: 700; font-size: 1rem; }
.ins { display: flex; justify-content: space-between; align-items: center; gap: 10px; padding: 10px 0; border-bottom: 1px solid #EEF2EE; }
.ins:last-child { border-bottom: 0; }
.ins .k { display: flex; align-items: center; gap: 8px; font-size: .86rem; color: #2A3A31; }
.ins .k i { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.ins .v { font-family: var(--mono); font-weight: 600; font-size: .86rem; text-align: right; white-space: nowrap; }
.pos { color: var(--canopy); } .neg { color: var(--brick); } .gold { color: #A87819; }

/* st.metric as cards */
[data-testid="stMetric"] { background: #fff; border: 1px solid var(--line); border-radius: 16px; padding: 14px 16px; }
[data-testid="stMetricLabel"] p { font-size: .74rem !important; font-weight: 700 !important; letter-spacing: .06em; text-transform: uppercase; color: var(--muted) !important; }
[data-testid="stMetricValue"] { font-family: var(--display); font-weight: 700; color: var(--field); font-size: 1.75rem !important; }
[data-testid="stMetricDelta"] { font-family: var(--mono); font-size: .76rem !important; }

/* buttons & alerts */
[data-testid="stBaseButton-secondary"] { background: #fff; border: 1px solid var(--line); border-radius: 10px; color: var(--field); font-weight: 600; }
[data-testid="stBaseButton-secondary"]:hover { border-color: var(--canopy); color: var(--canopy); background: #F7FBF7; }
[data-testid="stAlert"] { border-radius: 12px; }

.footer { margin-top: 26px; padding-top: 12px; border-top: 1px solid var(--line); display: flex; justify-content: space-between;
  flex-wrap: wrap; gap: 8px; font-size: .74rem; color: var(--muted); }

@media (max-width: 900px) {
  .kpis, .hero-stats { grid-template-columns: repeat(2, 1fr); }
  .hstat:nth-child(3) { border-left: 0; padding-left: 0; }
  .bench { grid-template-columns: 1fr; }
  .prices { grid-template-columns: repeat(5, minmax(110px, 1fr)); overflow-x: auto; }
  .prices .lbl { display: none; }
}
@media (max-width: 640px) {
  .topbar { flex-wrap: wrap; padding: 10px 14px; }
  .brand small { display: none; }
  .status { white-space: nowrap; }
  .hero { padding: 24px 20px 18px; }
  .block-container { padding-left: .85rem !important; padding-right: .85rem !important; }
  .prices { grid-template-columns: repeat(3, 1fr); overflow-x: visible; row-gap: 8px; padding: 10px 8px; }
  .price { padding: 2px 10px; }
  .price:nth-child(2), .price:nth-child(5) { border-left: 0; }
  .hstat .n { font-size: 1.35rem; }
  .kpis { gap: 10px; }
  .kpi { min-height: 0; padding: 12px 14px; }
  .conds { grid-template-columns: repeat(2, 1fr); }
  .stTabs [data-baseweb="tab"] { padding: 8px 10px; font-size: .85rem; }
  .modebar-container { display: none !important; }
}
@media (prefers-reduced-motion: reduce) { .status i { animation: none; } }
</style>
"""
for k, v in {"__FIELD__": FIELD, "__CANOPY__": CANOPY, "__SPROUT__": SPROUT, "__HARVEST__": HARVEST, "__BRICK__": BRICK,
             "__SAGE__": SAGE, "__LINE__": LINE, "__MUTED__": MUTED, "__HERO_IMG__": hero_img}.items():
    CSS = CSS.replace(k, v)
st.markdown(CSS, unsafe_allow_html=True)

M = predictor.metrics
CV = M.get("cv", {})
TIERS = M.get("tiers", {})
REGIONS = ["Oromia", "Amhara", "SNNPR", "Tigray", "Somali"]
CROPS = ["Maize", "Teff", "Wheat", "Barley", "Sorghum"]
MONTH_LABELS = {
    "Feb": "Feb · Belg", "Mar": "Mar · Belg",
    "Jun": "Jun · Meher", "Jul": "Jul · Meher", "Aug": "Aug · Meher",
}
PLOT_COLUMNS = [
    "region", "crop_type", "survey_year", "planting_month", "altitude_m", "farm_size_ha",
    "fertilizer_kg_per_ha", "improved_seed_used", "pest_disease_flag", "soil_quality_index",
    "labor_days_per_ha",
]


def style_fig(fig, height=300):
    fig.update_layout(
        template="plotly_white", height=height, margin=dict(l=8, r=8, t=36, b=8),
        font=dict(family="Instrument Sans, sans-serif", size=12, color="#2A3A31"),
        title_font=dict(family="Bricolage Grotesque, sans-serif", size=15, color=FIELD),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="top", y=-0.34, xanchor="left", x=0, font=dict(size=11)),
        hoverlabel=dict(font_family="IBM Plex Mono, monospace"),
    )
    fig.update_xaxes(gridcolor="#E6ECE6", zeroline=False, linecolor=LINE)
    fig.update_yaxes(gridcolor="#E6ECE6", zeroline=False, linecolor=LINE)
    return fig


def sign_cls(x: float) -> str:
    return "pos" if x >= 0 else "neg"


@st.cache_data(show_spinner=False)
def build_id() -> str:
    """Short git commit of the running code, read from .git without needing the git CLI."""
    try:
        git = project_dir / ".git"
        head = (git / "HEAD").read_text().strip()
        if not head.startswith("ref:"):
            return head[:7]
        ref = head.split(" ", 1)[1]
        ref_file = git / ref
        if ref_file.exists():
            return ref_file.read_text().strip()[:7]
        for line in (git / "packed-refs").read_text().splitlines():
            if line.endswith(" " + ref):
                return line[:7]
    except Exception:
        pass
    return "unknown"


@st.cache_data(show_spinner=False)
def price_ticker():
    p = predictor.prices.reset_index()
    nat = p.groupby(["crop_type", "year"])["price_birr_per_quintal"].mean().unstack()
    last, prev = max(nat.columns), max(nat.columns) - 1
    return last, [(c, nat.loc[c, last], (nat.loc[c, last] / nat.loc[c, prev] - 1) * 100) for c in nat.index]


# -----------------------------------------------------------------------------
# TOP BAR · PRICE STRIP · HERO
# -----------------------------------------------------------------------------
LEAF = (f'<svg width="26" height="26" viewBox="0 0 26 26" aria-hidden="true"><rect width="26" height="26" rx="7" fill="{FIELD}"/>'
        f'<path d="M13 20V11" stroke="{SPROUT}" stroke-width="1.8" stroke-linecap="round"/>'
        f'<path d="M13 13c0-3.2 2.4-5.6 6-5.6 0 3.4-2.5 5.6-6 5.6Z" fill="{SPROUT}"/>'
        f'<path d="M13 15.5c0-2.6-2-4.6-5-4.6 0 2.8 2.1 4.6 5 4.6Z" fill="#A7D3A6"/></svg>')

price_year, ticker_rows = price_ticker()
price_html = "".join(
    f'<div class="price"><div class="c">{c}</div><span class="v">{v:,.0f}</span>'
    f'<span class="d" style="color:{"#8FD3A0" if d >= 0 else "#F0A08C"}">{d:+.0f}%</span></div>'
    for c, v, d in ticker_rows
)
st.markdown(f"""
<div class="topbar">
  <div class="brand">{LEAF} AgriYield <small>Ethiopia · Smallholder forecasts</small></div>
  <div class="topbar-right">
    <span class="status"><i></i>Model live · CV error ±{CV.get("rmse", 0):.2f} t/ha</span>
    <span class="mono">build {build_id()}</span>
  </div>
</div>
<div class="prices">
  <div class="lbl">Price {price_year}<br>ETB / quintal</div>
  {price_html}
</div>
<div class="hero">
  <div class="eyebrow">Oromia · Amhara · SNNPR · Tigray · Somali</div>
  <h1>Know the harvest before you plant.</h1>
  <p>Yield and income forecasts for smallholder plots, learned from surveyed fields, seasonal weather and market prices.</p>
  <div class="hero-stats">
    <div class="hstat"><div class="n">{M.get("n_train_plots", 0):,}</div><div class="l">surveyed plots learned</div></div>
    <div class="hstat"><div class="n">{CV.get("r2", 0):.1%}</div><div class="l">of yield variation explained</div></div>
    <div class="hstat"><div class="n">±{CV.get("rmse", 0):.2f} t/ha</div><div class="l">typical error on unseen plots</div></div>
    <div class="hstat"><div class="n">{TIERS.get("accuracy", 0):.1%}</div><div class="l">food-security tier accuracy</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

t_farm, t_coop, t_climate, t_audit = st.tabs([
    ":material/agriculture: Farm forecast",
    ":material/groups: Cooperative",
    ":material/thunderstorm: Climate stress",
    ":material/fact_check: Model audit",
])

# =============================================================================
# TAB 1: FARM FORECAST
# =============================================================================
PRESETS = {
    "maize":   {"region": "Oromia", "crop": "Maize",   "size": 2.5, "alt": 1850, "fert": 85, "seed": 1, "labor": 45, "pest": 0, "sqi": 0.75, "month": "Jun"},
    "teff":    {"region": "Amhara", "crop": "Teff",    "size": 1.5, "alt": 2100, "fert": 45, "seed": 1, "labor": 40, "pest": 0, "sqi": 0.70, "month": "Jul"},
    "wheat":   {"region": "Oromia", "crop": "Wheat",   "size": 3.0, "alt": 2350, "fert": 90, "seed": 1, "labor": 50, "pest": 0, "sqi": 0.80, "month": "Jun"},
    "barley":  {"region": "Tigray", "crop": "Barley",  "size": 1.2, "alt": 2450, "fert": 50, "seed": 1, "labor": 35, "pest": 0, "sqi": 0.65, "month": "Jul"},
    "sorghum": {"region": "Somali", "crop": "Sorghum", "size": 2.0, "alt": 1200, "fert": 25, "seed": 0, "labor": 25, "pest": 0, "sqi": 0.50, "month": "Mar"},
}
SEED_OPTS = ["Farm-saved", "Certified improved"]


def apply_preset(name: str) -> None:
    p = PRESETS[name]
    st.session_state.update({
        "f_region": p["region"], "f_crop": p["crop"], "f_size": float(p["size"]), "f_month": p["month"],
        "f_fert": int(p["fert"]), "f_seed": SEED_OPTS[p["seed"]], "f_labor": int(p["labor"]),
        "f_pest": bool(p["pest"]), "f_alt": int(p["alt"]), "f_sqi": float(p["sqi"]), "f_year": 2024,
        "f_rain_override": False,
    })


if "f_region" not in st.session_state or st.session_state.get("f_seed") not in SEED_OPTS:
    apply_preset("maize")


def gauge_html(value, p10, p50, p90, unit="t/ha"):
    hi = max(p90 * 1.3, value * 1.1, 1.0)
    pos = lambda x: max(0.0, min(100.0, x / hi * 100))  # noqa: E731
    return f"""
    <div class="gauge">
      <div class="band" style="left:{pos(p10):.1f}%; width:{pos(p90) - pos(p10):.1f}%"></div>
      <div class="med" style="left:{pos(p50):.1f}%"></div>
      <div class="you" style="left:{pos(value):.1f}%"></div>
    </div>
    <div class="gauge-scale"><span>0</span><span>{hi / 2:.1f}</span><span>{hi:.1f} {unit}</span></div>
    <div class="legend"><span><b style="background:{HARVEST}"></b>This plot {value:.2f}</span>
      <span><b style="background:rgba(31,107,74,.35)"></b>Middle 80% of plots {p10:.1f}–{p90:.1f}</span>
      <span><b style="background:{CANOPY}"></b>Median {p50:.2f}</span></div>"""


with t_farm:
    p_cols = st.columns(5)
    for col, (key, label) in zip(p_cols, [
        ("maize", "Arsi maize · 2.5 ha"), ("teff", "Gojjam teff · 1.5 ha"), ("wheat", "Bale wheat · 3.0 ha"),
        ("barley", "Tigray barley · 1.2 ha"), ("sorghum", "Somali sorghum · 2.0 ha"),
    ]):
        col.button(label, width="stretch", on_click=apply_preset, args=(key,), icon=":material/grass:")

    col_deck, col_display = st.columns([1.05, 1.95], gap="medium")

    with col_deck, st.container(border=True, key="plotcard"):
        st.markdown('<div class="card-title">Plot</div>', unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        reg_val = d1.selectbox("Region", REGIONS, key="f_region")
        crop_val = d2.selectbox("Crop", CROPS, key="f_crop")

        d3, d4, d5 = st.columns([0.95, 1.25, 0.9])
        farm_size = d3.number_input("Area (ha)", min_value=0.2, max_value=6.0, step=0.1, key="f_size",
                                    help="1 ha ≈ 4 timad")
        month_val = d4.selectbox("Planted", list(MONTH_LABELS), format_func=MONTH_LABELS.get, key="f_month")
        year_val = d5.selectbox("Season", [2024, 2023, 2022, 2021], key="f_year")

        fert_val = st.slider("Fertilizer (kg/ha)", 0, 160, step=5, key="f_fert")
        seed_opt = st.segmented_control("Seed", SEED_OPTS, key="f_seed", width="stretch")
        seed_val = 1 if seed_opt == SEED_OPTS[1] else 0
        labor_val = st.slider("Labor (days/ha)", 10, 100, step=5, key="f_labor")
        pest_val = 1 if st.toggle("Pest or disease pressure", key="f_pest") else 0

        with st.expander("Land & rainfall"):
            alt_val = st.slider("Altitude (m)", 500, 3100, step=50, key="f_alt")
            sqi_val = st.slider("Soil quality index", 0.05, 1.0, step=0.05, key="f_sqi")
            typical_rain = predictor.get_typical_plot_rainfall(reg_val, year_val, month_val)
            if st.checkbox("Enter plot-reported rainfall", key="f_rain_override"):
                plot_rain = st.number_input("Plot rainfall (mm)", 100.0, 4000.0, float(typical_rain), step=25.0)
            else:
                plot_rain = typical_rain
                st.caption(f"Survey median for {reg_val}, {month_val} {year_val}: {typical_rain:,.0f} mm")

        with st.expander("Cost assumptions (ETB)"):
            st.caption("Used for profit only. They do not change the yield forecast.")
            c_fert_price = st.number_input("Fertilizer per kg", 0.0, 500.0, 42.0, step=1.0)
            c_labor_price = st.number_input("Labor per day", 0.0, 2000.0, 280.0, step=10.0)
            c_seed_price = st.number_input("Certified seed per ha", 0.0, 50000.0, 4800.0, step=100.0)
            c_pest_price = st.number_input("Pest control per ha", 0.0, 20000.0, 2400.0, step=100.0)

    with col_display:
        in_dict = {
            "region": reg_val, "crop_type": crop_val, "survey_year": year_val,
            "planting_month": month_val, "farm_size_ha": farm_size, "altitude_m": alt_val,
            "fertilizer_kg_per_ha": fert_val, "improved_seed_used": seed_val,
            "pest_disease_flag": pest_val, "soil_quality_index": sqi_val,
            "labor_days_per_ha": labor_val, "rainfall_mm_season": plot_rain,
        }

        # One vectorised model call: current plot, seed/pest counterfactuals and the fertilizer curve
        steps = np.arange(0, 165, 10)
        rows = [in_dict, dict(in_dict, improved_seed_used=1 - seed_val), dict(in_dict, pest_disease_flag=1 - pest_val)]
        rows += [dict(in_dict, fertilizer_kg_per_ha=int(f)) for f in steps]
        batch = predictor.predict_batch(pd.DataFrame(rows))
        cur, alt_seed, alt_pest, curve = batch.iloc[0], batch.iloc[1], batch.iloc[2], batch.iloc[3:]

        pred_y = float(cur["predicted_yield_t_ha"])
        tot_tons = float(cur["total_harvest_tons"])
        tot_bags = float(cur["total_quintals"])
        spot_price = float(cur["price_birr_per_quintal"])
        gross_sales = float(cur["gross_revenue_birr"])
        crop_err = M.get("by_crop", {}).get(crop_val.lower(), {}).get("rmse", CV.get("rmse", 0))

        cost_fert = fert_val * farm_size * c_fert_price
        cost_seed = farm_size * (c_seed_price if seed_val == 1 else 0.0)
        cost_labor = labor_val * farm_size * c_labor_price
        cost_pest = farm_size * (c_pest_price if pest_val == 1 else 0.0)
        tot_costs = cost_fert + cost_seed + cost_labor + cost_pest
        net_cash = gross_sales - tot_costs
        roi = (net_cash / tot_costs * 100.0) if tot_costs > 0 else 0.0
        breakeven = (tot_costs / (farm_size * 10.0 * spot_price)) if (farm_size * spot_price > 0) else 0.0

        st.markdown(f"""
        <div class="kpis">
          <div class="kpi hl"><div class="t">Expected harvest</div>
            <div class="n">{tot_bags:,.0f}<span>bags</span></div>
            <div class="s">{pred_y:.2f} ± {crop_err:.2f} t/ha</div></div>
          <div class="kpi"><div class="t">Crop value</div>
            <div class="n">{gross_sales / 1e3:,.1f}k<span>ETB</span></div>
            <div class="s">@ {spot_price:,.0f} ETB/qt</div></div>
          <div class="kpi"><div class="t">Net profit</div>
            <div class="n {sign_cls(net_cash)}">{net_cash / 1e3:,.1f}k<span>ETB</span></div>
            <div class="s">ROI {roi:+.0f}%</div></div>
          <div class="kpi"><div class="t">Break-even yield</div>
            <div class="n">{breakeven:.2f}<span>t/ha</span></div>
            <div class="s">{(pred_y / breakeven) if breakeven else 0:.1f}× covered</div></div>
        </div>
        """, unsafe_allow_html=True)

        prof = predictor.get_profile(reg_val, crop_val)
        st.markdown(f"""
        <div class="card"><div class="bench">
          <div>
            <div class="card-title">Against surveyed {crop_val.lower()} plots in {reg_val}</div>
            <div class="sub">{int(prof["n_plots"]):,} plots, 2021–2024</div>
            {gauge_html(pred_y, prof["yield_p10"], prof["yield_p50"], prof["yield_p90"])}
          </div>
          <div>
            <div class="card-title">Season looked up</div>
            <div class="sub">{reg_val} · planted {month_val} {year_val} · 4-month window</div>
            <div class="conds" style="margin-top:10px">
              <div class="cond"><div class="l">Mean temp</div><div class="v">{cur["model_weather_season_mean_temp"]:.1f} °C</div></div>
              <div class="cond"><div class="l">vs normal</div><div class="v">{cur["model_weather_temp_anomaly_c"]:+.1f} °C</div></div>
              <div class="cond"><div class="l">Heat days</div><div class="v">{cur["model_weather_season_heat_days"]:.0f}</div></div>
              <div class="cond"><div class="l">Station rain</div><div class="v">{cur["model_weather_season_rainfall_mm"]:,.0f} mm</div></div>
              <div class="cond"><div class="l">Plot rain</div><div class="v">{cur["model_rainfall_mm_season"]:,.0f} mm</div></div>
              <div class="cond"><div class="l">Price</div><div class="v">{spot_price:,.0f}</div></div>
            </div>
          </div>
        </div></div>
        """, unsafe_allow_html=True)

        notes = [n for n, cond in (("area above 4.5 ha", farm_size > 4.5), ("fertilizer above 135 kg/ha", fert_val > 135)) if cond]
        if notes:
            st.caption(f":material/info: Outside the range of 98% of surveyed plots ({', '.join(notes)}). Treat with caution.")

        curve_bags = curve["total_quintals"].values
        curve_profits = curve["gross_revenue_birr"].values - ((steps * farm_size * c_fert_price) + cost_seed + cost_labor + cost_pest)
        opt_idx = int(np.argmax(curve_profits))
        opt_fert = int(steps[opt_idx])
        opt_gain = float(curve_profits[opt_idx] - net_cash)

        seed_rev = float(alt_seed["gross_revenue_birr"] - cur["gross_revenue_birr"])
        seed_pct = (float(alt_seed["predicted_yield_t_ha"]) / pred_y - 1) * 100 if pred_y > 0 else 0.0
        pest_rev = float(alt_pest["gross_revenue_birr"] - cur["gross_revenue_birr"])
        pest_pct = (float(alt_pest["predicted_yield_t_ha"]) / pred_y - 1) * 100 if pred_y > 0 else 0.0

        if seed_val == 1:
            seed_k, seed_pct, seed_rev = "Certified seed gain", -seed_pct, -seed_rev
        else:
            seed_k = "If certified seed"
        if pest_val == 1:
            pest_k = "If pests controlled"
        else:
            pest_k = "If pests strike"
        fert_v = (f"{opt_fert} kg/ha · +{opt_gain:,.0f} ETB" if opt_gain > 1 else f"{opt_fert} kg/ha · current")

        pnl_col, ins_col = st.columns([1, 1], gap="medium")
        with pnl_col:
            st.markdown(f"""<div class="card"><div class="card-title">Profit &amp; loss · {farm_size:g} ha</div>
              <div class="row"><span>Harvest value</span><span class="v pos">+{gross_sales:,.0f}</span></div>
              <div class="row"><span>Fertilizer · {fert_val * farm_size:,.0f} kg</span><span class="v neg">−{cost_fert:,.0f}</span></div>
              <div class="row"><span>Seed</span><span class="v {'neg' if cost_seed else ''}">{'−' if cost_seed else ''}{cost_seed:,.0f}</span></div>
              <div class="row"><span>Labor · {labor_val * farm_size:,.0f} days</span><span class="v neg">−{cost_labor:,.0f}</span></div>
              <div class="row"><span>Pest control</span><span class="v {'neg' if cost_pest else ''}">{'−' if cost_pest else ''}{cost_pest:,.0f}</span></div>
              <div class="row total"><span>Net cash (ETB)</span><span class="v {sign_cls(net_cash)}">{net_cash:,.0f}</span></div>
            </div>""", unsafe_allow_html=True)
        with ins_col:
            st.markdown(f"""<div class="card"><div class="card-title">What moves this plot</div>
              <div class="ins"><span class="k"><i style="background:{CANOPY}"></i>{seed_k}</span>
                <span class="v {sign_cls(seed_rev)}">{seed_pct:+.1f}% · {seed_rev:+,.0f} ETB</span></div>
              <div class="ins"><span class="k"><i style="background:{HARVEST}"></i>Best fertilizer rate</span>
                <span class="v gold">{fert_v}</span></div>
              <div class="ins"><span class="k"><i style="background:{BRICK}"></i>{pest_k}</span>
                <span class="v {sign_cls(pest_rev)}">{pest_pct:+.1f}% · {pest_rev:+,.0f} ETB</span></div>
              <div class="sub" style="margin-top:8px">Each figure is a separate model prediction for this exact plot.</div>
            </div>""", unsafe_allow_html=True)

        fig_sim = go.Figure()
        fig_sim.add_trace(go.Bar(x=steps, y=curve_bags, name="Harvest (bags)", marker_color="#CFE6D4",
                                 marker_line_width=0, yaxis="y1", hovertemplate="%{x} kg/ha · %{y:.0f} bags<extra></extra>"))
        fig_sim.add_trace(go.Scatter(x=steps, y=curve_profits, name="Net profit (ETB)", mode="lines+markers",
                                     line=dict(color=CANOPY, width=3), marker=dict(size=5), yaxis="y2",
                                     hovertemplate="%{x} kg/ha · %{y:,.0f} ETB<extra></extra>"))
        fig_sim.add_trace(go.Scatter(x=[opt_fert], y=[curve_profits[opt_idx]], mode="markers", name="Most profitable",
                                     marker=dict(size=13, color=HARVEST, line=dict(color="#fff", width=2)), yaxis="y2",
                                     hovertemplate="Peak %{x} kg/ha<extra></extra>"))
        fig_sim.add_vline(x=fert_val, line_width=1, line_dash="dot", line_color=MUTED,
                          annotation_text="now", annotation_position="top", annotation_font_color=MUTED)
        style_fig(fig_sim, 300)
        fig_sim.update_layout(
            title="Fertilizer response for this plot", bargap=0.35,
            xaxis=dict(title="Fertilizer (kg/ha)"),
            yaxis=dict(title="Bags", showgrid=False),
            yaxis2=dict(title="Net profit (ETB)", overlaying="y", side="right", gridcolor="#E6ECE6"),
        )
        st.plotly_chart(fig_sim, width="stretch")

# =============================================================================
# TAB 2: COOPERATIVE
# =============================================================================
def validate_portfolio(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Normalises an uploaded portfolio and drops rows the model cannot score."""
    errors = []
    missing = [c for c in PLOT_COLUMNS if c not in df.columns]
    if missing:
        return df.iloc[0:0], [f"Missing required columns: {', '.join(missing)}"]
    df = df.copy()
    if "plot_id" not in df.columns:
        df["plot_id"] = [f"PLOT-{i + 1:03d}" for i in range(len(df))]
    df["region"] = df["region"].astype(str).str.strip().map(lambda r: "SNNPR" if r.upper() == "SNNPR" else r.title())
    df["crop_type"] = df["crop_type"].astype(str).str.strip().str.lower()
    df["planting_month"] = df["planting_month"].astype(str).str.strip().str[:3].str.title()
    num_cols = [c for c in PLOT_COLUMNS if c not in ("region", "crop_type", "planting_month")]
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce")
    ok = (
        df["region"].isin(REGIONS) & df["crop_type"].isin([c.lower() for c in CROPS])
        & df["planting_month"].isin(list(MONTH_LABELS)) & df["survey_year"].isin([2021, 2022, 2023, 2024])
        & df[num_cols].notna().all(axis=1)
    )
    if (~ok).any():
        errors.append(
            f"{int((~ok).sum())} row(s) skipped: region, crop, planting month (Feb/Mar/Jun/Jul/Aug) or "
            f"season (2021–2024) not recognised, or a numeric value is missing."
        )
    return df[ok].reset_index(drop=True), errors


@st.cache_data(show_spinner=False)
def load_sample_portfolio() -> pd.DataFrame:
    return pd.read_csv(app_dir / "assets" / "coop_sample.csv")


with t_coop:
    st.markdown("### Cooperative portfolio")
    sample_df = load_sample_portfolio()
    src_col, dl_col = st.columns([3, 1])
    with src_col:
        source = st.segmented_control(
            "Plots", [f"{len(sample_df)} sample plots (2024, unseen)", "Upload CSV"],
            default=f"{len(sample_df)} sample plots (2024, unseen)", label_visibility="collapsed",
        )
    with dl_col:
        st.download_button(
            "CSV template", sample_df.to_csv(index=False).encode("utf-8"), icon=":material/download:",
            file_name="cooperative_portfolio_template.csv", mime="text/csv", width="stretch",
        )

    portfolio, issues = sample_df, []
    if source == "Upload CSV":
        up = st.file_uploader("Portfolio CSV (same columns as the template)", type=["csv"])
        if up is None:
            st.info("Upload a CSV to score your own plots. The sample portfolio is shown until then.")
        else:
            try:
                portfolio, issues = validate_portfolio(pd.read_csv(up))
            except Exception as exc:  # malformed file
                portfolio, issues = sample_df.iloc[0:0], [f"Could not read file: {exc}"]
    for msg in issues:
        st.warning(msg)

    if portfolio.empty:
        st.error("No valid plots to score. Check the file against the CSV template.")
    else:
        batch_res = predictor.predict_batch(portfolio)
        c_tons = batch_res["total_harvest_tons"].sum()
        c_val = batch_res["gross_revenue_birr"].sum()
        credit_needed = (
            batch_res["fertilizer_kg_per_ha"] * batch_res["farm_size_ha"] * 42.0
            + batch_res["improved_seed_used"] * batch_res["farm_size_ha"] * 4800.0
        ).sum()
        ltv = (credit_needed / c_val * 100.0) if c_val > 0 else 0.0

        info = dict(delta_color="off", delta_arrow="off")  # descriptive sub-labels, not changes
        cm1, cm2, cm3, cm4 = st.columns(4)
        cm1.metric("Grain output", f"{c_tons:.1f} t", f"{len(batch_res)} plots · {batch_res['farm_size_ha'].sum():.1f} ha", **info)
        cm2.metric("Storage", f"{c_tons * 10:,.0f} bags", "100 kg each", **info)
        cm3.metric("Transport", f"{max(1, int(np.ceil(c_tons / 40.0)))} trucks", "40 t loads", **info)
        cm4.metric("Harvest value", f"{c_val / 1e6:.2f}M ETB", f"input credit {ltv:.1f}% of value", **info)

        cc1, cc2 = st.columns(2, gap="medium")
        with cc1:
            by_crop = batch_res.groupby("crop_type")["total_harvest_tons"].sum().sort_values().reset_index()
            by_crop["crop_type"] = by_crop["crop_type"].str.title()
            f_crop = px.bar(by_crop, x="total_harvest_tons", y="crop_type", orientation="h", title="Harvest by crop (t)",
                            labels={"total_harvest_tons": "Tons", "crop_type": ""}, text_auto=".1f")
            f_crop.update_traces(marker_color=CANOPY, textfont_family="IBM Plex Mono", textposition="outside", cliponaxis=False)
            style_fig(f_crop, 280).update_xaxes(range=[0, by_crop["total_harvest_tons"].max() * 1.18])
            st.plotly_chart(f_crop, width="stretch")
        with cc2:
            by_reg = batch_res.groupby("region")["gross_revenue_birr"].sum().reset_index()
            f_reg = px.pie(by_reg, names="region", values="gross_revenue_birr", title="Harvest value by region",
                           hole=0.62, color_discrete_sequence=GREENS)
            f_reg.update_traces(textinfo="percent", textfont_family="IBM Plex Mono", marker_line=dict(color="#fff", width=2), sort=False)
            style_fig(f_reg, 280).update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02))
            st.plotly_chart(f_reg, width="stretch")

        show_cols = ["plot_id", "region", "crop_type", "planting_month", "farm_size_ha",
                     "predicted_yield_t_ha", "total_harvest_tons", "gross_revenue_birr"]
        nice = {
            "plot_id": "Plot", "region": "Region", "crop_type": "Crop", "planting_month": "Planted",
            "farm_size_ha": "Area (ha)", "predicted_yield_t_ha": "Yield (t/ha)",
            "total_harvest_tons": "Harvest (t)", "gross_revenue_birr": "Value (ETB)",
        }
        table = batch_res[show_cols].assign(crop_type=batch_res["crop_type"].str.title()).rename(columns=nice)
        st.dataframe(
            table, width="stretch", hide_index=True,
            column_config={
                "Area (ha)": st.column_config.NumberColumn(format="%.2f"),
                "Yield (t/ha)": st.column_config.ProgressColumn(format="%.2f", min_value=0.0, max_value=float(max(6.0, table["Yield (t/ha)"].max()))),
                "Harvest (t)": st.column_config.NumberColumn(format="%.2f"),
                "Value (ETB)": st.column_config.NumberColumn(format="localized"),
            },
        )
        st.download_button(
            "Download forecasts", batch_res[show_cols].to_csv(index=False).encode("utf-8"), icon=":material/download:",
            file_name="cooperative_forecast.csv", mime="text/csv",
        )
        st.caption("Input credit uses default costs: 42 ETB/kg fertilizer, 4,800 ETB/ha certified seed.")

# =============================================================================
# TAB 3: CLIMATE STRESS
# =============================================================================
SCENARIOS = {
    "Heatwave · +2.25 °C, +5 heat days": {"temp_delta": 2.25, "heat_days_add": 5.0},
    "Drought · −35% rain": {"rain_mult": 0.65},
    "Fertilizer price · +50%": None,
}


@st.cache_data(show_spinner=False)
def stress_test(region: str, crop: str, scenario: str) -> dict:
    """Runs the model on real surveyed plots of this region x crop, with and without the shock."""
    panel = pd.read_csv(app_dir / "assets" / "stress_panel.csv")
    plots = panel[(panel["region"] == region) & (panel["crop_type"] == crop.lower())]
    base = predictor.predict_batch(plots)
    shock = predictor.predict_batch(plots, weather_overrides=SCENARIOS[scenario]) if SCENARIOS[scenario] else base
    return {
        "n": len(plots),
        "base_y": float(base["predicted_yield_t_ha"].mean()),
        "shock_y": float(shock["predicted_yield_t_ha"].mean()),
        "share_hit": float((shock["predicted_yield_t_ha"].values < base["predicted_yield_t_ha"].values - 0.05).mean()),
        "fert": float(plots["fertilizer_kg_per_ha"].median()),
        "temp": (float(base["model_weather_season_mean_temp"].mean()), float(shock["model_weather_season_mean_temp"].mean())),
        "rain": (float(base["model_weather_season_rainfall_mm"].mean()), float(shock["model_weather_season_rainfall_mm"].mean())),
        "heat": (float(base["model_weather_season_heat_days"].mean()), float(shock["model_weather_season_heat_days"].mean())),
    }


with t_climate:
    st.markdown("### Climate stress test")
    st.caption("The model is re-run with shocked season weather on real surveyed plots, then scaled to your farm.")

    cs_sel = st.segmented_control("Scenario", list(SCENARIOS), default=list(SCENARIOS)[0], key="c_scen")
    cs_sel = cs_sel or list(SCENARIOS)[0]
    c_b1, c_b2, c_b3 = st.columns(3)
    c_crop = c_b1.selectbox("Crop", CROPS, key="c_crop")
    c_reg = c_b2.selectbox("Region", REGIONS, key="c_reg")
    c_ha = c_b3.slider("Farm area (ha)", 0.5, 4.0, 2.0, step=0.5, key="c_ha")

    stt = stress_test(c_reg, c_crop, cs_sel)
    price = predictor.get_market_price(c_reg, c_crop, 2024)
    b_y, s_y = stt["base_y"], stt["shock_y"]
    b_bags, s_bags = b_y * c_ha * 10.0, s_y * c_ha * 10.0
    b_val, s_val = b_bags * price, s_bags * price
    base_cost = stt["fert"] * c_ha * 42.0
    shock_cost = stt["fert"] * c_ha * 42.0 * (1.5 if SCENARIOS[cs_sel] is None else 1.0)
    loss = (b_val - base_cost) - (s_val - shock_cost)
    pct = (s_y / b_y - 1) * 100 if b_y > 0 else 0.0

    m_s1, m_s2, m_s3 = st.columns(3)
    m_s1.metric("Normal season", f"{b_bags:.0f} bags", f"{b_y:.2f} t/ha", delta_color="off", delta_arrow="off")
    m_s2.metric("Under stress", f"{s_bags:.0f} bags", f"{s_y - b_y:+.2f} t/ha ({pct:+.1f}%)")
    m_s3.metric("Net income change", f"{-loss:+,.0f} ETB", f"{-loss / max(b_val - base_cost, 1) * 100:+.1f}% of normal")

    if SCENARIOS[cs_sel]:
        if abs(pct) < 2.0:
            st.info(f"Little net effect for {c_crop.lower()} in {c_reg}: gains and losses offset across plots "
                    f"({stt['share_hit']:.0%} of plots lose yield).", icon=":material/balance:")
        elif pct >= 2.0:
            st.info(f"{c_crop} in {c_reg} gains here. Warm-season crops in cool highlands benefit from warmer seasons; "
                    "cool-season crops (wheat, barley, teff) lose.", icon=":material/trending_up:")

        st.caption(
            f"{stt['n']} surveyed plots · {stt['temp'][0]:.1f} → {stt['temp'][1]:.1f} °C · "
            f"{stt['rain'][0]:,.0f} → {stt['rain'][1]:,.0f} mm · {stt['heat'][0]:.1f} → {stt['heat'][1]:.1f} heat days"
        )

        impact = pd.DataFrame([
            {"Crop": c, "Change": (lambda r: (r["shock_y"] / r["base_y"] - 1) * 100)(stress_test(c_reg, c, cs_sel))}
            for c in CROPS
        ]).sort_values("Change")
        f_imp = go.Figure(go.Bar(
            x=impact["Change"], y=impact["Crop"], orientation="h",
            marker_color=[BRICK if v < 0 else CANOPY for v in impact["Change"]],
            marker_line=dict(color=[HARVEST if c == c_crop else "rgba(0,0,0,0)" for c in impact["Crop"]], width=3),
            text=[f"{v:+.1f}%" for v in impact["Change"]], textposition="outside", cliponaxis=False,
            textfont=dict(family="IBM Plex Mono"), hovertemplate="%{y}: %{x:+.1f}%<extra></extra>",
        ))
        style_fig(f_imp, 250)
        lo, hi = min(impact["Change"].min(), 0), max(impact["Change"].max(), 0)
        span = max(hi - lo, 1.0)
        f_imp.update_layout(title=f"Yield change by crop in {c_reg}",
                            xaxis=dict(ticksuffix="%", zeroline=True, zerolinecolor=MUTED,
                                       range=[lo - 0.35 * span, hi + 0.35 * span]))
        st.plotly_chart(f_imp, width="stretch")
    else:
        st.caption(f"Yield is unchanged. Fertilizer for the median {stt['fert']:.0f} kg/ha on {c_ha:g} ha rises "
                   f"from {base_cost:,.0f} to {shock_cost:,.0f} ETB.")

    need_col, food_col = st.columns([1, 2.6], gap="medium")
    need_q = need_col.number_input("Household need (bags/year)", 1.0, 60.0, 12.0, step=1.0,
                                   help="Planning assumption for annual household grain consumption")
    ok_food = s_bags >= need_q
    food_col.markdown(f"""
    <div class="card" style="border-left: 4px solid {CANOPY if ok_food else BRICK};">
      <div class="ins"><span class="k">Household food security under this scenario</span>
        <span class="v {'pos' if ok_food else 'neg'}">{s_bags:.0f} of {need_q:.0f} bags · {'covered' if ok_food else 'shortfall'}</span></div>
      <div class="sub">{'Surplus available to sell.' if ok_food else 'Below the subsistence floor: a candidate for safety-net or index-insurance support.'}</div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# TAB 4: MODEL AUDIT
# =============================================================================
REQUIRED_FIGS = [
    "fig01_missingness.png", "fig02_before_after_cleaning.png", "fig03_yield_distribution.png",
    "fig04_region_crop_heatmap.png", "fig05_correlation_heatmap.png", "fig06_climate_by_region.png",
    "fig07_yield_vs_season_temp.png", "fig08_price_trends.png", "fig09_revenue_by_crop_region.png",
    "fig10_model_comparison.png", "fig11_predicted_vs_actual_residuals.png", "fig12_feature_importance.png",
]


@st.cache_data(show_spinner=False)
def run_compliance_checks() -> list[dict]:
    checks = []
    feats = predictor.feature_names
    weather_feats = [f for f in feats if f.startswith("weather_")]
    checks.append({"Check": "Model uses weather-derived features (Rule 5)", "Result": f"✅ {len(weather_feats)} weather features" if weather_feats else "❌ none"})
    checks.append({"Check": "Market price excluded from model inputs", "Result": "✅ excluded" if "price_birr_per_quintal" not in feats else "❌ price is a feature"})

    sub_p = project_dir / "submission" / "team_11_submission.csv"
    tpl_p = project_dir / "data" / "raw" / "submission_template.csv"
    test_p = project_dir / "data" / "processed" / "master_test.csv"
    if sub_p.exists() and tpl_p.exists():
        sub, tpl = pd.read_csv(sub_p), pd.read_csv(tpl_p)
        ok = list(sub.columns) == list(tpl.columns) and len(sub) == len(tpl) and (sub["plot_id"] == tpl["plot_id"]).all() and sub.notna().all().all()
        checks.append({"Check": "Submission matches template (rows, columns, order, no nulls)", "Result": f"✅ {len(sub):,} rows" if ok else "❌ mismatch"})
        if test_p.exists():
            test = pd.read_csv(test_p)
            app_pred = predictor.predict_batch(test[PLOT_COLUMNS + ["rainfall_mm_season"]])["predicted_yield_t_ha"].values
            diff = float(np.abs(app_pred - sub.iloc[:, 1].values).max())
            checks.append({"Check": "App reproduces every submitted prediction", "Result": f"✅ max diff {diff:.4f} t/ha" if diff < 1e-2 else f"❌ max diff {diff:.3f} t/ha"})
    else:
        checks.append({"Check": "Submission file", "Result": "ℹ️ not bundled with this deployment"})

    fig_dir = project_dir / "figures" if (project_dir / "figures").exists() else app_dir / "assets" / "figures"
    n_figs = sum((fig_dir / f).exists() for f in REQUIRED_FIGS)
    checks.append({"Check": "12 required figures present", "Result": f"{'✅' if n_figs == 12 else '❌'} {n_figs}/12"})
    return checks


with t_audit:
    st.markdown("### Model audit")
    st.caption("All metrics are 5-fold out-of-fold: every plot is scored by a model that never saw it.")

    oot = M.get("out_of_time", {})
    weather_gain = (CV.get("no_weather_rmse", 0) / CV.get("rmse", 1) - 1) * 100 if CV else 0
    info = dict(delta_color="off", delta_arrow="off")
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("CV error (RMSE)", f"{CV.get('rmse', 0):.3f} t/ha", f"MAE {CV.get('mae', 0):.3f}", **info)
    a2.metric("Variance explained", f"{CV.get('r2', 0):.1%}", f"baseline error {CV.get('baseline_mean_rmse', 0):.2f} t/ha", **info)
    a3.metric("Future season test", f"{oot.get('rmse', 0):.3f} t/ha", f"train 2021–23 → test {oot.get('test_year', '')}", **info)
    a4.metric("Without weather", f"{CV.get('no_weather_rmse', 0):.3f} t/ha", f"+{weather_gain:.1f}% error", delta_color="inverse")

    cm = np.array(TIERS.get("confusion_matrix", [[0] * 3] * 3))
    n_total = int(cm.sum()) or 1
    st.markdown("#### Food-security tiers")
    cm_l, cm_r = st.columns([1, 1.7], gap="medium")
    with cm_l:
        st.markdown(f"""<div class="card">
          <div class="ins"><span class="k">Plots in their true tier</span><span class="v pos">{TIERS.get("accuracy", 0):.1%}</span></div>
          <div class="ins"><span class="k">Subsistence precision</span><span class="v">{TIERS.get("subsistence_precision", 0):.1%}</span></div>
          <div class="ins"><span class="k">Subsistence recall</span><span class="v">{TIERS.get("subsistence_recall", 0):.1%}</span></div>
          <div class="ins"><span class="k">Subsistence ↔ commercial mix-ups</span><span class="v">{TIERS.get("extreme_errors", 0)} of {n_total:,}</span></div>
          <div class="sub" style="margin-top:8px">Tiers: subsistence &lt;2.0, standard 2.0–3.5, commercial &gt;3.5 t/ha.</div>
        </div>""", unsafe_allow_html=True)
    with cm_r:
        row_pct = cm / np.maximum(cm.sum(axis=1, keepdims=True), 1) * 100
        t_labels = ["Subsistence", "Standard", "Commercial"]
        fig_cm = go.Figure(go.Heatmap(
            z=row_pct, x=t_labels, y=t_labels, zmin=0, zmax=100, showscale=False,
            text=[[f"{cm[i, j]:,}<br>{row_pct[i, j]:.1f}%" for j in range(3)] for i in range(3)],
            texttemplate="%{text}", textfont=dict(family="IBM Plex Mono", size=12),
            colorscale=[[0, "#F6F9F6"], [0.35, "#D8EBDC"], [1.0, "#86C79A"]],
            hovertemplate="Actual %{y} → predicted %{x}<extra></extra>",
        ))
        style_fig(fig_cm, 290)
        fig_cm.update_layout(title="Actual vs predicted tier", xaxis=dict(title="Predicted", showgrid=False),
                             yaxis=dict(title="Actual", autorange="reversed", showgrid=False))
        st.plotly_chart(fig_cm, width="stretch")

    with st.expander("Error by crop and region"):
        e1, e2 = st.columns(2)
        for col, key, label in ((e1, "by_crop", "Crop"), (e2, "by_region", "Region")):
            tbl = pd.DataFrame(M.get(key, {})).T.reset_index().rename(columns={
                "index": label, "rmse": "RMSE (t/ha)", "mae": "MAE (t/ha)", "mean_yield": "Mean yield (t/ha)", "n": "Plots"})
            if label == "Crop":
                tbl[label] = tbl[label].str.title()
            col.dataframe(tbl, hide_index=True, width="stretch")

    st.markdown("#### Figures")
    fig_dir = project_dir / "figures" if (project_dir / "figures").exists() else app_dir / "assets" / "figures"
    fig_opts = {
        "fig13_yield_tier_confusion_matrix.png": "Figure 13 · Food-security tier confusion matrix",
        "fig10_model_comparison.png": "Figure 10 · Model comparison",
        "fig11_predicted_vs_actual_residuals.png": "Figure 11 · Predicted vs actual & residuals",
        "fig12_feature_importance.png": "Figure 12 · Feature importance",
        "fig04_region_crop_heatmap.png": "Figure 4 · Yield by region × crop",
        "fig06_climate_by_region.png": "Figure 6 · Climate by region",
        "fig08_price_trends.png": "Figure 8 · Price trends 2021–2024",
        "fig09_revenue_by_crop_region.png": "Figure 9 · Revenue per hectare",
    }
    fig_sel = st.selectbox("Figure", list(fig_opts), format_func=fig_opts.get, label_visibility="collapsed")
    p_fig = fig_dir / fig_sel
    if not p_fig.exists():
        p_fig = app_dir / "assets" / "figures" / fig_sel
    if p_fig.exists():
        _, img_col, _ = st.columns([1, 3, 1])
        img_col.image(str(p_fig), caption=fig_opts[fig_sel], width="stretch")
    else:
        st.info("This figure is not bundled with the deployment.")

    st.markdown("#### Compliance checks")
    st.dataframe(pd.DataFrame(run_compliance_checks()), hide_index=True, width="stretch")

st.markdown(f"""
<div class="footer">
  <span>Team 11 · Qiyas / IADE AI Hackathon 2026 · Addis Ababa University</span>
  <span class="mono">Survey, weather &amp; price tables 2021–2024 · build {build_id()}</span>
</div>
""", unsafe_allow_html=True)
