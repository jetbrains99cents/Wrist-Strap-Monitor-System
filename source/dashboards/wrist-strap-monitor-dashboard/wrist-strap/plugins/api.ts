// File: plugins/api.ts

import { ofetch } from 'ofetch';
import { useUserStore } from '~/stores/userStore';
import { useLogger } from '~/composables/useLogger';
import { useActionStatusModal } from '~/composables/useActionStatusModal';
import { useLanguage } from '~/composables/useLanguage';

export default defineNuxtPlugin((_nuxtApp) => {
    const userStore = useUserStore();
    const config = useRuntimeConfig();
    const logger = useLogger();
    const { show: showActionModal } = useActionStatusModal();
    const { currentLanguage } = useLanguage();

    const apiFetch = ofetch.create({
        baseURL: config.public.apiBase,

        // This interceptor runs before every request
        onRequest({ request, options }) {
            // --- ADDED: Only log in development mode ---
            if (process.dev) {
                logger.log(`=> Request: ${options.method || 'GET'} ${request}`);
                console.groupCollapsed('Request Details');
                console.log('Options:', options);

                if (userStore.token) {
                    const headers = (options.headers ? new Headers(options.headers) : new Headers());
                    headers.set('Authorization', `Bearer ${userStore.token}`);
                    // Note: We are modifying options directly here as it's passed by reference
                    options.headers = headers;
                    console.log('Headers:', options.headers);
                }
                if (options.body) {
                    console.log('Body:', options.body);
                }
                console.groupEnd();
            } else { // --- ADDED: In production, just add the token without logging ---
                if (userStore.token) {
                    const headers = (options.headers ? new Headers(options.headers) : new Headers());
                    headers.set('Authorization', `Bearer ${userStore.token}`);
                    options.headers = headers;
                }
            }
        },

        // Logging for successful responses
        onResponse({ request, response, options }) {
            // --- ADDED: Only log in development mode ---
            if (process.dev) {
                logger.log(`<= Response (Success): ${response.status} ${request}`);
                console.groupCollapsed('Response Details');
                console.log('Data:', response._data);
                console.groupEnd();
            }
        },

        // This interceptor runs on every API error
        onResponseError({ request, response, options }) {
            // --- ADDED: Only log in development mode ---
            if (process.dev) {
                logger.error(`<= Response (Error): ${response.status} ${request}`);
                console.groupCollapsed('Error Response Details');
                console.log('Status:', response.status);
                console.log('Status Text:', response.statusText);
                console.log('Data:', response._data);
                console.groupEnd();
            }

            // Logic for 401 errors
            if (response.status === 401) {
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