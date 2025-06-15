import { useLanguage } from '~/composables/useLanguage';
import type { LogStatus, EventType } from '~/config/constants';

/**
 * A centralized composable for handling all language-specific translations.
 */
export function useLocalization() {
    // Internally uses the useLanguage composable to react to language changes.
    const { currentLanguage } = useLanguage();

    /**
     * Translates a device status into the currently selected language.
     * @param status The status string to translate.
     * @returns The translated string, or the original string if no translation is available.
     */
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

    /**
     * Translates an event type into the currently selected language.
     * @param type The event type string to translate.
     * @returns The translated string, or the original string if no translation is available.
     */
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

    return {
        getLocalizedStatus,
        getLocalizedEventType,
    };
}