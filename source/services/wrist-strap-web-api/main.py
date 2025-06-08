# File: main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# --- CORRECTED: Import the main api_router, not individual endpoints ---
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title="Wrist Strap Web API",
    openapi_url="/api/v1/openapi.json"
)

# Configure CORS
origins = [
    "https://172.16.9.183:3001",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CORRECTED: Include the single main router with the version prefix ---
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": f"Welcome to the {settings.database_name} API"}
