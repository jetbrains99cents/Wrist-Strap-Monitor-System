<template>
  <div class="flex flex-1 min-h-0 overflow-hidden">
    <!-- Desktop Sidebar -->
    <aside
        class="hidden md:flex md:flex-col bg-gray-100 dark:bg-dark-surface border-r border-gray-200 dark:border-dark-border p-4 w-60 lg:w-64 overflow-y-auto shrink-0"
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

    <!-- Main Content Area -->
    <section class="flex-1 flex flex-col overflow-hidden p-4 sm:p-6 md:p-8">
      <div class="md:hidden mb-4 shrink-0">
        <UButton
            icon="i-heroicons-bars-3-20-solid"
            color="gray"
            variant="ghost"
            aria-label="Open navigation menu"
            @click="isMobileMenuOpen = true"
        />
      </div>

      <!-- Filter Bar -->
      <UCard class="filter-bar shrink-0 mb-6" :ui="{ body: { padding: 'p-4' } }">
        <div class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 items-end">
            <div>
              <label :for="startDateInputId" class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">{{
                startDateLabel
                }}</label>
              <UInput :id="startDateInputId" type="datetime-local" v-model="filters.startDate" size="md"/>
            </div>
            <div>
              <label :for="endDateInputId"
                     class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">{{ endDateLabel }}</label>
              <UInput :id="endDateInputId" type="datetime-local" v-model="filters.endDate" size="md"/>
            </div>
            <UButtonGroup size="md" orientation="horizontal" class="self-end">
              <UButton :label="todayLabel" @click="setDateRangePreset('today')"
                       :variant="selectedDateRangePreset === 'today' ? 'solid' : 'outline'"/>
              <UButton :label="yesterdayLabel" @click="setDateRangePreset('yesterday')"
                       :variant="selectedDateRangePreset === 'yesterday' ? 'solid' : 'outline'"/>
              <UButton :label="last7DaysLabel" @click="setDateRangePreset('7days')"
                       :variant="selectedDateRangePreset === '7days' ? 'solid' : 'outline'"/>
              <UButton :label="last30DaysLabel" @click="setDateRangePreset('30days')"
                       :variant="selectedDateRangePreset === '30days' ? 'solid' : 'outline'"/>
              <UButton :label="allTimeLabel" @click="setDateRangePreset('all')"
                       :variant="selectedDateRangePreset === 'all' ? 'solid' : 'outline'"/>
            </UButtonGroup>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 items-end">
            <USelectMenu
                v-model="filters.eventType"
                :options="eventTypeOptions"
                value-attribute="value"
                option-attribute="label"
                :placeholder="allEventTypesLabel"
                size="md"
                clearable
                searchable
            />
            <USelectMenu
                v-model="filters.status"
                :options="statusOptions"
                value-attribute="value"
                option-attribute="label"
                :placeholder="allStatusesLabel"
                size="md"
                clearable
                searchable
            />
            <UInput
                v-model="filters.searchTerm"
                :placeholder="freeTextSearchPlaceholder"
                icon="i-heroicons-magnifying-glass-20-solid"
                size="md"
                clearable
                @trailing-icon-click="filters.searchTerm = ''"
            />
          </div>
        </div>
      </UCard>

      <!-- Data Table Area -->
      <div ref="dataTableContainerRef" class="data-table-area flex-grow min-h-0 flex flex-col">
        <UTable
            :columns="tableColumns"
            :rows="paginatedLogs"
            :loading="isLoading"
            :empty-state="{ icon: 'i-heroicons-circle-stack-20-solid', label: noHistoryDataLabel }"
            sort-asc-icon="i-heroicons-bars-arrow-up-20-solid"
            sort-desc-icon="i-heroicons-bars-arrow-down-20-solid"
            v-model:sort="sort"
            class="flex-grow custom-scrollbar overflow-y-auto"
            :ui="{
                thead: 'sticky top-0 z-10 bg-gray-100 dark:bg-gray-800',
                tbody: 'bg-white dark:bg-dark-surface'
             }"
        >
          <template #timestamp-data="{ row }">
            <span>{{ formatTimestampForDisplay(row.timestamp) }}</span>
          </template>
          <template #raw_data-header="{ column }">
            <div class="flex items-center justify-center">
              <span class="text-sm font-normal text-gray-600 dark:text-gray-300">{{ column.label }}</span>
            </div>
          </template>
          <template #raw_data-data="{ row }">
            <div class="flex justify-center items-center">
              <UButton icon="i-heroicons-document-text-20-solid" size="xs" variant="ghost"
                       @click="openPayloadModal(row)" :aria-label="viewPayloadLabel"/>
            </div>
          </template>
          <template #status-data="{ row }">
            <UBadge v-if="row.status" :color="getStatusColor(row.status as LogStatus)" variant="subtle" size="xs">
              {{ getLocalizedStatus(row.status as LogStatus) }}
            </UBadge>
            <span v-else>-</span>
          </template>
        </UTable>
      </div>

      <!-- Pagination Controls & Actions -->
      <div class="pagination-actions-bar flex justify-between items-center mt-4 shrink-0">
        <div class="flex items-center gap-2">
          <UPagination
              v-if="totalPages > 1"
              v-model="currentPage"
              :page-count="itemsPerPage"
              :total="totalItems"
              :max="5"
          />
          <div v-if="totalPages > 1" class="flex items-center gap-1 text-sm">
            <UInput
                v-model.number="pageInput"
                type="number"
                size="xs"
                class="w-16 text-center"
                :min="1"
                :max="totalPages"
                @keyup.enter="goToPage"
                @blur="goToPageOnBlur"
            />
            <span>/ {{ totalPages }}</span>
          </div>
          <div v-else class="h-8"></div>
        </div>
        <div class="flex gap-3">
          <UButton :label="refreshDataLabel" icon="i-heroicons-arrow-path-20-solid" variant="outline"
                   @click="fetchHistoricalData" :loading="isLoading"/>
          <UButton :label="exportToExcelLabel" icon="i-heroicons-document-arrow-down-20-solid" @click="exportToExcel"
                   :disabled="filteredLogs.length === 0"/>
        </div>
      </div>
    </section>

    <!-- Mobile Sidebar -->
    <USlideover v-model="isMobileMenuOpen" side="left" :ui="{ width: 'max-w-xs w-full sm:w-72' }">
      <UCard class="flex flex-col flex-1 h-full"
             :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800', body: { padding: '', base: 'flex-1 overflow-y-auto' } }">
        <template #header>
          <div class="flex items-center justify-between p-4">
            <h3 class="text-lg font-semibold text-gray-800 dark:text-dark-text-primary">{{ mobileMenuTitle }}</h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" @click="isMobileMenuOpen = false"/>
          </div>
        </template>
        <div class="p-4">
          <UVerticalNavigation
              :links="localizedNavigationItems"
              :ui="{ base: 'group relative flex items-start gap-x-3', padding: 'px-3 py-3', label: 'text-base whitespace-pre-line break-words text-left', icon: { base: 'flex-shrink-0 w-5 h-5 mt-0.5' }}"
              @click="isMobileMenuOpen = false"
          />
        </div>
      </UCard>
    </USlideover>

    <!-- Payload Modal -->
    <UModal v-model="isPayloadModalOpen">
      <UCard :ui="{ divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-base font-semibold leading-6 text-gray-900 dark:text-white">
              {{ payloadModalTitleLabel }}
            </h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" class="-my-1"
                     @click="isPayloadModalOpen = false"/>
          </div>
        </template>
        <div class="p-4 max-h-[60vh] overflow-y-auto custom-scrollbar">
          <pre class="text-sm bg-gray-100 dark:bg-gray-800 p-3 rounded-md whitespace-pre-wrap break-all">{{
              selectedLogPayload
            }}</pre>
        </div>
      </UCard>
    </UModal>

  </div>
