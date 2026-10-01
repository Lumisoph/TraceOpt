import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

root = Path('.').resolve()
wheel = root / 'dist' / 'traceopt-0.1.0-py3-none-any.whl'
source_hashes = {}
wheel_hashes = {}
with ZipFile(wheel) as archive:
    for source in sorted((root / 'src' / 'traceopt').glob('*.py')):
        rel = source.name
        data = source.read_bytes()
        source_hashes[rel] = hashlib.sha256(data).hexdigest()
        wheel_hashes[rel] = hashlib.sha256(archive.read(f'traceopt/{rel}')).hexdigest()
result = {
    'wheel_sha256': hashlib.sha256(wheel.read_bytes()).hexdigest(),
    'source_hashes': source_hashes,
    'wheel_hashes': wheel_hashes,
    'identical': source_hashes == wheel_hashes,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
if not result['identical']:
    raise SystemExit(1)
