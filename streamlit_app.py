"""OceanTrace public dashboard — ByteX branded UI.
Scientific CSV/NPZ exports are read-only inputs; this app does not retrain or modify model outputs.
"""
from pathlib import Path
import base64
import html
import json
import re

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit.components.v1 import html as embed_html
import folium

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
HOTSPOTS = DATA / "hotspots"
BYTEX_LOGO = BASE / "assets" / "bytex_logo.png"
BYTEX_LOGO_B64 = base64.b64encode(BYTEX_LOGO.read_bytes()).decode("ascii") if BYTEX_LOGO.exists() else ""

REGIONS = {
    "South China Sea": "south_china_sea",
    "Strait of Malacca": "strait_of_malacca",
    "Sulu–Celebes Sea": "sulu_celebes_sea",
}
CLASS_COLORS = {1: "#F4C95D", 2: "#F77F00", 3: "#D62828"}
CLASS_NAMES = {1: "Occasional", 2: "Recurring", 3: "Persistent"}

# ByteX brand palette: red + warm off-white.
BRAND_RED = "#E31837"
BRAND_RED_DARK = "#B5122B"
OFF_WHITE = "#FFF9F7"
CARD_WHITE = "#FFFFFF"
INK = "#282329"
MUTED = "#71656A"
BORDER = "#EADDE0"
GRID = "#E9E0E2"
SECONDARY = "#9A7D85"

