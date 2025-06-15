// ~/config/constants.ts

// The single source of truth for all possible log statuses
export const LOG_STATUSES = [
    "Connected",
    "Disconnected",
    "Voltage reading ok",
    "Voltage reading failed",
    "Info",
    "Warning",
    "Error",
    "Critical",
    "Configured",
    "Reset",
    "Fault",
    "Unknown"
] as const;

// The single source of truth for all possible event types
export const EVENT_TYPES = [
    "Connection",
    "Sensor Reading",
    "Alert",
    "User action",
    "System"
] as const;

// Automatically generate the TypeScript types from the arrays above
export type LogStatus = typeof LOG_STATUSES[number];
export type EventType = typeof EVENT_TYPES[number];