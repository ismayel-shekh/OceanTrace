# OceanTrace — ByteX branded Streamlit dashboard

This release keeps the ByteX red/off-white interface and presents the Ocean Time Machine as a static, interactive Plotly chart. The automatic timeline animation and its Play/Pause/Replay controls have been removed.

## What changed

- Removed the Ocean Time Machine autoplay toggle, frame animation, and Replay/Pause buttons.
- The full monthly series is visible immediately when the section opens; visitors can inspect values using Plotly hover and zoom controls.
- Both concentration and anomaly views remain available.
- Retained the ByteX red/off-white theme, readable chart margins and y-axis labels, masthead logo, scientific-context notice, and five-section navigation.

## Scientific data preservation

**The scientific CSV and NPZ files in `data/` and `data/hotspots/` are included byte-for-byte from the previous supplied ZIP.** This is a UI-only change. It does not retrain the model, recalculate estimates, or modify scientific outputs.

## Project contents

- `streamlit_app.py`: Streamlit dashboard.
- `.streamlit/config.toml`: ByteX theme configuration.
- `assets/bytex_logo.png`: ByteX logo.
- `data/monthly_global_timeseries.csv`: global monthly time series.
- `data/regional_ocean_masked_timeseries.csv`: regional monthly estimates and coverage.
- `data/hac_trend_validation.csv`: exploratory trend screening.
- `data/hotspots/*.npz`: regional hotspot persistence arrays.
- `scripts/export_from_colab.py`: existing export utility.

## Deploy

1. Extract the ZIP.
2. Upload/commit the contents to the same GitHub repository connected to Streamlit Community Cloud.
3. Keep `data/` and `data/hotspots/` at the same relative locations.
4. Keep the app entrypoint as `streamlit_app.py`.
5. Reboot the app after the commit is deployed.

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Scientific limitations

CYGNSS does not directly count plastic particles. OceanTrace presents inferred research estimates and exploratory hotspot rankings, not a verified census or pollution-risk map. The source product uses moving 30-day temporal smoothing; the 0.25° grid spacing is finer than the approximately 1° underlying retrieval footprint.
