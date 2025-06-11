# File: main.py

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging

# Call the logging setup function right at the beginning
setup_logging()

app = FastAPI(
    title=settings.project_name,
    openapi_url="/api/v1/openapi.json"
)

# Configure CORS with the specific origins from your configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": f"Welcome to the {settings.project_name}. Access docs at /docs"}