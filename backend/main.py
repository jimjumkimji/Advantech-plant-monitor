# app/main.py
from fastapi import FastAPI

from backend.api.router import api_router

app = FastAPI(title="Decarbonator3000")

app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok"}
