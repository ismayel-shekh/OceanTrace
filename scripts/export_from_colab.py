"""Run this script in Google Colab with Drive mounted; no NetCDF data is opened."""
from pathlib import Path
import shutil
import pandas as pd

BASE = Path('/content/drive/MyDrive/OceanTrace_Project')
APP = BASE / '09_STREAMLIT_DASHBOARD'
DATA = APP / 'data'
HOT = DATA / 'hotspots'
HOT.mkdir(parents=True, exist_ok=True)

# Install starter files by extracting the accompanying ZIP into 09_STREAMLIT_DASHBOARD
# before running this script, or upload them manually into the folder.
files = {
    BASE / '02_PROCESSED_DATA/TIME_SERIES/monthly_global_timeseries.csv': DATA / 'monthly_global_timeseries.csv',
    BASE / '04_REGIONAL_RESULTS/regional_ocean_masked_timeseries.csv': DATA / 'regional_ocean_masked_timeseries.csv',
    BASE / '04_REGIONAL_RESULTS/hac_trend_validation.csv': DATA / 'hac_trend_validation.csv',
}
for key in ('south_china_sea', 'strait_of_malacca', 'sulu_celebes_sea'):
    files[BASE / f'07_HOTSPOT_INTELLIGENCE/{key}_persistence.npz'] = HOT / f'{key}_persistence.npz'

missing = [str(src) for src in files if not src.exists()]
if missing:
    raise FileNotFoundError('Required files missing:\n' + '\n'.join(missing))

for src, dst in files.items():
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f'Copied: {dst.relative_to(APP)} ({dst.stat().st_size/1024:.1f} KB)')

# Verify content schema so deployment failures are caught before GitHub upload.
monthly = pd.read_csv(DATA / 'monthly_global_timeseries.csv')
regional = pd.read_csv(DATA / 'regional_ocean_masked_timeseries.csv')
required_monthly = {'month', 'global_mean_concentration'}
required_regional = {'region', 'date', 'month', 'mean_concentration', 'coverage_percent'}
assert required_monthly.issubset(monthly.columns), f'Global missing: {required_monthly - set(monthly.columns)}'
assert required_regional.issubset(regional.columns), f'Regional missing: {required_regional - set(regional.columns)}'
assert len(monthly) == 99, f'Unexpected global months: {len(monthly)}'
assert len(regional) == 297, f'Unexpected regional rows: {len(regional)}'
print(f'Export validated: {len(monthly)} monthly global rows; {len(regional)} regional rows.')
print(f'App folder: {APP}')
