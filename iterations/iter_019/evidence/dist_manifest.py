import hashlib
import json
import platform
from pathlib import Path

root = Path('.').resolve()
files = {}
for path in sorted((root / 'dist').glob('traceopt-0.1.0*')):
    files[path.name] = {
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'size': path.stat().st_size,
    }
result = {'cwd': str(root), 'python': platform.python_version(), 'files': files}
print(json.dumps(result, ensure_ascii=False, indent=2))