st.set_page_config(
    page_title="OceanTrace | ByteX",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    f"""
    <style>
    :root {{
      --ot-red: {BRAND_RED};
      --ot-red-dark: {BRAND_RED_DARK};
      --ot-bg: {OFF_WHITE};
      --ot-card: {CARD_WHITE};
      --ot-ink: {INK};
      --ot-muted: {MUTED};
      --ot-border: {BORDER};
    }}
    html, body, [data-testid="stAppViewContainer"] {{
      background: var(--ot-bg);
      color: var(--ot-ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    /* Keep the page content safely below Streamlit's fixed top toolbar. */
    [data-testid="stHeader"] {{
      background: rgba(255,249,247,.98);
      border-bottom: 1px solid var(--ot-border);
      min-height: 3.25rem;
      z-index: 1001;
    }}
    [data-testid="stToolbar"] {{
      top: .15rem;
    }}
    .block-container {{
      max-width: 1440px;
      padding-top: 4.35rem !important;
      padding-bottom: 3rem;
    }}
    h1, h2, h3, h4 {{
      color: var(--ot-ink) !important;
      letter-spacing: -0.025em;
    }}
    h1 {{ font-weight: 800 !important; }}
    h2, h3 {{ font-weight: 750 !important; }}
    p, li, label, [data-testid="stCaptionContainer"] {{
      color: var(--ot-ink);
    }}
    [data-testid="stCaptionContainer"] p {{
      color: var(--ot-muted) !important;
    }}
    .bytex-topline {{
      display:flex; align-items:center; gap:.9rem;
      width:fit-content; max-width:100%;
      margin:.15rem 0 1.2rem 0;
      padding:.55rem .9rem .55rem .55rem;
      background:#FFFFFF;
      border:1px solid var(--ot-border);
      border-radius:16px;
      box-shadow:0 8px 24px rgba(53,26,34,.07);
      position:relative; z-index:2;
    }}
    .bytex-logo {{
      display:block; flex:0 0 54px;
      width:54px; height:54px; object-fit:cover;
      border-radius:15px;
      border:1px solid rgba(227,24,55,.12);
      box-shadow:0 7px 18px rgba(227,24,55,.20);
      background:#E31837;
    }}
    .bytex-wordmark {{
      font-size:.76rem; line-height:1.25; font-weight:900;
      letter-spacing:.13em; text-transform:uppercase; color:var(--ot-red) !important;
      opacity:1 !important;
    }}
    .bytex-submark {{
      margin-top:.18rem; font-size:.88rem; color:#493A40 !important;
      font-weight:700; letter-spacing:.01em; opacity:1 !important;
    }}
    [data-testid="stMetric"] {{
      background:var(--ot-card);
      border:1px solid var(--ot-border);
      border-radius:16px;
      padding:1rem 1.05rem;
      box-shadow:0 5px 18px rgba(53,26,34,.035);
      animation:ot-rise .55s ease both;
    }}
    [data-testid="stMetricLabel"] {{ color:var(--ot-muted) !important; }}
    [data-testid="stMetricValue"] {{
      color:var(--ot-red) !important;
      font-size:1.75rem !important;
      font-weight:800 !important;
    }}
    /* Make the five main sections read as clear, tappable navigation cards. */
    [data-testid="stTabs"] [role="tablist"] {{
      display:flex; flex-wrap:wrap; gap:.62rem;
      border-bottom:0 !important;
      padding:.35rem .05rem .85rem;
      overflow:visible;
    }}
    [data-testid="stTabs"] [role="tab"],
    [data-testid="stTabs"] button[data-baseweb="tab"] {{
      flex:1 1 auto;
      min-height:58px;
      padding:.78rem 1rem !important;
      border:1px solid var(--ot-border) !important;
      border-radius:14px !important;
      background:#FFFFFF !important;
      color:#47383E !important;
      font-weight:750 !important;
      white-space:normal;
      box-shadow:0 4px 13px rgba(53,26,34,.045);
      transition:transform .18s ease, border-color .18s ease, box-shadow .18s ease, background .18s ease;
    }}
    [data-testid="stTabs"] [role="tab"] p,
    [data-testid="stTabs"] button[data-baseweb="tab"] p {{
      color:inherit !important; font-weight:750 !important;
    }}
    [data-testid="stTabs"] [role="tab"]:hover,
    [data-testid="stTabs"] button[data-baseweb="tab"]:hover {{
      border-color:#EFA5B2 !important;
      background:#FFF5F6 !important;
      box-shadow:0 7px 18px rgba(227,24,55,.09);
      transform:translateY(-2px);
    }}
    [data-testid="stTabs"] [role="tab"][aria-selected="true"],
    [data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {{
      color:var(--ot-red) !important;
      background:#FCE9ED !important;
      border:1.5px solid var(--ot-red) !important;
      box-shadow:0 6px 18px rgba(227,24,55,.12);
    }}
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] p {{
      color:var(--ot-red) !important;
    }}
    [data-testid="stTabs"] [data-baseweb="tab-highlight"],
    [data-testid="stTabs"] [data-baseweb="tab-border"] {{
      display:none !important;
      background:transparent !important;
    }}
    [data-testid="stTabs"] [role="tab"]:focus-visible {{
      outline:3px solid rgba(227,24,55,.32) !important;
      outline-offset:2px;
    }}
    .stButton button, [data-testid="stDownloadButton"] button {{
      border-radius:999px;
      border:1px solid var(--ot-red);
      background:var(--ot-red);
      color:#fff;
      font-weight:750;
      transition:transform .18s ease, box-shadow .18s ease, background .18s ease;
    }}
    .stButton button:hover, [data-testid="stDownloadButton"] button:hover {{
      background:var(--ot-red-dark);
      border-color:var(--ot-red-dark);
      color:#fff;
      transform:translateY(-1px);
      box-shadow:0 7px 18px rgba(227,24,55,.18);
    }}
    [data-testid="stAlert"] {{
      border-radius:14px;
      border:1px solid var(--ot-border);
    }}
    [data-testid="stExpander"] {{
      background:var(--ot-card);
      border:1px solid var(--ot-border);
      border-radius:14px;
    }}
    [data-testid="stDataFrame"], [data-testid="stTable"] {{
      border:1px solid var(--ot-border);
      border-radius:12px;
      overflow:hidden;
    }}
    [data-testid="stRadio"] label, [data-testid="stMultiSelect"] label,
    [data-testid="stSelectbox"] label, [data-testid="stToggle"] label {{
      font-weight:650;
    }}
    .ot-science-alert {{
      display:flex; align-items:flex-start; gap:.85rem;
      background:#FCE9ED !important;
      border:1px solid #F2B9C4 !important;
      border-left:5px solid var(--ot-red) !important;
      border-radius:14px;
      padding:1rem 1.15rem;
      margin:.65rem 0 1.15rem 0;
      color:#42252D !important;
      box-shadow:0 5px 16px rgba(82,20,34,.055);
    }}
    .ot-science-alert * {{ color:#42252D !important; opacity:1 !important; }}
    .ot-science-alert strong {{
      display:block; color:#9E102A !important; font-size:.96rem;
      margin-bottom:.18rem; font-weight:850;
    }}
    .ot-science-alert p {{ margin:0; line-height:1.55; font-size:.94rem; }}
    .ot-alert-icon {{
      display:flex; align-items:center; justify-content:center;
      flex:0 0 30px; width:30px; height:30px; border-radius:50%;
      background:var(--ot-red); color:#FFFFFF !important; font-weight:900;
      margin-top:.05rem;
    }}
    .ot-section-note {{
      background:#FFF0F2;
      border:1px solid #F4CCD4;
      border-left:4px solid var(--ot-red);
      border-radius:12px;
      padding:.85rem 1rem;
      margin:.5rem 0 1rem 0;
      color:#51333A;
    }}
    .ot-footer {{
      color:var(--ot-muted); font-size:.82rem;
      padding-top:.75rem;
    }}
    @keyframes ot-rise {{
      from {{ opacity:0; transform:translateY(9px); }}
      to {{ opacity:1; transform:translateY(0); }}
    }}
    @media (max-width: 760px) {{
      .block-container {{ padding-top:3.8rem !important; }}
      .bytex-topline {{ width:100%; }}
      [data-testid="stTabs"] [role="tablist"] {{ gap:.45rem; }}
      [data-testid="stTabs"] [role="tab"] {{ flex:1 1 145px; min-height:54px; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{ animation:none !important; transition:none !important; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_csv(name, date_col=None):
    path = DATA / name
    return pd.read_csv(path, parse_dates=[date_col] if date_col else None)


@st.cache_data(show_spinner=False)
def load_hotspot(key):
    path = HOTSPOTS / f"{key}_persistence.npz"
    with np.load(path, allow_pickle=False) as d:
        return {k: d[k].copy() for k in d.files}


def file_guard():
    required = [
        DATA / "monthly_global_timeseries.csv",
        DATA / "regional_ocean_masked_timeseries.csv",
    ]
    required += [HOTSPOTS / f"{key}_persistence.npz" for key in REGIONS.values()]
    missing = [str(p.relative_to(BASE)) for p in required if not p.exists()]
    if missing:
        st.error("Dashboard data files are missing: " + ", ".join(missing))
        st.info(
            "Restore the existing exported data/ folder from the OceanTrace project. "
            "The dashboard reads these files directly; no model retraining is required."
        )
        st.stop()


def style_figure(fig, height=460, title=None):
    """Shared layout with a generous left gutter so y-axis ticks and title never collide."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        title=title,
        title_font={"size": 18, "color": INK},
        font={"family": "Inter, Arial, sans-serif", "size": 12, "color": INK},
        paper_bgcolor=OFF_WHITE,
        plot_bgcolor=CARD_WHITE,
        margin={"l": 132, "r": 34, "t": 76 if title else 38, "b": 78},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
            "font": {"size": 11, "color": INK},
        },
        hoverlabel={
            "bgcolor": CARD_WHITE,
            "bordercolor": BORDER,
            "font": {"color": INK, "size": 12},
        },
    )
    fig.update_xaxes(
        automargin=True,
        tickfont={"size": 11, "color": MUTED},
        title_font={"size": 12, "color": INK},
        showline=True,
        linecolor=BORDER,
        gridcolor=GRID,
        zerolinecolor=GRID,
    )
    fig.update_yaxes(
        automargin=True,
        tickfont={"size": 11, "color": MUTED},
        title_font={"size": 12, "color": INK},
        title_standoff=28,
        ticklabelposition="outside",
        tickformat=",.0f",
        showline=False,
        gridcolor=GRID,
        zerolinecolor=GRID,
    )
    return fig


