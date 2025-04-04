# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.db.database import init_models
from app.services.aptos_minter import ensure_collection_exists
from app.services import ml_validator

app = FastAPI(title="Aptos NFT Guardian")

# CORS config for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    print("Loading ML model into memory...")
    _ = ml_validator.model
    _ = ml_validator.processor
    print("ML model loaded.")
    print("Backend starting up...")
    await init_models()
    await ensure_collection_exists()
