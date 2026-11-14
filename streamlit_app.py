"""OceanTrace public MVP: reads exported, compact CYGNSS research outputs only."""
from pathlib import Path
import html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import folium
from streamlit.components.v1 import html as embed_html

BASE = Path(__file__).resolve().parent
DATA = BASE / 'data'
HOTSPOTS = DATA / 'hotspots'
REGIONS = {
    'South China Sea': 'south_china_sea',
    'Strait of Malacca': 'strait_of_malacca',
    'Sulu–Celebes Sea': 'sulu_celebes_sea',
}
CLASS_COLORS = {1: '#f4c95d', 2: '#f77f00', 3: '#d62828'}
CLASS_NAMES = {1: 'Occasional', 2: 'Recurring', 3: 'Persistent'}
st.set_page_config(page_title='OceanTrace | CYGNSS Ocean Explorer', page_icon='🌊', layout='wide')
st.markdown('''<style>
.block-container {padding-top: 1.5rem; max-width: 1400px}
[data-testid="stMetricValue"] {font-size: 1.75rem}
</style>''', unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_csv(name, date_col=None):
    path = DATA / name
    return pd.read_csv(path, parse_dates=[date_col] if date_col else None)

@st.cache_data(show_spinner=False)
def load_hotspot(key):
    path = HOTSPOTS / f'{key}_persistence.npz'
    with np.load(path, allow_pickle=False) as d:
        return {k: d[k].copy() for k in d.files}

def file_guard():
    required = [DATA / 'monthly_global_timeseries.csv',
                DATA / 'regional_ocean_masked_timeseries.csv']
    required += [HOTSPOTS / f'{key}_persistence.npz' for key in REGIONS.values()]
    missing = [str(p.relative_to(BASE)) for p in required if not p.exists()]
    if missing:
        st.error('Dashboard data is not exported yet. Missing: ' + ', '.join(missing))
        st.info('In Google Colab, run scripts/export_from_colab.py from the starter folder. Then upload the resulting app folder to GitHub.')
        st.stop()

file_guard()
global_monthly = load_csv('monthly_global_timeseries.csv', 'month')
regional = load_csv('regional_ocean_masked_timeseries.csv', 'date')
regional = regional.sort_values(['region', 'date']).copy()
regional['region_label'] = regional['region'].replace({'Sulu-Celebes Sea': 'Sulu–Celebes Sea'})

st.title('🌊 OceanTrace')
st.caption('Explore changes in CYGNSS-derived near-surface ocean microplastic estimates | August 2018–October 2026')
st.info('CYGNSS does **not** directly count plastic particles. Estimates are inferred from sea-surface roughness and can be influenced by other ocean conditions. The 0.25° grid is more finely spaced than the approximately 1° underlying retrieval footprint.')

tabs = st.tabs(['Overview', 'Ocean Time Machine', 'Regional Intelligence', 'Hotspot Explorer', 'Understand the Science'])

with tabs[0]:
    st.subheader('The ocean, through satellite-derived indicators')
    a, b, c, d = st.columns(4)
    a.metric('Global monthly records', f'{len(global_monthly):,}')
    b.metric('Regional study areas', '3')
    c.metric('CYGNSS latitude range', '37°S–37°N')
    d.metric('Monthly snapshots for hotspots', '99')
    st.markdown('''**What OceanTrace can show:** how satellite-derived estimates vary through time, where relative high-estimate cells recur, and how observation coverage differs between seas. These outputs are research indicators, not a verified census of ocean plastics.''')
    f = px.line(global_monthly.sort_values('month'), x='month', y='global_mean_concentration',
                labels={'month': 'Observation month', 'global_mean_concentration': 'Estimated concentration (count/km²)'},
                title='Global study-area concentration history — mean of daily 30-day-smoothed products')
    f.update_layout(height=410)
    st.plotly_chart(f, use_container_width=True)
    st.caption('Global summary reflects changing valid-cell coverage and averages of overlapping daily retrieval windows. It is not an independent daily sampling record.')

with tabs[1]:
    st.subheader('Ocean Time Machine')
    df = global_monthly.sort_values('month').copy()
    df['rolling_12'] = df['global_mean_concentration'].rolling(12, min_periods=12).mean()
    base = df.loc[df['month'].dt.year.between(2019, 2025), 'global_mean_concentration'].mean()
    df['anomaly'] = df['global_mean_concentration'] - base
    metric = st.radio('Display', ['Estimated concentration', 'Difference from 2019–2025 mean'], horizontal=True)
    if metric == 'Estimated concentration':
        fig = go.Figure()
        fig.add_scatter(x=df['month'], y=df['global_mean_concentration'], mode='lines+markers', name='Monthly mean')
        fig.add_scatter(x=df['month'], y=df['rolling_12'], mode='lines', name='12-month rolling mean', line={'width': 4})
        fig.update_yaxes(title='Estimated concentration (count/km²)')
    else:
        fig = px.bar(df, x='month', y='anomaly', color='anomaly', color_continuous_scale='RdBu_r',
                     labels={'month': 'Observation month', 'anomaly': 'Difference (count/km²)'})
        fig.add_hline(y=0, line_dash='dash')
        fig.update_coloraxes(showscale=False)
    fig.update_layout(height=500, xaxis_title='Observation month')
    st.plotly_chart(fig, use_container_width=True)
    st.caption('The 2019–2025 reference is a descriptive mean, not a seasonal baseline. Trend and anomaly graphics alone cannot establish a change in actual pollution.')

with tabs[2]:
    st.subheader('Regional Intelligence')
    region_names = sorted(regional['region_label'].dropna().unique())
    selection = st.multiselect('Compare regions', region_names, default=region_names)
    if not selection:
        st.warning('Choose at least one region.')
    else:
        filtered = regional[regional['region_label'].isin(selection)].copy()
        fig = px.line(filtered, x='date', y='mean_concentration', color='region_label',
                      labels={'date': 'Observation date', 'mean_concentration': 'Estimated concentration (count/km²)', 'region_label': 'Region'},
                      title='Representative monthly 30-day-centered CYGNSS estimates')
        fig.update_layout(height=460)
        st.plotly_chart(fig, use_container_width=True)
        cov = px.line(filtered, x='date', y='coverage_percent', color='region_label',
                      labels={'date': 'Observation date', 'coverage_percent': 'Ocean-mask valid-cell coverage (%)', 'region_label': 'Region'},
                      title='Spatial data coverage (Natural Earth approximate ocean mask)')
        cov.update_yaxes(range=[0, 100])
        st.plotly_chart(cov, use_container_width=True)
        table = filtered.groupby('region_label', as_index=False).agg(
            months=('month', 'nunique'),
            mean_estimate=('mean_concentration', 'mean'),
            mean_ocean_coverage=('coverage_percent', 'mean'))
        st.dataframe(table.round(2), hide_index=True, use_container_width=True)
        st.caption('Regional windows are exploratory rectangles, not official maritime boundaries. The Strait of Malacca has materially lower valid ocean-cell coverage. Differences may also reflect changing observation support.')
    hac = DATA / 'hac_trend_validation.csv'
    if hac.exists():
        with st.expander('Statistical trend screening — HAC regression'):
            st.dataframe(load_csv('hac_trend_validation.csv').round(4), hide_index=True, use_container_width=True)
            st.caption('Exploratory seasonal-adjusted HAC regression. Standard errors depend on model assumptions and the specified lag setting; p>0.05 is not proof of no trend.')

with tabs[3]:
    st.subheader('Hotspot Explorer')
    selected = st.selectbox('Study region', list(REGIONS))
    key = REGIONS[selected]
    d = load_hotspot(key)
    ptype = st.radio('Relative hotspot threshold', ['P90', 'P95'], horizontal=True)
    metric_key = 'persistence90' if ptype == 'P90' else 'persistence95'
    class_key = 'classification90' if ptype == 'P90' else 'classification95'
    count_key = 'hotspot90_count' if ptype == 'P90' else 'hotspot95_count'
    persist = d[metric_key]
    classes = d[class_key]
    nobs = d['eligible_observations']
    hcount = d[count_key]
    mean_c = d['mean_concentration']
    lat, lon = d['latitude'], d['longitude']
    show = st.multiselect('Display classifications', ['Persistent', 'Recurring', 'Occasional'], default=['Persistent', 'Recurring'])
    c1, c2, c3 = st.columns(3)
    c1.metric('Persistent cells', f'{(classes == 3).sum():,}')
    c2.metric('Recurring cells', f'{(classes == 2).sum():,}')
    c3.metric('Cells with ≥12 qualified months', f'{(nobs >= 12).sum():,}')
    m = folium.Map(location=[float(np.mean(lat)), float(np.mean(lon))], tiles=None,
                   zoom_start=6, prefer_canvas=True, control_scale=True)
    folium.TileLayer(tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
                     attr='Tiles © Esri', name='Esri World Street Map', overlay=False, control=True).add_to(m)
    for cat in (3, 2, 1):
        if CLASS_NAMES[cat] not in show:
            continue
        group = folium.FeatureGroup(name=CLASS_NAMES[cat], show=True)
        ii, jj = np.where(classes == cat)
        for i, j in zip(ii, jj):
            text = (f'<b>{html.escape(selected)}</b><hr>{CLASS_NAMES[cat]} {ptype}<br>'
                    f'Lat: {lat[i]:.2f}°, Lon: {lon[j]:.2f}°<br>'
                    f'Hotspot frequency: {persist[i,j]:.1f}%<br>'
                    f'Hotspot months: {hcount[i,j]} / {nobs[i,j]} qualified months<br>'
                    f'Mean estimate: {mean_c[i,j]:,.1f} count/km²')
            folium.CircleMarker(location=[float(lat[i]), float(lon[j])],
                radius=4 if cat == 3 else 2.5, color=CLASS_COLORS[cat],
                fill=True, fill_color=CLASS_COLORS[cat], fill_opacity=.65,
                weight=.6, tooltip=f'{CLASS_NAMES[cat]}: {persist[i,j]:.1f}%',
                popup=folium.Popup(text, max_width=310)).add_to(group)
        group.add_to(m)
    folium.LayerControl(collapsed=True).add_to(m)
    m.fit_bounds([[float(lat.min()), float(lon.min())], [float(lat.max()), float(lon.max())]])
    embed_html(m.get_root().render(), height=590, scrolling=False)
    st.caption('P90/P95 rank cells against other eligible cells within the same region and month; persistence is the fraction of qualified months with such a ranking. Thresholds and classes are exploratory, not pollution risk levels. Cells overlap spatially in CYGNSS retrieval support.')
    st.caption('Esri basemap tiles load from an external provider and are subject to its usage conditions. If tiles are unavailable, data remain accessible through your saved CSV/NPZ files.')

with tabs[4]:
    st.subheader('Understand the Science')
    st.markdown('''
**What is being measured?** NASA's CYGNSS constellation observes sea-surface scattering and roughness. The Level 3 microplastic product infers near-surface microplastic number-density estimates from roughness anomalies. It does **not** directly identify individual pieces of plastic.

**What dates are covered?** This OceanTrace build uses observations from August 2018 through October 2026. Its hotspot persistence analysis uses one representative **30-day-centered estimate per month** (99 files), not 99 independent calendar-month averages.

**How precise are the grids?** Values are reported every 0.25° but have an approximately 1° spatial averaging footprint. Nearby cells should not be treated as separate, independent locations.

**What is an OceanTrace hotspot?** A P90 cell ranks in the highest 10% of adequately sampled cells in its region **for that month**; P95 is the highest 5%. Recurrence measures how often the same cell achieves that rank during its qualified observed months. At least 30 samples are required to qualify a monthly cell and 12 qualified months to classify a location. These are project-specific exploratory thresholds.

**What about confidence?** CYGNSS sample counts show observation support. `stddev_mp_samples` is a **geometric standard deviation**, not a confidence interval. We do not equate sample count with verified measurement accuracy.

**What can affect this estimate?** Other sea-surface processes (including weather, biological slicks and oil) can influence roughness. Low coverage, coastlines, the ocean mask, and satellite retrieval limitations all matter.

**How to interpret trends?** Statistical tests here are exploratory. No statistically significant monotonic/linear regional trend was established by the supplied initial analyses; this does not prove zero change, and does not prove real-world plastic levels are stable.

**Source:** NASA PO.DAAC CYGNSS Level 3 Ocean Microplastic Concentration v3.2; public NASA dataset and the OceanTrace exploratory processing pipeline.
''')

st.divider()
st.caption('OceanTrace · Independent educational and exploratory project · Not an official NASA assessment')
