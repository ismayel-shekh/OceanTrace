"""OceanTrace by ByteX | Visual-first UI. Data inputs and model-derived results are read-only."""
from __future__ import annotations

from pathlib import Path
import html as html_escape
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import folium
from streamlit.components.v1 import html as render_html

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
HOTSPOTS = DATA / "hotspots"
REGIONS = {
    "South China Sea": "south_china_sea",
    "Strait of Malacca": "strait_of_malacca",
    "Sulu–Celebes Sea": "sulu_celebes_sea",
}
COLORS = {"South China Sea": "#4EDBD0", "Strait of Malacca": "#FFB86B", "Sulu–Celebes Sea": "#8F9AFF"}
HOT_COLORS = {1: "#FFD36B", 2: "#FF934D", 3: "#FF647A"}
HOT_NAMES = {1: "Occasional", 2: "Recurring", 3: "Persistent"}
BASEMAP = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"

st.set_page_config(page_title="OceanTrace · by ByteX", page_icon="🌊", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --sea:#43E6CC; --ink:#071421; --panel:#11253A; --muted:#99AEC3; }
html { scroll-behavior:smooth; }
body, .stApp { font-family:'DM Sans',sans-serif; background: #071421; color:#EEF8FB; }
.stApp { background-image: radial-gradient(ellipse at 70% -10%,rgba(33,128,157,.17),transparent 34%), radial-gradient(ellipse at 2% 52%,rgba(20,86,117,.12),transparent 25%); }
.block-container {max-width:1300px;padding:1.25rem 2rem 4rem;}
header[data-testid="stHeader"] { background:transparent; }
h1,h2,h3 {font-family:'Manrope',sans-serif !important; letter-spacing:-.035em;}
h1 {font-weight:800 !important;}
[data-testid="stMarkdownContainer"] p {line-height:1.6;}
.stTabs [data-baseweb="tab-list"] {gap: .28rem; border-bottom:1px solid rgba(210,234,250,.14); overflow-x:auto;}
.stTabs [data-baseweb="tab"] {font-family:'DM Sans',sans-serif;font-weight:650; color:#A8BDD0; border-radius:12px 12px 0 0; padding:11px 15px;white-space:nowrap;}
.stTabs [aria-selected="true"] {color:#58E9D2 !important;background:rgba(67,230,204,.08);}
.stTabs [data-baseweb="tab-highlight"] {background-color:#43E6CC;}
.stTabs [data-baseweb="tab-border"] {background-color:transparent;}
[data-testid="stVerticalBlock"] > div {transition: background .3s ease;}
[data-testid="stSelectbox"] [data-baseweb="select"], [data-testid="stMultiSelect"] [data-baseweb="select"] {border-radius:13px;}
[data-testid="stMetric"] {background:rgba(18,43,63,.92);border:1px solid rgba(155,213,228,.14);border-radius:18px;padding:1rem;}
[data-testid="stMetricValue"] {color:#E8FBFA;font-family:'Manrope',sans-serif;font-weight:800;}
.stButton button[kind="primary"] {background:#43E6CC;color:#071421;border:none;border-radius:99px;font-weight:750;}
.stButton button {border-radius:12px;}
[data-testid="stExpander"] {border:1px solid rgba(170,215,234,.14);background:rgba(13,33,49,.75);border-radius:13px;}
[data-testid="stDataFrame"], [data-testid="stPlotlyChart"] {border-radius:18px;overflow:hidden;}
.bytex-top {display:flex;align-items:center;justify-content:space-between;gap:12px;padding:8px 0 22px;flex-wrap:wrap;}
.bytex-logo {font-family:'Manrope',sans-serif;font-size:1.3rem;font-weight:800;letter-spacing:-.05em;color:#F4FAFE;}
.bytex-logo span {color:#43E6CC;}
.bytex-byline {font-size:.85rem;font-weight:650;color:#95AFC5;letter-spacing:.02em;}
.bytex-live {border:1px solid rgba(67,230,204,.27);color:#9DF9E9;border-radius:99px;padding:7px 12px;background:rgba(67,230,204,.06);font-size:.74rem;font-weight:750;}
.bytex-dot {display:inline-block;width:7px;height:7px;border-radius:50%;background:#43E6CC;box-shadow:0 0 14px #43E6CC;margin-right:7px;animation:glow 2.4s infinite;}
.hero {position:relative;overflow:hidden;background:linear-gradient(124deg,#10314B 1%,#0C2137 45%,#073947 100%);border:1px solid rgba(110,195,210,.21);border-radius:28px;padding:clamp(26px,5vw,62px) clamp(25px,5vw,64px);min-height:300px;box-shadow:0 26px 60px rgba(0,0,0,.14);}
.hero:before {content:"";position:absolute;width:390px;height:390px;right:-40px;top:-55px;border-radius:50%;background:radial-gradient(circle at 48% 45%, rgba(74,233,213,.11),rgba(69,164,192,.08) 33%,transparent 34%),repeating-radial-gradient(circle at 48% 45%,transparent 0 30px,rgba(81,231,207,.16) 31px 32px,transparent 33px 57px);animation:orbit 20s ease-in-out infinite alternate;pointer-events:none;}
.hero:after {content:"";position:absolute;width:440px;height:175px;right:-25px;bottom:-84px;background:linear-gradient(135deg,rgba(48,194,183,.12),rgba(46,104,157,.02));border:1px solid rgba(100,209,216,.17);border-radius:50%;transform:rotate(-17deg);pointer-events:none;}
.hero-kicker {position:relative;z-index:1;color:#77F5DE;letter-spacing:.18em;font-weight:800;font-size:.72rem;text-transform:uppercase;}
.hero-headline {position:relative;z-index:1;font-family:'Manrope',sans-serif;font-weight:800;font-size:clamp(2.1rem,4.6vw,4.3rem);line-height:1.1;letter-spacing:-.065em;max-width:720px;margin:13px 0 17px;animation:rise .7s ease-out both;}
.hero-headline em {font-style:normal;color:#56E6D1;}
.hero-copy {position:relative;z-index:1;color:#BDD6E1;font-size:clamp(.99rem,1.3vw,1.15rem);max-width:610px;line-height:1.6;margin:0 0 24px;}
.hero-tags {position:relative;z-index:1;display:flex;flex-wrap:wrap;gap:8px;}
.hero-tag {border:1px solid rgba(162,220,225,.24);border-radius:99px;padding:8px 12px;font-size:.76rem;font-weight:650;color:#D7E8EE;background:rgba(255,255,255,.04);}
.section-kicker {color:#68E9D7;font-weight:800;letter-spacing:.17em;text-transform:uppercase;font-size:.69rem;margin:24px 0 10px;}
.section-head {font-family:'Manrope',sans-serif;font-weight:800;font-size:clamp(1.4rem,2.4vw,2.1rem);letter-spacing:-.05em;margin:5px 0 14px;}
.intro {color:#A6BECF;font-size:.98rem;max-width:870px;line-height:1.65;margin:0 0 15px;}
.stat-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px;margin:20px 0 27px;}
.stat-tile {background:linear-gradient(160deg,rgba(24,57,78,.85),rgba(12,32,49,.85));border:1px solid rgba(128,202,215,.18);border-radius:20px;padding:20px;transition:transform .22s ease,border-color .22s ease;animation:rise .6s both;}
.stat-tile:hover {transform:translateY(-4px);border-color:rgba(92,227,206,.43);}
.stat-label {color:#9DB5C6;font-size:.78rem;font-weight:650;margin-bottom:12px;}
.stat-num {font:800 clamp(1.55rem,2.9vw,2.2rem) 'Manrope',sans-serif;letter-spacing:-.06em;color:#F2FCFE;}
.stat-sub {color:#73CBBB;font-size:.76rem;margin-top:8px;}
.insight {border:1px solid rgba(80,223,205,.23);background:linear-gradient(95deg,rgba(67,230,204,.09),rgba(67,230,204,.025));border-radius:18px;padding:17px 20px;margin:16px 0;color:#D4E8ED;}
.insight b {color:#70F0DD;}
.insight strong {color:#EAFDFA;}
.reading {display:flex;gap:14px;background:rgba(15,37,54,.7);border:1px solid rgba(151,200,215,.14);border-radius:16px;padding:16px 18px;margin:10px 0 22px;}
.reading .reading-icon {font-size:1.3rem;line-height:1.4;}
.reading b {display:block;color:#E8F8F9;font-size:.92rem;margin-bottom:4px;}
.reading p {color:#AEC6D1;font-size:.88rem;line-height:1.55;margin:0;}
.story-grid {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:13px;margin:18px 0 25px;}
.story-card {background:rgba(16,40,60,.78);border:1px solid rgba(154,216,224,.14);border-radius:18px;padding:22px;transition:transform .2s ease;}
.story-card:hover {transform:translateY(-3px);}
.story-icon {font-size:1.55rem;margin-bottom:12px;}
.story-title {font-family:'Manrope',sans-serif;font-weight:800;font-size:1.02rem;margin-bottom:8px;}
.story-copy {font-size:.84rem;color:#A9C1D0;line-height:1.65;}
.chip {display:inline-block;background:rgba(67,230,204,.08);border:1px solid rgba(67,230,204,.25);border-radius:99px;color:#8DF3E3;font-weight:700;font-size:.72rem;padding:6px 10px;margin:5px 4px 5px 0;}
.footer {border-top:1px solid rgba(143,196,210,.16);margin-top:44px;padding:22px 0;color:#8BA9B9;font-size:.82rem;display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;}
@keyframes rise {from {transform:translateY(14px);opacity:0} to {transform:translateY(0);opacity:1}}
@keyframes glow {50% {opacity:.55;box-shadow:0 0 3px #43E6CC}}
@keyframes orbit {to {transform:translate(-22px,20px) rotate(8deg)}}
@media(max-width:900px){.stat-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.story-grid{grid-template-columns:1fr 1fr}.block-container{padding:1rem 1rem 3rem}.hero:before{opacity:.45}}
@media(max-width:600px){.hero{min-height:245px;border-radius:22px}.stat-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.stat-tile{padding:15px}.stat-num{font-size:1.6rem}.story-grid{grid-template-columns:1fr}.hero-tags{gap:6px}.hero-tag{font-size:.68rem}.bytex-byline{font-size:.72rem}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
</style>
""", unsafe_allow_html=True)


def panel_reading(title: str, text: str, icon: str = "✦") -> None:
    st.markdown(f'<div class="reading"><div class="reading-icon">{icon}</div><div><b>{html_escape.escape(title)}</b><p>{html_escape.escape(text)}</p></div></div>', unsafe_allow_html=True)


def heading(kicker: str, title: str, subtitle: str = "") -> None:
    st.markdown(f'<div class="section-kicker">{html_escape.escape(kicker)}</div><div class="section-head">{html_escape.escape(title)}</div>' + (f'<p class="intro">{html_escape.escape(subtitle)}</p>' if subtitle else ""), unsafe_allow_html=True)


def stat_tile(label: str, value: str, detail: str) -> str:
    return f'<div class="stat-tile"><div class="stat-label">{html_escape.escape(label)}</div><div class="stat-num">{html_escape.escape(value)}</div><div class="stat-sub">{html_escape.escape(detail)}</div></div>'


def charts_style(fig: go.Figure, height: int = 390, ytitle: str | None = None) -> go.Figure:
    fig.update_layout(
        height=height, margin=dict(l=12, r=15, t=18, b=45),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#AFCCDB", size=12),
        hoverlabel=dict(bgcolor="#153247", font_color="#F3FFFF"),
        hovermode="x unified", legend=dict(orientation="h", y=1.12, x=0, font_size=11),
        xaxis=dict(showgrid=False, linecolor="rgba(159,203,221,.16)", tickfont=dict(color="#91ABBC")),
        yaxis=dict(gridcolor="rgba(159,203,221,.10)", zerolinecolor="rgba(159,203,221,.25)", tickfont=dict(color="#91ABBC")),
    )
    if ytitle:
        fig.update_yaxes(title_text=ytitle)
    return fig


@st.cache_data(show_spinner=False)
def load_csv(name: str, parse_date: str | None = None) -> pd.DataFrame:
    return pd.read_csv(DATA / name, parse_dates=[parse_date] if parse_date else None)


@st.cache_data(show_spinner=False)
def load_hotspot(key: str) -> dict[str, np.ndarray]:
    with np.load(HOTSPOTS / f"{key}_persistence.npz", allow_pickle=False) as d:
        return {k: d[k].copy() for k in d.files}


def data_guard() -> None:
    required = [DATA / "monthly_global_timeseries.csv", DATA / "regional_ocean_masked_timeseries.csv"]
    required += [HOTSPOTS / f"{key}_persistence.npz" for key in REGIONS.values()]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.is_file()]
    if missing:
        st.error("Dashboard data not found: " + ", ".join(missing))
        st.info("Keep your existing data/ directory and replace only streamlit_app.py and .streamlit/config.toml. Or run the original Colab export script.")
        st.stop()


data_guard()
monthly = load_csv("monthly_global_timeseries.csv", "month").sort_values("month").copy()
regional = load_csv("regional_ocean_masked_timeseries.csv", "date").sort_values(["region", "date"]).copy()
regional["display_region"] = regional["region"].replace({"Sulu-Celebes Sea": "Sulu–Celebes Sea"})

st.markdown('<div class="bytex-top"><div class="bytex-logo">◉ OCEAN<span>TRACE</span> <span style="font-size:.75rem;letter-spacing:0;font-weight:700;color:#9BB8C9">/ ByteX</span></div><div class="bytex-live"><span class="bytex-dot"></span>NASA CYGNSS · Research explorer</div></div>', unsafe_allow_html=True)

st.markdown('''<div class="hero"><div class="hero-kicker">TEAM BYTEX PRESENTS · OCEAN INTELLIGENCE</div><div class="hero-headline">The ocean has a story.<br><em>Let's make it visible.</em></div><p class="hero-copy">Explore where satellite-derived microplastic estimates are elevated, how they change through time, and how much evidence supports them.</p><div class="hero-tags"><span class="hero-tag">🌊 2018–2026</span><span class="hero-tag">◉ 3 marine study regions</span><span class="hero-tag">✧ Built from NASA CYGNSS data</span></div></div>''', unsafe_allow_html=True)

nav = st.tabs(["✦ Discover", "◷ Time machine", "◈ Explore regions", "◎ Hotspot map", "? Learn in 60 seconds"])

with nav[0]:
    heading("01 / The big picture", "See the ocean differently", "A quick way to understand the patterns—not a wall of scientific jargon.")
    st.markdown('<div class="stat-grid">' + "".join([
        stat_tile("Monthly snapshots", f"{len(monthly):,}", "2018–2026 overview"),
        stat_tile("Ocean regions", str(len(REGIONS)), "Malaysia & surrounding seas"),
        stat_tile("Satellite latitude belt", "±37°", "Not the whole world's oceans"),
        stat_tile("Hotspot approach", "P90 / P95", "Relative rank, not risk score"),
    ]) + '</div>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly["month"], y=monthly["global_mean_concentration"], name="Estimated concentration", mode="lines", line=dict(color="#55E6D4", width=3), fill="tozeroy", fillcolor="rgba(85,230,212,.07)", hovertemplate="%{x|%b %Y}<br>%{y:,.0f} count/km²<extra></extra>"))
    charts_style(fig, 380, "Estimate (count/km²)")
    st.plotly_chart(fig, width="stretch", theme=None, config={"displayModeBar": False})
    panel_reading("How to read this line", "Each point is a monthly summary of CYGNSS estimates within its satellite coverage. Higher means a higher estimated value—not a confirmed rise in real ocean plastic.", "📈")
    st.markdown('''<div class="story-grid"><div class="story-card"><div class="story-icon">🛰️</div><div class="story-title">Satellite signals</div><div class="story-copy">CYGNSS measures ocean-surface scattering. Researchers infer possible microplastic-related patterns from these signals.</div></div><div class="story-card"><div class="story-icon">📍</div><div class="story-title">Regional snapshots</div><div class="story-copy">Choose a sea to compare satellite estimates and see how complete the available observations are.</div></div><div class="story-card"><div class="story-icon">🔎</div><div class="story-title">Recurring patterns</div><div class="story-copy">Find places that repeatedly ranked high relative to nearby observed cells—not officially designated pollution hotspots.</div></div></div>''', unsafe_allow_html=True)
    st.markdown('<div class="insight"><b>THE BIG TAKEAWAY</b><br><strong>Patterns are not proof.</strong> OceanTrace helps you ask better questions about the ocean, while showing where the data are uncertain.</div>', unsafe_allow_html=True)

with nav[1]:
    heading("02 / Time machine", "Travel through the data", "See what the satellite-based estimates suggest at different points in time.")
    left, right = st.columns([1.3, 1], gap="large")
    with left:
        display_mode = st.radio("What would you like to see?", ["Concentration", "Above / below typical"], horizontal=True, key="time_mode")
    with right:
        animate = st.toggle("Enable animated timeline", value=False, help="Adds a play button to trace the data month by month.")
    df = monthly.copy()
    df["rolling"] = df["global_mean_concentration"].rolling(12, min_periods=12).mean()
    reference = df.loc[df["month"].dt.year.between(2019, 2025), "global_mean_concentration"].mean()
    df["anomaly"] = df["global_mean_concentration"] - reference
    df["month_label"] = df["month"].dt.strftime("%b %Y")
    fig = go.Figure()
    if display_mode == "Concentration":
        fig.add_trace(go.Scatter(x=df["month"], y=df["global_mean_concentration"], mode="lines", line=dict(color="#54E6D1", width=3), name="Monthly estimate", hovertemplate="%{x|%b %Y}<br>%{y:,.0f} count/km²<extra></extra>"))
        fig.add_trace(go.Scatter(x=df["month"], y=df["rolling"], mode="lines", line=dict(color="#FFCA82", width=3), name="12-month smoother", hovertemplate="%{x|%b %Y}<br>%{y:,.0f} count/km²<extra></extra>"))
        y_label = "Estimated count/km²"
    else:
        shades = ["#65DDC7" if value >= 0 else "#A3A8FA" for value in df["anomaly"]]
        fig.add_trace(go.Bar(x=df["month"], y=df["anomaly"], marker_color=shades, name="Difference", hovertemplate="%{x|%b %Y}<br>%{y:+,.0f} count/km²<extra></extra>"))
        fig.add_hline(y=0, line_color="rgba(225,245,255,.6)", line_width=1)
        y_label = "Difference from reference"
    if animate:
        # Frames change only display visibility; underlying source values remain untouched.
        source_y = df["global_mean_concentration"].to_numpy() if display_mode == "Concentration" else df["anomaly"].to_numpy()
        if display_mode == "Concentration":
            fig.data[0].x = df["month"].iloc[:1]
            fig.data[0].y = source_y[:1]
            fig.data[1].visible = False
            fig.frames = [go.Frame(name=str(i), data=[go.Scatter(x=df["month"].iloc[:i+1], y=source_y[:i+1], mode="lines", line=dict(color="#54E6D1", width=3))], traces=[0]) for i in range(len(df))]
        else:
            fig.data[0].x = df["month"].iloc[:1]
            fig.data[0].y = source_y[:1]
            fig.frames = [go.Frame(name=str(i), data=[go.Bar(x=df["month"].iloc[:i+1], y=source_y[:i+1], marker_color=shades[:i+1])], traces=[0]) for i in range(len(df))]
        fig.update_layout(updatemenus=[dict(type="buttons", showactive=False, x=.02, y=1.17, buttons=[dict(label="▶ Play timeline", method="animate", args=[None, {"frame":{"duration":110,"redraw":True}, "transition":{"duration":0}, "fromcurrent":True, "mode":"immediate"}]), dict(label="Ⅱ Pause", method="animate", args=[[None],{"mode":"immediate", "frame":{"duration":0}, "transition":{"duration":0}}])])])
        fig.update_xaxes(range=[df["month"].min(), df["month"].max()])
        fig.update_yaxes(range=[float(np.nanmin(source_y))-max(12,float(np.nanstd(source_y))*.3), float(np.nanmax(source_y))+max(12,float(np.nanstd(source_y))*.3)])
    charts_style(fig, 440, y_label)
    st.plotly_chart(fig, width="stretch", theme=None, config={"displayModeBar": False})
    panel_reading("What does this mean?" if display_mode == "Concentration" else "What's above or below typical?", "The smooth gold line helps show longer patterns, but does not prove plastic pollution is changing." if display_mode == "Concentration" else "Teal means above the 2019–2025 reference average; purple means below. These bars show differences in estimates, not environmental safety levels.", "💡")
    with st.expander("Curious about the numbers?"):
        st.caption("The underlying 99 monthly summary records are unchanged. Each daily CYGNSS file uses a centered 30-day retrieval window. Neighboring days overlap; the global monthly series averages those daily products.")
        st.dataframe(df[["month", "global_mean_concentration", "anomaly"]].rename(columns={"month":"Month", "global_mean_concentration":"Estimated count/km²", "anomaly":"Difference from reference"}), hide_index=True, width="stretch")

with nav[2]:
    heading("03 / Regional intelligence", "Three seas. Different stories.", "Compare the same type of satellite indicator across nearby seas—while keeping data coverage in view.")
    options = list(REGIONS)
    selected = st.multiselect("Choose the regions to compare", options, default=options, key="region_select")
    if not selected:
        st.info("Choose at least one sea to start the comparison.")
    else:
        visible = regional[regional["display_region"].isin(selected)].copy()
        tiles = []
        summary = visible.groupby("display_region", sort=False).agg(mean_est=("mean_concentration","mean"), mean_cov=("coverage_percent","mean"))
        for name in selected:
            mean_est = float(summary.loc[name,"mean_est"])
            mean_cov = float(summary.loc[name,"mean_cov"])
            tiles.append(stat_tile(name, f"{mean_est:,.0f}", f"count/km² · {mean_cov:.0f}% mean coverage"))
        st.markdown('<div class="stat-grid" style="grid-template-columns:repeat(auto-fit,minmax(200px,1fr))">' + "".join(tiles) + '</div>', unsafe_allow_html=True)
        comparison = go.Figure()
        for name in selected:
            sub = visible[visible["display_region"] == name]
            comparison.add_trace(go.Scatter(x=sub["date"], y=sub["mean_concentration"], mode="lines", name=name, line=dict(color=COLORS[name], width=2.6), hovertemplate="%{x|%b %Y}<br>%{y:,.0f} count/km²<extra></extra>"))
        charts_style(comparison, 420, "Estimated count/km²")
        st.plotly_chart(comparison, width="stretch", theme=None, config={"displayModeBar": False})
        panel_reading("How to read these lines", "Each colour represents one sea. A higher line means a higher estimated concentration in its observed cells—not necessarily more plastic across the whole sea. The study areas are approximate rectangles.", "🌊")
        with st.expander("Show observation coverage (why some readings need caution)", expanded=True):
            cover = go.Figure()
            for name in selected:
                sub = visible[visible["display_region"] == name]
                cover.add_trace(go.Scatter(x=sub["date"], y=sub["coverage_percent"], name=name, mode="lines", line=dict(color=COLORS[name], width=2.5), hovertemplate="%{x|%b %Y}<br>%{y:.1f}% observed grid coverage<extra></extra>"))
            cover.update_yaxes(range=[0,100])
            charts_style(cover, 295, "Valid ocean grid cells (%)")
            st.plotly_chart(cover, width="stretch", theme=None, config={"displayModeBar": False})
            panel_reading("Why coverage matters", "If a region has fewer valid ocean cells, its average describes a smaller observed area. Low coverage does not mean the sea has less plastic.", "🧭")
        with st.expander("Advanced: statistical trend evidence"):
            hac = DATA / "hac_trend_validation.csv"
            if hac.is_file():
                st.dataframe(load_csv("hac_trend_validation.csv").round(4), hide_index=True, width="stretch")
                st.caption("No statistically significant regional linear trend was established by the supplied HAC screening. This is not proof of no change.")
            else:
                st.caption("No statistical detail file in this deployment.")

with nav[3]:
    heading("04 / Hotspot explorer", "Where patterns keep returning", "Explore locations that repeatedly appeared among the highest estimated values in their own region.")
    a, b = st.columns([1.5, 1], gap="large")
    with a:
        region_name = st.selectbox("Choose an ocean region", list(REGIONS), key="hot_region")
    with b:
        threshold = st.radio("Hotspot threshold", ["P90", "P95"], horizontal=True, key="hot_threshold")
    d = load_hotspot(REGIONS[region_name])
    p = d["persistence90" if threshold == "P90" else "persistence95"]
    cat = d["classification90" if threshold == "P90" else "classification95"]
    count = d["hotspot90_count" if threshold == "P90" else "hotspot95_count"]
    obs = d["eligible_observations"]
    mean = d["mean_concentration"]
    lat, lon = d["latitude"], d["longitude"]
    st.markdown('<div class="stat-grid" style="grid-template-columns:repeat(3,minmax(0,1fr))">' + "".join([
        stat_tile("Persistent cells", str(int((cat==3).sum())), "High in ≥50% of qualified months"),
        stat_tile("Recurring cells", str(int((cat==2).sum())), "High in 25%–<50% of months"),
        stat_tile("Qualified cells", f"{int((obs>=12).sum()):,}", "At least 12 qualified months"),
    ]) + '</div>', unsafe_allow_html=True)
    choices = st.multiselect("Which locations should appear on the map?", ["Persistent", "Recurring", "Occasional"], default=["Persistent", "Recurring"], key="hot_choice")
    m = folium.Map(location=[float(lat.mean()), float(lon.mean())], zoom_start=6, tiles=None, prefer_canvas=True, control_scale=True)
    folium.TileLayer(tiles=BASEMAP, attr="Tiles © Esri", name="Esri street map", overlay=False, control=True).add_to(m)
    for category in [3,2,1]:
        if HOT_NAMES[category] not in choices:
            continue
        layer = folium.FeatureGroup(name=HOT_NAMES[category], show=True)
        ii,jj = np.where(cat==category)
        for i,j in zip(ii,jj):
            label = (f"<b>{html_escape.escape(region_name)}</b><hr>"
                     f"<b>{HOT_NAMES[category]} · {threshold}</b><br>"
                     f"Latitude {lat[i]:.2f}°, longitude {lon[j]:.2f}°<br>"
                     f"Ranked high in <b>{count[i,j]} of {obs[i,j]}</b> qualified months<br>"
                     f"Persistence: <b>{p[i,j]:.1f}%</b><br>"
                     f"Average CYGNSS estimate: {mean[i,j]:,.0f} count/km²<br>"
                     f"<small>Relative hotspot—not a verified pollution risk</small>")
            folium.CircleMarker(location=[float(lat[i]),float(lon[j])], radius=4 if category==3 else 2.5,
                color=HOT_COLORS[category], fill=True, fill_color=HOT_COLORS[category], fill_opacity=.75,
                weight=.55, tooltip=f"{HOT_NAMES[category]} · {p[i,j]:.0f}%", popup=folium.Popup(label,max_width=300)).add_to(layer)
        layer.add_to(m)
    folium.LayerControl(collapsed=True).add_to(m)
    m.fit_bounds([[float(lat.min()),float(lon.min())],[float(lat.max()),float(lon.max())]])
    render_html(m.get_root().render(),height=565,scrolling=False)
    panel_reading("What do the coloured dots mean?", "Red = frequently among the highest values (≥50% of qualified months). Orange = sometimes (25–<50%). Yellow = occasionally (>0–<25%). Tap a dot to see how many observations support it.", "📍")
    with st.expander("What's a P90 or P95 hotspot?"):
        st.write("P90 means the top 10% of eligible cells **within that same region and month**; P95 is the top 5%. These are relative rankings, not pollution danger thresholds. A cell needs at least 30 supporting samples in a month and 12 qualified months to receive a persistence category.")
        st.caption("The CYGNSS 0.25° grid represents overlapping ~1° retrieval footprints. Nearby dots are not independent measurement sites. An external Esri map layer provides the basemap.")

with nav[4]:
    heading("05 / In plain language", "The science, without the jargon", "Four quick ideas are enough to start exploring OceanTrace confidently.")
    st.markdown('''<div class="story-grid"><div class="story-card"><div class="story-icon">🛰️</div><div class="story-title">01 · What does NASA observe?</div><div class="story-copy">CYGNSS picks up signals scattered from the sea surface. Researchers look for patterns in roughness that may relate to floating microplastics.</div></div><div class="story-card"><div class="story-icon">🌍</div><div class="story-title">02 · Is it the whole ocean?</div><div class="story-copy">No. CYGNSS spans roughly 37° south to 37° north. Missing areas are not zero-pollution areas.</div></div><div class="story-card"><div class="story-icon">📊</div><div class="story-title">03 · Is a high number dangerous?</div><div class="story-copy">Not necessarily. It is a satellite-derived estimate—not a safety rating or a direct count of plastic particles.</div></div><div class="story-card"><div class="story-icon">🔁</div><div class="story-title">04 · What's a recurring hotspot?</div><div class="story-copy">A location that often ranks among the higher estimated cells in its region when enough observations are available.</div></div><div class="story-card"><div class="story-icon">🧪</div><div class="story-title">05 · Can other things affect it?</div><div class="story-copy">Yes. Waves, wind, organic surface material, oil and other conditions can influence the signal.</div></div><div class="story-card"><div class="story-icon">✅</div><div class="story-title">06 · Did pollution increase?</div><div class="story-copy">The preliminary regional analyses did not establish a statistically significant trend. That does not prove the ocean is unchanged.</div></div></div>''', unsafe_allow_html=True)
    st.markdown('<div class="insight"><b>REMEMBER</b><br><strong>OceanTrace is a guide to questions—not a final verdict on plastic pollution.</strong> Our goal is to make satellite evidence understandable to more people.</div>', unsafe_allow_html=True)
    with st.expander("Read the full scientific methodology"):
        st.markdown("""
**Dataset.** NASA PO.DAAC CYGNSS Level 3 Ocean Microplastic Concentration v3.2, covering the observations used here from August 2018 through October 2026.

**Observation design.** The time-series chart uses monthly means derived from daily products; each daily estimate contains a centered 30-day rolling window. Hotspot analysis uses one representative 30-day-centered granule per month (99 selected observations), not independent full-calendar-month measurements.

**Footprints.** The underlying retrieval is approximately 1° even though values are available every 0.25°. Neighbouring grid cells overlap spatially and are not independent observations.

**Regional masks.** Study areas are approximate geographic windows with Natural Earth land masks, not official marine boundaries. Coverage uses cells with valid NASA retrievals within each study area.

**Hotspot rule.** Within each region and selected month, a cell ranks at or above its observed P90/P95 concentration threshold if it has at least 30 samples. The persistence denominator is the number of months that cell qualifies. Classification requires at least 12 qualified months; occasional >0–<25%, recurring 25–<50%, persistent ≥50%.

**Quality.** `num_mp_samples` is a retrieval support count. `stddev_mp_samples` is a dimensionless geometric standard deviation—not a confidence interval or proof of measurement accuracy.

**Interpretation.** Surface roughness may be influenced by ocean weather, biology, oil and other causes. The provided initial statistical screening did not establish a significant regional long-term trend; it did not prove absence of change. OceanTrace is an educational exploratory analysis, not an official NASA assessment.
""")

st.markdown('<div class="footer"><span>© Team ByteX · OceanTrace · NASA Space Apps Challenge</span><span>Satellite-derived estimates · August 2018–October 2026 · Not an official NASA product</span></div>', unsafe_allow_html=True)
