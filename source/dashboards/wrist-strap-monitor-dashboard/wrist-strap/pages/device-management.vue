<template>
  <div class="flex flex-1 min-h-0 overflow-hidden">
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

      <div class="action-bar mb-6 p-4 bg-gray-50 dark:bg-dark-surface rounded-lg shadow shrink-0">
        <div class="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div class="flex flex-wrap items-center gap-3">
            <UButton :label="addDeviceLabel" icon="i-heroicons-plus-circle-20-solid" size="md" color="primary"
                     @click="handleAddDevice"/>
            <UButton :label="removeDeviceLabel" icon="i-heroicons-trash-20-solid" size="md" color="red"
                     variant="outline" @click="handleRemoveDevice"/>
            <UButton :label="editDeviceLabel" icon="i-heroicons-pencil-square-20-solid" size="md" color="amber"
                     variant="outline" @click="handleEditDevice"/>
            <UButton :label="exportExcelLabel" icon="i-heroicons-document-arrow-down-20-solid" size="md" color="green"
                     variant="solid" @click="handleExportExcel"/>
          </div>
          <div class="flex items-center gap-3 w-full md:w-auto">
            <UInput
                v-model="searchTerm"
                :placeholder="generalSearchPlaceholder"
                icon="i-heroicons-magnifying-glass-20-solid"
                class="w-full sm:w-auto sm:min-w-[250px]"
                clearable
                @trailing-icon-click="searchTerm = ''"
                :ui="{ trailingIcon: { pointerEvents: searchTerm ? 'auto' : 'none' } }"
            />
          </div>
        </div>
      </div>

      <div class="filters-section mb-4 p-4 bg-gray-50 dark:bg-dark-surface rounded-lg shadow shrink-0">
        <div class="flex flex-wrap gap-4">
          <USelectMenu
              v-model="selectedFilterArea"
              :options="areaColumnFilterOptions"
              size="sm"
              :style="{ minWidth: areaFilterWidth + 'px' }"
              :placeholder="filterByAreaPlaceholder"
              value-attribute="value"
              option-attribute="label"
              clearable
          />
          <USelectMenu
              v-model="selectedFilterStatus"
              :options="statusColumnFilterOptions"
              size="sm"
              :style="{ minWidth: statusFilterWidth + 'px' }"
              :placeholder="filterByStatusPlaceholder"
              value-attribute="value"
              option-attribute="label"
              clearable
          />
          <USelectMenu
              v-model="selectedFilterDate"
              :options="dateColumnFilterOptions"
              size="sm"
              :style="{ minWidth: dateFilterWidth + 'px' }"
              :placeholder="filterByDatePlaceholder"
              value-attribute="value"
              option-attribute="label"
              clearable
          />
        </div>
      </div>

      <div ref="deviceTableContainerRef" class="device-table-container flex-grow overflow-hidden mb-6 flex flex-col">
        <UTable
            :sort="sort"
            :columns="localizedColumns"
            :rows="paginatedDevices"
            :loading="pending"
            :empty-state="{ icon: 'i-heroicons-circle-stack-20-solid', label: noDevicesMessage }"
            :ui="{
              base: 'min-w-full table-fixed',
              thead: 'sticky top-0 z-10 bg-gray-50 dark:bg-dark-surface', // Make header sticky
              th: { base: 'text-left rtl:text-right group align-top whitespace-nowrap', padding: 'px-3 py-3', font: 'font-semibold text-sm', color: 'text-gray-600 dark:text-gray-300' },
              td: { base: 'align-middle whitespace-nowrap overflow-hidden text-ellipsis', padding: 'px-3 py-3', color: 'text-gray-700 dark:text-gray-200' },
              tbody: 'divide-y divide-gray-200 dark:divide-gray-700'
            }"
            @update:sort="handleSort"
            class="h-full"
        >
          <template v-for="header in localizedColumns" #[`${header.key}-header`]="{ column }"
                    :key="`${header.key}-custom-header`">
            <div class="flex items-center justify-between w-full">
              <span class="text-sm font-semibold">{{ column.label }}</span>
              <UButton
                  v-if="column.sortable"
                  :icon="sort.column === column.key ? (sort.direction === 'asc' ? 'i-heroicons-chevron-up-20-solid' : 'i-heroicons-chevron-down-20-solid') : 'i-heroicons-arrows-up-down-20-solid'"
                  color="gray"
                  variant="link"
                  :padded="false"
                  square
                  size="xs"
                  class="-mr-1.5"
                  @click="sortColumn(column.key)"
              />
            </div>
          </template>

          <template #status-data="{ row }">
            <UBadge :color="getStatusColor(row.status)" variant="subtle" size="md">{{
                getLocalizedStatus(row.status)
              }}
            </UBadge>
          </template>
          <template #actions-data="{ row }">
            <UDropdown :items="getDeviceActions(row)">
              <UButton color="gray" variant="ghost" icon="i-heroicons-ellipsis-horizontal-20-solid"/>
            </UDropdown>
          </template>
        </UTable>
        <div v-if="!pending && paginatedDevices.length === 0 && filteredDevices.length > 0 && itemsPerPage > 0"
             class="flex flex-col items-center justify-center flex-grow text-center py-8 text-gray-500 dark:text-dark-text-secondary">
          <UIcon name="i-heroicons-exclamation-circle-20-solid" class="w-12 h-12 mb-2"/>
          <p>No devices to display on this page.</p>
        </div>
      </div>

      <div v-if="totalPages > 1" class="pagination-controls flex justify-center mt-auto pt-4 shrink-0">
        <UPagination v-model="currentPage" :page-count="itemsPerPage" :total="filteredDevices.length"/>
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
          <UVerticalNavigation
              :links="localizedNavigationItems"
              :ui="{ base: 'group relative flex items-start gap-x-3', padding: 'px-3 py-3', label: 'text-base whitespace-pre-line break-words text-left', icon: { base: 'flex-shrink-0 w-5 h-5 mt-0.5' }}"
              @click="isMobileMenuOpen = false"
          />
        </div>
      </UCard>
    </USlideover>
  </div>
