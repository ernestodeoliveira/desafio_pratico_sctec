"""Vercel serverless entrypoint."""

import sys
from pathlib import Path

# Add project root to Python path so `app` package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402, F401
