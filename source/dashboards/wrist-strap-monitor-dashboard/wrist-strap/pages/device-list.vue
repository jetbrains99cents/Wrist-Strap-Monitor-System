<template>
  <div class="flex flex-1 min-h-0 overflow-hidden">
    <aside
        class="hidden md:flex md:flex-col
             bg-gray-100 dark:bg-dark-surface
             border-r border-gray-200 dark:border-dark-border
             p-4
             w-60 lg:w-64
             overflow-y-auto shrink-0"
        aria-label="Desktop Dashboard Navigation"
    >
      <UVerticalNavigation
          :links="localizedNavigationItems"
          :ui="{
          base: 'group relative flex items-start gap-x-3',
          padding: 'px-3 py-2.5',
          label: 'text-base whitespace-pre-line break-words text-left',
          icon: { base: 'flex-shrink-0 w-5 h-5 mt-0.5' }
        }"
      />
    </aside>

    <section class="flex-1 flex flex-col overflow-hidden p-3 sm:p-4 md:p-6">
      <div class="md:hidden mb-4 shrink-0">
        <UButton
            icon="i-heroicons-bars-3-20-solid"
            color="gray"
            variant="ghost"
            aria-label="Open navigation menu"
            @click="isMobileMenuOpen = true"
        />
      </div>

      <div class="filter-bar mb-6 p-4 bg-gray-50 dark:bg-dark-surface rounded-lg shadow shrink-0">
        <div class="flex flex-col sm:flex-row flex-wrap items-center gap-4">
          <UInput
              v-model="filterName"
              :placeholder="filterByNamePlaceholder"
              class="flex-grow sm:flex-grow-0 sm:w-auto min-w-[150px]"
              icon="i-heroicons-magnifying-glass-20-solid"
              :trailing-icon="filterName ? 'i-heroicons-x-mark-20-solid' : undefined"
              @trailing-icon-click="clearFilterName"
              :ui="{ trailingIcon: { pointerEvents: filterName ? 'auto' : 'none' } }"
          />
          <USelectMenu
              v-model="selectedStatusValue"
              :options="localizedStatusOptions"
              value-attribute="value"
              option-attribute="label"
              :placeholder="filterByStatusPlaceholder"
              class="flex-grow sm:flex-grow-0 sm:w-auto min-w-[170px]"
              clearable
          />
          <USelectMenu
              v-model="selectedAreaValue"
              :options="localizedAreaOptions"
              value-attribute="value"
              option-attribute="label"
              :placeholder="filterByAreaPlaceholder"
              class="flex-grow sm:flex-grow-0 sm:w-auto min-w-[200px]"
              clearable
          />
          <UButton :label="applyFiltersLabel" icon="i-heroicons-funnel"/>
        </div>
      </div>

      <div ref="deviceGridAreaRef" class="device-grid-area flex-grow overflow-y-auto mb-6 custom-scrollbar">
        <div v-if="paginatedDevices.length > 0"
             class="grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-4">
          <DeviceCard
              v-for="device in paginatedDevices"
              :key="device.id"
              :device="device"
              class="device-card-item"
          />
        </div>
        <div v-else
             class="flex flex-col items-center justify-center h-full text-center py-8 text-gray-500 dark:text-dark-text-secondary">
          <UIcon name="i-heroicons-exclamation-circle-20-solid" class="w-12 h-12 mb-2"/>
          <p>{{ noDevicesMessage }}</p>
        </div>
      </div>

      <div v-if="totalPages > 1" class="pagination-controls flex justify-center mt-auto pt-4 shrink-0">
        <UPagination
            v-model="currentPage"
            :page-count="itemsPerPage"
            :total="filteredDevices.length"
        />
      </div>
    </section>

    <USlideover v-model="isMobileMenuOpen" side="left" :ui="{ width: 'max-w-xs w-full sm:w-72' }">
      <UCard class="flex flex-col flex-1 h-full"
             :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800', body: { padding: '', base: 'flex-1 overflow-y-auto' } }">
        <template #header>
          <div class="flex items-center justify-between p-4">
            <h3 class="text-lg font-semibold text-gray-800 dark:text-dark-text-primary">Wrist Strap Menu</h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" @click="isMobileMenuOpen = false"/>
          </div>
        </template>
        <div class="p-4">
          <UVerticalNavigation :links="localizedNavigationItems"
                               :ui="{ base: 'group relative flex items-start gap-x-3', padding: 'px-3 py-3', label: 'text-base whitespace-pre-line break-words text-left', icon: { base: 'flex-shrink-0 w-5 h-5 mt-0.5' }}"
                               @click="isMobileMenuOpen = false"/>
        </div>
      </UCard>
    </USlideover>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { useLanguage } from '~/composables/useLanguage';
// import DeviceCard from '~/components/device/DeviceCard.vue'; // Explicit import if not auto-imported