def make_timeline_figure(df, metric):
    """Build a progressive Plotly animation from the unchanged monthly CSV values."""
    dates = df["month"].tolist()
    frame_names = [str(i) for i in range(1, len(df) + 1)]
    fig = go.Figure()

    if metric == "Estimated concentration":
        y = df["global_mean_concentration"].astype(float).tolist()
        rolling = df["rolling_12"].astype(float).where(df["rolling_12"].notna(), None).tolist()
        fig.add_trace(
            go.Scatter(
                x=dates[:1], y=y[:1], mode="lines+markers", name="Monthly estimate",
                line={"color": BRAND_RED, "width": 3.2},
                marker={"color": BRAND_RED, "size": 5},
                hovertemplate="%{x|%b %Y}<br>Estimate: %{y:,.0f} count/km²<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=dates[:1], y=rolling[:1], mode="lines", name="12-month smoother",
                line={"color": SECONDARY, "width": 3.2},
                hovertemplate="%{x|%b %Y}<br>12-month mean: %{y:,.0f} count/km²<extra></extra>",
            )
        )
        frames = []
        for i in range(1, len(df) + 1):
            frames.append(
                go.Frame(
                    name=str(i),
                    data=[
                        go.Scatter(x=dates[:i], y=y[:i]),
                        go.Scatter(x=dates[:i], y=rolling[:i]),
                    ],
                    traces=[0, 1],
                )
            )
        fig.frames = frames
        fig.update_yaxes(title="Estimated concentration (count/km²)")
        fig.update_layout(
            xaxis_title="Observation month",
            yaxis={"rangemode": "normal"},
            updatemenus=[
                {
                    "type": "buttons",
                    "direction": "left",
                    "showactive": False,
                    "x": 1,
                    "xanchor": "right",
                    "y": 1.18,
                    "yanchor": "top",
                    "buttons": [
                        {
                            "label": "Replay",
                            "method": "animate",
                            "args": [
                                None,
                                {
                                    "fromcurrent": False,
                                    "frame": {"duration": 48, "redraw": True},
                                    "transition": {"duration": 0},
                                    "mode": "immediate",
                                },
                            ],
                        },
                        {
                            "label": "Pause",
                            "method": "animate",
                            "args": [
                                [None],
                                {
                                    "mode": "immediate",
                                    "frame": {"duration": 0, "redraw": False},
                                    "transition": {"duration": 0},
                                },
                            ],
                        },
                    ],
                }
            ],
        )
    else:
        y = df["anomaly"].astype(float).tolist()
        colors = [BRAND_RED if v >= 0 else "#C9AEB5" for v in y]
        fig.add_trace(
            go.Bar(
                x=dates[:1], y=y[:1], name="Difference from reference mean",
                marker={"color": colors[:1]},
                hovertemplate="%{x|%b %Y}<br>Difference: %{y:,.0f} count/km²<extra></extra>",
            )
        )
        fig.frames = [
            go.Frame(
                name=str(i),
                data=[go.Bar(x=dates[:i], y=y[:i], marker={"color": colors[:i]})],
                traces=[0],
            )
            for i in range(1, len(df) + 1)
        ]
        fig.add_hline(y=0, line_dash="dash", line_color=SECONDARY)
        fig.update_yaxes(title="Difference from 2019–2025 mean (count/km²)")
        fig.update_layout(
            xaxis_title="Observation month",
            updatemenus=[
                {
                    "type": "buttons",
                    "direction": "left",
                    "showactive": False,
                    "x": 1,
                    "xanchor": "right",
                    "y": 1.18,
                    "yanchor": "top",
                    "buttons": [
                        {
                            "label": "Replay",
                            "method": "animate",
                            "args": [
                                None,
                                {
                                    "fromcurrent": False,
                                    "frame": {"duration": 48, "redraw": True},
                                    "transition": {"duration": 0},
                                    "mode": "immediate",
                                },
                            ],
                        },
                        {
                            "label": "Pause",
                            "method": "animate",
                            "args": [
                                [None],
                                {
                                    "mode": "immediate",
                                    "frame": {"duration": 0, "redraw": False},
                                    "transition": {"duration": 0},
                                },
                            ],
                        },
                    ],
                }
            ],
        )

    style_figure(fig, height=535)
    return fig, frame_names


