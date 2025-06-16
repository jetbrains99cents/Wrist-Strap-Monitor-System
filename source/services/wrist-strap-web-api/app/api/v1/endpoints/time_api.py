from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel

# Create a router object instead of a full FastAPI app
router = APIRouter()

# Define the response model
class TimeResponse(BaseModel):
    timestamp_utc_seconds: int
    iso_8601_utc: str

# Define the endpoint at the ROOT of this router ("/").
# The full path will be determined by how you include this router in your main app.
@router.get(
    "/",  # CHANGED: The path is now just "/"
    response_model=TimeResponse,
    summary="Get Current UTC Time"
)
def get_current_time():
    """
    Provides the official, synchronized time for all IoT devices on the network.
    """
    now_utc = datetime.now(timezone.utc)
    unix_timestamp_seconds = int(now_utc.timestamp())
    iso_format_string = now_utc.isoformat().replace('+00:00', 'Z')

    return TimeResponse(
        timestamp_utc_seconds=unix_timestamp_seconds,
        iso_8601_utc=iso_format_string
    )