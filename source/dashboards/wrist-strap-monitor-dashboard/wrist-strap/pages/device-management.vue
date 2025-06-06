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
                     @click="openAddModal"/>
            <UButton :label="removeDeviceLabel" icon="i-heroicons-trash-20-solid" size="md" color="red"
                     variant="outline" @click="handleRemoveDevice" :disabled="selectedDevices.length === 0"/>
            <UButton :label="exportExcelLabel" icon="i-heroicons-document-arrow-down-20-solid" size="md" color="green"
                     variant="solid" @click="handleExportExcel" :disabled="filteredDevices.length === 0"/>
          </div>
          <div class="flex items-center gap-3 w-full md:w-auto">
            <UInput
                v-model="searchTerm"
                :placeholder="generalSearchPlaceholder"
                icon="i-heroicons-magnifying-glass-20-solid"
                class="w-full sm:w-auto sm:min-w-[250px]"
                clearable
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
              :style="{ minWidth: '180px' }"
              :placeholder="filterByAreaPlaceholder"
              value-attribute="value"
              option-attribute="label"
              clearable
          />
          <USelectMenu
              v-model="selectedFilterStatus"
              :options="statusColumnFilterOptions"
              size="sm"
              :style="{ minWidth: '180px' }"
              :placeholder="filterByStatusPlaceholder"
              value-attribute="value"
              option-attribute="label"
              clearable
          />
          <USelectMenu
              v-model="selectedFilterDate"
              :options="dateColumnFilterOptions"
              size="sm"
              :style="{ minWidth: '180px' }"
              :placeholder="filterByDatePlaceholder"
              value-attribute="value"
              option-attribute="label"
              clearable
          />
        </div>
      </div>

      <div ref="deviceTableContainerRef" class="device-table-container flex-grow overflow-hidden mb-6 flex flex-col">
        <UTable
            v-model="selectedDevices"
            :sort="sort"
            :columns="localizedColumns"
            :rows="paginatedDevices"
            :loading="pending"
            row-key="id"
            :empty-state="{ icon: 'i-heroicons-circle-stack-20-solid', label: noDevicesMessage }"
            :ui="{
              base: 'min-w-full table-fixed',
              thead: 'sticky top-0 z-10 bg-gray-50 dark:bg-dark-surface',
              th: { base: 'text-left rtl:text-right group align-top whitespace-nowrap', padding: 'px-3 py-3', font: 'font-semibold text-sm', color: 'text-gray-600 dark:text-gray-300' },
              td: { base: 'align-middle whitespace-nowrap overflow-hidden text-ellipsis', padding: 'px-3 py-3', color: 'text-gray-700 dark:text-gray-200' },
              tbody: 'divide-y divide-gray-200 dark:divide-gray-700',
              tr: { base: 'cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800/50', selected: 'bg-primary-50 dark:bg-primary-900' }
            }"
            @select="handleRowClick"
            class="h-full"
        >
          <template #status-data="{ row }">
            <UBadge :color="getStatusColor(row.status)" variant="subtle" size="md">{{
                getLocalizedStatus(row.status)
              }}
            </UBadge>
          </template>
        </UTable>
        <div v-if="!pending && paginatedDevices.length === 0 && filteredDevices.length > 0 && itemsPerPage > 0"
             class="flex flex-col items-center justify-center flex-grow text-center py-8 text-gray-500 dark:text-dark-text-secondary">
          <UIcon name="i-heroicons-exclamation-circle-20-solid" class="w-12 h-12 mb-2"/>
          <p>{{ noDevicesOnPageMessage }}</p>
        </div>
      </div>

      <div v-if="totalPages > 1" class="pagination-controls flex justify-center items-center mt-auto pt-4 shrink-0 gap-2">
        <UPagination v-model="currentPage" :page-count="itemsPerPage" :total="filteredDevices.length" :max="5"/>
        <div class="flex items-center gap-1 text-sm">
          <UInput
              v-model.number="pageInput"
              type="number"
              size="xs"
              class="w-16 text-center"
              :min="1"
              :max="totalPages"
              @keyup.enter="goToPage"
              @blur="goToPage"
          />
          <span>/ {{ totalPages }}</span>
        </div>
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

    <UModal v-model="isModalOpen">
      <UForm v-if="formState" :state="formState" @submit="isEditing ? handleUpdateDevice() : handleSaveNewDevice()">
        <UCard :ui="{ divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
          <template #header>
            <h3 class="text-lg font-semibold">{{ isEditing ? editDeviceModalTitle : addDeviceModalTitle }}</h3>
          </template>

          <div class="p-4 space-y-4">
            <UFormGroup :label="deviceNameLabel" name="name" required>
              <UInput v-model="formState.name" />
            </UFormGroup>
            <UFormGroup :label="areaLabel" name="installationArea" required>
              <USelectMenu v-model="formState.installationArea" :options="allAreas" />
            </UFormGroup>
            <UFormGroup :label="macAddressLabel" name="deviceMacAddress" required>
              <UInput v-model="formState.deviceMacAddress" />
            </UFormGroup>
          </div>

          <template #footer>
            <div class="flex justify-end gap-3">
              <UButton :label="cancelLabel" color="gray" @click="isModalOpen = false"/>
              <UButton :label="saveLabel" type="submit" color="primary" />
            </div>
          </template>
        </UCard>
      </UForm>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import {ref, computed, watch, onMounted, onBeforeUnmount, nextTick} from 'vue';
