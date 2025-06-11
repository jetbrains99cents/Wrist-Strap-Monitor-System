// composables/useStatusColor.ts

export const useStatusColor = () => {
    const config = useRuntimeConfig();
    const colorMap = config.public.statusColors as Record<string, string>;

    const getStatusColor = (status: string | null | undefined): string => {
        if (!status) {
            return 'slate'; // Use 'slate' as the safe default
        }
        return colorMap[status] || 'slate'; // Fallback to 'slate'
    };

    return {
        getStatusColor
    };
};