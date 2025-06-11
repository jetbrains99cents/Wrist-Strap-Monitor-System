# File: app/api/v1/endpoints/analytics.py

import logging
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional
import pymongo.database

from app.db.session import get_db
from app.security import get_current_user
from app.schemas.user import User
from app.crud import analytics as analytics_crud

# Get a logger instance for this file
logger = logging.getLogger(__name__)
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
    user_email = current_user.get("email")
    log_details = f"metric: {metric}, dateRange: {dateRange}, area: {area or 'all'}"
    logger.info(f"User '{user_email}' requesting analytics data with filters: {log_details}")

    try:
        data = analytics_crud.get_analytics_data(
            db=db,
            metric=metric,
            date_range=dateRange,
            area=area
        )
        logger.info(f"Successfully processed analytics request for user '{user_email}' with filters: {log_details}")
        return data
    except Exception as e:
        logger.error(
            f"Error processing analytics for user '{user_email}' with filters: {log_details}. Error: {e}",
            exc_info=True  # This will include the full traceback in the log
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing analytics data."
        )