const { currentLanguage } = useLanguage();
const isMobileMenuOpen = ref(false);

// --- Sidebar Navigation Items ---
const rawNavigationItems = ref([
  { id: 'home', label_en: 'Home', label_vi: 'Trang chủ', icon: 'i-heroicons-home-solid', to: '/' },
  { id: 'device-list', label_en: 'Device List', label_vi: 'Danh sách thiết bị', icon: 'i-heroicons-queue-list-solid', to: '/device-list' },
  { id: 'device-management', label_en: 'Device Management', label_vi: 'Quản lý thiết bị', icon: 'i-heroicons-cog-8-tooth-solid', to: '/device-management' },
  { id: 'production-plan', label_en: 'Production Plan\n& Working Time', label_vi: 'Kế hoạch & Thời gian\nsản xuất', icon: 'i-heroicons-calendar-days-solid', to: '/production-plan' },
  { id: 'data-visualization', label_en: 'Data Visualization', label_vi: 'Trực quan hóa dữ liệu', icon: 'i-heroicons-chart-pie-solid', to: '/data-visualization' },
  { id: 'data-analysis', label_en: 'Data Analysis', label_vi: 'Phân tích dữ liệu', icon: 'i-heroicons-presentation-chart-line-solid', to: '/data-analysis' },
]);
const localizedNavigationItems = computed(() => rawNavigationItems.value.map(item => ({
  id: item.id,
  label: currentLanguage.value === 'vi' ? item.label_vi : item.label_en,
  icon: item.icon,
  to: item.to,
})));

// --- Page Title and UI Text Translations ---
const pageTitle = computed(() => currentLanguage.value === 'vi' ? 'Danh sách Thiết bị' : 'Device List');
const filterByNamePlaceholder = computed(() => currentLanguage.value === 'vi' ? 'Lọc theo tên...' : 'Filter by name...');
const filterByStatusPlaceholder = computed(() => currentLanguage.value === 'vi' ? 'Tất cả trạng thái' : 'All Statuses');
const filterByAreaPlaceholder = computed(() => currentLanguage.value === 'vi' ? 'Tất cả khu vực' : 'All Areas');
const applyFiltersLabel = computed(() => currentLanguage.value === 'vi' ? 'Lọc' : 'Filter');
const noDevicesMessage = computed(() => currentLanguage.value === 'vi' ? 'Không tìm thấy thiết bị nào.' : 'No devices match your filters.');

useHead({ title: pageTitle.value });
watch(pageTitle, (newTitle) => { useHead({ title: `${newTitle} - Wrist Strap Dashboard | IoT Hub` }); });

// --- Device List Data and Logic ---
interface Device {
  id: string | number;
  name: string;
  area: string;
  status: 'connected' | 'voltage_read_failed' | 'disconnected';
}
const areasData: string[] = ["CG Appearance Inspection", "For Line Work", "OQC Lighting", "D Inspection", "POL", "FLW", "Assembly Line A", "Testing Bay", "Packaging", "Warehouse", "Logistics Hub", "Receiving Dock"];
const statusesList: Device['status'][] = ['connected', 'voltage_read_failed', 'disconnected'];
const mockDevices = ref<Device[]>([]);

for (let i = 1; i <= 100; i++) { // 100 devices
  const randomArea = areasData[Math.floor(Math.random() * areasData.length)];
  mockDevices.value.push({
    id: `device-${i}`,
    name: `Device ${i}`, // MODIFIED: Simplified device name
    area: randomArea,
    status: statusesList[Math.floor(Math.random() * statusesList.length)],
  });
}

// --- Filter State ---
const filterName = ref('');
const selectedStatusValue = ref<Device['status'] | undefined>(undefined);
const selectedAreaValue = ref<string | undefined>(undefined);
const clearFilterName = () => { filterName.value = ''; };

// --- Dynamic Filter Options ---
const localizedStatusOptions = computed(() => [ { label: filterByStatusPlaceholder.value, value: undefined as Device['status'] | undefined }, { label: currentLanguage.value === 'vi' ? 'Đã kết nối' : 'Connected', value: 'connected' as Device['status'] }, { label: currentLanguage.value === 'vi' ? 'Lỗi đọc điện áp' : 'Voltage Read Failed', value: 'voltage_read_failed' as Device['status'] }, { label: currentLanguage.value === 'vi' ? 'Mất kết nối' : 'Disconnected', value: 'disconnected' as Device['status'] } ]);
const localizedAreaOptions = computed(() => [ { label: filterByAreaPlaceholder.value, value: undefined as string | undefined }, ...areasData.map(area => ({ label: area, value: area })) ]);

// --- Computed Filtered Devices ---
const filteredDevices = computed(() => mockDevices.value.filter(device => {
  const nameMatch = filterName.value ? device.name.toLowerCase().includes(filterName.value.toLowerCase()) : true;
  const statusMatch = selectedStatusValue.value !== undefined ? device.status === selectedStatusValue.value : true;
  const areaMatch = selectedAreaValue.value !== undefined ? device.area === selectedAreaValue.value : true;
  return nameMatch && statusMatch && areaMatch;
}));

