// File: plugins/api.ts

import { ofetch } from 'ofetch';
import { useUserStore } from '~/stores/userStore';
import { useLogger } from '~/composables/useLogger'; // <-- Import your logger
import { useActionStatusModal } from '~/composables/useActionStatusModal'; // Keep your modal composable

export default defineNuxtPlugin((_nuxtApp) => {
    const userStore = useUserStore();
    const config = useRuntimeConfig();
    const logger = useLogger(); // <-- Initialize your logger
    const { show: showActionModal } = useActionStatusModal();

    const apiFetch = ofetch.create({
        baseURL: config.public.apiBase,

        // This interceptor runs before every request
        onRequest({ request, options }) {
            // --- ADDED: Detailed request logging ---
            logger.log(`=> Request: ${options.method || 'GET'} ${request}`);
            console.groupCollapsed('Request Details');
            console.log('Options:', options);

            if (userStore.token) {
                // This correctly adds the token
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

        // --- ADDED: Logging for successful responses ---
        onResponse({ request, response, options }) {
            logger.log(`<= Response (Success): ${response.status} ${request}`);
            console.groupCollapsed('Response Details');
            console.log('Data:', response._data);
            console.groupEnd();
        },

        // This interceptor runs on every API error
        onResponseError({ request, response, options }) {
            // --- ADDED: Detailed error logging ---
            logger.error(`<= Response (Error): ${response.status} ${request}`);
            console.groupCollapsed('Error Response Details');
            console.log('Status:', response.status);
            console.log('Status Text:', response.statusText);
            console.log('Data:', response._data);
            console.groupEnd();

            // --- KEPT: Your existing modal logic for 401 errors ---
            if (response.status === 401) {
                showActionModal({
                    title: 'Session Expired',
                    description: 'Redirecting to the login page in {countdown} seconds...',
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