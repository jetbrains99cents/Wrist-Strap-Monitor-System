<template>
  <div class="default-layout flex flex-col h-screen overflow-hidden bg-white dark:bg-dark-bg text-gray-900 dark:text-dark-text-primary">
    <AppHeader />

    <main
        class="flex-1 w-full self-stretch flex flex-col overflow-hidden"
        :style="{ paddingBottom: footerHeight + 'px' }"
    >
      <slot />
    </main>

    <AppFooter ref="appFooterInstance" />

    <!-- ADD THIS NEW COMPONENT AT THE END -->
    <LayoutActionStatusModal />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import AppFooter from "~/components/layout/AppFooter.vue";
import AppHeader from "~/components/layout/AppHeader.vue";
// Import the new modal component
import LayoutActionStatusModal from '~/components/layout/ActionStatusModal.vue';

const appFooterInstance = ref<{ $el: HTMLElement } | null>(null);
const footerHeight = ref(0);
let resizeObserver: ResizeObserver | null = null;

const updateFooterHeightCallback = () => {
  if (appFooterInstance.value?.$el) {
    const footerEl = appFooterInstance.value.$el;
    if (window.getComputedStyle(footerEl).position === 'fixed') {
      footerHeight.value = footerEl.offsetHeight;
    } else {
      footerHeight.value = 0;
    }
  } else {
    footerHeight.value = 0;
  }
};

onMounted(async () => {
  await nextTick();
  updateFooterHeightCallback();

  if (appFooterInstance.value?.$el) {
    resizeObserver = new ResizeObserver(updateFooterHeightCallback);
    resizeObserver.observe(appFooterInstance.value.$el);
  }
  window.addEventListener('resize', updateFooterHeightCallback);
});

onUnmounted(() => {
  if (resizeObserver && appFooterInstance.value?.$el) {
    resizeObserver.unobserve(appFooterInstance.value.$el);
  }
  if (resizeObserver) {
    resizeObserver.disconnect();
  }
  window.removeEventListener('resize', updateFooterHeightCallback);
});
</script>

<style scoped>
/* Styles for hiding scrollbar on main are removed as main now has overflow:hidden */
</style>