</template>

<script setup lang="ts">
import {ref, computed, watch, onMounted, onBeforeUnmount, nextTick} from 'vue';
import {useLanguage} from '~/composables/useLanguage';
import {useLogger} from '~/composables/useLogger';

type Sort = { column: string; direction: 'asc' | 'desc'; };

const logger = useLogger();
const {currentLanguage} = useLanguage();
const isMobileMenuOpen = ref(false);

// --- Types ---
type LogStatus =
    | "Connected"
    | "Disconnected"
    | "Voltage reading failed"
    | "Info"
    | "Warning"
    | "Error"
    | "Critical"
    | "Configured"
    | "Reset";

type EventCategory = "Connection" | "Sensor Reading" | "Alert" | "User action" | "System";

interface HistoricalLog {
  id: string;
  timestamp: string;
  deviceId: string;
  deviceName: string;
  deviceMacAddress: string;
  area?: string;
  eventType: EventCategory;
  status?: LogStatus;
  messageSummary: string;
  fullPayload: {
    created_at: string;
    device_name: string;
    mac_address: string;
    wifi_ssid?: string;
    firmware_version?: string;
    event: {
      type: EventCategory;
      status?: LogStatus;
      value: string | Record<string, any>;
    };
  };
}

interface FilterOption {
  label: string;
  value: string | undefined;
}

