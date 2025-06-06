import { useUserStore } from '~/composables/stores/userStore';

export default defineNuxtRouteMiddleware((to, from) => {
    // This middleware runs on every route change.

    // The login page is a public page, so we don't want to run the auth check on it.
    // This prevents an infinite redirect loop.
    if (to.path === '/login') {
        return;
    }

    // Initialize the user store.
    const userStore = useUserStore();

    // Check if the user is logged in by looking for the token.
    // In a real application, you might also want to verify the token's expiry.
    if (!userStore.token) {
        // If there is no token, the user is not authenticated.
        // Redirect them to the login page.
        console.log('User not authenticated, redirecting to /login');
        return navigateTo('/login');
    }

    // If the user has a token, they are allowed to proceed to the requested page.
    console.log('User is authenticated, allowing access.');
});