import {useLanguage} from '~/composables/useLanguage';

type AppBadgeColor = 'green' | 'red' | 'amber' | 'gray' | 'primary' | 'blue' | 'orange' | 'yellow' | 'purple' | 'pink' | 'cyan' | 'teal' | 'indigo' | 'white' | 'black';

const {currentLanguage} = useLanguage();
const toast = useToast();
const isMobileMenuOpen = ref(false);

const rawNavigationItems = ref([
  {id: 'home', label_en: 'Home', label_vi: 'Trang chủ', icon: 'i-heroicons-home-solid', to: '/'},
  {id: 'device-list', label_en: 'Device List', label_vi: 'Danh sách thiết bị', icon: 'i-heroicons-queue-list-solid', to: '/device-list'},
  {id: 'device-management', label_en: 'Device Management', label_vi: 'Quản lý thiết bị', icon: 'i-heroicons-cog-8-tooth-solid', to: '/device-management'},
  {id: 'production-plan', label_en: 'Production Plan\n& Working Time', label_vi: 'Kế hoạch & Thời gian\nsản xuất', icon: 'i-heroicons-calendar-days-solid', to: '/production-plan'},
  {id: 'data-visualization', label_en: 'Data Visualization', label_vi: 'Trực quan hóa dữ liệu', icon: 'i-heroicons-chart-pie-solid', to: '/data-visualization'},
  {id: 'data-analysis', label_en: 'Data Analysis', label_vi: 'Phân tích dữ liệu', icon: 'i-heroicons-presentation-chart-line-solid', to: '/data-analysis'},
]);
const localizedNavigationItems = computed(() => rawNavigationItems.value.map(item => ({
  id: item.id,
  label: currentLanguage.value === 'vi' ? item.label_vi : item.label_en,
  icon: item.icon,
  to: item.to
})));

// --- Labels & Translations ---
const pageTitle = computed(() => currentLanguage.value === 'vi' ? 'Quản lý Thiết bị' : 'Device Management');
const addDeviceLabel = computed(() => currentLanguage.value === 'vi' ? 'Thêm mới' : 'Add Device');
const removeDeviceLabel = computed(() => currentLanguage.value === 'vi' ? 'Xóa' : 'Remove');
const exportExcelLabel = computed(() => currentLanguage.value === 'vi' ? 'Xuất Excel' : 'Export Excel');
const generalSearchPlaceholder = computed(() => currentLanguage.value === 'vi' ? 'Tìm tên, MAC...' : 'Search name, MAC...');
const noDevicesMessage = computed(() => currentLanguage.value === 'vi' ? 'Không có thiết bị nào phù hợp.' : 'No devices match your criteria.');
const noDevicesOnPageMessage = computed(() => currentLanguage.value === 'vi' ? 'Không có thiết bị để hiển thị trên trang này.' : 'No devices to display on this page.');
const filterByAreaPlaceholder = computed(() => currentLanguage.value === 'vi' ? 'Lọc theo khu vực' : 'Filter by Area');
const filterByStatusPlaceholder = computed(() => currentLanguage.value === 'vi' ? 'Lọc theo trạng thái' : 'Filter by Status');
const filterByDatePlaceholder = computed(() => currentLanguage.value === 'vi' ? 'Lọc theo ngày' : 'Filter by Date');

const addDeviceModalTitle = computed(() => currentLanguage.value === 'vi' ? 'Thêm thiết bị mới' : 'Add New Device');
const editDeviceModalTitle = computed(() => currentLanguage.value === 'vi' ? 'Chỉnh sửa thông tin thiết bị' : 'Edit Device Information');
const deviceNameLabel = computed(() => currentLanguage.value === 'vi' ? 'Tên thiết bị' : 'Device Name');
const areaLabel = computed(() => currentLanguage.value === 'vi' ? 'Khu vực lắp đặt' : 'Installation Area');
const macAddressLabel = computed(() => currentLanguage.value === 'vi' ? 'Địa chỉ MAC' : 'MAC Address');
const cancelLabel = computed(() => currentLanguage.value === 'vi' ? 'Hủy' : 'Cancel');
const saveLabel = computed(() => currentLanguage.value === 'vi' ? 'Lưu' : 'Save');

