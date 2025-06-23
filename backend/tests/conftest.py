"""Pytest configuration for backend tests.
Ensures the `src` package (located in backend/src) is on `sys.path`
so that tests can simply `import src...` regardless of current
working directory.
"""

import sys
from pathlib import Path

# Resolve <repo_root>/backend/src
repo_root = Path(__file__).resolve().parents[2]
src_path = repo_root / "backend" / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path)) 