// --- DYNAMIC PAGINATION LOGIC ---
const deviceGridAreaRef = ref<HTMLElement | null>(null);
const itemsPerPage = ref(12); // Initial default, will be updated by calculateDynamicItemsPerPage
const currentPage = ref(1);

const CARD_ESTIMATED_HEIGHT = ref(100); // Adjust based on your DeviceCard's typical rendered height + grid gap
const CARD_ESTIMATED_MIN_WIDTH = ref(200); // Corresponds to minmax(200px,...)
const GRID_GAP = ref(16); // Corresponds to gap-4 (1rem)

const calculateDynamicItemsPerPage = () => {
  if (!deviceGridAreaRef.value || filteredDevices.value.length === 0) {
    // itemsPerPage.value = 12; // Retain previous or a sensible minimum if no items/grid
    return;
  }

  const gridAreaHeight = deviceGridAreaRef.value.offsetHeight;
  const gridAreaWidth = deviceGridAreaRef.value.offsetWidth;

  let actualCardHeight = CARD_ESTIMATED_HEIGHT.value;
  let actualCardWidth = CARD_ESTIMATED_MIN_WIDTH.value;

  const firstCardEl = deviceGridAreaRef.value.querySelector('.device-card-item');
  if (firstCardEl) {
    const cardRect = firstCardEl.getBoundingClientRect();
    if (cardRect.height > GRID_GAP.value) actualCardHeight = cardRect.height + GRID_GAP.value; // card height + vertical gap
    if (cardRect.width > 0) actualCardWidth = cardRect.width;
  }

  if (gridAreaHeight <= 0 || actualCardHeight <= GRID_GAP.value || gridAreaWidth <= 0 || actualCardWidth <=0) {
    itemsPerPage.value = Math.max(1, filteredDevices.value.length > 0 ? 1 : 12);
    return;
  }

  const numRowsThatFit = Math.max(1, Math.floor(gridAreaHeight / actualCardHeight));
  const numColsThatFit = Math.max(1, Math.floor((gridAreaWidth + GRID_GAP.value) / (actualCardWidth + GRID_GAP.value)));

  const newItemsPerPage = numRowsThatFit * numColsThatFit;

  if (newItemsPerPage > 0 && itemsPerPage.value !== newItemsPerPage) {
    itemsPerPage.value = newItemsPerPage;
  } else if (newItemsPerPage === 0 && filteredDevices.value.length > 0) {
    itemsPerPage.value = 1;
  }
  // If no items, itemsPerPage can remain its last calculated value or a default.
  // It will be used by totalPages which would become 1 if filteredDevices is empty.
};

let resizeObserver: ResizeObserver | null = null;

onMounted(() => {
  nextTick(() => {
    if (deviceGridAreaRef.value) {
      calculateDynamicItemsPerPage();
      resizeObserver = new ResizeObserver(calculateDynamicItemsPerPage);
      resizeObserver.observe(deviceGridAreaRef.value);
    }
  });
});

onBeforeUnmount(() => {
  if (resizeObserver && deviceGridAreaRef.value) {
    resizeObserver.unobserve(deviceGridAreaRef.value);
  }
  if (resizeObserver) {
    resizeObserver.disconnect();
    resizeObserver = null;
  }
});

watch(
    () => filteredDevices.value.length,
    () => {
      nextTick(() => {
        calculateDynamicItemsPerPage();
        if (totalPages.value > 0 && currentPage.value > totalPages.value) {
          currentPage.value = totalPages.value;
        } else if (currentPage.value <= 0 && totalPages.value > 0) { // Ensure current page is at least 1
          currentPage.value = 1;
        } else if (filteredDevices.value.length === 0) { // If no devices, reset to page 1
          currentPage.value = 1;
        }
      });
    }
);

const totalPages = computed(() => {
  if (!filteredDevices.value.length || itemsPerPage.value <= 0) return 1;
  return Math.ceil(filteredDevices.value.length / itemsPerPage.value);
});

const paginatedDevices = computed(() => {
  if (itemsPerPage.value <= 0) return filteredDevices.value.slice(0,1);
  const start = (currentPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return filteredDevices.value.slice(start, end);
});

watch([filterName, selectedStatusValue, selectedAreaValue], () => {
  currentPage.value = 1;
});
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

html.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background: #4a5568;
}

.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}

html.dark .custom-scrollbar {
  scrollbar-color: #4a5568 transparent;
}

/* Ensure the device grid area has some presence for the "No devices" message */
.device-grid-area:empty::before,
.device-grid-area > div:empty::before { /* Target the inner grid div too if it's empty */
  content: '';
  display: block;
  min-height: 200px; /* Adjust as needed */
}
</style>