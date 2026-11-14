# OceanTrace — Streamlit MVP

## From Google Colab to a portable Streamlit app

1. With Drive mounted, extract this ZIP's contents into `/content/drive/MyDrive/OceanTrace_Project/09_STREAMLIT_DASHBOARD`.
2. Run `exec(open('/content/drive/MyDrive/OceanTrace_Project/09_STREAMLIT_DASHBOARD/scripts/export_from_colab.py').read())` in Colab.
3. Confirm files exist under `data/` and `data/hotspots/`.
4. Download or upload the entire `09_STREAMLIT_DASHBOARD` directory to a **public GitHub repository** (only the tiny exports — never the 19 GB NetCDF source archive).
5. Deploy from https://share.streamlit.io with entrypoint `streamlit_app.py`; Community Cloud reads `requirements.txt`.

## Local test

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Files in data

- `monthly_global_timeseries.csv`: global timeline based on daily source products.
- `regional_ocean_masked_timeseries.csv`: 99 monthly sampled regional estimates and data coverage.
- `hac_trend_validation.csv`: exploratory trend screening.
- `hotspots/*.npz`: 99-month regional hotspot persistence output.

These exported files are created by `scripts/export_from_colab.py` using existing Google Drive outputs; this starter does **not** contain actual satellite data. Source CYGNSS product has a moving 30-day temporal smoothing window, and the listed 0.25° grid values are not independent retrievals. Hotspot ranks are comparative, not confirmed pollution.

## Notes

- Esri geographic tiles are requested live by the Hotspot Explorer. They are subject to Esri's terms and may have usage limits. For a high-traffic production deployment, obtain an appropriate licensed tile solution.
- Folium map rendering is performed inside Streamlit, not with local notebook iframes.
- This is a public educational dashboard starter, not a NASA product or validated microplastic risk map.
