import { defineStore } from 'pinia';

// Define the structure of the User object
interface User {
    id: number;
    name: string;
    email: string;
    roles: string[];
}

export const useUserStore = defineStore('user', {
    // The state holds the current user's data and token
    state: () => ({
        user: null as User | null,
        token: useCookie('auth_token').value || null,
    }),
    getters: {
        // A simple getter to check if the user is logged in
        isLoggedIn: (state) => !!state.user,
        // A function to check if the logged-in user has a specific permission
        hasPermission: (state) => (permission: string) => {
            if (!state.user) return false;
            // This is where you will implement real permission logic based on roles.
            // For example, an admin can do anything.
            if (state.user.roles.includes('admin')) return true;
            // A manager might only have "edit" permissions
            if (state.user.roles.includes('manager') && permission.startsWith('edit')) return true;

            return false; // By default, deny permission
        },
    },
    actions: {
        // This function simulates a successful login for testing purposes.
        // Replace this with your actual login logic later.
        async mockLogin(email: string) {
            // In a real app, this data would come from your API response
            const mockUser: User = { id: 1, name: 'Tan Nguyen', email, roles: ['admin', 'manager'] };
            const mockToken = 'mock-jwt-token-for-testing-12345';

            const userToken = useCookie('auth_token', { maxAge: 60 * 60 * 24 * 7 }); // Cookie expires in 7 days
            userToken.value = mockToken;

            this.token = mockToken;
            this.user = mockUser;
        },

        // This function will be used when you connect to the real API
        finishLogin(userData: User, token: string) {
            const userToken = useCookie('auth_token', { maxAge: 60 * 60 * 24 * 7 });
            userToken.value = token;
            this.token = token;
            this.user = userData;
        },

        // Clears the user's session and redirects to the login page
        logout() {
            const userToken = useCookie('auth_token');
            userToken.value = null;
            this.user = null;
            this.token = null;
            navigateTo('/login');
        },
    },
});