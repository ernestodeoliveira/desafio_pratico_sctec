"""Vercel entrypoint — minimal test."""

from fastapi import FastAPI

app = FastAPI(title="Test")


@app.get("/")
def root():
    return {"status": "ok"}
