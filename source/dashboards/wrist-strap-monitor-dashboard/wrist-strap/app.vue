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

const { $api } = useNuxtApp();
const logger = useLogger();

useHead({
  htmlAttrs: { lang: 'en' }
});

const userStore = useUserStore();

onMounted(async () => {
  if (userStore.token && !userStore.user) {
    logger.log('[app.vue] Token found, attempting to fetch user profile...');
    try {
      const user = await $api('/api/v1/users/me');

      logger.log('[app.vue] User profile hydrated successfully. User data:', JSON.parse(JSON.stringify(user)));

      userStore.user = user;
    } catch (error) {
      logger.error('[app.vue] Failed to fetch user profile on startup.', error);
    }
  }
});
</script>