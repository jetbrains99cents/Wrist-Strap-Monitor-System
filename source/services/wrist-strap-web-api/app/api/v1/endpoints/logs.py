# File: app/api/v1/endpoints/logs.py

import logging
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, List
from app.schemas.log import HistoricalLogResponse, PaginatedLogsResponse
from app.crud import log as log_crud
from app.security import get_current_user
from app.schemas.user import User
from datetime import datetime
from http import HTTPStatus
from fastapi.concurrency import run_in_threadpool
from app.db.session import get_db
import pymongo.database

# Get a logger instance for this file
logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedLogsResponse,
    summary="Retrieve Paginated and Filtered Historical Logs",
    description="Fetches historical log data with comprehensive filtering, searching, sorting, and pagination.",
    status_code=status.HTTP_200_OK
)
async def read_logs(
        db: pymongo.database.Database = Depends(get_db),
        start_date: Optional[datetime] = Query(None, description="Start date and time (ISO 8601)."),
        end_date: Optional[datetime] = Query(None, description="End date and time (ISO 8601)."),
        event_type: Optional[str] = Query(None,
                                          enum=["Connection", "Sensor Reading", "Alert", "User action", "System"]),
        status: Optional[str] = Query(None,
                                      enum=["Connected", "Disconnected", "Voltage reading failed", "Info", "Warning",
                                            "Error", "Critical", "Configured", "Reset"]),
        search_term: Optional[str] = Query(None, description="General full-text search term."),
        page: int = Query(1, ge=1, description="Page number."),
        page_size: int = Query(15, ge=1, le=100, description="Number of items per page."),
        sort_by: str = Query("timestamp",
                             enum=["timestamp", "deviceName", "deviceMacAddress", "area", "eventType", "status"]),
        sort_direction: str = Query("desc", enum=["asc", "desc"]),
        current_user: User = Depends(get_current_user)
):
    user_email = current_user.get("email")
    log_details = f"page: {page}, page_size: {page_size}, sort: {sort_by} {sort_direction}, search: '{search_term or ''}'"
    logger.info(f"User '{user_email}' requesting historical logs. {log_details}")

    skip = (page - 1) * page_size
    try:
        logs_raw_data, total_count = await run_in_threadpool(
            log_crud.get_multi_logs,
            db, start_date=start_date, end_date=end_date, event_type=event_type, status=status,
            search_term=search_term, skip=skip, limit=page_size, sort_by=sort_by, sort_direction=sort_direction
        )
        logs_response_items = [HistoricalLogResponse(**log_doc) for log_doc in logs_raw_data]
        logger.info(f"Successfully served {len(logs_response_items)} of {total_count} logs to user '{user_email}'.")
        return {"items": logs_response_items, "total_count": total_count}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching logs for user '{user_email}': {e}", exc_info=True)
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                            detail="An internal server error occurred while fetching logs.")


@router.get(
    "/export/",
    response_model=List[HistoricalLogResponse],
    summary="Export All Filtered Historical Logs",
    description="Fetches ALL historical log data matching the applied filters, without pagination.",
    status_code=status.HTTP_200_OK
)
async def export_logs(
        db: pymongo.database.Database = Depends(get_db),
        start_date: Optional[datetime] = Query(None),
        end_date: Optional[datetime] = Query(None),
        event_type: Optional[str] = Query(None,
                                          enum=["Connection", "Sensor Reading", "Alert", "User action", "System"]),
        status: Optional[str] = Query(None,
                                      enum=["Connected", "Disconnected", "Voltage reading failed", "Info", "Warning",
                                            "Error", "Critical", "Configured", "Reset"]),
        search_term: Optional[str] = Query(None),
        sort_by: str = Query("timestamp",
                             enum=["timestamp", "deviceName", "deviceMacAddress", "area", "eventType", "status"]),
        sort_direction: str = Query("desc"),
        current_user: User = Depends(get_current_user)
):
    user_email = current_user.get("email")
    log_details = f"sort: {sort_by} {sort_direction}, search: '{search_term or ''}'"
    logger.info(f"User '{user_email}' requesting log export. {log_details}")

    try:
        logs_raw_data = await run_in_threadpool(
            log_crud.get_all_filtered_logs,
            db, start_date=start_date, end_date=end_date, event_type=event_type,
            status=status, search_term=search_term, sort_by=sort_by, sort_direction=sort_direction
        )
        logs_response_items = [HistoricalLogResponse(**log_doc) for log_doc in logs_raw_data]
        logger.info(f"Successfully processed export of {len(logs_response_items)} logs for user '{user_email}'.")
        return logs_response_items
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting logs for user '{user_email}': {e}", exc_info=True)
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                            detail="An internal server error occurred during export.")