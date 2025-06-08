// composables/useLogger.ts

export const useLogger = () => {
    const config = useRuntimeConfig();

    const log = (...args: any[]) => {
        if (config.public.loggingEnabled) {
            console.log('[LOG]:', ...args);
        }
    };

    const error = (...args: any[]) => {
        // We can choose to always show errors, or control them as well
        // if (config.public.loggingEnabled) {
        console.error('[ERROR]:', ...args);
        // }
    };

    const warn = (...args: any[]) => {
        if (config.public.loggingEnabled) {
            console.warn('[WARN]:', ...args);
        }
    };

    return {
        log,
        error,
        warn,
    };
};