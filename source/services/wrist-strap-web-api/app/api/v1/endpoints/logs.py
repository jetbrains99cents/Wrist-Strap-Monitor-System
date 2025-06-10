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

print("--- Loading logs.py endpoints ---")

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedLogsResponse,
    summary="Retrieve Paginated and Filtered Historical Logs",
    description="Fetches historical log data with comprehensive filtering, searching, sorting, and pagination. All filtering and sorting is handled server-side.",
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_200_OK
)
async def read_logs(
        db: pymongo.database.Database = Depends(get_db),
        start_date: Optional[datetime] = Query(
            None,
            description="Start date and time for filtering logs (ISO 8601 format, e.g., 2023-01-01T00:00:00Z).",
            examples=["2023-01-01T00:00:00Z"]
        ),
        end_date: Optional[datetime] = Query(
            None,
            description="End date and time for filtering logs (ISO 8601 format, e.g., 2023-01-31T23:59:59Z).",
            examples=["2023-01-31T23:59:59Z"]
        ),
        event_type: Optional[str] = Query(
            None,
            description="Filter logs by event category.",
            enum=["Connection", "Sensor Reading", "Alert", "User action", "System"]
        ),
        status: Optional[str] = Query(
            None,
            description="Filter logs by event status.",
            enum=["Connected", "Disconnected", "Voltage reading failed", "Info", "Warning", "Error", "Critical",
                  "Configured", "Reset"]
        ),
        search_term: Optional[str] = Query(
            None,
            description="General full-text search term applied across device name, MAC address, installation area, event type, and status."
        ),
        page: int = Query(1, ge=1, description="Page number (1-indexed) for pagination."),
        page_size: int = Query(15, ge=1, le=100, description="Number of items per page for pagination."),
        sort_by: str = Query(
            "timestamp",
            description="Field to sort the logs by. Corresponds to frontend column keys.",
            enum=["timestamp", "deviceName", "deviceMacAddress", "area", "eventType", "status"]
        ),
        sort_direction: str = Query(
            "desc",
            description="Sort direction ('asc' for ascending, 'desc' for descending).",
            enum=["asc", "desc"]
        ),
        current_user: User = Depends(get_current_user)
):
    skip = (page - 1) * page_size
    try:
        logs_raw_data, total_count = await run_in_threadpool(
            log_crud.get_multi_logs,
            db,
            start_date=start_date,
            end_date=end_date,
            event_type=event_type,
            status=status,
            search_term=search_term,
            skip=skip,
            limit=page_size,
            sort_by=sort_by,
            sort_direction=sort_direction
        )

        logs_response_items = [HistoricalLogResponse(**log_doc) for log_doc in logs_raw_data]

        return {"items": logs_response_items, "total_count": total_count}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching logs: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")


# NEW: Endpoint for Exporting All Filtered Logs
@router.get(
    "/export/",  # New path for export
    response_model=List[HistoricalLogResponse],  # Returns a list of log objects, no pagination envelope
    summary="Export All Filtered Historical Logs",
    description="Fetches ALL historical log data matching the applied filters, without pagination, for export purposes.",
    dependencies=[Depends(get_current_user)],  # Requires authentication
    status_code=status.HTTP_200_OK
)
async def export_logs(
        db: pymongo.database.Database = Depends(get_db),
        start_date: Optional[datetime] = Query(None, description="Start date and time for filtering logs."),
        end_date: Optional[datetime] = Query(None, description="End date and time for filtering logs."),
        event_type: Optional[str] = Query(None, description="Filter logs by event category.",
                                          enum=["Connection", "Sensor Reading", "Alert", "User action", "System"]),
        status: Optional[str] = Query(None, description="Filter logs by event status.",
                                      enum=["Connected", "Disconnected", "Voltage reading failed", "Info", "Warning",
                                            "Error", "Critical", "Configured", "Reset"]),
        search_term: Optional[str] = Query(None, description="General full-text search term."),
        sort_by: str = Query("timestamp", description="Field to sort the logs by.",
                             enum=["timestamp", "deviceName", "deviceMacAddress", "area", "eventType", "status"]),
        sort_direction: str = Query("desc", description="Sort direction ('asc' or 'desc')."),
        current_user: User = Depends(get_current_user)
):
    try:
        # Call a new CRUD function that fetches all matching logs without limit/skip
        # Or modify get_multi_logs to handle an optional 'limit' of None or a very large number
        logs_raw_data = await run_in_threadpool(
            log_crud.get_all_filtered_logs,  # NEW: Calling a dedicated CRUD function
            db,
            start_date=start_date,
            end_date=end_date,
            event_type=event_type,
            status=status,
            search_term=search_term,
            sort_by=sort_by,
            sort_direction=sort_direction
        )

        # Transform raw MongoDB dicts into Pydantic models for response.
        logs_response_items = [HistoricalLogResponse(**log_doc) for log_doc in logs_raw_data]

        return logs_response_items
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error exporting logs: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                            detail=f"Internal Server Error during export: {e}")