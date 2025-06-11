# File: app/api/v1/endpoints/settings.py

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.setting import SystemSettingsResponse, SystemSettingsCreateUpdate
from app.crud import setting as setting_crud
from app.security import get_current_user, get_current_admin_user
from app.schemas.user import User
from fastapi.concurrency import run_in_threadpool
from app.db.session import get_db
import pymongo.database
from http import HTTPStatus
from pydantic import ValidationError

# Get a logger instance for this file
logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/",
    response_model=SystemSettingsResponse,
    summary="Get System Settings",
    description="Retrieves the global system settings for working time and production plan alerts.",
    status_code=status.HTTP_200_OK
)
async def read_settings(
        db: pymongo.database.Database = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Retrieves the global system settings.
    """
    user_email = current_user.get("email")
    logger.info(f"User '{user_email}' is requesting system settings.")
    try:
        settings_data = await run_in_threadpool(setting_crud.get_settings, db)
        if settings_data is None:
            logger.info("No system settings document found in the database. Returning a default structure.")
            return SystemSettingsResponse(
                _id=setting_crud.SETTINGS_DOC_ID,
                workingTime=[],
                productionPlan=[],
                createdAt=None,
                updatedAt=None
            )
        return SystemSettingsResponse(**settings_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while user '{user_email}' was reading settings: {e}", exc_info=True)
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="An internal server error occurred while reading settings.")


@router.put(
    "/",
    response_model=SystemSettingsResponse,
    summary="Update System Settings",
    description="Updates the global system settings. Requires admin privileges.",
    status_code=status.HTTP_200_OK
)
async def update_system_settings(
        settings_in: SystemSettingsCreateUpdate,
        db: pymongo.database.Database = Depends(get_db),
        current_user: User = Depends(get_current_admin_user)
):
    """
    Updates the global system settings. Admin only.
    """
    admin_email = current_user.get("email")
    logger.info(f"Admin '{admin_email}' is attempting to update system settings.")
    try:
        updated_data = await run_in_threadpool(setting_crud.update_settings, db, settings_in)
        logger.info(f"System settings successfully updated by admin '{admin_email}'.")
        return SystemSettingsResponse(**updated_data)
    except ValidationError as e:
        logger.warning(f"Validation error during settings update by admin '{admin_email}': {e.errors()}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while admin '{admin_email}' was updating settings: {e}", exc_info=True)
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="An internal server error occurred while updating settings.")