import { useLanguage } from '~/composables/useLanguage';
import type { LogStatus, EventType } from '~/config/constants';

/**
 * A centralized composable for handling all language-specific translations.
 */
export function useLocalization() {
    const { currentLanguage } = useLanguage();

    const getLocalizedStatus = (status: LogStatus | string | null | undefined): string => {
        if (!status) return 'N/A';
        if (currentLanguage.value !== 'vi') {
            return status;
        }

        const translations: Record<string, string> = {
            "Connected": "Đã kết nối",
            "Disconnected": "Mất kết nối",
            "Voltage reading ok": "Đọc điện áp OK",
            "Voltage reading failed": "Lỗi đọc điện áp",
            "Info": "Thông tin",
            "Warning": "Cảnh báo",
            "Error": "Lỗi",
            "Critical": "Nghiêm trọng",
            "Configured": "Đã cấu hình",
            "Reset": "Đặt lại",
            "Fault": "Sự cố",
            "Unknown": "Không xác định",
        };
        return translations[status] || status;
    };

    const getLocalizedEventType = (type: EventType | null | undefined): string => {
        if (!type) return 'N/A';
        if (currentLanguage.value !== 'vi') {
            return type;
        }

        const translations: Record<string, string> = {
            "Connection": "Kết nối",
            "Sensor Reading": "Đọc cảm biến",
            "Alert": "Cảnh báo",
            "User action": "Hành động người dùng",
            "System": "Hệ thống"
        };
        return translations[type] || type;
    };

    // --- MODIFICATION: Updated the formatting logic ---
    const getFormattedDeviceType = (type: string): string => {
        if (!type) return 'N/A';
        // This regex adds a space before a capital letter if it's preceded by a lowercase letter or a number.
        // This correctly splits "WristStrap" and "MonitorKD" but not "KD".
        let formatted = type.replace(/([a-z0-9])([A-Z])/g, '$1 $2');
        // Capitalize the first letter
        return formatted.charAt(0).toUpperCase() + formatted.slice(1);
    };

    return {
        getLocalizedStatus,
        getLocalizedEventType,
        getFormattedDeviceType,
    };
}