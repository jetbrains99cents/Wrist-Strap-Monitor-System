from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings # Keep settings imported as it's used if other settings were defined

app = FastAPI(
    title="Wrist Strap Web API", # Hardcoded project name
    openapi_url="/api/v1/openapi.json" # Hardcoded API version string here
)

# Configure CORS
origins = [
    "https://172.16.9.183:3001",  # Your Nuxt dashboard HTTPS dev server
    "https://172.21.16.1SS:3001",  # Your Nuxt dashboard HTTPS dev server
    "https://localhost:3001",    # Localhost version of dashboard
    "http://localhost:3001",     # Fallback for HTTP dashboard dev if used
    "https://172.16.9.183:3000",  # Your Nuxt landing page HTTPS dev server
    "http://localhost:3000",     # Localhost version of landing page
    "http://127.0.0.1:3000",     # Common alternative localhost for landing page
    "https://127.0.0.1:3000",    # Common alternative localhost for landing page (HTTPS)
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the single main router with the version prefix (hardcoded)
app.include_router(api_router, prefix="/api/v1") # Hardcoded API version string here

@app.get("/")
def read_root():
    return {"message": "Welcome to the Wrist Strap Web API. Access docs at /api/v1/docs"}