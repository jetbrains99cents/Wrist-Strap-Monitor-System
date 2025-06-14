// stores/deviceRealtime.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useNuxtApp } from '#app';
import { useLogger } from '~/composables/useLogger';

// Type definition for a single real-time message (matches RealtimeDeviceStatusMessage from backend)
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

// Type definition for the stored device snapshot (latest per device in the store)
interface DeviceRealtimeSnapshot {
    id: string;
    name: string;
    mac_address: string;
    device_type: string;
    installation_area: string;
    firmware_version?: string | null;
    coordinates?: { row: number; col: number } | null;
    last_event: {
        type: 'Connection' | 'Sensor Reading' | 'Alert' | 'User action' | 'System';
        status?: 'Connected' | 'Disconnected' | 'Voltage reading ok' | 'Voltage reading failed' | 'Info' | 'Warning' | 'Error' | 'Critical' | 'Configured' | 'Reset' | null;
        timestamp: number;
        value: any;
    };
}

export const useDeviceRealtimeStore = defineStore('deviceRealtime', () => {
    const logger = useLogger();
    const {$socketClient} = useNuxtApp(); // Inject the WebSocket client

    // State: Map device_id to its latest real-time status snapshot
    const latestDeviceSnapshots = ref<Map<string, DeviceRealtimeSnapshot>>(new Map());

    // Action to initialize WebSocket listener
    const initRealtimeListeners = () => {
        logger.log('[DeviceRealtimeStore] initRealtimeListeners called.'); // NEW DEBUG LOG

        if (!$socketClient) {
            logger.error('[DeviceRealtimeStore] Socket client not available. Real-time updates will not work.');
            return;
        }

        logger.log('[DeviceRealtimeStore] $socketClient is available. Attempting connect.'); // NEW DEBUG LOG

        // Connect the socket if not already connected
        $socketClient.connect();

        // Register the listener for 'wristStrapData' event
        $socketClient.on('wristStrapData', (data: RealtimeDeviceStatusMessage) => {
            logger.log('[DeviceRealtimeStore] Received real-time update:', data);
            latestDeviceSnapshots.value.set(data.id, data as DeviceRealtimeSnapshot);
            logger.log(`[DeviceRealtimeStore] Updated snapshot for device ${data.id}: Status=${data.last_event.status}, Voltage=${data.last_event.value}`);
        });

        logger.log('[DeviceRealtimeStore] Real-time listeners registered.'); // NEW DEBUG LOG
    };

    // Getter to retrieve the latest snapshot for a specific device ID
    const getLatestSnapshotForDevice = computed(() => (deviceId: string) => {
        return latestDeviceSnapshots.value.get(deviceId);
    });

    // Cleanup action for when the store is no longer needed (optional)
    const cleanupRealtimeListeners = () => {
        if ($socketClient) {
            $socketClient.off('wristStrapData');
            logger.log('[DeviceRealtimeStore] Real-time listeners cleaned up.');
        }
    };

    return {
        latestDeviceSnapshots,
        initRealtimeListeners,
        getLatestSnapshotForDevice,
        cleanupRealtimeListeners,
    };
});