// --- Sidebar Navigation ---
const rawNavigationItems = ref([
  {id: 'home', label_en: 'Home', label_vi: 'Trang chủ', icon: 'i-heroicons-home-solid', to: '/'},
  {
    id: 'device-list',
    label_en: 'Device List',
    label_vi: 'Danh sách thiết bị',
    icon: 'i-heroicons-queue-list-solid',
    to: '/device-list'
  },
  {
    id: 'device-management',
    label_en: 'Device Management',
    label_vi: 'Quản lý thiết bị',
    icon: 'i-heroicons-cog-8-tooth-solid',
    to: '/device-management'
  },
  {
    id: 'production-plan',
    label_en: 'Production Plan\n& Working Time',
    label_vi: 'Kế hoạch & Thời gian\nsản xuất',
    icon: 'i-heroicons-calendar-days-solid',
    to: '/production-plan'
  },
  {
    id: 'data-visualization',
    label_en: 'Data Visualization',
    label_vi: 'Trực quan hóa dữ liệu',
    icon: 'i-heroicons-chart-pie-solid',
    to: '/data-visualization'
  },
  {
    id: 'data-analysis',
    label_en: 'Data Analysis',
    label_vi: 'Phân tích dữ liệu',
    icon: 'i-heroicons-presentation-chart-line-solid',
    to: '/data-analysis'
  },
]);
const localizedNavigationItems = computed(() => rawNavigationItems.value.map(item => ({
  id: item.id,
  label: currentLanguage.value === 'vi' ? item.label_vi : item.label_en,
  icon: item.icon,
  to: item.to,
})));