</template>

<script setup lang="ts">
import {ref, computed, watch, onMounted, onBeforeUnmount, nextTick} from 'vue';
import {useLanguage} from '~/composables/useLanguage';

type AppBadgeColor =
    'green'
    | 'red'
    | 'amber'
    | 'gray'
    | 'primary'
    | 'blue'
    | 'orange'
    | 'yellow'
    | 'purple'
    | 'pink'
    | 'cyan'
    | 'teal'
    | 'indigo'
    | 'white'
    | 'black';

const {currentLanguage} = useLanguage();
const isMobileMenuOpen = ref(false);

const rawNavigationItems = ref([{
  id: 'home',
  label_en: 'Home',
  label_vi: 'Trang chủ',
  icon: 'i-heroicons-home-solid',
  to: '/'
}, {
  id: 'device-list',
  label_en: 'Device List',
  label_vi: 'Danh sách thiết bị',
  icon: 'i-heroicons-queue-list-solid',
  to: '/device-list'
}, {
  id: 'device-management',
  label_en: 'Device Management',
  label_vi: 'Quản lý thiết bị',
  icon: 'i-heroicons-cog-8-tooth-solid',
  to: '/device-management'
}, {
  id: 'production-plan',
  label_en: 'Production Plan\n& Working Time',
  label_vi: 'Kế hoạch & Thời gian\nsản xuất',
  icon: 'i-heroicons-calendar-days-solid',
  to: '/production-plan'
}, {
  id: 'data-visualization',
  label_en: 'Data Visualization',
  label_vi: 'Trực quan hóa dữ liệu',
  icon: 'i-heroicons-chart-pie-solid',
  to: '/data-visualization'
}, {
  id: 'data-analysis',
  label_en: 'Data Analysis',
  label_vi: 'Phân tích dữ liệu',
  icon: 'i-heroicons-presentation-chart-line-solid',
  to: '/data-analysis'
},]);
const localizedNavigationItems = computed(() => rawNavigationItems.value.map(item => ({
  id: item.id,
  label: currentLanguage.value === 'vi' ? item.label_vi : item.label_en,
  icon: item.icon,
  to: item.to
})));

const pageTitle = computed(() => currentLanguage.value === 'vi' ? 'Quản lý Thiết bị' : 'Device Management');
const addDeviceLabel = computed(() => currentLanguage.value === 'vi' ? 'Thêm mới' : 'Add Device');
const removeDeviceLabel = computed(() => currentLanguage.value === 'vi' ? 'Xóa' : 'Remove');
const editDeviceLabel = computed(() => currentLanguage.value === 'vi' ? 'Sửa' : 'Edit');
const exportExcelLabel = computed(() => currentLanguage.value === 'vi' ? 'Xuất Excel' : 'Export Excel');
const generalSearchPlaceholder = computed(() => currentLanguage.value === 'vi' ? 'Tìm tên, MAC...' : 'Search name, MAC...');
const noDevicesMessage = computed(() => currentLanguage.value === 'vi' ? 'Không có thiết bị nào phù hợp.' : 'No devices match your criteria.'); // Made more general for UTable empty state
const filterByAreaPlaceholder = computed(() => currentLanguage.value === 'vi' ? 'Tất cả khu vực' : 'All Areas');
const filterByStatusPlaceholder = computed(() => currentLanguage.value === 'vi' ? 'Tất cả trạng thái' : 'All Statuses');
const filterByDatePlaceholder = computed(() => currentLanguage.value === 'vi' ? 'Tất cả ngày' : 'All Dates');

