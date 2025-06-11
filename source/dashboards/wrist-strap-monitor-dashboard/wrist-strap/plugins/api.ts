// File: plugins/api.ts

import { ofetch } from 'ofetch';
import { useUserStore } from '~/stores/userStore';
import { useLogger } from '~/composables/useLogger';
import { useActionStatusModal } from '~/composables/useActionStatusModal';
import { useLanguage } from '~/composables/useLanguage'; // --- ADDED: Import language composable ---

export default defineNuxtPlugin((_nuxtApp) => {
    const userStore = useUserStore();
    const config = useRuntimeConfig();
    const logger = useLogger();
    const { show: showActionModal } = useActionStatusModal();
    const { currentLanguage } = useLanguage(); // --- ADDED: Get reactive language state ---

    const apiFetch = ofetch.create({
        baseURL: config.public.apiBase,

        // This interceptor runs before every request
        onRequest({ request, options }) {
            // Detailed request logging
            logger.log(`=> Request: ${options.method || 'GET'} ${request}`);
            console.groupCollapsed('Request Details');
            console.log('Options:', options);

            if (userStore.token) {
                const headers = (options.headers ? new Headers(options.headers) : new Headers());
                headers.set('Authorization', `Bearer ${userStore.token}`);
                options.headers = headers;
                console.log('Headers:', options.headers);
            }
            if (options.body) {
                console.log('Body:', options.body);
            }
            console.groupEnd();
        },

        // Logging for successful responses
        onResponse({ request, response, options }) {
            logger.log(`<= Response (Success): ${response.status} ${request}`);
            console.groupCollapsed('Response Details');
            console.log('Data:', response._data);
            console.groupEnd();
        },

        // This interceptor runs on every API error
        onResponseError({ request, response, options }) {
            // Detailed error logging
            logger.error(`<= Response (Error): ${response.status} ${request}`);
            console.groupCollapsed('Error Response Details');
            console.log('Status:', response.status);
            console.log('Status Text:', response.statusText);
            console.log('Data:', response._data);
            console.groupEnd();

            // Logic for 401 errors
            if (response.status === 401) {
                // --- UPDATED: Use dynamic text based on current language ---
                showActionModal({
                    title: currentLanguage.value === 'vi'
                        ? 'Phiên đã hết hạn'
                        : 'Session Expired',
                    description: currentLanguage.value === 'vi'
                        ? 'Đang chuyển hướng đến trang đăng nhập trong {countdown} giây...'
                        : 'Redirecting to the login page in {countdown} seconds...',
                    icon: 'i-heroicons-clock-solid',
                    color: 'text-amber-500',
                    onComplete: () => {
                        userStore.logout();
                    },
                });
            }
        }
    });

    // Provide the global fetch instance to the entire app
    return {
        provide: {
            api: apiFetch,
        },
    };
});
