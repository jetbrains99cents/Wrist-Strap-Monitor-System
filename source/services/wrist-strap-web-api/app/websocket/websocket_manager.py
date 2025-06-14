import logging
from typing import Dict, Any, Optional
# REMOVED: from fastapi import WebSocket, WebSocketDisconnect # No longer needed for native WS connection management
import socketio # NEW: Import socketio for type hinting

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self._sio: Optional[socketio.AsyncServer] = None # NEW: To hold the Socket.IO server instance

    def set_socketio_instance(self, sio_instance: socketio.AsyncServer): # NEW METHOD
        """Sets the initialized Socket.IO server instance."""
        self._sio = sio_instance
        logger.info("WebSocketManager received Socket.IO server instance.")

    # connect and disconnect methods are no longer needed as socketio manages connections
    # def connect(self, websocket: WebSocket): ...
    # def disconnect(self, websocket: WebSocket): ...

    async def broadcast_json(self, data: Dict[str, Any]):
        """
        Broadcasts a JSON serializable dictionary to all connected Socket.IO clients.
        """
        if self._sio is None:
            logger.error("Socket.IO instance not set in WebSocketManager. Cannot broadcast.")
            return

        try:
            # Use sio.emit to broadcast to all connected clients (room=None or omit)
            await self._sio.emit('wristStrapData', data) # 'wristStrapData' is the event name for frontend
            logger.debug(f"Broadcasted data via Socket.IO: {data}")
        except Exception as e:
            logger.error(f"Error broadcasting via Socket.IO: {e}", exc_info=True)

websocket_manager = ConnectionManager()