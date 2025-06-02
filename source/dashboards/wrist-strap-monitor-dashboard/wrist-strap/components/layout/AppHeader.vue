<template>
  <header
      ref="headerElement"
      class="app-header self-stretch overflow-hidden flex flex-row items-end justify-between p-3 md:p-4 box-border gap-5 max-w-full"
  >
    <!-- Logo Container -->
    <div
        ref="logoWrapper"
        class="overflow-hidden flex items-end justify-start p-0"
        aria-label="Company Logo"
    >
      <img
          ref="logoImage"
          class="relative object-contain h-12 sm:h-14 w-full"
          loading="lazy"
          alt="Sharp Logo"
          src="/sharp-logo.svg"
          onerror="this.onerror=null; this.src='https://placehold.co/150x60/cccccc/000000?text=Logo';"
      />
    </div>

    <!-- Text Container -->
    <div
        ref="textWrapper"
        class="overflow-hidden flex flex-col items-start justify-end p-0"
    >
      <h1
          class="app-header-title m-0 relative text-2xl md:text-[32px] lg:text-[40px] font-normal font-abeezee"
      >
        IoT Hub
      </h1>
      <h3
          class="app-header-subtitle m-0 relative text-base md:text-lg lg:text-2xl font-normal font-abeezee"
      >
        Researched and developed by Sharp Manufacturing Viet Nam
      </h3>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';

const logoWrapper = ref<HTMLElement | null>(null);
const logoImage = ref<HTMLImageElement | null>(null);
const textWrapper = ref<HTMLElement | null>(null);
const headerElement = ref<HTMLElement | null>(null);

const updateLogoWidth = () => {
  if (logoWrapper.value && textWrapper.value) {
    const textWidth = textWrapper.value.offsetWidth;
    logoWrapper.value.style.width = `${textWidth * 0.5}px`; // 50% of text container width
  }
};

onMounted(() => {
  updateLogoWidth();
  watch(() => textWrapper.value?.offsetWidth, updateLogoWidth);
  window.addEventListener('resize', updateLogoWidth);
});

onUnmounted(() => {
  window.removeEventListener('resize', updateLogoWidth);
});
</script>

<style scoped>
/* No additional scoped styles needed; Tailwind classes handle the layout */
</style>