// --- Translations ---
const pageTitle = computed(() => currentLanguage.value === 'vi' ? 'Phân tích dữ liệu' : 'Data analysis');
const startDateLabel = computed(() => currentLanguage.value === 'vi' ? 'Ngày & giờ bắt đầu' : 'Start date & time');
const endDateLabel = computed(() => currentLanguage.value === 'vi' ? 'Ngày & giờ kết thúc' : 'End date & time');
const todayLabel = computed(() => currentLanguage.value === 'vi' ? 'Hôm nay' : 'Today');
const yesterdayLabel = computed(() => currentLanguage.value === 'vi' ? 'Hôm qua' : 'Yesterday');
const last7DaysLabel = computed(() => currentLanguage.value === 'vi' ? '7 ngày qua' : 'Last 7 days');
const last30DaysLabel = computed(() => currentLanguage.value === 'vi' ? '30 ngày qua' : 'Last 30 days');
const allTimeLabel = computed(() => currentLanguage.value === 'vi' ? 'Tất cả thời gian' : 'All time');
const allEventTypesLabel = computed(() => currentLanguage.value === 'vi' ? 'Tất cả loại sự kiện' : 'All event types');
const allStatusesLabel = computed(() => currentLanguage.value === 'vi' ? 'Tất cả trạng thái' : 'All statuses');
const freeTextSearchPlaceholder = computed(() => currentLanguage.value === 'vi' ? 'Tìm kiếm...' : 'Search all...');
const exportToExcelLabel = computed(() => currentLanguage.value === 'vi' ? 'Xuất ra excel' : 'Export to excel');
const refreshDataLabel = computed(() => currentLanguage.value === 'vi' ? 'Làm mới dữ liệu' : 'Refresh data');
const timestampLabel = computed(() => currentLanguage.value === 'vi' ? 'Thời gian' : 'Timestamp');
const deviceNameLabel = computed(() => currentLanguage.value === 'vi' ? 'Tên thiết bị' : 'Device name');
const deviceMacAddressLabel = computed(() => currentLanguage.value === 'vi' ? 'Địa chỉ MAC thiết bị' : 'Device MAC address');
const areaLabel = computed(() => currentLanguage.value === 'vi' ? 'Khu vực' : 'Area');
const eventTypeLabel = computed(() => currentLanguage.value === 'vi' ? 'Loại sự kiện' : 'Event type');
const messageTableColumnLabel = computed(() => currentLanguage.value === 'vi' ? 'Dữ liệu gốc' : 'Raw data');
const messageExcelHeaderLabel = computed(() => currentLanguage.value === 'vi' ? 'Nội dung đầy đủ (JSON)' : 'Full message (JSON)');
const statusTableColumnLabel = computed(() => currentLanguage.value === 'vi' ? 'Trạng thái' : 'Status');
const viewPayloadLabel = computed(() => currentLanguage.value === 'vi' ? 'Xem chi tiết' : 'View details');
const noHistoryDataLabel = computed(() => currentLanguage.value === 'vi' ? 'Không có dữ liệu lịch sử nào phù hợp.' : 'No historical data matches your query.');
const mobileMenuTitle = computed(() => currentLanguage.value === 'vi' ? 'Menu' : 'Menu');
const payloadModalTitleLabel = computed(() => currentLanguage.value === 'vi' ? 'Nội dung chi tiết' : 'Message payload');

const connectedLabel = computed(() => currentLanguage.value === 'vi' ? 'Đã kết nối' : 'Connected');
const disconnectedLabel = computed(() => currentLanguage.value === 'vi' ? 'Mất kết nối' : 'Disconnected');
const voltageReadingFailedLabel = computed(() => currentLanguage.value === 'vi' ? 'Lỗi đọc điện áp' : 'Voltage reading failed');
const infoLabel = computed(() => currentLanguage.value === 'vi' ? 'Thông tin' : 'Info');
const warningLabel = computed(() => currentLanguage.value === 'vi' ? 'Cảnh báo' : 'Warning');
const errorLabel = computed(() => currentLanguage.value === 'vi' ? 'Lỗi' : 'Error');
const criticalLabel = computed(() => currentLanguage.value === 'vi' ? 'Nghiêm trọng' : 'Critical');
const configuredLabel = computed(() => currentLanguage.value === 'vi' ? 'Đã cấu hình' : 'Configured');
const resetLabel = computed(() => currentLanguage.value === 'vi' ? 'Đã đặt lại' : 'Reset');

useHead({title: pageTitle});
watch(pageTitle, (newTitle) => {
  useHead({title: `${newTitle} - Wrist Strap Dashboard | IoT Hub`});
});