type DeviceStatus = 'Online' | 'Offline' | 'Voltage reading failed';

interface Device {
  id: number;
  index: number;
  name: string;
  installationArea: string;
  installationDate: string;
  status: DeviceStatus;
  deviceMacAddress: string;
}

const mockDevices = ref<Device[]>([]);
const allAreas = ["POL", "FLW", "CG", "OQC Lighting", "D Inspection", "Assembly X", "Testing Y", "Warehouse Z"];
const allStatuses: DeviceStatus[] = ['Online', 'Offline', 'Voltage reading failed'];
const pending = ref(false);

for (let i = 1; i <= 100; i++) {
  const randomStatus = allStatuses[Math.floor(Math.random() * allStatuses.length)];
  mockDevices.value.push({
    id: i,
    index: i,
    name: `Device ${i}`,
    installationArea: allAreas[Math.floor(Math.random() * allAreas.length)],
    installationDate: `${String(Math.floor(Math.random() * 28) + 1).padStart(2, '0')}/${String(Math.floor(Math.random() * 12) + 1).padStart(2, '0')}/202${Math.floor(Math.random() * 3) + 3}`,
    status: randomStatus,
    deviceMacAddress: `12.A.8F.123.${String(i).padStart(3, '0')}`
  });
}

const rawColumns = [{key: 'index', label_en: 'Index', label_vi: 'Số thứ tự', sortable: true}, {
  key: 'name',
  label_en: 'Device Name',
  label_vi: 'Tên thiết bị',
  sortable: true
}, {
  key: 'installationArea',
  label_en: 'Installation Area',
  label_vi: 'Khu vực lắp đặt',
  sortable: true
}, {key: 'installationDate', label_en: 'Installation Date', label_vi: 'Ngày lắp đặt', sortable: true}, {
  key: 'status',
  label_en: 'Status',
  label_vi: 'Trạng thái',
  sortable: true
}, {key: 'deviceMacAddress', label_en: 'Device Mac Address', label_vi: 'Địa chỉ MAC', sortable: false}, {
  key: 'actions',
  label_en: 'Actions',
  label_vi: 'Hành động',
  sortable: false
}];
const formatColumnHeader = (str: string): string => {
  if (!str) return '';
  const firstWord = str.split(' ')[0];
  if (!firstWord) return str;
  const firstWordFormatted = firstWord.charAt(0).toUpperCase() + firstWord.slice(1).toLowerCase();
  return firstWordFormatted + (str.includes(' ') ? ' ' + str.split(' ').slice(1).join(' ').toLowerCase() : '');
};
const localizedColumns = computed(() => rawColumns.map(col => ({
  key: col.key,
  label: formatColumnHeader(currentLanguage.value === 'vi' ? col.label_vi : col.label_en),
  sortable: col.sortable,
})));

const searchTerm = ref('');
const selectedFilterArea = ref<string | undefined>(undefined);
const selectedFilterStatus = ref<DeviceStatus | undefined>(undefined);
const selectedFilterDate = ref<string | undefined>(undefined);
const sort = ref<{ column: string; direction: 'asc' | 'desc' }>({column: 'index', direction: 'asc'});

const areaFilterWidth = computed(() => {
  const longest = Math.max(0, ...areaColumnFilterOptions.value.map(option => option.label.length));
  return longest * 8 + 60;
});
const statusFilterWidth = computed(() => {
  const longest = Math.max(0, ...statusColumnFilterOptions.value.map(option => option.label.length));
  return longest * 8 + 60;
});
const dateFilterWidth = computed(() => {
  const longest = Math.max(0, ...dateColumnFilterOptions.value.map(option => option.label.length));
  return longest * 8 + 60;
});

