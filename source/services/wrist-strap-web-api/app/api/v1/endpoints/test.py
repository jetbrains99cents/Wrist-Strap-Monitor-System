# File: app/api/v1/endpoints/test.py

from fastapi import APIRouter

print("--- Loading test.py endpoints ---")  # <-- ADD THIS LINE

router = APIRouter()


@router.get("/ping")
def ping_server():
    """
    A simple endpoint to check if the server is running and reachable.
    """
    return {"message": "pong"}
