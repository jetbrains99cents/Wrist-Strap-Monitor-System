# File: app/api/v1/endpoints/analytics.py

from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional
import pymongo.database

from app.db.session import get_db
from app.security import get_current_user
from app.schemas.user import User
from app.crud import analytics as analytics_crud

print("--- Loading analytics.py endpoints ---")

router = APIRouter()


@router.get(
    "/{metric}",
    summary="Get Analytics Data for Visualization",
    description="Fetches aggregated data for charts and key metrics based on the specified metric and filters.",
    status_code=status.HTTP_200_OK
)
def get_analytics(
        metric: str,
        db: pymongo.database.Database = Depends(get_db),
        dateRange: str = Query("7days", enum=["today", "7days", "30days", "all"]),
        area: Optional[str] = Query(None),
        current_user: User = Depends(get_current_user)
):
    """
    Main endpoint to retrieve all data needed for the data visualization page.

    - **metric**: The specific chart data to retrieve.
    - **dateRange**: The time period for the data.
    - **area**: Optional filter for a specific installation area.
    """
    try:
        data = analytics_crud.get_analytics_data(
            db=db,
            metric=metric,
            date_range=dateRange,
            area=area
        )
        return data
    except Exception as e:
        # In a real app, you would have more specific error logging here
        print(f"Error getting analytics for metric '{metric}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing analytics data."
        )