const areaColumnFilterOptions = computed(() => {
  const options: { label: string; value: string | undefined }[] = [{
    label: filterByAreaPlaceholder.value,
    value: undefined
  }];
  if (Array.isArray(mockDevices.value)) {
    const unique = [...new Set(mockDevices.value.map(d => d.installationArea))].sort();
    unique.forEach(area => options.push({label: area, value: area}));
  }
  return options;
});
const statusColumnFilterOptions = computed(() => {
  const options: { label: string; value: DeviceStatus | undefined }[] = [{
    label: filterByStatusPlaceholder.value,
    value: undefined
  }];
  allStatuses.forEach(status => options.push({label: getLocalizedStatus(status), value: status}));
  return options;
});
const dateColumnFilterOptions = computed(() => {
  const options: { label: string; value: string | undefined }[] = [{
    label: filterByDatePlaceholder.value,
    value: undefined
  }];
  if (Array.isArray(mockDevices.value)) {
    const uniqueDates = [...new Set(mockDevices.value.map(d => d.installationDate))];
    uniqueDates.sort((a, b) => {
      const [dayA, monthA, yearA] = a.split('/').map(Number);
      const [dayB, monthB, yearB] = b.split('/').map(Number);
      return new Date(yearA, monthA - 1, dayA).getTime() - new Date(yearB, monthB - 1, dayB).getTime();
    });
    uniqueDates.forEach(date => options.push({label: date, value: date}));
  }
  return options;
});

const filteredDevices = computed(() => {
  let results = [...mockDevices.value];
  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    results = results.filter(device => (device.name && device.name.toLowerCase().includes(term)) || (device.deviceMacAddress && device.deviceMacAddress.toLowerCase().includes(term)));
  }
  if (selectedFilterArea.value !== undefined) results = results.filter(device => device.installationArea === selectedFilterArea.value);
  if (selectedFilterStatus.value !== undefined) results = results.filter(device => device.status === selectedFilterStatus.value);
  if (selectedFilterDate.value !== undefined) results = results.filter(device => device.installationDate === selectedFilterDate.value);
  results.sort((a, b) => {
    let valA = a[sort.value.column as keyof Device];
    let valB = b[sort.value.column as keyof Device];
    if (sort.value.column === 'installationDate') {
      const [dayA, monthA, yearA] = (valA as string).split('/').map(Number);
      const [dayB, monthB, yearB] = (valB as string).split('/').map(Number);
      const dateA = new Date(yearA, monthA - 1, dayA).getTime();
      const dateB = new Date(yearB, monthB - 1, dayB).getTime();
      if (dateA < dateB) return sort.value.direction === 'asc' ? -1 : 1;
      if (dateA > dateB) return sort.value.direction === 'asc' ? 1 : -1;
      return 0;
    }
    if (typeof valA === 'string' && typeof valB === 'string') {
      const comparison = valA.localeCompare(valB);
      return sort.value.direction === 'asc' ? comparison : -comparison;
    }
    if (typeof valA === 'number' && typeof valB === 'number') {
      return sort.value.direction === 'asc' ? valA - valB : valB - valA;
    }
    return 0;
  });
  return results;
});

const sortColumn = (columnKey: string) => {
  if (!rawColumns.find(col => col.key === columnKey)?.sortable) return;
  if (sort.value.column === columnKey) {
    sort.value.direction = sort.value.direction === 'asc' ? 'desc' : 'asc';
  } else {
    sort.value.column = columnKey;
    sort.value.direction = 'asc';
  }
};
const handleSort = (newSort: { column: string; direction: 'asc' | 'desc' }) => {
  sort.value = newSort;
};

// --- DYNAMIC PAGINATION LOGIC for Table ---
const deviceTableContainerRef = ref<HTMLElement | null>(null);
const itemsPerPage = ref(10); // Will be updated dynamically
const currentPage = ref(1);

const tableHeaderActualHeight = ref(42); // Initial estimate, adjust if UTable header is taller/shorter
const tableRowActualHeight = ref(45);    // Initial estimate for UTable row height (padding py-3 = 24px + line height)

const calculateDynamicItemsPerPageForTable = () => {
  if (!deviceTableContainerRef.value || !deviceTableContainerRef.value.offsetParent) {
    return; // Container not rendered or visible
  }

  const containerHeight = deviceTableContainerRef.value.offsetHeight;

  // Use measured heights as primary, fallback to estimates if measurement failed or is zero
  const headerH = tableHeaderActualHeight.value > 10 ? tableHeaderActualHeight.value : 42;
  const rowH = tableRowActualHeight.value > 10 ? tableRowActualHeight.value : 45;

  let newIPP = 10; // Default

  if (containerHeight > headerH && rowH > 0) {
    const availableHeightForRows = containerHeight - headerH;
    const numRowsThatFit = Math.floor(availableHeightForRows / rowH);

    if (numRowsThatFit > 0) {
      newIPP = numRowsThatFit;
    } else if (filteredDevices.value.length > 0) {
      newIPP = 1; // Not enough space for a full row, but show 1 item if data exists
    } else {
      newIPP = 1; // No data, no space for row, default to 1 (totalPages will be 1)
    }
  } else if (filteredDevices.value.length > 0) {
    newIPP = 1; // Container too small or invalid row height, show 1 item if data exists
  }

  if (itemsPerPage.value !== newIPP) {
    itemsPerPage.value = newIPP;
  }
};

