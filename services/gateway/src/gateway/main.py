from contracts.models import Language
from fastapi import FastAPI

app = FastAPI(title="Voicebridge Gateway", version="0.1.0")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "gateway"}


@app.get("/api/languages")
def get_languages():
    return {"languages": Language.load_languages()}
