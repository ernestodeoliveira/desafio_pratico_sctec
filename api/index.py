from fastapi import FastAPI

app = FastAPI(title="Debug Test")


@app.get("/")
def root():
    return {"status": "alive"}


@app.get("/{path:path}")
def catch(path: str):
    return {"path": path}
