import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import textwrap

from src.risk_engine import (
    load_data,
    filter_records,
    get_summary,
    get_risk_scorecard,
)
from src.generator import generate_answer


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="AgriRisk AI | Agricultural Risk Intelligence",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# PREMIUM STYLING & DESIGN SYSTEM
# --------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Sans:wght@400;500;600;700&display=swap');

    :root {
        --forest-dark: #064e3b;
        --forest: #14532d;
        --emerald: #15803d;
        --emerald-light: #22c55e;
        --mint-light: #dcfce7;
        --mint-soft: #f0fdf4;
        --bg-page: #f6faf6;
        --card-bg: #ffffff;
        --ink-primary: #0d281e;
        --ink-secondary: #3d5a4c;
        --border-subtle: #dbe8df;
        --risk-low: #10b981;
        --risk-mod: #f59e0b;
        --risk-high: #f97316;
        --risk-crit: #ef4444;
    }

    /* Core Page Styling */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    .stApp {
        background-color: var(--bg-page) !important;
        background-image: 
            radial-gradient(at 100% 0%, rgba(220, 252, 231, 0.4) 0px, transparent 50%),
            radial-gradient(at 0% 100%, rgba(209, 250, 229, 0.3) 0px, transparent 50%) !important;
        color: var(--ink-primary) !important;
    }

    /* Explicit typography colors to avoid dark mode conflicts */
    h1, h2, h3, h4, h5, h6, 
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: var(--forest-dark) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }

    p, span, label, div[data-testid="stMarkdownContainer"] p {
        color: var(--ink-secondary) !important;
    }

    /* Streamlit Header */
    [data-testid="stHeader"] {
        background: rgba(246, 250, 246, 0.92) !important;
        backdrop-filter: blur(8px);
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #edf6ee 0%, #f7faf7 60%, #e8f3ea 100%) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }

    [data-testid="stSidebar"] label {
        color: var(--forest-dark) !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }

    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: var(--ink-secondary) !important;
    }

    /* Brand Logo Lockup */
    .brand-container {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 0.2rem 0 0.4rem 0;
    }

    .brand-icon-box {
        width: 44px;
        height: 44px;
        background: linear-gradient(135deg, #15803d 0%, #064e3b 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        box-shadow: 0 4px 12px rgba(21, 128, 61, 0.25);
    }

    .brand-text-box {
        display: flex;
        flex-direction: column;
    }

    .brand-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.35rem;
        font-weight: 800;
        color: var(--forest-dark);
        letter-spacing: -0.5px;
        line-height: 1.1;
    }

    .brand-subtitle {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: var(--emerald);
        margin-top: 2px;
    }

    /* Hero Banner */
    .hero-card {
        background: linear-gradient(125deg, #064e3b 0%, #0c6742 45%, #15803d 100%);
        border-radius: 20px;
        padding: 1.8rem 2.2rem;
        margin: 0.2rem 0 1.4rem 0;
        color: #ffffff;
        box-shadow: 0 10px 28px rgba(6, 78, 59, 0.16);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }

    .hero-card::after {
        content: "🌱";
        position: absolute;
        right: 25px;
        top: -15px;
        font-size: 8rem;
        opacity: 0.08;
        pointer-events: none;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(220, 252, 231, 0.18);
        border: 1px solid rgba(220, 252, 231, 0.35);
        color: #bbf7d0;
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        padding: 0.3rem 0.75rem;
        border-radius: 999px;
        margin-bottom: 0.6rem;
    }

    .hero-heading {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: clamp(1.8rem, 2.5vw, 2.4rem);
        font-weight: 800;
        letter-spacing: -0.8px;
        line-height: 1.15;
        margin: 0;
        color: #ffffff !important;
    }

    .hero-description {
        margin-top: 0.6rem;
        color: #d1fae5;
        font-size: 0.98rem;
        max-width: 780px;
        line-height: 1.5;
    }

    .hero-footer-bar {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 10px;
        margin-top: 1.1rem;
        padding-top: 0.9rem;
        border-top: 1px solid rgba(255, 255, 255, 0.12);
    }

    .pill-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.22);
        padding: 0.28rem 0.7rem;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #f0fdf4;
    }

    /* Metric Cards Override */
    div[data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 16px !important;
        padding: 1rem 1.2rem !important;
        box-shadow: 0 4px 16px rgba(13, 40, 30, 0.04) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 22px rgba(13, 40, 30, 0.07) !important;
    }

    div[data-testid="stMetricLabel"] {
        color: var(--ink-secondary) !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMetricValue"] {
        color: var(--forest-dark) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 800 !important;
        font-size: 1.75rem !important;
        letter-spacing: -0.5px !important;
    }

    /* Container Cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 18px !important;
        box-shadow: 0 4px 18px rgba(13, 40, 30, 0.035) !important;
        padding: 1.1rem 1.3rem !important;
    }

    /* Tabs Styling */
    div[data-testid="stTabs"] button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        color: var(--ink-secondary) !important;
        padding: 0.65rem 1.25rem !important;
        font-size: 0.95rem !important;
        border: 1px solid transparent !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: var(--forest-dark) !important;
        background-color: #e6f4ea !important;
        border-color: #c7e5cf !important;
    }

    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        background-color: var(--emerald) !important;
        height: 3px !important;
        border-radius: 3px !important;
    }

    /* Primary Buttons */
    button[data-testid="stBaseButton-primary"], .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #15803d 0%, #064e3b 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 11px !important;
        font-weight: 700 !important;
        padding: 0.65rem 1.4rem !important;
        box-shadow: 0 4px 14px rgba(21, 128, 61, 0.24) !important;
        transition: all 0.2s ease !important;
    }

    button[data-testid="stBaseButton-primary"]:hover, .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(21, 128, 61, 0.34) !important;
    }

    /* Secondary Buttons */
    button[data-testid="stBaseButton-secondary"], .stButton > button[kind="secondary"] {
        background: #ffffff !important;
        color: var(--forest-dark) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 11px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    button[data-testid="stBaseButton-secondary"]:hover, .stButton > button[kind="secondary"]:hover {
        background: #f0fdf4 !important;
        border-color: #86efac !important;
    }

    /* Form Inputs */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border-color: var(--border-subtle) !important;
        color: var(--ink-primary) !important;
        border-radius: 10px !important;
    }

    input, textarea {
        background-color: #ffffff !important;
        color: var(--ink-primary) !important;
        border-color: var(--border-subtle) !important;
        border-radius: 10px !important;
    }

    /* Expanders */
    div[data-testid="stExpander"] {
        background: #ffffff !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 14px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02) !important;
        overflow: hidden;
    }

    /* Custom Dashboard Cards */
    .agri-card {
        background: #ffffff;
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 1.25rem 1.4rem;
        box-shadow: 0 4px 18px rgba(13, 40, 30, 0.04);
        margin-bottom: 1rem;
    }

    .agri-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.8rem;
    }

    .agri-card-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.05rem;
        font-weight: 800;
        color: var(--forest-dark);
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Progress bar styles */
    .risk-bar-container {
        margin-bottom: 0.75rem;
    }

    .risk-bar-label {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--ink-secondary);
        margin-bottom: 0.3rem;
    }

    .risk-bar-track {
        height: 10px;
        background: #eef5f0;
        border-radius: 999px;
        overflow: hidden;
        display: flex;
    }

    .risk-bar-fill {
        height: 100%;
        border-radius: 999px;
        transition: width 0.5s ease-in-out;
    }

    /* Scorecard Indicator Card */
    .indicator-card {
        background: linear-gradient(145deg, #ffffff, #f9fbf9);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 1.1rem;
        text-align: center;
        box-shadow: 0 3px 12px rgba(0,0,0,0.02);
    }

    .indicator-val {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.7rem;
        font-weight: 800;
        color: var(--forest-dark);
        margin: 0.2rem 0;
    }

    .indicator-tag {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 999px;
        font-size: 0.74rem;
        font-weight: 700;
    }

    /* Action ranking item */
    .action-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 0.9rem;
        background: #fbfdfb;
        border: 1px solid #e7efe9;
        border-radius: 12px;
        margin-bottom: 0.5rem;
    }

    .action-rank {
        width: 26px;
        height: 26px;
        background: #e2f0e5;
        color: var(--forest-dark);
        font-weight: 800;
        font-size: 0.78rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .action-name {
        flex-grow: 1;
        margin: 0 12px;
        font-size: 0.88rem;
        font-weight: 600;
        color: var(--ink-primary);
    }

    .action-badge {
        background: #edf6ee;
        border: 1px solid #d0e5d5;
        color: var(--forest-dark);
        font-weight: 700;
        font-size: 0.78rem;
        padding: 0.25rem 0.6rem;
        border-radius: 8px;
    }

    /* Section Subheadings */
    .section-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.25rem;
        font-weight: 800;
        color: var(--forest-dark);
        margin: 0.4rem 0 0.15rem 0;
        letter-spacing: -0.3px;
    }

    .section-desc {
        color: var(--ink-secondary);
        font-size: 0.9rem;
        margin-bottom: 1.1rem;
    }

    /* Reference Cards in Advisory */
    .citation-card {
        background: #ffffff;
        border: 1px solid #dce8df;
        border-left: 4px solid var(--emerald);
        border-radius: 12px;
        padding: 1rem 1.15rem;
        margin-bottom: 0.8rem;
    }

    .citation-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }

    .citation-title {
        font-weight: 700;
        color: var(--forest-dark);
        font-size: 0.95rem;
    }

    .citation-score {
        background: #e6f4ea;
        color: #137333;
        font-size: 0.74rem;
        font-weight: 700;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
    }

    .citation-text {
        color: #2c4a3b;
        font-size: 0.88rem;
        line-height: 1.45;
        margin-bottom: 0.5rem;
    }

    .citation-meta {
        font-size: 0.76rem;
        color: #6b8073;
    }

    /* Plotly Chart High-Contrast Text Overrides & Modebar Removal */
    .js-plotly-plot .plotly .ytick text,
    .js-plotly-plot .plotly .xtick text,
    .js-plotly-plot .plotly .g-ytitle text,
    .js-plotly-plot .plotly .g-xtitle text,
    .js-plotly-plot .plotly .legendtext,
    .js-plotly-plot .plotly .axis-title,
    .js-plotly-plot .plotly .textpoint text {
        fill: #0d281e !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
    }

    /* Completely hide intrusive floating modebar toolbar */
    .js-plotly-plot .plotly .modebar-container,
    .js-plotly-plot .plotly .modebar,
    .modebar-container,
    [data-testid="stPlotlyChart"] .modebar {
        display: none !important;
        opacity: 0 !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# DATA INGESTION & CACHING
# --------------------------------------------------
@st.cache_data(show_spinner=False)
def load_agri_dataset():
    return load_data()


try:
    df = load_agri_dataset()
except Exception as exc:
    st.error(f"❌ Could not load agricultural risk dataset: {exc}")
    st.info("Please verify that data/agriculture_risk_dataset.csv exists and is accessible.")
    st.stop()

if df.empty:
    st.error("❌ The agricultural dataset is empty.")
    st.stop()


# Detect Year Column safely
year_lookup = {str(col).strip().lower(): col for col in df.columns}
year_candidates = ["year", "record_year", "data_year", "harvest_year", "season_year"]
year_column = next((year_lookup[name] for name in year_candidates if name in year_lookup), None)
if year_column is None:
    year_column = next((col for col in df.columns if "year" in str(col).strip().lower()), None)


# --------------------------------------------------
# SIDEBAR FILTERS & BRANDING
# --------------------------------------------------
st.sidebar.markdown(
    """
    <div class="brand-container">
        <div class="brand-icon-box">🌱</div>
        <div class="brand-text-box">
            <span class="brand-title">AgriRisk AI</span>
            <span class="brand-subtitle">Risk Intelligence</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Analytics Scope")
st.sidebar.caption("Filter risk analytics by location, commodity, and timeline.")

# Country Filter
if "country" in df.columns:
    country_list = sorted(df["country"].dropna().astype(str).unique().tolist())
    selected_country = st.sidebar.selectbox("🌍 Geographic Region / Country", ["All"] + country_list, index=0)
else:
    selected_country = "All"

# Crop Filter
if "crop" in df.columns:
    crop_list = sorted(df["crop"].dropna().astype(str).unique().tolist())
    selected_crop = st.sidebar.selectbox("🌾 Crop / Commodity", ["All"] + crop_list, index=0)
else:
    selected_crop = "All"

# Year Filter
selected_year = "All"
if year_column is not None:
    year_values = pd.to_numeric(df[year_column], errors="coerce").dropna()
    available_years = sorted(year_values.astype(int).unique().tolist(), reverse=True)
    selected_year = st.sidebar.selectbox(
        "📅 Observation Year",
        options=["All"] + available_years,
        index=0,
        help="Filter dataset by recording period.",
    )
else:
    st.sidebar.info("Year timeline column unavailable.")

# Reset Filters Helper
if st.sidebar.button("🔄 Reset to Full Dataset", use_container_width=True):
    st.session_state["reset_filters"] = True
    st.rerun()

st.sidebar.markdown("---")

# Data Snapshot Widget
st.sidebar.markdown("### 📊 Dataset Scope")
filtered_df_pre = filter_records(df, country=selected_country, crop=selected_crop)
if selected_year != "All" and year_column is not None:
    numeric_years = pd.to_numeric(filtered_df_pre[year_column], errors="coerce")
    filtered_df_pre = filtered_df_pre[numeric_years == int(selected_year)]

total_rows = len(df)
filtered_rows = len(filtered_df_pre)
filter_share = (filtered_rows / total_rows * 100) if total_rows else 0

st.sidebar.metric("Active Sample Records", f"{filtered_rows:,}", delta=f"{filter_share:.1f}% of total" if filter_share < 100 else "100% Full Dataset")

st.sidebar.markdown(
    """
    <div style="background:#eaf5ec; border:1px solid #c9e4cf; border-radius:12px; padding:0.85rem; margin-top:0.8rem;">
        <div style="font-weight:700; color:#0f5132; font-size:0.82rem; margin-bottom:0.25rem;">🌿 Advisory Note</div>
        <div style="font-size:0.75rem; color:#3b5c49; line-height:1.4;">
            Analytical scores represent empirical dataset records and local retrieval guidance. Verify findings with licensed agronomists for on-farm implementation.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# FILTER APPLICATION
# --------------------------------------------------
filtered_df = filtered_df_pre

if filtered_df.empty:
    st.warning("⚠️ No records match the selected combination of Country, Crop, and Year.")
    if st.button("Reset Filters to 'All'"):
        st.rerun()
    st.stop()


# --------------------------------------------------
# COMPUTED RISK METRICS
# --------------------------------------------------
total_records = len(filtered_df)

if "risk_category" in filtered_df.columns:
    risk_counts = filtered_df["risk_category"].value_counts()
    high_critical_count = (
        filtered_df["risk_category"].astype(str).str.strip().str.lower()
        .isin(["high", "critical"]).sum()
    )
    high_critical_pct = high_critical_count / total_records * 100 if total_records else 0
else:
    risk_counts = pd.Series(dtype=int)
    high_critical_pct = 0.0

def get_col_avg(column_name):
    if column_name in filtered_df.columns:
        val = pd.to_numeric(filtered_df[column_name], errors="coerce").mean()
        return float(val) if pd.notna(val) else float("nan")
    return float("nan")

climate_avg = get_col_avg("climate_stress_index")
disease_avg = get_col_avg("disease_risk_score")
pest_avg = get_col_avg("pest_risk_score")
moisture_avg = get_col_avg("soil_moisture_percent")
rainfall_avg = get_col_avg("annual_rainfall_mm")

# Determine status badge
if high_critical_pct >= 30:
    status_badge = "🔴 Elevated Vulnerability Profile"
    status_badge_bg = "rgba(239, 68, 68, 0.25)"
    status_badge_border = "#fca5a5"
elif high_critical_pct >= 15:
    status_badge = "🟡 Moderate Vulnerability Profile"
    status_badge_bg = "rgba(245, 158, 11, 0.25)"
    status_badge_border = "#fde68a"
else:
    status_badge = "🟢 Low Vulnerability Profile"
    status_badge_bg = "rgba(16, 185, 129, 0.25)"
    status_badge_border = "#a7f3d0"


# --------------------------------------------------
# HERO BANNER
# --------------------------------------------------
st.markdown(
    f"""
    <div class="hero-card">
        <div class="hero-badge">✨ Agricultural Risk Intelligence Platform</div>
        <div class="hero-heading">AgriRisk AI Dashboard</div>
        <div class="hero-description">
            Evaluate climate stress patterns, disease and pest vulnerabilities, and actionable agronomic mitigations 
            grounded in comprehensive agricultural intelligence and verified local advisory literature.
        </div>
        <div class="hero-footer-bar">
            <span class="pill-tag">🌍 Country: <b>{selected_country}</b></span>
            <span class="pill-tag">🌾 Crop: <b>{selected_crop}</b></span>
            <span class="pill-tag">📅 Period: <b>{selected_year}</b></span>
            <span class="pill-tag" style="background:{status_badge_bg}; border-color:{status_badge_border}; font-weight:700;">
                {status_badge}
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# MAIN WORKSPACE TABS
# --------------------------------------------------
tab_overview, tab_scorecard, tab_advisory, tab_explore = st.tabs(
    ["📊 Risk Overview", "🎯 Risk Scorecard", "🤖 AI Advisory", "🔎 Explore Dataset"]
)


# --------------------------------------------------
# TAB 1: 📊 RISK OVERVIEW
# --------------------------------------------------
with tab_overview:
    st.markdown('<div class="section-title">Macro Risk Overview</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">Key risk metrics, category composition, and recorded agricultural indicators across the active scope.</div>',
        unsafe_allow_html=True,
    )

    # Top KPI Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(
        "📚 Analyzed Records",
        f"{total_records:,}",
        delta=f"{(total_records / total_rows * 100):.1f}% of total" if total_records < total_rows else "All records",
        help="Volume of field records matching the active filters.",
    )
    m2.metric(
        "🚨 High & Critical Risk",
        f"{high_critical_pct:.1f}%",
        delta="Requires Attention" if high_critical_pct > 20 else "Within Nominal Range",
        delta_color="inverse" if high_critical_pct > 20 else "normal",
        help="Percentage of records classified as High or Critical risk.",
    )
    m3.metric(
        "🌡️ Avg. Climate Stress",
        f"{climate_avg:.1f}/100" if pd.notna(climate_avg) else "N/A",
        delta="Severe" if climate_avg > 60 else "Manageable",
        delta_color="inverse" if climate_avg > 60 else "normal",
        help="Mean climate stress index (0-100 scale).",
    )
    pest_disease_max = max([val for val in [disease_avg, pest_avg] if pd.notna(val)] or [0])
    m4.metric(
        "🐛 Avg. Pest / Disease",
        f"{pest_avg:.1f}" if pd.notna(pest_avg) else "N/A",
        delta=f"Disease: {disease_avg:.1f}" if pd.notna(disease_avg) else None,
        help="Average pest risk index and disease vulnerability score.",
    )

    st.write("")

    # Visual Analytics Row
    chart_left, chart_right = st.columns([1, 1.15], gap="large")

    with chart_left:
        with st.container(border=True):
            st.markdown("#### 🧭 Risk Category Distribution")
            if not risk_counts.empty:
                risk_order_map = ["Low", "Moderate", "High", "Critical"]
                risk_df = risk_counts.reindex(risk_order_map, fill_value=0).reset_index()
                risk_df.columns = ["Category", "Records"]
                risk_df["Share"] = (risk_df["Records"] / total_records * 100).round(1)

                palette = {
                    "Low": "#10b981",
                    "Moderate": "#f59e0b",
                    "High": "#f97316",
                    "Critical": "#ef4444",
                }

                fig_pie = px.pie(
                    risk_df,
                    names="Category",
                    values="Records",
                    hole=0.64,
                    color="Category",
                    color_discrete_map=palette,
                )
                fig_pie.update_traces(
                    textposition="inside",
                    textinfo="percent+label",
                    textfont_size=12,
                    hovertemplate="<b>%{label} Risk</b><br>Records: %{value:,}<br>Proportion: %{percent}<extra></extra>",
                    marker=dict(line=dict(color="#ffffff", width=2.5)),
                )
                fig_pie.update_layout(
                    margin=dict(t=15, b=15, l=15, r=15),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Plus Jakarta Sans, sans-serif", color="#0d281e"),
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.15,
                        xanchor="center",
                        x=0.5,
                        font=dict(color="#0d281e", size=12, family="Plus Jakarta Sans", weight=700),
                    ),
                )
                st.plotly_chart(fig_pie, use_container_width=True, theme=None, config={"displayModeBar": False})
            else:
                st.info("Risk category data is unavailable for this filter selection.")

    with chart_right:
        with st.container(border=True):
            st.markdown("#### 📈 Key Stress Indicators (0 - 100 Scale)")
            indicators = [
                ("Climate Stress", climate_avg, "#10b981"),
                ("Pest Risk", pest_avg, "#f59e0b"),
                ("Disease Risk", disease_avg, "#3b82f6"),
                ("Soil Moisture (%)", moisture_avg, "#06b6d4"),
            ]
            valid_indicators = [(name, val, col) for name, val, col in indicators if pd.notna(val)]

            if valid_indicators:
                ind_df = pd.DataFrame(valid_indicators, columns=["Indicator", "Score", "Color"])
                fig_bar = px.bar(
                    ind_df,
                    x="Indicator",
                    y="Score",
                    text_auto=".1f",
                    color="Indicator",
                    color_discrete_sequence=[item[2] for item in valid_indicators],
                )
                fig_bar.update_traces(
                    textposition="outside",
                    texttemplate="<b>%{y:.1f}</b>",
                    textfont=dict(color="#0d281e", size=12, family="Plus Jakarta Sans"),
                    marker_line_width=0,
                    hovertemplate="<b>%{x}</b><br>Average Value: %{y:.2f}<extra></extra>",
                )
                fig_bar.update_layout(
                    margin=dict(t=25, b=25, l=10, r=10),
                    xaxis_title="",
                    yaxis_title=dict(
                        text="<b>Average Metric Score</b>",
                        font=dict(color="#0d281e", size=12, family="Plus Jakarta Sans"),
                    ),
                    xaxis=dict(
                        tickfont=dict(color="#0d281e", size=12, family="Plus Jakarta Sans", weight=700),
                        color="#0d281e",
                    ),
                    yaxis=dict(
                        range=[0, max(100, ind_df["Score"].max() * 1.18)],
                        gridcolor="#e9f3ec",
                        zeroline=False,
                        tickfont=dict(color="#0d281e", size=11, family="Plus Jakarta Sans", weight=600),
                        color="#0d281e",
                    ),
                    showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Plus Jakarta Sans, sans-serif", color="#0d281e"),
                )
                st.plotly_chart(fig_bar, use_container_width=True, theme=None, config={"displayModeBar": False})
            else:
                st.info("Stress indicator metrics are unavailable.")

    # Lower Grid: Recommended Actions & Analytical Takeaway
    col_actions, col_insights = st.columns([1.15, 1], gap="large")

    with col_actions:
        with st.container(border=True):
            st.markdown("#### 🛠️ Most Recorded Farm Interventions")
            if "recommended_action" in filtered_df.columns:
                actions_series = filtered_df["recommended_action"].dropna().astype(str).value_counts().head(5)
                if not actions_series.empty:
                    action_chart_df = actions_series.rename_axis("Action").reset_index(name="Frequency").sort_values("Frequency", ascending=True)
                    action_chart_df["Wrapped_Action"] = action_chart_df["Action"].apply(
                        lambda x: "<br>".join(textwrap.wrap(str(x), width=28))
                    )
                    fig_actions = px.bar(
                        action_chart_df,
                        x="Frequency",
                        y="Wrapped_Action",
                        orientation="h",
                        text="Frequency",
                    )
                    fig_actions.update_traces(
                        marker=dict(
                            color="#15803d",
                            line=dict(color="#064e3b", width=1.5),
                        ),
                        texttemplate="<b>%{text:,}</b>",
                        textposition="outside",
                        cliponaxis=False,
                        textfont=dict(color="#0d281e", size=12, family="Plus Jakarta Sans"),
                        hovertemplate="<b>%{y}</b><br>Records: %{x:,}<extra></extra>",
                    )
                    fig_actions.update_layout(
                        margin=dict(t=15, b=25, l=15, r=60),
                        xaxis_title=dict(
                            text="<b>Total Record Count</b>",
                            font=dict(color="#0d281e", size=12, family="Plus Jakarta Sans"),
                        ),
                        yaxis_title="",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Plus Jakarta Sans, sans-serif", color="#0d281e"),
                        yaxis=dict(
                            tickfont=dict(color="#0d281e", size=12, family="Plus Jakarta Sans", weight=700),
                            color="#0d281e",
                            automargin=True,
                        ),
                        xaxis=dict(
                            tickfont=dict(color="#0d281e", size=11, family="Plus Jakarta Sans", weight=600),
                            color="#0d281e",
                            gridcolor="#dbe8df",
                            zeroline=False,
                        ),
                    )
                    st.plotly_chart(
                        fig_actions,
                        use_container_width=True,
                        theme=None,
                        config={"displayModeBar": False},
                    )
                else:
                    st.info("No recorded recommended actions found.")
            else:
                st.info("Recommended action data column not found.")

    with col_insights:
        with st.container(border=True):
            st.markdown("#### 💡 Strategic Risk Assessment")
            
            dominant_cat = risk_counts.idxmax() if not risk_counts.empty else "N/A"
            dominant_num = int(risk_counts.max()) if not risk_counts.empty else 0
            dominant_pct = (dominant_num / total_records * 100) if total_records else 0

            st.markdown(
                f"""
                <div style="background:#f4fbf5; border:1px solid #cce8d2; border-radius:12px; padding:0.9rem; margin-bottom:0.75rem;">
                    <div style="font-size:0.8rem; font-weight:700; color:#15803d; text-transform:uppercase;">Dominant Classification</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#064e3b; margin-top:0.2rem;">
                        {dominant_cat} Risk Profile ({dominant_pct:.1f}%)
                    </div>
                    <div style="font-size:0.83rem; color:#4a6956; margin-top:0.2rem;">
                        Accounts for <b>{dominant_num:,}</b> of {total_records:,} observed records in this cohort.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Indicator highlight
            all_inds = {"Climate Stress": climate_avg, "Pest Risk": pest_avg, "Disease Risk": disease_avg}
            valid_inds = {k: v for k, v in all_inds.items() if pd.notna(v)}
            if valid_inds:
                highest_stressor = max(valid_inds, key=valid_inds.get)
                st.markdown(f"• **Primary Stress Factor:** **{highest_stressor}** index averages **{valid_inds[highest_stressor]:.1f}/100**.")

            if "recommended_action" in filtered_df.columns:
                top_act = filtered_df["recommended_action"].dropna().astype(str).value_counts()
                if not top_act.empty:
                    st.markdown(f"• **Prevailing Advisory:** *\"{top_act.index[0]}\"* ({top_act.iloc[0]:,} applications).")

            st.caption("ℹ️ Insights are generated from statistical distributions of empirical observations and structured local knowledge bases.")


# --------------------------------------------------
# TAB 2: 🎯 RISK SCORECARD (COMPREHENSIVE REDESIGN)
# --------------------------------------------------
with tab_scorecard:
    st.markdown('<div class="section-title">Agricultural Risk Scorecard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">Structured vulnerability benchmarks, category distributions, and prioritized agricultural actions.</div>',
        unsafe_allow_html=True,
    )

    raw_scorecard = get_risk_scorecard(filtered_df)

    # 1. Executive Summary Strip
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Cohort Sample", f"{raw_scorecard.get('records', total_records):,}")
    with c2:
        hc_pct = raw_scorecard.get("high_critical_percent", high_critical_pct)
        st.metric("Critical / High Exposure", f"{hc_pct:.2f}%")
    with c3:
        dominant_risk_name = risk_counts.idxmax() if not risk_counts.empty else "N/A"
        st.metric("Prevailing Risk Tier", dominant_risk_name)
    with c4:
        st.metric("Primary Environmental Factor", "Climate Stress" if (climate_avg >= pest_avg and climate_avg >= disease_avg) else "Pest / Disease")

    st.write("")

    # 2. Risk Distribution Progress Breakdown & Indicator Gauges
    sc_col1, sc_col2 = st.columns([1.1, 1], gap="large")

    with sc_col1:
        with st.container(border=True):
            st.markdown("#### 🛡️ Risk Category Exposure Breakdown")
            st.caption("Proportion of selected field observations across standard severity classifications.")

            dist = raw_scorecard.get("risk_distribution", {})
            cat_styles = {
                "Low": ("#10b981", "#e6f9f1", "Safe / Optimal Management"),
                "Moderate": ("#f59e0b", "#fef8e7", "Standard Operational Caution"),
                "High": ("#f97316", "#fef3eb", "Targeted Intervention Required"),
                "Critical": ("#ef4444", "#fef2f2", "Urgent Priority Mitigation"),
            }

            for cat_name in ["Low", "Moderate", "High", "Critical"]:
                count = dist.get(cat_name, 0)
                share = (count / total_records * 100) if total_records else 0
                color, bg_color, description = cat_styles.get(cat_name, ("#15803d", "#f0fdf4", ""))

                st.markdown(
                    f"""
                    <div class="risk-bar-container">
                        <div class="risk-bar-label">
                            <span style="font-weight:700; color:#0f4629;">
                                <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:{color}; margin-right:6px;"></span>
                                {cat_name} Risk
                            </span>
                            <span style="font-weight:700; color:#0f4629;">{count:,} rows ({share:.1f}%)</span>
                        </div>
                        <div class="risk-bar-track">
                            <div class="risk-bar-fill" style="width:{share}%; background:{color};"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                """
                <div style="font-size:0.78rem; color:#5b7868; margin-top:0.6rem; padding-top:0.4rem; border-top:1px dashed #d5e6db;">
                    Classification thresholds reflect validated agronomic vulnerability indicators.
                </div>
                """,
                unsafe_allow_html=True,
            )

    with sc_col2:
        with st.container(border=True):
            st.markdown("#### 🧭 Core Vulnerability Index Scores")
            st.caption("Normalized metric benchmarks evaluated against optimal baseline conditions.")

            ic1, ic2 = st.columns(2)
            with ic1:
                st.markdown(
                    f"""
                    <div class="indicator-card">
                        <div style="font-size:0.8rem; font-weight:700; color:#5c7869;">🌡️ CLIMATE STRESS</div>
                        <div class="indicator-val">{climate_avg:.1f}</div>
                        <div class="indicator-tag" style="background:{'#fee2e2; color:#b91c1c' if climate_avg > 60 else '#e0f2fe; color:#0369a1'};">
                            {'High Severity' if climate_avg > 60 else 'Within Tolerances'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with ic2:
                st.markdown(
                    f"""
                    <div class="indicator-card">
                        <div style="font-size:0.8rem; font-weight:700; color:#5c7869;">🐛 PEST RISK</div>
                        <div class="indicator-val">{pest_avg:.1f}</div>
                        <div class="indicator-tag" style="background:{'#fee2e2; color:#b91c1c' if pest_avg > 60 else '#fef3c7; color:#92400e'};">
                            {'Active Threat' if pest_avg > 60 else 'Moderate Presence'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.write("")
            ic3, ic4 = st.columns(2)
            with ic3:
                st.markdown(
                    f"""
                    <div class="indicator-card">
                        <div style="font-size:0.8rem; font-weight:700; color:#5c7869;">🦠 DISEASE RISK</div>
                        <div class="indicator-val">{disease_avg:.1f}</div>
                        <div class="indicator-tag" style="background:#e6f4ea; color:#137333;">
                            {'Elevated' if disease_avg > 50 else 'Low Incidence'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with ic4:
                soil_txt = f"{moisture_avg:.1f}%" if pd.notna(moisture_avg) else "N/A"
                st.markdown(
                    f"""
                    <div class="indicator-card">
                        <div style="font-size:0.8rem; font-weight:700; color:#5c7869;">💧 SOIL MOISTURE</div>
                        <div class="indicator-val">{soil_txt}</div>
                        <div class="indicator-tag" style="background:#ecfdf5; color:#065f46;">
                            Mean Hydration
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # 3. Action Priority Leaderboard
    st.write("")
    with st.container(border=True):
        st.markdown("#### 📋 Prioritized Action Leaderboard")
        st.caption("Top 5 recommended farming mitigations ranked by empirical frequency in the selected cohort.")

        top_acts = raw_scorecard.get("top_actions", {})
        if top_acts:
            for rank, (act_text, act_count) in enumerate(top_acts.items(), 1):
                act_pct = (act_count / total_records * 100) if total_records else 0
                st.markdown(
                    f"""
                    <div class="action-row">
                        <div class="action-rank">#{rank}</div>
                        <div class="action-name">{act_text}</div>
                        <div class="action-badge">{act_count:,} farms ({act_pct:.1f}%)</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No recorded recommended actions found in this cohort.")

    # 4. Structured Technical JSON Export Expander
    with st.expander("🛠️ Inspect Structured Scorecard JSON"):
        st.json(raw_scorecard)


# --------------------------------------------------
# TAB 3: 🤖 AI ADVISORY
# --------------------------------------------------
with tab_advisory:
    st.markdown('<div class="section-title">Agricultural Risk Advisory & Guidance</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">Interactive query engine paired with authoritative agricultural guidance and structured citations.</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("#### 💬 Ask an Agricultural Advisory Question")

        # Quick Suggestion Chips
        st.caption("Select a prompt template or formulate your own inquiry below:")
        prompt_col1, prompt_col2, prompt_col3, prompt_col4 = st.columns(4)

        if prompt_col1.button("🐛 Pest Control Strategies", use_container_width=True):
            st.session_state["advisory_input_query"] = "What actions can help manage high pest risk?"
        if prompt_col2.button("🦠 Disease Mitigation", use_container_width=True):
            st.session_state["advisory_input_query"] = "How can farmers reduce disease risk?"
        if prompt_col3.button("🌡️ Climate & Heat Stress", use_container_width=True):
            st.session_state["advisory_input_query"] = "What factors contribute to high climate stress and how to adapt?"
        if prompt_col4.button("🌾 Regional Risk Summary", use_container_width=True):
            st.session_state["advisory_input_query"] = f"Summarize the main agricultural risks for {selected_country} and {selected_crop}."

        default_text = st.session_state.get("advisory_input_query", "")

        query_text = st.text_area(
            "Enter agricultural question:",
            value=default_text,
            placeholder="Type your agronomic question (e.g., 'What steps should be taken to mitigate high temperature stress in wheat?')...",
            height=100,
            key="user_agri_query_input",
        )

        active_query = query_text.strip()

        st.caption(f"Active Query Context: 🌍 **{selected_country}** · 🌾 **{selected_crop}** · 📅 **{selected_year}**")

        run_btn = st.button("✨ Retrieve Verified Advisory", type="primary", use_container_width=True)

        if run_btn:
            if not active_query:
                st.warning("Please enter a question or click one of the quick prompt suggestions above.")
            else:
                with st.spinner("🔍 Querying dataset insights and retrieving verified advisory citations..."):
                    try:
                        advisory_result = generate_answer(
                            active_query,
                            country=selected_country,
                            crop=selected_crop,
                        )
                        st.session_state["stored_advisory"] = advisory_result
                        st.session_state["stored_query"] = active_query
                    except Exception as err:
                        st.error(f"Advisory generation failed: {err}")

    # Display Response
    stored_result = st.session_state.get("stored_advisory")
    stored_q = st.session_state.get("stored_query")

    if stored_result and isinstance(stored_result, dict):
        with st.container(border=True):
            st.markdown("#### 🌿 Advisory Analysis")
            if stored_q:
                st.markdown(f"**Inquiry:** *\"{stored_q}\"*")

            answer_text = stored_result.get("answer", "")
            citations = stored_result.get("citations", [])

            # Split answer text before the raw citations if present to avoid duplication
            cleaned_answer = answer_text
            if "#### Retrieved agricultural guidance" in cleaned_answer:
                cleaned_answer = cleaned_answer.split("#### Retrieved agricultural guidance")[0].strip()

            st.markdown(cleaned_answer)

            # Structured Citations Cards
            if citations:
                st.markdown("---")
                st.markdown("#### 📚 Verified Advisory References & Citations")
                st.caption("Curated agronomic reference literature matching this inquiry:")

                for cite in citations:
                    ref_id = cite.get("id", "AGRI-REF")
                    topic = cite.get("topic", "Agricultural Advisory")
                    source = cite.get("source", "Standard Reference")
                    sim_score = cite.get("similarity", 0.0)
                    body_text = cite.get("text", "")
                    url = cite.get("url", "")

                    st.markdown(
                        f"""
                        <div class="citation-card">
                            <div class="citation-header">
                                <span class="citation-title">📄 {ref_id} — {topic}</span>
                                <span class="citation-score">{(sim_score * 100):.1f}% Relevance</span>
                            </div>
                            <div class="citation-text">{body_text}</div>
                            <div class="citation-meta"><b>Source:</b> {source}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if url and url.startswith(("http://", "https://")):
                        st.markdown(f"[🔗 View Authoritative Source Document ↗]({url})")

            st.info("⚠️ **Agronomic Notice**: Advisory recommendations are informational. Validate chemical, biological, and irrigation interventions with certified local agricultural extension services.")


# --------------------------------------------------
# TAB 4: 🔎 EXPLORE DATASET
# --------------------------------------------------
with tab_explore:
    st.markdown('<div class="section-title">Explore & Export Agricultural Dataset</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">Search, inspect individual field records, filter by attributes, and download filtered CSV extracts.</div>',
        unsafe_allow_html=True,
    )

    exp_col1, exp_col2, exp_col3 = st.columns([2, 1, 1])

    with exp_col1:
        search_query = st.text_input(
            "🔎 Search across text columns",
            placeholder="Type farm type, soil type, irrigation type, country...",
        )

    with exp_col2:
        risk_filter = st.selectbox(
            "Filter by Risk Level",
            options=["All Levels", "Low", "Moderate", "High", "Critical"],
            index=0,
        )

    with exp_col3:
        max_rows = st.selectbox(
            "Display Rows",
            options=[50, 100, 200, 500],
            index=1,
        )

    # Filter display records
    display_data = filtered_df.copy()

    if risk_filter != "All Levels" and "risk_category" in display_data.columns:
        display_data = display_data[display_data["risk_category"].astype(str).str.lower() == risk_filter.lower()]

    if search_query.strip():
        text_cols = display_data.select_dtypes(include=["object", "string"]).columns
        if len(text_cols) > 0:
            query_mask = display_data[text_cols].astype(str).apply(
                lambda s: s.str.contains(search_query, case=False, na=False)
            ).any(axis=1)
            display_data = display_data[query_mask]

    st.caption(f"Displaying **{min(len(display_data), max_rows):,}** of **{len(display_data):,}** matching records (Filtered from {total_rows:,} total).")

    # Interactive Dataframe
    st.dataframe(
        display_data.head(max_rows),
        use_container_width=True,
        hide_index=True,
    )

    # Export Download Button
    csv_bytes = display_data.to_csv(index=False).encode("utf-8")
    export_filename = f"agririsk_{selected_country}_{selected_crop}_{selected_year}.csv".replace(" ", "_")

    st.download_button(
        label=f"⬇️ Export {len(display_data):,} Records as CSV",
        data=csv_bytes,
        file_name=export_filename,
        mime="text/csv",
        type="primary",
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; padding:1rem 0; color:#5b7868; font-size:0.84rem;">
        🌱 <b>AgriRisk AI</b> · Agricultural Risk Intelligence & Decision Support Platform · Designed for Data-Driven Agriculture
    </div>
    """,
    unsafe_allow_html=True,
)