// --- Filters State ---
const filters = ref({
  startDate: '',
  endDate: '',
  eventType: undefined as EventCategory | undefined,
  status: undefined as LogStatus | undefined,
  searchTerm: '',
});
const selectedDateRangePreset = ref<'today' | 'yesterday' | '7days' | '30days' | 'all' | null>(null);

const eventTypeOptions = computed<FilterOption[]>(() => [
  {label: allEventTypesLabel.value, value: undefined},
  {label: currentLanguage.value === 'vi' ? 'Kết nối' : 'Connection', value: 'Connection'},
  {label: currentLanguage.value === 'vi' ? 'Đọc cảm biến' : 'Sensor Reading', value: 'Sensor Reading'},
  {label: currentLanguage.value === 'vi' ? 'Cảnh báo' : 'Alert', value: 'Alert'},
  {label: currentLanguage.value === 'vi' ? 'Hành động người dùng' : 'User action', value: 'User action'},
  {label: currentLanguage.value === 'vi' ? 'Hệ thống' : 'System', value: 'System'},
]);

const statusOptions = computed<FilterOption[]>(() => [
  {label: allStatusesLabel.value, value: undefined},
  {label: connectedLabel.value, value: 'Connected'},
  {label: disconnectedLabel.value, value: 'Disconnected'},
  {label: voltageReadingFailedLabel.value, value: 'Voltage reading failed'},
  {label: infoLabel.value, value: 'Info'},
  {label: warningLabel.value, value: 'Warning'},
  {label: errorLabel.value, value: 'Error'},
  {label: criticalLabel.value, value: 'Critical'},
  {label: configuredLabel.value, value: 'Configured'},
  {label: resetLabel.value, value: 'Reset'},
]);

let debounceTimer: ReturnType<typeof setTimeout>;
const DEBOUNCE_DELAY = 500;

watch(filters, () => {
  clearTimeout(debounceTimer);
  currentPage.value = 1;
  debounceTimer = setTimeout(() => {
    fetchHistoricalData();
  }, DEBOUNCE_DELAY);
}, {deep: true});

const setDateRangePreset = (preset: 'today' | 'yesterday' | '7days' | '30days' | 'all') => {
  selectedDateRangePreset.value = preset;
  const now = new Date();
  let start = new Date();
  let end = new Date(now);

  start.setHours(0, 0, 0, 0);
  end.setHours(23, 59, 59, 999);

  if (preset === 'today') {
  } else if (preset === 'yesterday') {
    start.setDate(now.getDate() - 1);
    end.setDate(now.getDate() - 1);
  } else if (preset === '7days') {
    start.setDate(now.getDate() - 6);
  } else if (preset === '30days') {
    start.setDate(now.getDate() - 29);
  } else if (preset === 'all') {
    start.setFullYear(now.getFullYear() - 1);
  }

  filters.value.startDate = `${start.getFullYear()}-${String(start.getMonth() + 1).padStart(2, '0')}-${String(start.getDate()).padStart(2, '0')}T${String(start.getHours()).padStart(2, '0')}:${String(start.getMinutes()).padStart(2, '0')}`;
  filters.value.endDate = `${end.getFullYear()}-${String(end.getMonth() + 1).padStart(2, '0')}-${String(end.getDate()).padStart(2, '0')}T${String(end.getHours()).padStart(2, '0')}:${String(end.getMinutes()).padStart(2, '0')}`;
};

const isLoading = ref(false);
const allLogs = ref<HistoricalLog[]>([]);
const currentPage = ref(1);
const itemsPerPage = ref(15);
const sort = ref<Sort>({column: 'timestamp', direction: 'desc'});
const pageInput = ref(currentPage.value);
const dataTableContainerRef = ref<HTMLElement | null>(null);
const tableHeaderActualHeight = ref(42);
const tableRowActualHeight = ref(45);

