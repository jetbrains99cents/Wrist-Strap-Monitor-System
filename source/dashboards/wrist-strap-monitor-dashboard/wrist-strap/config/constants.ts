// config/constants.ts

export const LOG_STATUSES = [
    "Connected", "Disconnected", "Voltage reading ok", "Voltage reading failed",
    "Info", "Warning", "Error", "Critical", "Configured", "Reset", "Fault", "Unknown"
] as const;

export const EVENT_TYPES = [
    "Connection", "Sensor Reading", "Alert", "User action", "System"
] as const;

// --- MODIFICATION: Add Device Types constant array ---
export const DEVICE_TYPES = [
    "WristStrapMonitorKD2001",
    "WristStrapMonitorKD2002"
] as const;

export type LogStatus = typeof LOG_STATUSES[number];
export type EventType = typeof EVENT_TYPES[number];
// --- MODIFICATION: Add DeviceType export ---
export type DeviceType = typeof DEVICE_TYPES[number];