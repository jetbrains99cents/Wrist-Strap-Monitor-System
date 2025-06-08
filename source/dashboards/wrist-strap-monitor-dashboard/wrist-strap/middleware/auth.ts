import { useUserStore } from '~/stores/userStore';
import { useLogger } from '~/composables/useLogger';

export default defineNuxtRouteMiddleware((to, from) => {
    // This middleware runs on every route change.
    const logger = useLogger();
    const userStore = useUserStore();

    // The login page is a public page, so we don't want to run the auth check on it.
    // This prevents an infinite redirect loop.
    if (to.path === '/login') {
        return;
    }

    // Initialize the user store.

    // Check if the user is logged in by looking for the token.
    // In a real application, you might also want to verify the token's expiry.
    if (!userStore.token) {
        // If there is no token, the user is not authenticated.
        // Redirect them to the login page.
        logger.log('User not authenticated, redirecting to /login');
        return navigateTo('/login');
    }

    // If the user has a token, they are allowed to proceed to the requested page.
    logger.log('User is authenticated, allowing access.');
});