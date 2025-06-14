// plugins/websocket.client.ts
import { defineNuxtPlugin, useRuntimeConfig } from '#app';
import { useLogger } from '~/composables/useLogger';
import { io, Socket } from 'socket.io-client'; // Import socket.io-client

// Define the type for the real-time event payload (matches RealtimeDeviceStatusMessage from backend)
interface RealtimeDeviceStatusMessage {
    id: string; // Device ID
    name: string;
    mac_address: string;
    device_type: string;
    installation_area: string;
    firmware_version?: string | null;
    coordinates?: { row: number; col: number } | null;
    last_event: { // EventDetails from backend schema
        type: 'Connection' | 'Sensor Reading' | 'Alert' | 'User action' | 'System';
        status?: 'Connected' | 'Disconnected' | 'Voltage reading ok' | 'Voltage reading failed' | 'Info' | 'Warning' | 'Error' | 'Critical' | 'Configured' | 'Reset' | null;
        timestamp: number;
        value: any;
    };
}

// Type for the WebSocket client instance exposed by the plugin
interface MySocketClient {
    connect: () => void;
    disconnect: () => void;
    on: (event: string, callback: (payload: any) => void) => void;
    off: (event: string, callback?: (payload: any) => void) => void;
    emit: (event: string, payload: any) => void; // If dashboard needs to send messages
    isConnected: boolean;
}

export default defineNuxtPlugin({
    name: 'socket-io',
    enforce: 'pre', // Ensure this runs early

    setup() {
        const logger = useLogger();
        const runtimeConfig = useRuntimeConfig();

        let socket: Socket | null = null; // Private socket.io instance
        const listeners = new Map<string, Set<(payload: any) => void>>(); // Store callbacks

        // FIXED: Read 'apiBase' from runtimeConfig.public. This directly matches your nuxt.config.ts
        const backendApiBase = runtimeConfig.public.apiBase as string;

        // Your nuxt.config.ts has apiBase: 'https://172.16.9.183:3002'.
        // The socket.io URL should just be this base. No need to split anything off.
        const socketIoUrl = backendApiBase; // Use backendApiBase directly as the socket.io URL

        const connectSocket = () => {
            if (socket && socket.connected) {
                logger.log('[WebSocket] Already connected.');
                return;
            }

            logger.log(`[WebSocket] Attempting to connect to ${socketIoUrl}`);
            socket = io(socketIoUrl, {
                transports: ['websocket'],
                // auth: { token: localStorage.getItem('auth_token') }
            });

            socket.on('connect', () => {
                logger.log('[WebSocket] Connected!');
                listeners.forEach((callbacks, eventName) => {
                    callbacks.forEach(callback => {
                        if (eventName !== 'connect' && eventName !== 'disconnect' && eventName !== 'connect_error') {
                            socket?.on(eventName, callback);
                        }
                    });
                });
            });

            socket.on('disconnect', (reason: string) => {
                logger.warn(`[WebSocket] Disconnected: ${reason}`);
            });

            socket.on('connect_error', (error: Error) => {
                logger.error(`[WebSocket] Connection Error: ${error.message}`, error);
            });

            socket.on('wristStrapData', (data: RealtimeDeviceStatusMessage) => {
                logger.log('[WebSocket] Received wristStrapData:', data);
                listeners.get('wristStrapData')?.forEach(callback => callback(data));
            });
        };

        const disconnectSocket = () => {
            if (socket && socket.connected) {
                socket.disconnect();
                logger.log('[WebSocket] Disconnected manually.');
            }
        };

        const mySocketClient: MySocketClient = {
            connect: connectSocket,
            disconnect: disconnectSocket,
            on: (event: string, callback: (payload: any) => void) => {
                if (!listeners.has(event)) listeners.set(event, new Set());
                listeners.get(event)?.add(callback);
                if (socket?.connected && event !== 'connect' && event !== 'disconnect' && event !== 'connect_error') {
                    socket.on(event, callback);
                }
                logger.log(`[WebSocket] Registered listener for event: ${event}`);
            },
            off: (event: string, callback?: (payload: any) => void) => {
                if (listeners.has(event)) {
                    if (callback) {
                        listeners.get(event)?.delete(callback);
                        socket?.off(event, callback);
                        logger.log(`[WebSocket] Unregistered specific listener for event: ${event}`);
                    } else {
                        listeners.get(event)?.clear();
                        socket?.off(event);
                        logger.log(`[WebSocket] Unregistered all listeners for event: ${event}`);
                    }
                }
            },
            emit: (event: string, payload: any) => {
                if (socket?.connected) {
                    socket.emit(event, payload);
                    logger.log(`[WebSocket] Emitted event: ${event}`, payload);
                } else {
                    logger.warn(`[WebSocket] Attempted to emit '${event}' but socket is not connected.`);
                }
            },
            get isConnected() {
                return socket?.connected || false;
            }
        };

        return {
            provide: {
                socketClient: mySocketClient
            }
        };
    },
});