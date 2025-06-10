from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.setting import SystemSettingsResponse, SystemSettingsCreateUpdate
from app.crud import setting as setting_crud
from app.security import get_current_user, get_current_admin_user  # Assuming settings are protected
from app.schemas.user import User  # For current_user type hint
from fastapi.concurrency import run_in_threadpool
from app.db.session import get_db
import pymongo.database
from http import HTTPStatus  # For robust HTTP status codes
from pydantic import ValidationError  # To catch Pydantic validation errors

print("--- Loading settings.py endpoints ---")

router = APIRouter()


@router.get(
    "/",
    response_model=SystemSettingsResponse,
    summary="Get System Settings",
    description="Retrieves the global system settings for working time and production plan alerts.",
    dependencies=[Depends(get_current_user)],  # Use get_current_user for viewing settings
    status_code=status.HTTP_200_OK
)
async def read_settings(
        db: pymongo.database.Database = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    try:
        settings_data = await run_in_threadpool(setting_crud.get_settings, db)
        if settings_data is None:
            # If no settings document exists, return a default response or 404
            # Returning a default is often user-friendlier for initial load
            # Let's return an empty/default structure if not found
            # Ensure this matches a valid SystemSettingsResponse object
            return SystemSettingsResponse(
                _id=setting_crud.SETTINGS_DOC_ID,  # Use the defined fixed ID
                workingTime=[],
                productionPlan=[],
                createdAt=None,
                updatedAt=None  # Pydantic will handle default values if provided
            )
            # Alternatively, raise HTTPException(status.HTTP_404_NOT_FOUND, detail="System settings not found")

        # Pydantic model will handle conversion from 24hr to 12hr AM/PM and aliasing
        return SystemSettingsResponse(**settings_data)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error reading settings: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")


@router.put(
    "/",
    response_model=SystemSettingsResponse,
    summary="Update System Settings",
    description="Updates the global system settings for working time and production plan alerts.",
    dependencies=[Depends(get_current_admin_user)],  # Typically only admins can update settings
    status_code=status.HTTP_200_OK
)
async def update_system_settings(
        settings_in: SystemSettingsCreateUpdate,  # Input model handles frontend to backend conversion
        db: pymongo.database.Database = Depends(get_db),
        current_user: User = Depends(get_current_admin_user)  # Ensure user is admin
):
    try:
        # settings_in Pydantic model's validator automatically converts frontend 12hr to 24hr internal format
        updated_data = await run_in_threadpool(setting_crud.update_settings, db, settings_in)

        # Pydantic model will then convert from 24hr back to 12hr AM/PM for the response
        return SystemSettingsResponse(**updated_data)
    except ValidationError as e:
        # Catch Pydantic validation errors specifically to return 422
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors())
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating settings: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")