let tableResizeObserver: ResizeObserver | null = null;

onMounted(() => {
  nextTick(() => {
    if (deviceTableContainerRef.value) {
      const headerEl = deviceTableContainerRef.value.querySelector('thead');
      if (headerEl) tableHeaderActualHeight.value = headerEl.offsetHeight;

      const firstRowEl = deviceTableContainerRef.value.querySelector('tbody tr');
      if (firstRowEl) tableRowActualHeight.value = (firstRowEl as HTMLElement).offsetHeight;

      calculateDynamicItemsPerPageForTable();

      tableResizeObserver = new ResizeObserver(calculateDynamicItemsPerPageForTable);
      tableResizeObserver.observe(deviceTableContainerRef.value);
    }
  });
});

onBeforeUnmount(() => {
  if (tableResizeObserver && deviceTableContainerRef.value) {
    tableResizeObserver.unobserve(deviceTableContainerRef.value);
  }
  if (tableResizeObserver) {
    tableResizeObserver.disconnect();
    tableResizeObserver = null;
  }
});

watch(
    () => filteredDevices.value.length,
    () => {
      nextTick(() => {
        calculateDynamicItemsPerPageForTable();
        const newTotalPages = totalPages.value;
        if (newTotalPages > 0 && currentPage.value > newTotalPages) {
          currentPage.value = newTotalPages;
        } else if (currentPage.value <= 0 && newTotalPages > 0) {
          currentPage.value = 1;
        } else if (newTotalPages === 0 || (newTotalPages === 1 && filteredDevices.value.length === 0)) { // if filteredDevices is empty
          currentPage.value = 1;
        }
      });
    }
);

const totalPages = computed(() => {
  if (!filteredDevices.value.length) return 1;
  if (itemsPerPage.value <= 0) return 1;
  return Math.ceil(filteredDevices.value.length / itemsPerPage.value);
});
const paginatedDevices = computed(() => {
  // Ensure itemsPerPage is at least 1 for slicing if there are devices
  const currentIPP = (itemsPerPage.value > 0) ? itemsPerPage.value : (filteredDevices.value.length > 0 ? 1 : 10);
  const start = (currentPage.value - 1) * currentIPP;
  const end = start + currentIPP;
  return filteredDevices.value.slice(start, end);
});

watch([searchTerm, selectedFilterArea, selectedFilterStatus, selectedFilterDate], () => {
  currentPage.value = 1;
});

const getStatusColor = (status: DeviceStatus): AppBadgeColor => {
  switch (status) {
    case 'Online':
      return 'green';
    case 'Offline':
      return 'red';
    case 'Voltage reading failed':
      return 'amber';
    default:
      return 'gray';
  }
};
const getLocalizedStatus = (status: DeviceStatus): string => {
  if (currentLanguage.value === 'vi') {
    switch (status) {
      case 'Online':
        return 'Trực tuyến';
      case 'Offline':
        return 'Ngoại tuyến';
      case 'Voltage reading failed':
        return 'Lỗi đọc điện áp';
      default:
        return status;
    }
  }
  return status;
};
const handleAddDevice = () => {
  console.log('Add device clicked');
};
const handleRemoveDevice = () => {
  console.log('Remove device clicked');
};
const handleEditDevice = () => {
  console.log('Edit device clicked');
};
const handleExportExcel = () => {
  console.log('Export Excel clicked');
};
const getDeviceActions = (device: Device) => [[{
  label: currentLanguage.value === 'vi' ? 'Sửa' : 'Edit',
  icon: 'i-heroicons-pencil-square-20-solid',
  click: () => console.log('Edit', device.id)
}, {
  label: currentLanguage.value === 'vi' ? 'Xóa' : 'Delete',
  icon: 'i-heroicons-trash-20-solid',
  click: () => console.log('Delete', device.id)
}]];

useHead({title: pageTitle.value,});
watch(pageTitle, (newTitle) => {
  useHead({title: newTitle});
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

/* Light mode scrollbar thumb */
html.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background: #4a5568;
}

/* Dark mode scrollbar thumb */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}

/* Firefox */
html.dark .custom-scrollbar {
  scrollbar-color: #4a5568 transparent;
}

/* Firefox dark */

/* The device-table-container will use flex-grow. UTable's empty state should handle visual appearance when no data. */
</style>