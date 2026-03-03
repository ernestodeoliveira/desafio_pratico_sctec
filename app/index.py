"""Vercel entrypoint — re-exports the FastAPI app from main."""

from app.main import app  # noqa: F401