// --- Data & State ---
type DeviceStatus = 'Online' | 'Offline' | 'Voltage reading failed';
interface Device {
  id: number;
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
    name: `Device ${i}`,
    installationArea: allAreas[Math.floor(Math.random() * allAreas.length)],
    installationDate: `${String(Math.floor(Math.random() * 28) + 1).padStart(2, '0')}/${String(Math.floor(Math.random() * 12) + 1).padStart(2, '0')}/202${Math.floor(Math.random() * 3) + 3}`,
    status: randomStatus,
    deviceMacAddress: `12:34:56:78:9A:${String(10 + i).padStart(2, '0')}`
  });
}

const rawColumns = [
  {key: 'name', label_en: 'Device Name', label_vi: 'Tên thiết bị', sortable: true},
  {key: 'installationArea', label_en: 'Installation Area', label_vi: 'Khu vực lắp đặt', sortable: true},
  {key: 'installationDate', label_en: 'Installation Date', label_vi: 'Ngày lắp đặt', sortable: true},
  {key: 'status', label_en: 'Status', label_vi: 'Trạng thái', sortable: true},
  {key: 'deviceMacAddress', label_en: 'Device Mac Address', label_vi: 'Địa chỉ MAC', sortable: false},
];
const localizedColumns = computed(() => rawColumns.map(col => ({
  key: col.key,
  label: (currentLanguage.value === 'vi' ? col.label_vi : col.label_en),
  sortable: col.sortable,
})));

// --- Filtering & Sorting ---
const searchTerm = ref('');
const selectedFilterArea = ref<string | undefined>(undefined);
const selectedFilterStatus = ref<DeviceStatus | undefined>(undefined);
const selectedFilterDate = ref<string | undefined>(undefined);
const sort = ref<{ column: string; direction: 'asc' | 'desc' }>({column: 'name', direction: 'asc'});

const filteredDevices = computed(() => {
  let results = [...mockDevices.value];
  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    results = results.filter(device => (device.name.toLowerCase().includes(term)) || (device.deviceMacAddress.toLowerCase().includes(term)));
  }
  if (selectedFilterArea.value) results = results.filter(device => device.installationArea === selectedFilterArea.value);
  if (selectedFilterStatus.value) results = results.filter(device => device.status === selectedFilterStatus.value);
  if (selectedFilterDate.value) results = results.filter(device => device.installationDate === selectedFilterDate.value);

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
      const comparison = valA.localeCompare(valB, undefined, { sensitivity: 'base' });
      return sort.value.direction === 'asc' ? comparison : -comparison;
    }
    return 0;
  });
  return results;
});

// --- Dynamic Pagination ---
const deviceTableContainerRef = ref<HTMLElement | null>(null);
const itemsPerPage = ref(10);
const currentPage = ref(1);
const pageInput = ref(currentPage.value);
const tableHeaderActualHeight = ref(42);
const tableRowActualHeight = ref(45);

const calculateDynamicItemsPerPageForTable = () => {
  if (!deviceTableContainerRef.value || !deviceTableContainerRef.value.offsetParent) return;

  const containerHeight = deviceTableContainerRef.value.offsetHeight;
  const headerH = tableHeaderActualHeight.value || 42;
  const rowH = tableRowActualHeight.value || 45;

  if (containerHeight > headerH && rowH > 0) {
    const availableHeightForRows = containerHeight - headerH;
    const numRowsThatFit = Math.floor(availableHeightForRows / rowH);
    itemsPerPage.value = numRowsThatFit > 0 ? numRowsThatFit : 1;
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
  if (tableResizeObserver && deviceTableContainerRef.value) tableResizeObserver.unobserve(deviceTableContainerRef.value);
  if (tableResizeObserver) tableResizeObserver.disconnect();
});

watch(() => filteredDevices.value.length, () => {
  nextTick(() => {
    calculateDynamicItemsPerPageForTable();
    if (currentPage.value > totalPages.value) currentPage.value = totalPages.value || 1;
  });
});

const totalPages = computed(() => {
  if (filteredDevices.value.length === 0) return 1;
  return Math.ceil(filteredDevices.value.length / itemsPerPage.value);
});

const paginatedDevices = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return filteredDevices.value.slice(start, end);
});

watch(currentPage, (newPage) => { pageInput.value = newPage; });
const goToPage = () => {
  let page = Number(pageInput.value);
  if (isNaN(page) || page < 1) page = 1;
  if (page > totalPages.value) page = totalPages.value;
  currentPage.value = page;
  pageInput.value = page;
};

watch([searchTerm, selectedFilterArea, selectedFilterStatus, selectedFilterDate], () => { currentPage.value = 1; });

