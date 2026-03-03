"""Vercel serverless entrypoint — test import chain step by step."""

try:
    from app.main import app
except Exception as e:
    from fastapi import FastAPI
    app = FastAPI()

    @app.get("/")
    def error_handler():
        return {"error": str(e), "type": type(e).__name__}