const calculateDynamicItemsPerPageForTable = () => {
  if (!dataTableContainerRef.value || !dataTableContainerRef.value.offsetParent) {
    return;
  }
  const containerHeight = dataTableContainerRef.value.offsetHeight;
  const headerEl = dataTableContainerRef.value.querySelector('thead');
  if (headerEl) tableHeaderActualHeight.value = headerEl.offsetHeight;

  const firstRowEl = dataTableContainerRef.value.querySelector('tbody tr');
  if (firstRowEl) tableRowActualHeight.value = (firstRowEl as HTMLElement).offsetHeight;

  const headerH = tableHeaderActualHeight.value > 10 ? tableHeaderActualHeight.value : 42;
  const rowH = tableRowActualHeight.value > 10 ? tableRowActualHeight.value : 45;
  let newIPP = 10;

  if (containerHeight > headerH && rowH > 0) {
    const availableHeightForRows = containerHeight - headerH;
    const numRowsThatFit = Math.floor(availableHeightForRows / rowH);
    newIPP = numRowsThatFit > 0 ? numRowsThatFit : (filteredLogs.value.length > 0 ? 1 : 10);
  } else if (filteredLogs.value.length > 0) {
    newIPP = 1;
  }
  if (itemsPerPage.value !== newIPP) {
    itemsPerPage.value = newIPP;
  }
};

let tableResizeObserver: ResizeObserver | null = null;
onMounted(() => {
  setDateRangePreset('7days');
  nextTick(() => {
    if (dataTableContainerRef.value) {
      calculateDynamicItemsPerPageForTable();
      tableResizeObserver = new ResizeObserver(calculateDynamicItemsPerPageForTable);
      tableResizeObserver.observe(dataTableContainerRef.value);
    }
  });
});

onBeforeUnmount(() => {
  if (tableResizeObserver && dataTableContainerRef.value) {
    tableResizeObserver.unobserve(dataTableContainerRef.value);
  }
  if (tableResizeObserver) {
    tableResizeObserver.disconnect();
    tableResizeObserver = null;
  }
});

const tableColumns = computed(() => [
  {key: 'timestamp', label: timestampLabel.value, sortable: true},
  {key: 'deviceName', label: deviceNameLabel.value, sortable: true},
  {key: 'deviceMacAddress', label: deviceMacAddressLabel.value, sortable: true},
  {key: 'area', label: areaLabel.value, sortable: true},
  {key: 'eventType', label: eventTypeLabel.value, sortable: true},
  {key: 'status', label: statusTableColumnLabel.value, sortable: true},
  {key: 'raw_data', label: messageTableColumnLabel.value, sortable: false, class: 'text-center'}
]);

