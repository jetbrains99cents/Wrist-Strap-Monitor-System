from fastapi import APIRouter, Depends, Query, HTTPException, status # Added 'status' import
from typing import Optional, List
from app.schemas.log import LogInDB
from app.crud import log as log_crud
from app.security import get_current_user
from app.schemas.user import User
from datetime import datetime

print("--- Loading logs.py endpoints ---")

router = APIRouter()

@router.get("/", response_model=List[LogInDB])
def read_logs(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    event_type: Optional[str] = None,
    status: Optional[str] = None,
    search_term: Optional[str] = Query(None, alias="q"),
    page: int = 1,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    skip = (page - 1) * limit
    try:
        logs = log_crud.get_multi_logs(
            start_date=start_date,
            end_date=end_date,
            event_type=event_type,
            status=status,
            search_term=search_term,
            skip=skip,
            limit=limit
        )
        return logs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error while fetching logs: {e}"
        )


@router.get("/count", response_model=int)
def read_logs_count(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    event_type: Optional[str] = None,
    status: Optional[str] = None,
    search_term: Optional[str] = Query(None, alias="q"),
    current_user: User = Depends(get_current_user)
):
    try:
        count = log_crud.get_logs_count(
            start_date=start_date,
            end_date=end_date,
            event_type=event_type,
            status=status,
            search_term=search_term
        )
        return count
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error while counting logs: {e}"
        )