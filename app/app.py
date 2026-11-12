import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import base64

# Ensure local app module imports work
app_dir = Path(__file__).resolve().parent
project_dir = app_dir.parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

from predictor import CropYieldPredictor

# Page Configuration - Must be first Streamlit command
st.set_page_config(
    page_title="AgriYield™ Pro — Ethiopian Smallholder Intelligence",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# HIGH PERFORMANCE CACHING (PREVENTS SCREEN FREEZE & LAG)
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_cached_hero_bg():
    p = app_dir / "assets" / "hero_bg.jpg"
    if p.exists():
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

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

# -----------------------------------------------------------------------------
# LUXURY SAAS STYLESHEET (GLASSMORPHISM, MICRO-ANIMATIONS, CRISP CONTRAST)
# -----------------------------------------------------------------------------
hero_bg_css = f"background: linear-gradient(135deg, rgba(6, 30, 18, 0.88) 0%, rgba(10, 38, 24, 0.78) 50%, rgba(15, 23, 42, 0.90) 100%), url('data:image/jpeg;base64,{hero_bg_b64}') no-repeat center center; background-size: cover;" if hero_bg_b64 else "background: linear-gradient(135deg, #064e3b 0%, #065f46 50%, #047857 100%);"

css = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@600;700;800&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #0f172a;
    }}
    
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1320px !important;
    }}
    
    /* Header removal */
    header[data-testid="stHeader"], header {{
        display: none !important;
    }}
    
    /* Live Pulsing Dot Animation */
    @keyframes live-pulse {{
        0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }}
        70% {{ transform: scale(1.15); box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }}
        100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }}
    }}
    .pulse-indicator {{
        width: 8px;
        height: 8px;
        background: #22c55e;
        border-radius: 50%;
        display: inline-block;
        animation: live-pulse 2s infinite;
        margin-right: 6px;
    }}
    
    /* Executive Top Bar */
    .top-app-bar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 10px 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 10px -2px rgba(0,0,0,0.03);
    }}
    .brand-title {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.25rem;
        font-weight: 800;
        color: #064e3b;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .live-status-pill {{
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #166534;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 9999px;
        display: flex;
        align-items: center;
    }}
    
    /* Market Ticker Strip */
    .ticker-container {{
        background: #0f172a;
        color: #94a3b8;
        padding: 8px 18px;
        border-radius: 12px;
        font-size: 0.78rem;
        display: flex;
        gap: 16px;
        overflow-x: auto;
        white-space: nowrap;
        margin-bottom: 16px;
        border: 1px solid rgba(255,255,255,0.08);
    }}
    .ticker-item {{
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }}
    .ticker-val {{
        color: #f8fafc;
        font-weight: 700;
    }}
    .ticker-tag {{
        color: #4ade80;
        font-weight: 700;
        font-size: 0.72rem;
    }}
    
    /* Super Cool Hero Section */
    .hero-box {{
        {hero_bg_css}
        border-radius: 22px;
        padding: 38px 36px;
        color: #ffffff;
        box-shadow: 0 12px 30px -6px rgba(6, 78, 59, 0.28);
        margin-bottom: 22px;
        position: relative;
    }}
    .hero-badge {{
        background: rgba(255, 255, 255, 0.16);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.25);
        color: #a7f3d0;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 9999px;
        display: inline-block;
        margin-bottom: 12px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }}
    .hero-h1 {{
        font-family: 'Outfit', sans-serif;
        font-size: 2.35rem;
        font-weight: 800;
        line-height: 1.15;
        letter-spacing: -0.02em;
        margin-bottom: 8px;
    }}
    .hero-sub {{
        font-size: 0.98rem;
        color: #e2e8f0;
        max-width: 760px;
        line-height: 1.5;
        margin-bottom: 20px;
    }}
    .hero-stat-row {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
    }}
    .hero-stat-card {{
        background: rgba(255, 255, 255, 0.10);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 14px;
        padding: 12px 14px;
        text-align: center;
        transition: transform 0.2s ease;
    }}
    .hero-stat-card:hover {{
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.15);
    }}
    .hero-stat-num {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1;
    }}
    .hero-stat-desc {{
        font-size: 0.72rem;
        color: #cbd5e1;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }}

    /* Card Surfaces */
    .saas-card {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 20px 22px;
        box-shadow: 0 4px 16px -2px rgba(0,0,0,0.03);
        margin-bottom: 16px;
    }}
    
    /* Modern KPI Metric Tiles */
    .kpi-tile {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 4px 14px -2px rgba(0,0,0,0.03);
        position: relative;
        overflow: hidden;
    }}
    .kpi-tile-top {{
        font-size: 0.74rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 4px;
    }}
    .kpi-tile-num {{
        font-family: 'Outfit', sans-serif;
        font-size: clamp(1.25rem, 1.9vw, 1.95rem);
        font-weight: 800;
        line-height: 1.1;
        white-space: nowrap;
    }}
    .kpi-tile {{ min-height: 128px; }}
    .card-title {{
        font-weight: 800; font-size: 0.95rem; color: #0f172a; margin-bottom: 4px;
    }}
    .kpi-tile-badge {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.76rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 9999px;
        margin-top: 6px;
    }}
    
    /* P&L Flow Row */
    .pnl-strip {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #f1f5f9;
        font-size: 0.88rem;
    }}
    .pnl-strip-bold {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0 4px 0;
        font-size: 1.05rem;
        font-weight: 800;
        border-top: 2px solid #0f172a;
        margin-top: 6px;
    }}

    /* Action Chips */
    .action-chip {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #10b981;
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 0.85rem;
        color: #1e293b;
        line-height: 1.45;
    }}
    
    /* Streamlit Tabs Customization */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: #f1f5f9;
        padding: 6px;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 10px;
        padding: 8px 18px;
        font-weight: 700;
        font-size: 0.88rem;
        color: #475569;
        background: transparent;
        border: none !important;
        transition: all 0.15s ease;
    }}
    .stTabs [aria-selected="true"] {{
        background: #ffffff !important;
        color: #064e3b !important;
        box-shadow: 0 4px 10px -2px rgba(0,0,0,0.06);
    }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

M = predictor.metrics
CV = M.get("cv", {})
TIERS = M.get("tiers", {})
CROP_ICONS = {"teff": "🌾", "wheat": "🍞", "maize": "🌽", "barley": "🍺", "sorghum": "🌾"}
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
# 1. TOP APP BAR & MARKET PRICE STRIP (computed from cleaned price table)
# -----------------------------------------------------------------------------
price_year, ticker_rows = price_ticker()
ticker_html = "".join(
    f'<span class="ticker-item">{CROP_ICONS.get(c, "🌾")} {c.title()}: '
    f'<span class="ticker-val">{v:,.0f} ETB/qt</span> '
    f'<span class="ticker-tag" style="color: {"#4ade80" if d >= 0 else "#f87171"};">{"▲" if d >= 0 else "▼"} {d:+.0f}%</span></span>'
    for c, v, d in ticker_rows
)
st.markdown(f"""
<div class="top-app-bar">
    <div class="brand-title">
        <span>🌱</span> AgriYield™ Pro <span style="font-size: 0.75rem; background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 6px; font-weight: 700;">ENTERPRISE</span>
    </div>
    <div style="display: flex; gap: 10px; align-items: center;">
        <div class="live-status-pill">
            <span class="pulse-indicator"></span> Production ML Model Active · CV RMSE {CV.get("rmse", 0):.2f} t/ha
        </div>
        <div style="font-size: 0.75rem; color: #64748b; font-weight: 600;">
            Team 11 · {M.get("n_train_plots", 0):,} Survey Plots · build {build_id()}
        </div>
    </div>
</div>

<div class="ticker-container">
    <span style="font-weight: 800; color: #f8fafc;">📈 MARKET PRICE REFERENCE · {price_year} NATIONAL AVG (YoY):</span>
    {ticker_html}
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. HIGH-IMPACT HERO BANNER (all figures from 5-fold out-of-fold evaluation)
# -----------------------------------------------------------------------------
weather_gain = (CV.get("no_weather_rmse", 0) / CV.get("rmse", 1) - 1) * 100 if CV else 0
st.markdown(f"""
<div class="hero-box">
    <div class="hero-badge">Smallholder Yield, Income & Regional Food Security</div>
    <div class="hero-h1">Precision Harvest Intelligence for Ethiopia</div>
    <div class="hero-sub">
        Pre-season yield and revenue forecasts for extension agents, cooperatives and planners across
        Oromia, Amhara, SNNPR, Tigray, and Somali, combining plot surveys with seasonal weather and market prices.
    </div>
    <div class="hero-stat-row">
        <div class="hero-stat-card">
            <div class="hero-stat-num">{M.get("n_train_plots", 0):,}</div>
            <div class="hero-stat-desc">Survey Plots Learned</div>
        </div>
        <div class="hero-stat-card">
            <div class="hero-stat-num">{CV.get("r2", 0):.1%}</div>
            <div class="hero-stat-desc">Yield Variance Explained</div>
        </div>
        <div class="hero-stat-card">
            <div class="hero-stat-num">±{CV.get("rmse", 0):.2f} t/ha</div>
            <div class="hero-stat-desc">Cross-Validated Error</div>
        </div>
        <div class="hero-stat-card">
            <div class="hero-stat-num">{TIERS.get("accuracy", 0):.1%}</div>
            <div class="hero-stat-desc">Food-Security Tier Accuracy</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. WORKSPACES (STREAMLINED 4-TAB NAVIGATION)
# -----------------------------------------------------------------------------
t_appraisal, t_coop, t_climate, t_governance = st.tabs([
    "🌾 Farmgate Profit Studio",
    "🏢 Cooperative Command Hub",
    "🛡️ Climate Stress Radar",
    "📊 System Audit & Confusion Matrix"
])

# =============================================================================
# TAB 1: FARMGATE PROFIT STUDIO
# =============================================================================
PRESETS = {
    "maize":   {"region": "Oromia", "crop": "Maize",   "size": 2.5, "alt": 1850, "fert": 85, "seed": 1, "labor": 45, "pest": 0, "sqi": 0.75, "month": "Jun"},
    "teff":    {"region": "Amhara", "crop": "Teff",    "size": 1.5, "alt": 2100, "fert": 45, "seed": 1, "labor": 40, "pest": 0, "sqi": 0.70, "month": "Jul"},
    "wheat":   {"region": "Oromia", "crop": "Wheat",   "size": 3.0, "alt": 2350, "fert": 90, "seed": 1, "labor": 50, "pest": 0, "sqi": 0.80, "month": "Jun"},
    "barley":  {"region": "Tigray", "crop": "Barley",  "size": 1.2, "alt": 2450, "fert": 50, "seed": 1, "labor": 35, "pest": 0, "sqi": 0.65, "month": "Jul"},
    "sorghum": {"region": "Somali", "crop": "Sorghum", "size": 2.0, "alt": 1200, "fert": 25, "seed": 0, "labor": 25, "pest": 0, "sqi": 0.50, "month": "Mar"},
}
SEED_OPTS = ["🌾 Traditional Farm-Saved", "✨ Certified Improved Seed"]


def apply_preset(name: str) -> None:
    p = PRESETS[name]
    st.session_state.update({
        "f_region": p["region"], "f_crop": p["crop"], "f_size": float(p["size"]), "f_month": p["month"],
        "f_fert": int(p["fert"]), "f_seed": SEED_OPTS[p["seed"]], "f_labor": int(p["labor"]),
        "f_pest": bool(p["pest"]), "f_alt": int(p["alt"]), "f_sqi": float(p["sqi"]), "f_year": 2024,
        "f_rain_override": False,
    })


if "f_region" not in st.session_state:
    apply_preset("maize")

with t_appraisal:
    st.markdown("**⚡ 1-Click Regional Presets:**")
    p_cols = st.columns(5)
    for col, (key, label) in zip(p_cols, [
        ("maize", "🌽 Arsi Maize (2.5 ha)"), ("teff", "🌾 Gojjam Teff (1.5 ha)"), ("wheat", "🍞 Bale Wheat (3.0 ha)"),
        ("barley", "🍺 Tigray Barley (1.2 ha)"), ("sorghum", "🌾 Somali Sorghum (2.0 ha)"),
    ]):
        col.button(label, width="stretch", on_click=apply_preset, args=(key,))

    col_deck, col_display = st.columns([1.1, 1.9], gap="medium")

    with col_deck, st.container(border=True):
        st.markdown('<div class="card-title">📋 Plot Characteristics</div>', unsafe_allow_html=True)

        d1, d2 = st.columns(2)
        with d1:
            reg_val = st.selectbox("Region", REGIONS, key="f_region")
        with d2:
            crop_val = st.selectbox("Crop", CROPS, key="f_crop")

        d3, d4, d5 = st.columns([1.1, 1, 0.9])
        with d3:
            farm_size = st.number_input("Hectares", min_value=0.2, max_value=6.0, step=0.1, key="f_size")
            st.caption(f"≈ **{farm_size * 4:.1f} Timad**")
        with d4:
            month_val = st.selectbox("Planting Month", list(MONTH_LABELS), format_func=MONTH_LABELS.get, key="f_month")
        with d5:
            year_val = st.selectbox("Season", [2024, 2023, 2022, 2021], key="f_year")

        fert_val = st.slider("Fertilizer DAP/Urea (kg/ha)", 0, 160, step=5, key="f_fert")

        seed_opt = st.radio("Seed Source", SEED_OPTS, key="f_seed")
        seed_val = 1 if seed_opt == SEED_OPTS[1] else 0

        labor_val = st.slider("Labor (days/ha)", 10, 100, step=5, key="f_labor")

        p_risk = st.checkbox("⚠️ Pest / Disease Pressure Observed", key="f_pest")
        pest_val = 1 if p_risk else 0

        with st.expander("Agro-Ecological Fine Tuning"):
            alt_val = st.slider("Altitude (m)", 500, 3100, step=50, key="f_alt")
            sqi_val = st.slider("Soil Quality Index", 0.05, 1.0, step=0.05, key="f_sqi")
            typical_rain = predictor.get_typical_plot_rainfall(reg_val, year_val, month_val)
            rain_override = st.checkbox("Enter plot-reported season rainfall", key="f_rain_override")
            if rain_override:
                plot_rain = st.number_input("Plot-reported rainfall (mm)", 100.0, 4000.0, float(typical_rain), step=25.0)
            else:
                plot_rain = typical_rain
                st.caption(f"Using the median reported by surveyed plots in {reg_val}, {month_val} {year_val}: **{typical_rain:,.0f} mm**")

        with st.expander("Input Cost Assumptions (ETB)"):
            st.caption("Planning assumptions for the profit view only; edit to local prices. They do not affect the yield prediction.")
            c_fert_price = st.number_input("Fertilizer price (ETB/kg)", 0.0, 500.0, 42.0, step=1.0)
            c_labor_price = st.number_input("Labor wage (ETB/day)", 0.0, 2000.0, 280.0, step=10.0)
            c_seed_price = st.number_input("Certified seed (ETB/ha)", 0.0, 50000.0, 4800.0, step=100.0)
            c_pest_price = st.number_input("Pest control (ETB/ha, if pressure)", 0.0, 20000.0, 2400.0, step=100.0)

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
        scenario_rows = [in_dict, dict(in_dict, improved_seed_used=1 - seed_val), dict(in_dict, pest_disease_flag=1 - pest_val)]
        scenario_rows += [dict(in_dict, fertilizer_kg_per_ha=int(f)) for f in steps]
        batch = predictor.predict_batch(pd.DataFrame(scenario_rows))
        cur, alt_seed, alt_pest, curve = batch.iloc[0], batch.iloc[1], batch.iloc[2], batch.iloc[3:]

        pred_y = float(cur["predicted_yield_t_ha"])
        tot_tons = float(cur["total_harvest_tons"])
        tot_bags = float(cur["total_quintals"])
        spot_price = float(cur["price_birr_per_quintal"])
        gross_sales = float(cur["gross_revenue_birr"])
        crop_err = M.get("by_crop", {}).get(crop_val.lower(), {}).get("rmse", CV.get("rmse", 0))

        # Costs (planning assumptions)
        cost_fert = fert_val * farm_size * c_fert_price
        cost_seed = farm_size * (c_seed_price if seed_val == 1 else 0.0)
        cost_labor = labor_val * farm_size * c_labor_price
        cost_pest = farm_size * (c_pest_price if pest_val == 1 else 0.0)
        tot_costs = cost_fert + cost_seed + cost_labor + cost_pest
        net_cash = gross_sales - tot_costs
        roi = (net_cash / tot_costs * 100.0) if tot_costs > 0 else 0.0
        breakeven = (tot_costs / (farm_size * 10.0 * spot_price)) if (farm_size * spot_price > 0) else 0.0

        # KPI Tiles
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f"""<div class="kpi-tile" style="border-top: 4px solid #10b981;">
            <div class="kpi-tile-top">Expected Harvest</div>
            <div class="kpi-tile-num" style="color: #064e3b;">{tot_bags:.0f} <span style="font-size: 0.85rem; color: #64748b; font-weight: 500;">Bags</span></div>
            <div class="kpi-tile-badge" style="background: #f0fdf4; color: #15803d;">{pred_y:.2f} ± {crop_err:.2f} t/ha</div>
            </div>""", unsafe_allow_html=True)

        with k2:
            st.markdown(f"""<div class="kpi-tile" style="border-top: 4px solid #3b82f6;">
            <div class="kpi-tile-top">Gross Crop Value</div>
            <div class="kpi-tile-num" style="color: #0369a1;">{gross_sales/1e3:.1f}k <span style="font-size: 0.85rem; color: #64748b; font-weight: 500;">ETB</span></div>
            <div class="kpi-tile-badge" style="background: #eff6ff; color: #1d4ed8;">@{spot_price:,.0f} ETB/qt</div>
            </div>""", unsafe_allow_html=True)

        with k3:
            profit_c = "#15803d" if net_cash >= 0 else "#dc2626"
            badge_bg = "#f0fdf4" if net_cash >= 0 else "#fef2f2"
            st.markdown(f"""<div class="kpi-tile" style="border-top: 4px solid {profit_c};">
            <div class="kpi-tile-top">Net Family Profit</div>
            <div class="kpi-tile-num" style="color: {profit_c};">{net_cash/1e3:.1f}k <span style="font-size: 0.85rem; color: #64748b; font-weight: 500;">ETB</span></div>
            <div class="kpi-tile-badge" style="background: {badge_bg}; color: {profit_c};">ROI: {roi:+.0f}%</div>
            </div>""", unsafe_allow_html=True)

        with k4:
            st.markdown(f"""<div class="kpi-tile" style="border-top: 4px solid #f59e0b;">
            <div class="kpi-tile-top">Safety Threshold</div>
            <div class="kpi-tile-num" style="color: #b45309;">{breakeven:.2f} <span style="font-size: 0.85rem; color: #64748b; font-weight: 500;">t/ha</span></div>
            <div class="kpi-tile-badge" style="background: #fffbeb; color: #b45309;">Break-Even Target</div>
            </div>""", unsafe_allow_html=True)

        # Automatically looked-up context (user never enters weather or price)
        st.markdown(f"""
        <div class="action-chip" style="border-left-color: #0369a1; margin-top: 12px;">
            <strong>🛰️ Auto-looked-up for {reg_val}, {month_val} {year_val} planting (4-month season):</strong>
            {cur["model_weather_season_mean_temp"]:.1f} °C mean temp ({cur["model_weather_temp_anomaly_c"]:+.1f} °C vs regional norm) ·
            {cur["model_weather_season_rainfall_mm"]:,.0f} mm station rainfall ·
            {cur["model_weather_season_heat_days"]:.0f} extreme-heat days ·
            market price {spot_price:,.0f} ETB/quintal ({crop_val.lower()}, {reg_val}, {year_val})
        </div>
        """, unsafe_allow_html=True)

        notes = []
        if farm_size > 4.5:
            notes.append("farm size above 4.5 ha")
        if fert_val > 135:
            notes.append("fertilizer above 135 kg/ha")
        if notes:
            st.caption(f"ℹ️ Input outside the range of 98% of surveyed plots ({', '.join(notes)}); treat the forecast with extra caution.")

        st.markdown("<br>", unsafe_allow_html=True)

        # Fertilizer response curve from the production model
        curve_bags = curve["total_quintals"].values
        curve_revs = curve["gross_revenue_birr"].values
        curve_costs = (steps * farm_size * c_fert_price) + cost_seed + cost_labor + cost_pest
        curve_profits = curve_revs - curve_costs
        opt_idx = int(np.argmax(curve_profits))
        opt_fert = int(steps[opt_idx])
        opt_gain = float(curve_profits[opt_idx] - net_cash)

        seed_delta_rev = float(alt_seed["gross_revenue_birr"] - cur["gross_revenue_birr"])
        seed_delta_pct = (float(alt_seed["predicted_yield_t_ha"]) / pred_y - 1) * 100 if pred_y > 0 else 0.0
        pest_delta_rev = float(alt_pest["gross_revenue_birr"] - cur["gross_revenue_birr"])
        pest_delta_pct = (float(alt_pest["predicted_yield_t_ha"]) / pred_y - 1) * 100 if pred_y > 0 else 0.0

        # Crisp P&L Statement & Action Cards
        pnl_col, action_col = st.columns([1.1, 0.9], gap="medium")
        with pnl_col:
            st.markdown(f"""<div class="saas-card" style="margin-bottom: 0;">
            <div style="font-weight: 800; font-size: 0.95rem; color: #0f172a; margin-bottom: 10px;">📑 Financial Statement ({farm_size} ha)</div>
            <div class="pnl-strip"><span>Gross Harvest Value</span><strong style="color: #0369a1;">+{gross_sales:,.0f} ETB</strong></div>
            <div class="pnl-strip"><span>Fertilizer ({fert_val*farm_size:.0f} kg @ {c_fert_price:,.0f} ETB)</span><span style="color: #dc2626;">-{cost_fert:,.0f} ETB</span></div>
            <div class="pnl-strip"><span>Certified Seed</span><span style="color: #dc2626;">-{cost_seed:,.0f} ETB</span></div>
            <div class="pnl-strip"><span>Labor ({labor_val*farm_size:.0f} days @ {c_labor_price:,.0f} ETB)</span><span style="color: #dc2626;">-{cost_labor:,.0f} ETB</span></div>
            <div class="pnl-strip"><span>Pest Protection Spray</span><span style="color: {'#dc2626' if cost_pest else '#64748b'};">{f'-{cost_pest:,.0f}' if cost_pest else '0'} ETB</span></div>
            <div class="pnl-strip-bold"><span>Net Household Cash</span><span style="color: {profit_c};">{net_cash:,.0f} ETB</span></div>
            </div>""", unsafe_allow_html=True)

        with action_col:
            if seed_val == 1:
                seed_msg = f"Certified seed adds about <strong>{-seed_delta_pct:+.1f}%</strong> yield on this plot (<strong>{-seed_delta_rev:+,.0f} ETB</strong> vs farm-saved seed)."
            else:
                seed_msg = f"Switching to certified seed changes yield by <strong>{seed_delta_pct:+.1f}%</strong> (<strong>{seed_delta_rev:+,.0f} ETB</strong> gross revenue)."
            if pest_val == 1:
                pest_msg = f"Pest pressure is costing about <strong>{pest_delta_pct:+.1f}%</strong> yield. Controlling it recovers <strong>{pest_delta_rev:+,.0f} ETB</strong>."
            else:
                pest_msg = f"An outbreak would change yield by <strong>{pest_delta_pct:+.1f}%</strong> ({pest_delta_rev:+,.0f} ETB). Early scouting protects this margin."
            fert_msg = (
                f"Net profit peaks at <strong>{opt_fert} kg/ha</strong>"
                + (f", <strong>+{opt_gain:,.0f} ETB</strong> above your current {fert_val} kg/ha." if opt_gain > 1 else ", which is your current setting.")
            )
            st.markdown(f"""
            <div class="action-chip" style="border-left-color: #3b82f6;">
                <strong>💎 Seed Multiplier:</strong> {seed_msg}
            </div>
            <div class="action-chip" style="border-left-color: #10b981;">
                <strong>⚖️ Economic Sweet Spot:</strong> {fert_msg}
            </div>
            <div class="action-chip" style="border-left-color: #f59e0b;">
                <strong>🛡️ Risk Guard:</strong> {pest_msg}
            </div>
            """, unsafe_allow_html=True)

        fig_sim = go.Figure()
        fig_sim.add_trace(go.Scatter(
            x=steps, y=curve_bags, name='Harvest Bags (100 kg)', mode='lines+markers',
            line=dict(color='#10b981', width=3), marker=dict(size=5), yaxis='y1'
        ))
        fig_sim.add_trace(go.Scatter(
            x=steps, y=curve_profits, name='Net Family Profit (ETB)', mode='lines+markers',
            line=dict(color='#3b82f6', width=3, dash='dot'), marker=dict(size=5), yaxis='y2'
        ))
        fig_sim.add_vline(x=opt_fert, line_width=2, line_dash="dash", line_color="#f59e0b",
                          annotation_text=f"Peak: {opt_fert} kg/ha", annotation_position="top left")

        fig_sim.update_layout(
            template='plotly_white', height=300, margin=dict(l=10, r=10, t=30, b=10),
            xaxis=dict(title=dict(text='Fertilizer Application (kg/ha)', font=dict(color='#0f172a', size=11))),
            yaxis=dict(title=dict(text='Harvest Bags', font=dict(color='#10b981', size=11)), tickfont=dict(color='#10b981')),
            yaxis2=dict(title=dict(text='Net Profit (ETB)', font=dict(color='#3b82f6', size=11)), tickfont=dict(color='#3b82f6'), overlaying='y', side='right'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode='x unified'
        )
        st.plotly_chart(fig_sim, width="stretch")
        st.caption("Every point on this curve is a separate prediction from the production model; only fertilizer changes.")

# =============================================================================
# TAB 2: COOPERATIVE COMMAND HUB
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
    st.markdown("### 🏢 Agricultural Cooperative Union & Logistics Hub")
    st.caption("Multi-plot aggregation for union agronomists, warehouse managers, and credit officers.")

    sample_df = load_sample_portfolio()
    src_col, dl_col = st.columns([3, 1])
    with src_col:
        source = st.radio(
            "Portfolio source",
            [f"Sample: {len(sample_df)} real survey plots (2024, unseen by the model)", "Upload cooperative CSV"],
            horizontal=True, label_visibility="collapsed",
        )
    with dl_col:
        st.download_button(
            "⬇️ CSV template", sample_df.to_csv(index=False).encode("utf-8"),
            file_name="cooperative_portfolio_template.csv", mime="text/csv", width="stretch",
        )

    portfolio, issues = sample_df, []
    if source.startswith("Upload"):
        up = st.file_uploader("Upload portfolio (same columns as the template)", type=["csv"])
        if up is None:
            st.info("Upload a CSV to score your own plots. Showing the sample portfolio until then.")
        else:
            try:
                portfolio, issues = validate_portfolio(pd.read_csv(up))
            except Exception as exc:  # malformed file
                portfolio, issues = sample_df.iloc[0:0], [f"Could not read file: {exc}"]
    for msg in issues:
        st.warning(msg)

    if portfolio.empty:
        st.error("No valid plots to score.")
    else:
        batch_res = predictor.predict_batch(portfolio)
        c_tons = batch_res["total_harvest_tons"].sum()
        c_bags = c_tons * 10.0
        c_val = batch_res["gross_revenue_birr"].sum()
        trucks = c_tons / 40.0
        credit_needed = (
            batch_res["fertilizer_kg_per_ha"] * batch_res["farm_size_ha"] * 42.0
            + batch_res["improved_seed_used"] * batch_res["farm_size_ha"] * 4800.0
        ).sum()
        ltv = (credit_needed / c_val * 100.0) if c_val > 0 else 0.0

        cm1, cm2, cm3, cm4 = st.columns(4)
        info = dict(delta_color="off", delta_arrow="off")  # descriptive sub-labels, not changes
        cm1.metric("Total Grain Output", f"{c_tons:.1f} Tons", f"{len(batch_res)} plots · {batch_res['farm_size_ha'].sum():.1f} ha", **info)
        cm2.metric("Warehouse Jute Bags", f"{c_bags:,.0f} Units", "100-kg bags", **info)
        cm3.metric("Freight Fleet Needed", f"{max(1, int(np.ceil(trucks)))} Trucks", "40-ton loads", **info)
        cm4.metric("Harvest Collateral", f"{c_val/1e6:.2f}M ETB", f"Input credit / value: {ltv:.1f}%", **info)

        st.markdown("<br>", unsafe_allow_html=True)

        cc1, cc2 = st.columns([1, 1], gap="medium")
        with cc1:
            f_crop = px.bar(
                batch_res.groupby("crop_type")["total_harvest_tons"].sum().reset_index(),
                x="crop_type", y="total_harvest_tons", color="crop_type",
                title="Total Metric Tons by Staple Crop",
                color_discrete_sequence=px.colors.qualitative.Safe,
                labels={"crop_type": "Crop", "total_harvest_tons": "Harvest (tons)"},
            )
            f_crop.update_layout(template="plotly_white", height=280, showlegend=False, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(f_crop, width="stretch")

        with cc2:
            f_reg = px.pie(
                batch_res.groupby("region")["gross_revenue_birr"].sum().reset_index(),
                names="region", values="gross_revenue_birr",
                title="Regional Branch Revenue Distribution",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            f_reg.update_layout(template="plotly_white", height=280, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(f_reg, width="stretch")

        show_cols = ["plot_id", "region", "crop_type", "planting_month", "farm_size_ha",
                     "predicted_yield_t_ha", "total_harvest_tons", "gross_revenue_birr"]
        nice = {
            "plot_id": "Plot ID", "region": "Region", "crop_type": "Crop", "planting_month": "Planted",
            "farm_size_ha": "Area", "predicted_yield_t_ha": "Predicted Yield",
            "total_harvest_tons": "Harvest", "gross_revenue_birr": "Gross Revenue",
        }
        table = batch_res[show_cols].assign(crop_type=batch_res["crop_type"].str.title()).rename(columns=nice)
        st.dataframe(
            table.style.format({
                "Area": "{:.2f} ha",
                "Predicted Yield": "{:.2f} t/ha",
                "Harvest": "{:.2f} t",
                "Gross Revenue": "{:,.0f} ETB"
            }),
            width="stretch", hide_index=True,
        )
        st.download_button(
            "⬇️ Download forecasts (CSV)", batch_res[show_cols].to_csv(index=False).encode("utf-8"),
            file_name="cooperative_forecast.csv", mime="text/csv",
        )
        st.caption("Credit ratio uses the default input-cost assumptions (42 ETB/kg fertilizer, 4,800 ETB/ha certified seed).")

# =============================================================================
# TAB 3: CLIMATE STRESS RADAR
# =============================================================================
SCENARIOS = {
    "☀️ Severe Heatwave (+2.25°C, +5 heat days)": {"temp_delta": 2.25, "heat_days_add": 5.0},
    "🌧️ Seasonal Drought (-35% rain)": {"rain_mult": 0.65},
    "🧪 Fertilizer Price Shock (+50% cost)": None,
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
    st.markdown("### 🛡️ Climate Shock Stress Radar & Food Security")
    st.caption("The production model is re-run with shocked season weather on real surveyed plots of the chosen region and crop, then scaled to your farm area.")

    cs_sel = st.radio("Select Stress Scenario:", list(SCENARIOS), horizontal=True)

    c_b1, c_b2, c_b3 = st.columns(3)
    c_crop = c_b1.selectbox("Stress Crop", CROPS, key="c_crop")
    c_reg = c_b2.selectbox("Stress Region", REGIONS, key="c_reg")
    c_ha = c_b3.slider("Farm Area (ha)", 0.5, 4.0, 2.0, step=0.5, key="c_ha")

    stt = stress_test(c_reg, c_crop, cs_sel)
    price = predictor.get_market_price(c_reg, c_crop, 2024)
    b_y, s_y = stt["base_y"], stt["shock_y"]
    b_bags, s_bags = b_y * c_ha * 10.0, s_y * c_ha * 10.0
    b_val, s_val = b_bags * price, s_bags * price

    fert_price_shock = 42.0 * (1.5 if SCENARIOS[cs_sel] is None else 1.0)
    base_cost = stt["fert"] * c_ha * 42.0
    shock_cost = stt["fert"] * c_ha * fert_price_shock
    loss = (b_val - base_cost) - (s_val - shock_cost)

    st.markdown("<br>", unsafe_allow_html=True)
    m_s1, m_s2, m_s3 = st.columns(3)
    pct = (s_y / b_y - 1) * 100 if b_y > 0 else 0.0
    m_s1.metric("Normal Season Output", f"{b_bags:.0f} Bags", f"{b_y:.2f} t/ha", delta_color="off", delta_arrow="off")
    m_s2.metric("Stress-Tested Output", f"{s_bags:.0f} Bags", delta=f"{s_y - b_y:+.2f} t/ha ({pct:+.1f}%)")
    if loss >= 0:
        m_s3.metric("Household Loss Exposure", f"{loss:,.0f} ETB", delta=f"{-loss:+,.0f} ETB net income")
    else:
        m_s3.metric("Household Income Change", f"{-loss:+,.0f} ETB", delta=f"{-loss:+,.0f} ETB net income")
    if SCENARIOS[cs_sel] and abs(pct) < 2.0:
        st.info(
            f"Little net effect: for {c_crop.lower()} in {c_reg} the model shows gains and losses largely offsetting "
            f"across plots ({pct:+.1f}% on average, {stt['share_hit']:.0%} of plots lose yield)."
        )
    elif SCENARIOS[cs_sel] and pct >= 2.0:
        st.info(
            f"In the model, {c_crop.lower()} in {c_reg} benefits from this scenario. Warm-season crops (maize, sorghum) grown in "
            "cool highlands gain from warmer seasons, while cool-season crops (wheat, barley, teff) lose yield."
        )

    if SCENARIOS[cs_sel]:
        st.caption(
            f"Averaged over {stt['n']} surveyed {c_crop.lower()} plots in {c_reg} ({stt['share_hit']:.0%} lose yield). Season inputs: "
            f"{stt['temp'][0]:.1f} → {stt['temp'][1]:.1f} °C · {stt['rain'][0]:,.0f} → {stt['rain'][1]:,.0f} mm station rain · "
            f"{stt['heat'][0]:.1f} → {stt['heat'][1]:.1f} heat days. Responses are learned from 2021–2024 survey seasons."
        )
    else:
        st.caption(f"Yield is unchanged; fertilizer cost for the median {stt['fert']:.0f} kg/ha on {c_ha} ha rises from {base_cost:,.0f} to {shock_cost:,.0f} ETB (at {price:,.0f} ETB/quintal grain price).")

    need_q = st.number_input("Household annual grain need (quintals, planning assumption)", 1.0, 60.0, 12.0, step=1.0)
    st.markdown(f"""
    <div class="action-chip" style="border-left-color: {'#10b981' if s_bags >= need_q else '#dc2626'}; margin-top: 12px;">
        <strong>Household Subsistence Meter:</strong> Under this scenario the household produces <strong>{s_bags:.0f} bags</strong>
        against a need of {need_q:.0f} ({'above the threshold, with surplus to sell.' if s_bags >= need_q else '⚠️ below the subsistence floor; a candidate for safety-net or index-insurance support.'})
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# TAB 4: SYSTEM AUDIT & CONFUSION MATRIX
# =============================================================================
@st.cache_data(show_spinner=False)
def run_compliance_checks() -> list[dict]:
    checks = []
    feats = predictor.feature_names
    weather_feats = [f for f in feats if f.startswith("weather_")]
    checks.append({"Check": "Rule 5: model uses weather-derived features", "Result": f"✅ {len(weather_feats)} weather features" if weather_feats else "❌ none"})
    checks.append({"Check": "Market price excluded from model inputs", "Result": "✅ excluded" if "price_birr_per_quintal" not in feats else "❌ price is a feature"})

    sub_p = project_dir / "submission" / "team_11_submission.csv"
    tpl_p = project_dir / "data" / "raw" / "submission_template.csv"
    test_p = project_dir / "data" / "processed" / "master_test.csv"
    if sub_p.exists() and tpl_p.exists():
        sub, tpl = pd.read_csv(sub_p), pd.read_csv(tpl_p)
        ok = list(sub.columns) == list(tpl.columns) and len(sub) == len(tpl) and (sub["plot_id"] == tpl["plot_id"]).all() and sub.notna().all().all()
        checks.append({"Check": "Submission matches template (rows, columns, plot order, no nulls)", "Result": f"✅ {len(sub):,} rows" if ok else "❌ mismatch"})
        if test_p.exists():
            test = pd.read_csv(test_p)
            app_pred = predictor.predict_batch(test[PLOT_COLUMNS + ["rainfall_mm_season"]])["predicted_yield_t_ha"].values
            diff = float(np.abs(app_pred - sub.iloc[:, 1].values).max())
            checks.append({"Check": "App reproduces every submitted prediction (train/serve parity)", "Result": f"✅ max diff {diff:.4f} t/ha" if diff < 1e-2 else f"❌ max diff {diff:.3f} t/ha"})
    else:
        checks.append({"Check": "Submission file", "Result": "ℹ️ not bundled with this deployment"})

    fig_dir = project_dir / "figures" if (project_dir / "figures").exists() else app_dir / "assets" / "figures"
    n_figs = sum((fig_dir / f).exists() for f in REQUIRED_FIGS)
    checks.append({"Check": "Deliverable C: 12 required figures present", "Result": f"{'✅' if n_figs == 12 else '❌'} {n_figs}/12"})
    return checks


REQUIRED_FIGS = [
    "fig01_missingness.png", "fig02_before_after_cleaning.png", "fig03_yield_distribution.png",
    "fig04_region_crop_heatmap.png", "fig05_correlation_heatmap.png", "fig06_climate_by_region.png",
    "fig07_yield_vs_season_temp.png", "fig08_price_trends.png", "fig09_revenue_by_crop_region.png",
    "fig10_model_comparison.png", "fig11_predicted_vs_actual_residuals.png", "fig12_feature_importance.png",
]

with t_governance:
    st.markdown("### 📊 System Audit, Deliverable C Gallery & Confusion Matrix")
    st.caption("All metrics below are 5-fold out-of-fold results: every plot is scored by a model that never saw it. Generated by src/build_app_assets.py.")

    cm = np.array(TIERS.get("confusion_matrix", [[0] * 3] * 3))
    n_total = int(cm.sum()) or 1
    n_diag = int(np.trace(cm))

    st.markdown("#### 🎯 Smallholder Food Security Tier Confusion Matrix")
    st.caption("Discretizing continuous yield into 3 policy tiers: Subsistence (<2.0 t/ha), Standard (2.0–3.5 t/ha), Commercial (>3.5 t/ha).")

    cm_cols1, cm_cols2 = st.columns([1, 1.8], gap="medium")
    with cm_cols1:
        st.markdown(f"""
        <div class="saas-card" style="margin-bottom: 0;">
            <div style="font-weight: 800; font-size: 0.95rem; color: #064e3b; margin-bottom: 8px;">Audit Highlights ({n_total:,} Plots)</div>
            <div style="font-size: 0.85rem; color: #334155; line-height: 1.55;">
                • <strong>{TIERS.get("accuracy", 0):.1%} tier accuracy:</strong> {n_diag:,} of {n_total:,} plots land in their true tier.<br>
                • <strong>{TIERS.get("extreme_errors", 0)} extreme errors ({TIERS.get("extreme_errors", 0) / n_total:.2%}):</strong> subsistence ↔ commercial confusions are almost nonexistent.<br>
                • <strong>{TIERS.get("subsistence_precision", 0):.1%} subsistence precision</strong> and {TIERS.get("subsistence_recall", 0):.1%} recall for targeting food-security support.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        cm_k1, cm_k2 = st.columns(2)
        cm_k1.metric("CV RMSE", f"{CV.get('rmse', 0):.3f} t/ha", f"R² {CV.get('r2', 0):.3f}", delta_color="off", delta_arrow="off")
        cm_k2.metric("Without Weather", f"{CV.get('no_weather_rmse', 0):.3f} t/ha", f"+{weather_gain:.1f}% error", delta_color="inverse")

    with cm_cols2:
        row_pct = cm / np.maximum(cm.sum(axis=1, keepdims=True), 1) * 100
        t_labels = TIERS.get("labels", ["Subsistence (<2.0)", "Standard (2.0–3.5)", "Commercial (>3.5)"])
        t_texts = [[f"{cm[i, j]:,}<br>({row_pct[i, j]:.1f}%)" for j in range(3)] for i in range(3)]
        fig_cm = go.Figure(data=go.Heatmap(
            z=row_pct, x=t_labels, y=t_labels, text=t_texts,
            texttemplate="%{text}", textfont=dict(size=12),
            colorscale=[[0, "#f0fdf4"], [0.25, "#86efac"], [0.7, "#16a34a"], [1.0, "#064e3b"]],
            showscale=False, zmin=0, zmax=100,
        ))
        fig_cm.update_layout(
            title=dict(text="Ground Truth vs. Predicted Productivity Tier (out-of-fold)", font=dict(size=13, color="#0f172a")),
            xaxis=dict(title=dict(text="Predicted Tier", font=dict(color="#0f172a", size=11))),
            yaxis=dict(title=dict(text="Actual Tier", font=dict(color="#0f172a", size=11)), autorange="reversed"),
            height=280, margin=dict(l=10, r=10, t=30, b=10), template="plotly_white"
        )
        st.plotly_chart(fig_cm, width="stretch")

    with st.expander("Error by crop and region (out-of-fold)"):
        e1, e2 = st.columns(2)
        for col, key, label in ((e1, "by_crop", "Crop"), (e2, "by_region", "Region")):
            tbl = pd.DataFrame(M.get(key, {})).T.reset_index().rename(columns={
                "index": label, "rmse": "RMSE (t/ha)", "mae": "MAE (t/ha)", "mean_yield": "Mean yield (t/ha)", "n": "Plots"})
            col.dataframe(tbl, hide_index=True, width="stretch")
        oot = M.get("out_of_time", {})
        if oot:
            st.caption(f"Out-of-time check: trained on {oot['train_years'][0]}–{oot['train_years'][-1]} ({oot['n_train']:,} plots), "
                       f"tested on {oot['test_year']} ({oot['n_test']:,} plots): RMSE {oot['rmse']:.3f} t/ha, R² {oot['r2']:.3f}.")

    st.markdown("---")

    st.markdown("#### 🖼️ Deliverable C Publication Gallery (12 Required + Figure 13)")
    fig_dir = project_dir / "figures" if (project_dir / "figures").exists() else app_dir / "assets" / "figures"
    fig_opts = {
        "fig13_yield_tier_confusion_matrix.png": "Figure 13: Food Security Tier Confusion Matrix (5-fold out-of-fold, 15,090 plots)",
        "fig10_model_comparison.png": "Figure 10: Model Benchmark Comparison (Baseline vs. Production)",
        "fig11_predicted_vs_actual_residuals.png": "Figure 11: Predicted vs. Actual & Residual Diagnostics",
        "fig12_feature_importance.png": "Figure 12: Permutation Feature Importance",
        "fig04_region_crop_heatmap.png": "Figure 4: Mean Yield Heatmap (Region × Crop)",
        "fig06_climate_by_region.png": "Figure 6: Monthly Climate by Region with Growing Season",
        "fig08_price_trends.png": "Figure 8: Market Price Trends per Quintal (2021–2024)",
        "fig09_revenue_by_crop_region.png": "Figure 9: Estimated Gross Revenue per Hectare by Crop & Region",
    }

    fig_sel = st.selectbox("Inspect Publication Figure:", list(fig_opts.keys()), format_func=lambda k: fig_opts[k])
    p_fig = fig_dir / fig_sel
    if not p_fig.exists():
        p_fig = app_dir / "assets" / "figures" / fig_sel
    if p_fig.exists():
        st.image(str(p_fig), caption=fig_opts[fig_sel], width="stretch")
    else:
        st.info("Figure not bundled with this deployment.")

    st.markdown("---")
    st.markdown("#### ✅ Live Compliance Checks")
    st.caption("Computed when the app starts, from the files in this repository.")
    st.table(pd.DataFrame(run_compliance_checks()))
