# tests/conftest.py
import sys
from pathlib import Path

# /Users/ajeet/Developer/Code/general-scaler
ROOT = Path(__file__).resolve().parents[1]

# Make sure project root is on sys.path so `import generalscaler` works in tests
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