const formatTimestampForDisplay = (isoString: string): string => {
  if (!isoString) return '';
  try {
    const date = new Date(isoString);
    const options: Intl.DateTimeFormatOptions = { timeZone: 'Asia/Ho_Chi_Minh', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
    const parts = new Intl.DateTimeFormat('en-GB', options).formatToParts(date);
    const getPart = (type: Intl.DateTimeFormatPartTypes) => (parts.find(p => p.type === type)?.value || '');
    const day = getPart('day');
    const month = getPart('month');
    const year = getPart('year');
    const hour = getPart('hour');
    const minute = getPart('minute');
    const second = getPart('second');
    return `${day}/${month}/${year}-${hour}:${minute}:${second}`;
  } catch (e) {
    logger.error("Error formatting date:", isoString, e);
    return isoString;
  }
};

const filteredLogs = computed(() => {
  let logs = [...allLogs.value];
  if (filters.value.searchTerm) {
    const term = filters.value.searchTerm.toLowerCase();
    logs = logs.filter(log => formatTimestampForDisplay(log.fullPayload.created_at).toLowerCase().includes(term) || log.fullPayload.device_name.toLowerCase().includes(term) || log.fullPayload.mac_address.toLowerCase().includes(term) || (log.area && log.area.toLowerCase().includes(term)) || log.fullPayload.event.type.toLowerCase().includes(term) || (log.fullPayload.event.status && log.fullPayload.event.status.toLowerCase().includes(term)) );
  }
  if (filters.value.eventType) {
    logs = logs.filter(log => log.fullPayload.event.type === filters.value.eventType);
  }
  if (filters.value.status) {
    logs = logs.filter(log => log.fullPayload.event.status === filters.value.status);
  }
  if (filters.value.startDate && selectedDateRangePreset.value !== 'all') {
    logs = logs.filter(log => new Date(log.fullPayload.created_at) >= new Date(filters.value.startDate!));
  }
  if (filters.value.endDate && selectedDateRangePreset.value !== 'all') {
    logs = logs.filter(log => new Date(log.fullPayload.created_at) <= new Date(filters.value.endDate!));
  }
  if (sort.value.column) {
    const {column, direction} = sort.value;
    logs.sort((a, b) => {
      let valA: any, valB: any;
      if (column === 'timestamp') { valA = new Date(a.fullPayload.created_at).getTime(); valB = new Date(b.fullPayload.created_at).getTime(); }
      else if (column === 'deviceName') { valA = a.fullPayload.device_name; valB = b.fullPayload.device_name; }
      else if (column === 'deviceMacAddress') { valA = a.fullPayload.mac_address; valB = b.fullPayload.mac_address; }
      else if (column === 'area') { valA = a.area || ''; valB = b.area || ''; }
      else if (column === 'eventType') { valA = a.fullPayload.event.type; valB = b.fullPayload.event.type; }
      else if (column === 'status') { valA = a.fullPayload.event.status || ''; valB = b.fullPayload.event.status || ''; }
      else { valA = (a as any)[column]; valB = (b as any)[column]; }
      if (valA < valB) return direction === 'asc' ? -1 : 1;
      if (valA > valB) return direction === 'asc' ? 1 : -1;
      return 0;
    });
  }
  return logs;
});

const totalItems = computed(() => filteredLogs.value.length);
const totalPages = computed(() => Math.ceil(totalItems.value / itemsPerPage.value));
const paginatedLogs = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return filteredLogs.value.slice(start, end);
});

watch(currentPage, (newPage) => { pageInput.value = newPage; });
const goToPage = () => { let page = Number(pageInput.value); if (isNaN(page) || page < 1) page = 1; else if (page > totalPages.value) page = totalPages.value; currentPage.value = page; pageInput.value = page; };
const goToPageOnBlur = () => { goToPage(); };

const fetchHistoricalData = async () => {
  isLoading.value = true;
  logger.log("Fetching data with filters:", JSON.parse(JSON.stringify(filters.value)));
  await new Promise(resolve => setTimeout(resolve, 1000));
  const mockData: HistoricalLog[] = [];
  const eventTypeValues: EventCategory[] = ["Connection", "Sensor Reading", "Alert", "User action", "System"];
  const statusValues: LogStatus[] = ["Connected", "Disconnected", "Voltage reading failed", "Info", "Warning", "Error", "Critical", "Configured", "Reset"];
  const areas: string[] = ["POL", "FLW", "CG A", "CG B", "Testing Alpha", "Warehouse Main"];
  const numEntries = 200; const nowMs = Date.now();
  for (let i = 0; i < numEntries; i++) {
    const randomDayOffset = Math.floor(Math.random() * 30); const timestamp = new Date(nowMs); timestamp.setDate(timestamp.getDate() - randomDayOffset);
    const eventType = eventTypeValues[Math.floor(Math.random() * eventTypeValues.length)]; let eventStatus: LogStatus | undefined = undefined;
    if (eventType === 'Connection') { eventStatus = Math.random() > 0.5 ? "Connected" : "Disconnected"; } else if (eventType === 'Sensor Reading') { eventStatus = Math.random() > 0.05 ? "Info" : "Voltage reading failed"; }
    const deviceIndex = 1 + (i % 10); const deviceName = `Device ${deviceIndex}`;
    mockData.push({ id: `log-${i}`, timestamp: timestamp.toISOString(), deviceId: `ESP32-${100 + deviceIndex}`, deviceName: deviceName, deviceMacAddress: `00:1A:2B:3C:DD:${10 + deviceIndex}`, area: areas[Math.floor(Math.random() * areas.length)], eventType: eventType, status: eventStatus, messageSummary: "Summary", fullPayload: { created_at: timestamp.toISOString(), device_name: deviceName, mac_address: `00:1A:2B:3C:DD:${10 + deviceIndex}`, event: { type: eventType, status: eventStatus, value: "Details" } } });
  }
  allLogs.value = mockData;
  currentPage.value = 1; pageInput.value = 1; isLoading.value = false;
  nextTick(() => { calculateDynamicItemsPerPageForTable(); });
};

