"""Vercel serverless entrypoint — diagnose import errors."""

import traceback

try:
    from app.main import app
except Exception as e:
    from fastapi import FastAPI
    app = FastAPI()
    _error = traceback.format_exc()

    @app.get("/")
    def error_handler():
        return {"error": str(e), "type": type(e).__name__, "traceback": _error}

    @app.get("/{path:path}")
    def catch_all(path: str):
        return {"error": str(e), "type": type(e).__name__, "traceback": _error}