def render_autoplay_plotly(fig, frame_names, height=560):
    """Render an animated Plotly figure and start its frames automatically on load."""
    chart_html = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        auto_play=False,
        config={"responsive": True, "displayModeBar": True, "displaylogo": False},
    )
    match = re.search(r'<div id="([^"]+)" class="plotly-graph-div"', chart_html)
    if match and frame_names:
        graph_id = json.dumps(match.group(1))
        names_json = json.dumps(frame_names)
        autoplay_script = f"""
        <script>
        (function() {{
          const graphId = {graph_id};
          const frames = {names_json};
          function playWhenReady() {{
            const graph = document.getElementById(graphId);
            if (!graph || !graph._fullLayout || !window.Plotly) {{
              window.setTimeout(playWhenReady, 120);
              return;
            }}
            if (graph.dataset.oceantracePlayed === "yes") return;
            graph.dataset.oceantracePlayed = "yes";
            window.Plotly.animate(
              graph,
              frames,
              {{
                mode: "immediate",
                frame: {{duration: 48, redraw: true}},
                transition: {{duration: 0}}
              }}
            );
          }}
          window.setTimeout(playWhenReady, 250);
        }})();
        </script>
        """
        chart_html += autoplay_script
    embed_html(chart_html, height=height, scrolling=False)


