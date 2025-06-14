import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, status  # Removed WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio

# NEW IMPORTS FOR SOCKET.IO
import socketio  # Import the socketio library
from starlette.routing import Mount  # To mount the Socket.IO app

from app.core.config import settings

from app.db.session import connect_to_mongo_sync_managed, close_mongo_connection_sync_managed, \
    connect_to_mongo_async, close_mongo_connection_async

from app.mqtt.mqtt_client import mqtt_client_instance
from app.websocket.websocket_manager import websocket_manager

from app.api.v1.api import api_router

from app.core.logging_config import setup_logging

setup_logging()

logger = logging.getLogger(__name__)

# --- Initialize Socket.IO Server ---
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=settings.allowed_hosts)
socketio_app = socketio.ASGIApp(sio)  # Wrap the Socket.IO server as an ASGI app


# You can define Socket.IO events directly here or in a separate module
@sio.on("connect")
async def connect(sid, environ, auth):
    logger.info(f"Socket.IO client connected: {sid}")


@sio.on("disconnect")
async def disconnect(sid):
    logger.info(f"Socket.IO client disconnected: {sid}")


# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FastAPI application starting up...")

    # ... (MongoDB connections from before, unchanged) ...
    # 1. Connect to MongoDB (Synchronous Client FIRST)
    try:
        await connect_to_mongo_sync_managed()
    except RuntimeError as e:
        logger.critical(f"Failed to connect to MongoDB (synchronous client) during startup: {e}. Exiting application.")
        exit(1)

    # 2. Connect to MongoDB (Asynchronous Client)
    try:
        await connect_to_mongo_async()
    except RuntimeError as e:
        logger.critical(f"Failed to connect to MongoDB (asynchronous client) during startup: {e}. Exiting application.")
        await close_mongo_connection_sync_managed()
        exit(1)

    # NEW: Pass the Socket.IO server instance to the websocket_manager
    websocket_manager.set_socketio_instance(sio)

    # 3. Connect to MQTT Broker and subscribe
    try:
        await mqtt_client_instance.connect_and_subscribe(
            on_message_callback=websocket_manager.broadcast_json
        )
    except Exception as e:
        logger.critical(f"Failed to connect to MQTT broker or subscribe during startup: {e}. Exiting application.",
                        exc_info=True)
        await close_mongo_connection_sync_managed()
        await close_mongo_connection_async()
        exit(1)

    yield  # Application runs

    logger.info("FastAPI application shutting down...")

    # 1. Disconnect from MQTT Broker
    await mqtt_client_instance.disconnect()
    logger.info("MQTT client disconnected.")

    # 2. Close MongoDB Connections (both sync and async)
    await close_mongo_connection_async()
    await close_mongo_connection_sync_managed()
    logger.info("All MongoDB connections closed.")

    logger.info("FastAPI application shutdown complete.")


# Initialize FastAPI application
app = FastAPI(
    title=settings.project_name,
    description="Wrist Strap Web API (REST & Real-time)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the Socket.IO application on the /socket.io path
app.mount("/socket.io", socketio_app)

# Correct prefix for your API router
app.include_router(api_router, prefix="/api/v1")


# REMOVED: The native @app.websocket("/ws") endpoint is now gone
# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     # ... (code removed) ...
#     pass

# Example Root and Health Check Endpoints
@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    return {"message": f"Welcome to the {settings.project_name}!"}


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "ok", "message": "API is running and healthy."}