// --- Filter Options ---
const getLocalizedStatus = (status: DeviceStatus): string => {
  if (currentLanguage.value === 'vi') {
    switch (status) {
      case 'Online': return 'Trực tuyến';
      case 'Offline': return 'Ngoại tuyến';
      case 'Voltage reading failed': return 'Lỗi đọc điện áp';
      default: return status;
    }
  }
  return status;
};
const areaColumnFilterOptions = computed(() => [{ label: filterByAreaPlaceholder.value, value: undefined }, ...allAreas.map(a => ({ label: a, value: a }))]);
const statusColumnFilterOptions = computed(() => [{ label: filterByStatusPlaceholder.value, value: undefined }, ...allStatuses.map(s => ({ label: getLocalizedStatus(s), value: s }))]);
const dateColumnFilterOptions = computed(() => {
  const uniqueDates = [...new Set(mockDevices.value.map(d => d.installationDate))].sort((a, b) => {
    const [dayA, monthA, yearA] = a.split('/').map(Number);
    const [dayB, monthB, yearB] = b.split('/').map(Number);
    return new Date(yearA, monthA - 1, dayA).getTime() - new Date(yearB, monthB - 1, dayB).getTime();
  });
  return [{ label: filterByDatePlaceholder.value, value: undefined }, ...uniqueDates.map(d => ({ label: d, value: d }))];
});
const getStatusColor = (status: DeviceStatus): AppBadgeColor => {
  switch (status) {
    case 'Online': return 'green';
    case 'Offline': return 'red';
    case 'Voltage reading failed': return 'amber';
    default: return 'gray';
  }
};

// --- CRUD & Modal Logic ---
const selectedDevices = ref<Device[]>([]);
const isModalOpen = ref(false);
const isEditing = ref(false);
const editingDevice = ref<Device | null>(null);
const newDeviceForm = ref({ name: '', installationArea: '', deviceMacAddress: '', status: 'Offline' as DeviceStatus });

const formState = computed(() => isEditing.value ? editingDevice.value : newDeviceForm.value);

const openAddModal = () => {
  isEditing.value = false;
  newDeviceForm.value = { name: '', installationArea: allAreas[0], deviceMacAddress: '', status: 'Offline' };
  isModalOpen.value = true;
};

const handleRowClick = (row: Device) => {
  isEditing.value = true;
  editingDevice.value = { ...row };
  isModalOpen.value = true;
};

const handleSaveNewDevice = () => {
  const newId = Math.max(0, ...mockDevices.value.map(d => d.id)) + 1;
  const today = new Date();
  const newDevice: Device = {
    ...newDeviceForm.value,
    id: newId,
    installationDate: `${String(today.getDate()).padStart(2, '0')}/${String(today.getMonth() + 1).padStart(2, '0')}/${today.getFullYear()}`,
  };
  mockDevices.value.unshift(newDevice);
  isModalOpen.value = false;
  toast.add({ title: 'Device Added', color: 'green' });
};

const handleUpdateDevice = () => {
  if (!editingDevice.value) return;
  const index = mockDevices.value.findIndex(d => d.id === editingDevice.value!.id);
  if (index !== -1) {
    mockDevices.value[index] = { ...editingDevice.value };
  }
  isModalOpen.value = false;
  editingDevice.value = null;
  toast.add({ title: 'Device Updated', color: 'green' });
};

const handleRemoveDevice = () => {
  if (selectedDevices.value.length === 0) {
    toast.add({ title: 'No device selected', description: 'Please select a device from the table to remove.', color: 'amber' });
    return;
  }
  const deviceToRemove = selectedDevices.value[0];
  mockDevices.value = mockDevices.value.filter(d => d.id !== deviceToRemove.id);
  selectedDevices.value = [];
  toast.add({ title: 'Device Removed', color: 'red' });
};

// --- Excel Export ---
const handleExportExcel = async () => {
  const XLSX = await import('xlsx');
  const dataToExport = filteredDevices.value.map(device => ({
    [localizedColumns.value[0].label]: device.name,
    [localizedColumns.value[1].label]: device.installationArea,
    [localizedColumns.value[2].label]: device.installationDate,
    [localizedColumns.value[3].label]: getLocalizedStatus(device.status),
    [localizedColumns.value[4].label]: device.deviceMacAddress,
  }));

  if (dataToExport.length === 0) {
    toast.add({ title: 'No Data to Export', color: 'amber' });
    return;
  }
  const worksheet = XLSX.utils.json_to_sheet(dataToExport);
  const colWidths = Object.keys(dataToExport[0]).map(key => ({ wch: Math.max(key.length, 20) }));
  worksheet['!cols'] = colWidths;
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, "Device List");
  XLSX.writeFile(workbook, `Device_List_${new Date().toISOString().split('T')[0]}.xlsx`);
};

useHead({title: pageTitle.value});
watch(pageTitle, (newTitle) => { useHead({title: newTitle}); });
</script>