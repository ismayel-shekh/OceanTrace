"""Safe UI-only upgrade for OceanTrace ByteX V3. Run in Google Colab."""
from google.colab import drive, files
from pathlib import Path
import hashlib
import zipfile
import shutil
from datetime import datetime

drive.mount('/content/drive')
APP = Path('/content/drive/MyDrive/OceanTrace_Project/09_STREAMLIT_DASHBOARD')
assert (APP / 'streamlit_app.py').is_file(), f'Existing OceanTrace dashboard not found: {APP}'
DATA = APP / 'data'
assert DATA.is_dir(), 'Existing dashboard data folder missing; stopping to prevent a broken deployment.'

def hashes():
    return {str(f.relative_to(DATA)): hashlib.sha256(f.read_bytes()).hexdigest()
            for f in DATA.rglob('*') if f.is_file()}

before = hashes()
assert len(before) >= 5, 'Expected original CSV/NPZ data not present; stopping.'
print('Verified existing scientific data files:', len(before))
print('Upload oceantrace_bytex_ui_v3.zip')
uploaded = files.upload()
filename = next((name for name in uploaded if name.lower().endswith('.zip')), None)
assert filename, 'Upload the V3 ZIP file.'

STAGING = Path('/content/oceantrace_bytex_ui_v3_upgrade')
if STAGING.exists():
    shutil.rmtree(STAGING)
STAGING.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(filename) as z:
    members = set(z.namelist())
    required = {'streamlit_app.py', '.streamlit/config.toml', 'assets/bytex_logo.png'}
    assert required.issubset(members), f'Missing UI files in ZIP: {required - members}'
    # Extract only explicitly permitted presentation files.
    for path in sorted(required):
        dest = STAGING / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(z.read(path))

stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
BACKUP = APP / 'ui_backups' / stamp
BACKUP.mkdir(parents=True, exist_ok=True)
for path in ('streamlit_app.py', '.streamlit/config.toml', 'assets/bytex_logo.png'):
    original = APP / path
    if original.is_file():
        backup = BACKUP / path
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, backup)

try:
    for path in ('streamlit_app.py', '.streamlit/config.toml', 'assets/bytex_logo.png'):
        destination = APP / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(STAGING / path, destination)
    after = hashes()
    assert before == after, 'Scientific data hashes changed unexpectedly.'
except Exception:
    for path in ('streamlit_app.py', '.streamlit/config.toml', 'assets/bytex_logo.png'):
        backup = BACKUP / path
        destination = APP / path
        if backup.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup, destination)
    raise

print('\nBYTE X UI V3 INSTALLED')
print('Backup:', BACKUP)
print('Scientific data files:', len(after))
print('Scientific data changed: NO (SHA-256 verified)')
print('Updated: streamlit_app.py, .streamlit/config.toml, assets/bytex_logo.png')
print('\nFor GitHub deployment, commit only these three UI files. Do not commit replacements of data/.')