file_guard()
global_monthly = load_csv("monthly_global_timeseries.csv", "month")
regional = load_csv("regional_ocean_masked_timeseries.csv", "date")
regional = regional.sort_values(["region", "date"]).copy()
regional["region_label"] = regional["region"].replace(
    {"Sulu-Celebes Sea": "Sulu–Celebes Sea"}
)

st.markdown(
    f"""
    <div class="bytex-topline">
      <img class="bytex-logo" src="data:image/png;base64,{BYTEX_LOGO_B64}" alt="ByteX logo" />
      <div>
        <div class="bytex-wordmark">ByteX presents</div>
        <div class="bytex-submark">OceanTrace · Satellite ocean intelligence</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.title("OceanTrace")
st.caption(
    "Explore satellite-derived estimates of near-surface ocean microplastics "
    "across time and three Southeast Asian seas · August 2018–October 2026"
)
st.markdown(
    """
    <div class="ot-science-alert" role="note" aria-label="Important scientific context">
      <div class="ot-alert-icon">!</div>
      <div>
        <strong>Important scientific context</strong>
        <p>CYGNSS does not directly count plastic particles. OceanTrace displays inferred estimates based on sea-surface roughness. Weather, biological slicks, oil and other ocean conditions can also affect the signal.</p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tabs = st.tabs(
    [
        "🌐  Overview",
        "⏱️  Ocean Time Machine",
        "📍  Regional Intelligence",
        "🔥  Hotspot Explorer",
        "🔬  Understand the Science",
    ]
)

with tabs[0]:
    st.subheader("The ocean, through satellite-derived indicators")
    a, b, c, d = st.columns(4)
    a.metric("Global monthly records", f"{len(global_monthly):,}")
    b.metric("Regional study areas", "3")
    c.metric("CYGNSS latitude range", "37°S–37°N")
    d.metric("Hotspot snapshots", "99")
    st.markdown(
        """
        <div class="ot-section-note">
          <b>How to read this page:</b> the charts show how satellite-derived estimates
          vary over time and where relatively high-estimate grid cells recur. They are
          research indicators — not a verified count of plastic in the ocean.
        </div>
        """,
        unsafe_allow_html=True,
    )
    f = px.line(
        global_monthly.sort_values("month"),
        x="month",
        y="global_mean_concentration",
        labels={
            "month": "Observation month",
            "global_mean_concentration": "Estimated concentration (count/km²)",
        },
        title="Global study-area concentration history",
    )
    f.update_traces(line={"color": BRAND_RED, "width": 3}, hovertemplate="%{x|%b %Y}<br>%{y:,.0f} count/km²<extra></extra>")
    style_figure(f, height=430)
    st.plotly_chart(f, use_container_width=True, config={"displaylogo": False})
    st.caption(
        "Global summary averages the available daily 30-day-smoothed products. "
        "Valid-cell coverage changes over time, so this is not an independent daily sampling record."
    )

with tabs[1]:
    st.subheader("Ocean Time Machine")
    st.markdown(
        """
        <div class="ot-section-note">
          <b>What you are seeing:</b> each point is a monthly satellite-derived estimate.
          The smoother line helps reveal the longer pattern while reducing month-to-month noise.
        </div>
        """,
        unsafe_allow_html=True,
    )
    df = global_monthly.sort_values("month").copy()
    df["rolling_12"] = df["global_mean_concentration"].rolling(12, min_periods=12).mean()
    base = df.loc[df["month"].dt.year.between(2019, 2025), "global_mean_concentration"].mean()
    df["anomaly"] = df["global_mean_concentration"] - base
    metric = st.radio(
        "Choose what to explore",
        ["Estimated concentration", "Difference from 2019–2025 mean"],
        horizontal=True,
    )
    else:
        if metric == "Estimated concentration":
            fig = go.Figure()
            fig.add_scatter(
                x=df["month"], y=df["global_mean_concentration"],
                mode="lines+markers", name="Monthly estimate",
                line={"color": BRAND_RED, "width": 3},
                marker={"color": BRAND_RED, "size": 5},
            )
            fig.add_scatter(
                x=df["month"], y=df["rolling_12"], mode="lines",
                name="12-month smoother",
                line={"color": SECONDARY, "width": 3},
            )
            fig.update_yaxes(title="Estimated concentration (count/km²)")
        else:
            fig = px.bar(
                df, x="month", y="anomaly",
                color="anomaly",
                color_continuous_scale=["#C9AEB5", BRAND_RED],
                labels={"month": "Observation month", "anomaly": "Difference (count/km²)"},
            )
            fig.add_hline(y=0, line_dash="dash", line_color=SECONDARY)
            fig.update_coloraxes(showscale=False)
            fig.update_yaxes(title="Difference from 2019–2025 mean (count/km²)")
        fig.update_layout(xaxis_title="Observation month")
        style_figure(fig, height=535)
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    st.caption(
        "The 2019–2025 reference is a descriptive average, not a seasonal baseline. "
        "A rise or fall in this estimate alone cannot establish a change in actual ocean plastic."
    )

with tabs[2]:
    st.subheader("Regional Intelligence")
    region_names = sorted(regional["region_label"].dropna().unique())
    selection = st.multiselect("Compare regions", region_names, default=region_names)
    if not selection:
        st.warning("Choose at least one region.")
    else:
        filtered = regional[regional["region_label"].isin(selection)].copy()
        fig = px.line(
            filtered, x="date", y="mean_concentration", color="region_label",
            labels={
                "date": "Observation date",
                "mean_concentration": "Estimated concentration (count/km²)",
                "region_label": "Region",
            },
            title="Regional monthly estimates",
            color_discrete_sequence=[BRAND_RED, "#8F6875", "#D99AA7"],
        )
        style_figure(fig, height=460)
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
        cov = px.line(
            filtered, x="date", y="coverage_percent", color="region_label",
            labels={
                "date": "Observation date",
                "coverage_percent": "Ocean-mask valid-cell coverage (%)",
                "region_label": "Region",
            },
            title="How much of each study region has valid observations?",
            color_discrete_sequence=[BRAND_RED, "#8F6875", "#D99AA7"],
        )
        cov.update_yaxes(range=[0, 100], title="Valid ocean-cell coverage (%)", tickformat=".0f")
        style_figure(cov, height=420)
        st.plotly_chart(cov, use_container_width=True, config={"displaylogo": False})
        table = filtered.groupby("region_label", as_index=False).agg(
            months=("month", "nunique"),
            mean_estimate=("mean_concentration", "mean"),
            mean_ocean_coverage=("coverage_percent", "mean"),
        )
        st.dataframe(table.round(2), hide_index=True, use_container_width=True)
        st.caption(
            "Study regions are exploratory rectangles, not official maritime boundaries. "
            "The Strait of Malacca has lower valid-cell coverage; differences may also reflect observation support."
        )
    hac = DATA / "hac_trend_validation.csv"
    if hac.exists():
        with st.expander("Statistical trend screening — HAC regression"):
            st.dataframe(load_csv("hac_trend_validation.csv").round(4), hide_index=True, use_container_width=True)
            st.caption(
                "This is exploratory seasonal-adjusted regression. Standard errors depend on model assumptions "
                "and lag settings; p > 0.05 is not proof that no trend exists."
            )

with tabs[3]:
    st.subheader("Hotspot Explorer")
    st.markdown(
        """
        <div class="ot-section-note">
          <b>What is a hotspot here?</b> A hotspot is a grid cell that repeatedly ranks
          among the higher estimates in its own region. It is not automatically a pollution
          danger zone or a confirmed plastic accumulation site.
        </div>
        """,
        unsafe_allow_html=True,
    )
    selected = st.selectbox("Study region", list(REGIONS))
    key = REGIONS[selected]
    d = load_hotspot(key)
    ptype = st.radio("Relative hotspot threshold", ["P90", "P95"], horizontal=True)
    metric_key = "persistence90" if ptype == "P90" else "persistence95"
    class_key = "classification90" if ptype == "P90" else "classification95"
    count_key = "hotspot90_count" if ptype == "P90" else "hotspot95_count"
    persist = d[metric_key]
    classes = d[class_key]
    nobs = d["eligible_observations"]
    hcount = d[count_key]
    mean_c = d["mean_concentration"]
    lat, lon = d["latitude"], d["longitude"]
    show = st.multiselect(
        "Display classifications",
        ["Persistent", "Recurring", "Occasional"],
        default=["Persistent", "Recurring"],
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Persistent cells", f"{(classes == 3).sum():,}")
    c2.metric("Recurring cells", f"{(classes == 2).sum():,}")
    c3.metric("Cells with ≥12 qualified months", f"{(nobs >= 12).sum():,}")
    m = folium.Map(
        location=[float(np.mean(lat)), float(np.mean(lon))],
        tiles=None,
        zoom_start=6,
        prefer_canvas=True,
        control_scale=True,
    )
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles © Esri",
        name="Esri World Street Map",
        overlay=False,
        control=True,
    ).add_to(m)
    for cat in (3, 2, 1):
        if CLASS_NAMES[cat] not in show:
            continue
        group = folium.FeatureGroup(name=CLASS_NAMES[cat], show=True)
        ii, jj = np.where(classes == cat)
        for i, j in zip(ii, jj):
            popup_text = (
                f"<b>{html.escape(selected)}</b><hr>{CLASS_NAMES[cat]} {ptype}<br>"
                f"Lat: {lat[i]:.2f}°, Lon: {lon[j]:.2f}°<br>"
                f"Hotspot frequency: {persist[i,j]:.1f}%<br>"
                f"Hotspot months: {hcount[i,j]} / {nobs[i,j]} qualified months<br>"
                f"Mean estimate: {mean_c[i,j]:,.1f} count/km²"
            )
            folium.CircleMarker(
                location=[float(lat[i]), float(lon[j])],
                radius=4 if cat == 3 else 2.5,
                color=CLASS_COLORS[cat],
                fill=True,
                fill_color=CLASS_COLORS[cat],
                fill_opacity=0.65,
                weight=0.6,
                tooltip=f"{CLASS_NAMES[cat]}: {persist[i,j]:.1f}%",
                popup=folium.Popup(popup_text, max_width=310),
            ).add_to(group)
        group.add_to(m)
    folium.LayerControl(collapsed=True).add_to(m)
    m.fit_bounds([[float(lat.min()), float(lon.min())], [float(lat.max()), float(lon.max())]])
    embed_html(m.get_root().render(), height=590, scrolling=False)
    st.caption(
        "P90/P95 rank cells against other eligible cells within the same region and month. "
        "Persistence is the fraction of qualified months with that ranking. Classes are exploratory, "
        "not pollution-risk levels. Nearby cells can share overlapping CYGNSS retrieval support."
    )
    st.caption(
        "The Esri basemap loads from an external provider and is subject to its usage conditions. "
        "If map tiles are unavailable, the underlying exported CSV/NPZ research data remain unchanged."
    )

with tabs[4]:
    st.subheader("Understand the Science")
    st.markdown(
        """
**What is being measured?** NASA's CYGNSS constellation observes sea-surface scattering and roughness.
The Level 3 microplastic product infers near-surface microplastic number-density estimates from roughness
anomalies. It does **not** directly identify individual pieces of plastic.

**What dates are covered?** This OceanTrace build uses observations from August 2018 through October 2026.
Its hotspot persistence analysis uses one representative **30-day-centered estimate per month** (99 files),
not 99 independent calendar-month averages.

**How precise are the grids?** Values are reported every 0.25° but have an approximately 1° spatial
averaging footprint. Nearby cells should not be treated as separate, independent locations.

**What is an OceanTrace hotspot?** A P90 cell ranks in the highest 10% of adequately sampled cells in its
region **for that month**; P95 is the highest 5%. Recurrence measures how often the same cell achieves
that rank during its qualified observed months. At least 30 samples are required to qualify a monthly cell
and 12 qualified months to classify a location. These are project-specific exploratory thresholds.

**What about confidence?** CYGNSS sample counts show observation support. `stddev_mp_samples` is a
**geometric standard deviation**, not a confidence interval. We do not equate sample count with verified
measurement accuracy.

**What can affect this estimate?** Other sea-surface processes (including weather, biological slicks and oil)
can influence roughness. Low coverage, coastlines, the ocean mask, and satellite retrieval limitations matter.

**How to interpret trends?** Statistical tests here are exploratory. No statistically significant
monotonic/linear regional trend was established by the supplied initial analyses; this does not prove zero
change, and does not prove real-world plastic levels are stable.

**Source:** NASA PO.DAAC CYGNSS Level 3 Ocean Microplastic Concentration v3.2; public NASA dataset and the
OceanTrace exploratory processing pipeline.
"""
    )

st.divider()
st.markdown(
    '<div class="ot-footer">OceanTrace · ByteX team · Independent educational and exploratory project · Not an official NASA assessment</div>',
    unsafe_allow_html=True,
)
