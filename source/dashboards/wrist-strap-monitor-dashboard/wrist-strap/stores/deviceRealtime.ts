// stores/deviceRealtime.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useNuxtApp } from '#app';
import { useLogger } from '~/composables/useLogger';

// Type definitions remain the same...
interface RealtimeDeviceStatusMessage {
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
    const {$socketClient} = useNuxtApp();

    const latestDeviceSnapshots = ref<Map<string, DeviceRealtimeSnapshot>>(new Map());

    // --- MODIFICATION: Renamed and simplified action ---
    // This action ONLY registers the event listener. It no longer connects.
    const establishRealtimeCommunication = () => {
        logger.log('[DeviceRealtimeStore] Establishing real-time communication...');

        if (!$socketClient) {
            logger.error('[DeviceRealtimeStore] Socket client not available.');
            return;
        }

        $socketClient.on('wristStrapData', (data: RealtimeDeviceStatusMessage) => {
            // This logic remains the same
            latestDeviceSnapshots.value.set(data.id, data as DeviceRealtimeSnapshot);
        });

        logger.log('[DeviceRealtimeStore] Event listeners registered.');
    };

    // --- MODIFICATION: Renamed action ---
    // This action ONLY removes the event listener.
    const terminateRealtimeCommunication = () => {
        if ($socketClient) {
            $socketClient.off('wristStrapData');
            logger.log('[DeviceRealtimeStore] Event listeners terminated.');
        }
    };

    const getLatestSnapshotForDevice = computed(() => (deviceId: string) => {
        return latestDeviceSnapshots.value.get(deviceId);
    });

    return {
        latestDeviceSnapshots,
        establishRealtimeCommunication, // --- MODIFICATION: Exporting new action name
        terminateRealtimeCommunication,   // --- MODIFICATION: Exporting new action name
        getLatestSnapshotForDevice,
    };
});