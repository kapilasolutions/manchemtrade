
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import webhooks, positions, quicktrade, watchlist, chains

app = FastAPI(title="ManchemTrade POC", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(webhooks.router, prefix="/api/v1", tags=["webhooks"])
app.include_router(positions.router, prefix="/api", tags=["positions"])
app.include_router(quicktrade.router, prefix="/api", tags=["quicktrade"])
app.include_router(watchlist.router, prefix="/api", tags=["watchlist"])
app.include_router(chains.router, prefix="/api", tags=["chains"])

@app.get("/health")
def health():
    return {"status": "ok", "service": "manchemtrade-poc", "dry_run": True}

@app.get("/")
def root():
    return {"message": "ManchemTrade POC running", "docs": "/docs"}
