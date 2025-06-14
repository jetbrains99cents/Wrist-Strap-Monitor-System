// stores/userStore.ts
import { defineStore } from 'pinia';
import { useDeviceRealtimeStore } from './deviceRealtime'; // --- MODIFICATION: Import realtime store
import { useNuxtApp } from '#app'; // --- MODIFICATION: Import Nuxt app context

interface User {
    id: number;
    name: string;
    email: string;
    roles: string[];
}

export const useUserStore = defineStore('user', {
    state: () => ({
        user: null as User | null,
        token: useCookie('auth_token').value || null,
    }),
    getters: {
        isLoggedIn: (state) => !!state.user,
        hasPermission: (state) => (permission: string) => {
            if (!state.user) return false;
            if (state.user.roles.includes('admin')) return true;
            if (state.user.roles.includes('manager') && permission.startsWith('edit')) return true;
            return false;
        },
    },
    actions: {
        async mockLogin(email: string) {
            const mockUser: User = { id: 1, name: 'Tan Nguyen', email, roles: ['admin', 'manager'] };
            const mockToken = 'mock-jwt-token-for-testing-12345';
            const userToken = useCookie('auth_token', { maxAge: 60 * 60 * 24 * 7 });
            userToken.value = mockToken;
            this.token = mockToken;
            this.user = mockUser;
        },

        finishLogin(userData: User, token: string) {
            const userToken = useCookie('auth_token', { maxAge: 60 * 60 * 24 * 7 });
            userToken.value = token;
            this.token = token;
            this.user = userData;
        },

        logout() {
            // --- MODIFICATION: Cleanly shut down real-time services BEFORE logging out ---
            const { $socketClient } = useNuxtApp();
            const deviceRealtimeStore = useDeviceRealtimeStore();

            deviceRealtimeStore.terminateRealtimeCommunication(); // Remove listeners
            $socketClient.disconnect(); // Disconnect the socket

            // Original logout logic
            const userToken = useCookie('auth_token');
            userToken.value = null;
            this.user = null;
            this.token = null;
            navigateTo('/login');
        },
    },
});