const isPayloadModalOpen = ref(false);
const selectedLogPayload = ref<string>('');
const openPayloadModal = (log: HistoricalLog) => {
  selectedLogPayload.value = JSON.stringify(log.fullPayload, null, 2);
  isPayloadModalOpen.value = true;
};
const exportToExcel = async () => {
  const XLSX = await import('xlsx');
  const dataToExport = filteredLogs.value.map(log => ({ [timestampLabel.value]: formatTimestampForDisplay(log.fullPayload.created_at), [deviceNameLabel.value]: log.fullPayload.device_name, [deviceMacAddressLabel.value]: log.fullPayload.mac_address, [areaLabel.value]: log.area || '', [eventTypeLabel.value]: log.fullPayload.event.type, [statusTableColumnLabel.value]: log.fullPayload.event.status ? getLocalizedStatus(log.fullPayload.event.status) : '', [messageExcelHeaderLabel.value]: JSON.stringify(log.fullPayload) }));
  if (dataToExport.length === 0) { logger.warn("No data to export."); return; }
  const worksheet = XLSX.utils.json_to_sheet(dataToExport);
  const colWidths = Object.keys(dataToExport[0]).map(key => ({wch: Math.max(key.length, 20)})); worksheet['!cols'] = colWidths;
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, "Historical Data");
  XLSX.writeFile(workbook, "historical_data.xlsx");
};

type UBadgeColor = 'gray' | 'red' | 'orange' | 'amber' | 'yellow' | 'lime' | 'green' | 'emerald' | 'teal' | 'cyan' | 'sky' | 'blue' | 'indigo' | 'violet' | 'purple' | 'fuchsia' | 'pink' | 'rose' | 'primary';
const getLocalizedStatus = (status: LogStatus): string => { if (currentLanguage.value === 'vi') { switch (status) { case "Connected": return "Đã kết nối"; case "Disconnected": return "Mất kết nối"; case "Voltage reading failed": return "Lỗi đọc điện áp"; case "Info": return "Thông tin"; case "Warning": return "Cảnh báo"; case "Error": return "Lỗi"; case "Critical": return "Nghiêm trọng"; case "Configured": return "Đã cấu hình"; case "Reset": return "Đã đặt lại"; default: return status; } } return status; };
const getStatusColor = (status?: LogStatus): UBadgeColor => { if (!status) return 'gray'; switch (status) { case 'Connected': return 'green'; case 'Disconnected': return 'red'; case 'Info': return 'blue'; case 'Warning': return 'yellow'; case 'Error': return 'orange'; case 'Critical': return 'red'; case 'Voltage reading failed': return 'red'; case 'Configured': return 'yellow'; case 'Reset': return 'yellow'; default: return 'gray'; } };

const startDateInputId = 'start-date-input';
const endDateInputId = 'end-date-input';
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 8px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
html.dark .custom-scrollbar::-webkit-scrollbar-thumb { background: #4a5568; }
.custom-scrollbar { scrollbar-width: thin; scrollbar-color: #cbd5e1 transparent; }
html.dark .custom-scrollbar { scrollbar-color: #4a5568 transparent; }
</style>