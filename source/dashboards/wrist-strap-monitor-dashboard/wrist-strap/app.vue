<template>
  <div>
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useUserStore } from '~/stores/userStore';
import { useLogger } from '~/composables/useLogger';
import { useDeviceRealtimeStore } from '~/stores/deviceRealtime'; // --- MODIFICATION: Import realtime store

const { $api, $socketClient } = useNuxtApp(); // --- MODIFICATION: Add $socketClient
const logger = useLogger();

useHead({
  htmlAttrs: { lang: 'en' }
});

const userStore = useUserStore();
const deviceRealtimeStore = useDeviceRealtimeStore(); // --- MODIFICATION: Get store instance

onMounted(async () => {
  if (userStore.token && !userStore.user) {
    logger.log('[app.vue] Token found, attempting to fetch user profile...');
    try {
      const user = await $api('/api/v1/users/me');
      userStore.user = user;
      logger.log('[app.vue] User profile hydrated successfully.');

      // --- MODIFICATION: Start the global WebSocket connection and listeners ---
      // This now happens only ONCE per application session for a logged-in user.
      logger.log('[app.vue] Authenticated session confirmed. Starting real-time services...');
      $socketClient.connect();
      deviceRealtimeStore.establishRealtimeCommunication();

    } catch (error) {
      logger.error('[app.vue] Failed to fetch user profile on startup. Real-time services not started.', error);
      // Optional: you might want to log the user out if their token is invalid
      // userStore.logout();
    }
  }
});
</script>