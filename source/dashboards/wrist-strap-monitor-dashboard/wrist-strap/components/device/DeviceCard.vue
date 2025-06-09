<template>
  <UTooltip
      :popper="{ placement: 'top', strategy: 'fixed' }"
      :ui="{
        base: 'h-auto w-auto p-0 text-xs font-normal text-left rounded-md shadow-lg',
        background: 'bg-white dark:bg-gray-900',
        ring: 'ring-1 ring-gray-200 dark:ring-gray-800'
      }"
  >
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

    <template #text>
      <div
          class="p-2 space-y-1.5"
          :style="{ maxWidth: '350px', height: 'auto' }"
      >
        <div>
          <span class="font-bold">{{ macAddressLabel }}:</span>
          <span class="font-mono ml-1">{{ device.macAddress || 'N/A' }}</span>
        </div>
        <div>
          <span class="font-bold">{{ firmwareVersionLabel }}:</span>
          <span class="ml-1">{{ device.firmwareVersion || 'N/A' }}</span>
        </div>
        <div>
          <span class="font-bold">{{ lastEventLabel }}:</span>
          <div v-if="device.last_event" class="pl-2 mt-1 border-l-2 border-gray-200 dark:border-gray-700 text-xs">
            <div v-for="(value, key) in device.last_event" :key="key" class="flex items-start">
              <span class="font-semibold capitalize w-20 shrink-0 text-gray-500 dark:text-gray-400">{{ formatEventKey(key) }}:</span>
              <span class="font-mono break-all">{{ formatEventValue(key, value) }}</span>
            </div>
          </div>
          <span v-else class="ml-1">N/A</span>
        </div>
        <hr class="border-gray-300 dark:border-gray-600 my-1">
        <div>
          <span class="font-bold">{{ installationDateLabel }}:</span>
          <span class="ml-1">{{ formatTimestamp(device.installationDate) }}</span>
        </div>
        <div>
          <span class="font-bold">{{ createdDateLabel }}:</span>
          <span class="ml-1">{{ formatTimestamp(device.createdAt) }}</span>
        </div>
      </div>
    </template>
  </UTooltip>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useLanguage } from '~/composables/useLanguage';

// --- Props and Interface ---
interface Device {
  id: string;
  name: string;
  area: string;
  status: string;
  macAddress: string;
  firmwareVersion: string | null;
  createdAt: number;
  installationDate: number;
  last_event: object | null;
}

const props = defineProps<{
  device: Device;
}>();

const { currentLanguage } = useLanguage();

// --- Localization for Tooltip ---
const macAddressLabel = computed(() => currentLanguage.value === 'vi' ? 'Địa chỉ MAC' : 'MAC Address');
const firmwareVersionLabel = computed(() => currentLanguage.value === 'vi' ? 'Firmware' : 'Firmware');
const createdDateLabel = computed(() => currentLanguage.value === 'vi' ? 'Ngày tạo' : 'Created Date');
const installationDateLabel = computed(() => currentLanguage.value === 'vi' ? 'Ngày lắp đặt' : 'Installed Date');
const lastEventLabel = computed(() => currentLanguage.value === 'vi' ? 'Sự kiện cuối' : 'Last Event');

// --- Helper Functions ---
const formatTimestamp = (timestamp: number): string => {
  if (!timestamp) return 'N/A';
  return new Date(timestamp).toLocaleDateString(currentLanguage.value === 'vi' ? 'vi-VN' : 'en-US', {
    year: 'numeric', month: '2-digit', day: '2-digit',
  });
};

const formatEventKey = (key: string): string => {
  return (key.replace(/_/g, ' ') as string).replace(/^\w/, c => c.toUpperCase());
};

const formatEventValue = (key: string, value: any): string => {
  if (key === 'timestamp' && typeof value === 'number') {
    return new Date(value).toLocaleString(currentLanguage.value === 'vi' ? 'vi-VN' : 'en-US', {
      year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
  }
  if (typeof value === 'object' && value !== null) {
    return JSON.stringify(value);
  }
  return String(value);
};


// --- Computed Properties for Styling ---
const statusColorClasses = computed(() => {
  switch (props.device.status) {
    case 'Connected':
      return 'bg-green-600 dark:bg-green-700 text-white dark:text-green-50';
    case 'Voltage reading failed':
      return 'bg-yellow-500 dark:bg-yellow-600 text-yellow-950 dark:text-yellow-50';
    case 'Disconnected':
      return 'bg-red-600 dark:bg-red-700 text-white dark:text-red-50';
    default: // Catches 'Unknown' and any other statuses
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