# OceanTrace — Team ByteX | ByteX Brand UI V3

This release changes **only the website presentation layer**. It does not include or modify the model outputs, exported CSVs, hotspot NPZ arrays, thresholds, rankings, time series or scientific calculations.

## Requested fixes and design changes
- Fixes clipped Y-axis tick labels by reserving a larger left plot margin, enabling axis automargins, and adding title standoff.
- Changes the visual theme to ByteX red, white and warm off-white, using the supplied ByteX logo as the app brand mark and favicon.
- Sets the Time Machine animated timeline to **ON by default**. The plot starts animating automatically and loops through the historical months when the Time Machine view loads. Users can switch it off to inspect the complete static series. Devices with reduced-motion enabled show the full static chart instead.
- Uses red for monthly estimates and a dark neutral for the 12-month smoother.
- Retains the Play/Pause controls for the animation.
- Keeps the existing CSV/NPZ data inputs and existing scientific interpretations.

## Safest update
1. Back up your current GitHub repository or app folder.
2. Replace `streamlit_app.py`.
3. Add/replace `.streamlit/config.toml`.
4. Add `assets/bytex_logo.png`.
5. **Do not replace, rename, delete, regenerate or edit your existing `data/` folder.**
6. Commit the UI files and let Streamlit Community Cloud redeploy.

The `upgrade_in_colab.py` script performs a backup of the old UI files and compares SHA-256 hashes of every file in the existing `data/` folder before and after installing the new UI files. It copies only the UI script, theme config and ByteX logo.

## Expected app structure
```text
09_STREAMLIT_DASHBOARD/
  streamlit_app.py
  requirements.txt
  .streamlit/
    config.toml
  assets/
    bytex_logo.png
  data/
    monthly_global_timeseries.csv
    regional_ocean_masked_timeseries.csv
    hac_trend_validation.csv
    hotspots/
      strait_of_malacca_persistence.npz
      south_china_sea_persistence.npz
      sulu_celebes_sea_persistence.npz
```

## Local test
Install the existing `requirements.txt` and run:
`streamlit run streamlit_app.py`

The animated chart uses Plotly's HTML renderer with its JavaScript library from the Plotly CDN. If external CDN access is blocked in a deployment, switch the Time Machine toggle off to display the full static chart. The animation loops automatically; the toggle is the pause/static control.
