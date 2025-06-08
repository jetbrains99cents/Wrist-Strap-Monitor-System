// File: plugins/api.ts

import { ofetch } from 'ofetch';
import { useUserStore } from '~/stores/userStore';

export default defineNuxtPlugin((_nuxtApp) => {
    const userStore = useUserStore();
    const config = useRuntimeConfig();
    const { show: showActionModal } = useActionStatusModal();

    const apiFetch = ofetch.create({
        baseURL: config.public.apiBase,

        // This interceptor runs before every request
        onRequest({ options }) {
            if (userStore.token) {
                // Create a new headers object or augment the existing one
                const headers = (options.headers ? new Headers(options.headers) : new Headers());
                headers.set('Authorization', `Bearer ${userStore.token}`);
                options.headers = headers;
            }
        },

        // This interceptor runs on every API error
        onResponseError({ response }) {
            if (response.status === 401) {
                // Use our new composable to show the modal
                showActionModal({
                    title: 'Session Expired',
                    description: 'Redirecting to the login page in {countdown} seconds...',
                    icon: 'i-heroicons-clock-solid',
                    color: 'text-amber-500',
                    onComplete: () => {
                        // When the countdown finishes, log the user out
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