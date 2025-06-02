<template>
  <div
      class="device-card flex flex-col items-center justify-center text-center
           p-4 min-w-[180px] sm:min-w-[200px] h-28 rounded-3xl
           shadow-md transition-all duration-200 ease-in-out
           transform hover:scale-105 font-abeezee"
      :class="statusColorClasses"
  >
    <span class="device-name block font-semibold text-lg leading-tight truncate w-full">
      {{ device.name }}
    </span>
    <span class="device-area block text-xs mt-1 leading-tight opacity-90 truncate w-full">
      {{ device.area }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Device {
  id: string | number;
  name: string;
  area: string;
  status: 'connected' | 'voltage_read_failed' | 'disconnected';
}

const props = defineProps<{
  device: Device;
}>();

const statusColorClasses = computed(() => {
  switch (props.device.status) {
    case 'connected':
      // Light mode: Deeper green (600), Dark mode: Dark green (700)
      return 'bg-green-600 dark:bg-green-700 text-white dark:text-green-50';
    case 'voltage_read_failed':
      // Light mode: Deeper yellow (500), Dark mode: Dark yellow (600)
      // Using text-yellow-950 for better contrast on bg-yellow-500 in light mode.
      return 'bg-yellow-500 dark:bg-yellow-600 text-yellow-950 dark:text-yellow-50';
    case 'disconnected':
      // Light mode: Deeper red (600), Dark mode: Dark red (700)
      return 'bg-red-600 dark:bg-red-700 text-white dark:text-red-50';
    default:
      // Fallback: Deeper gray (400) for light, Dark gray (800) for dark
      return 'bg-gray-400 dark:bg-gray-800 text-gray-900 dark:text-gray-100';
  }
});
</script>

<style scoped>
.device-card {
  overflow: hidden;
}

.truncate {
  min-width: 0;
}
</style>