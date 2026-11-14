# OceanTrace — ByteX branded Streamlit dashboard

This UI refresh applies the ByteX red/off-white visual theme, improves chart readability, and makes the Ocean Time Machine animation start automatically by default.

## What changed

- ByteX-inspired red and warm off-white theme across the dashboard.
- More generous Plotly left margins, automatic axis sizing, and readable numeric tick labels so the y-axis is not clipped or overlapped.
- Ocean Time Machine now autoplays its monthly timeline animation on page load by default. Use **Pause** or **Replay** on the chart; the toggle can turn autoplay off.
- Small motion and card styling improvements, with reduced-motion accessibility support.
- Clearer plain-language chart guidance.

## Scientific data preservation

**The scientific data files in `data/` and `data/hotspots/` are included byte-for-byte from the supplied ZIP.** This UI-only update does not retrain the model, recalculate any estimates, or modify CSV/NPZ scientific outputs.

## Project contents

- `streamlit_app.py`: Streamlit dashboard.
- `.streamlit/config.toml`: ByteX light theme configuration.
- `data/monthly_global_timeseries.csv`: global monthly time series.
- `data/regional_ocean_masked_timeseries.csv`: regional monthly estimates and coverage.
- `data/hac_trend_validation.csv`: exploratory trend screening.
- `data/hotspots/*.npz`: regional hotspot persistence arrays.
- `scripts/export_from_colab.py`: existing export utility.

## Deploy

1. Extract the ZIP.
2. Upload/commit the contents to the same GitHub repository connected to Streamlit Community Cloud.
3. Keep the `data/` and `data/hotspots/` folders at the same relative locations.
4. In Streamlit Community Cloud, keep the app entrypoint as `streamlit_app.py`.
5. Reboot the app after the commit is deployed.

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Notes

- Esri basemap tiles in Hotspot Explorer load from an external provider and are subject to its usage conditions.
- CYGNSS does not directly count plastic particles. The dashboard presents inferred research estimates and exploratory hotspot rankings, not a verified census or pollution-risk map.
- The source product uses moving 30-day temporal smoothing; the 0.25° grid spacing is finer than the approximately 1° underlying retrieval footprint.
