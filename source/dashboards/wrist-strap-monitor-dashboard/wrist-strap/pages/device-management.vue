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

      <div class="action-bar mb-4 p-4 bg-gray-50 dark:bg-dark-surface rounded-lg shadow shrink-0">
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
          <USelectMenu v-model="selectedFilterArea" :options="areaColumnFilterOptions" size="sm" :style="{ minWidth: '180px' }" :placeholder="filterByAreaPlaceholder" value-attribute="value" option-attribute="label" clearable />
          <USelectMenu v-model="selectedFilterStatus" :options="statusColumnFilterOptions" size="sm" :style="{ minWidth: '180px' }" :placeholder="filterByStatusPlaceholder" value-attribute="value" option-attribute="label" clearable />
          <USelectMenu v-model="selectedFilterDate" :options="dateColumnFilterOptions" size="sm" :style="{ minWidth: '180px' }" :placeholder="filterByDatePlaceholder" value-attribute="value" option-attribute="label" clearable />
        </div>
      </div>

      <div ref="deviceTableContainerRef" class="device-table-container flex-grow flex flex-col overflow-hidden min-h-0">
        <UTable
            ref="tableRef"
            v-model="selectedDevices"
            :sort="sort"
            :columns="localizedColumns"
            :rows="paginatedDevices"
            :loading="pending"
            row-key="id"
            :empty-state="{ icon: 'i-heroicons-circle-stack-20-solid', label: noDevicesMessage }"
            :ui="{
              base: 'min-w-full table-fixed',
              wrapper: '',
              tbody: 'divide-y divide-gray-200 dark:divide-gray-700',
              th: { base: 'text-left rtl:text-right group align-top whitespace-nowrap', padding: 'px-3 py-3', font: 'font-semibold text-sm', color: 'text-gray-600 dark:text-gray-300' },
              td: { base: 'align-middle whitespace-nowrap overflow-hidden text-ellipsis', padding: 'px-3 py-3', color: 'text-gray-700 dark:text-gray-200' },
              tr: { base: 'cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800/50', selected: 'bg-primary-50 dark:bg-primary-900' }
            }"
            @select="handleRowClick"
        >
          <template #installationDate-data="{ row }"><span>{{ formatTimestamp(row.installationDate) }}</span></template>

          <template #status-data="{ row }">
            <UBadge :color="getStatusColor(row.status)" variant="subtle" size="md">{{ getLocalizedStatus(row.status) }}</UBadge>
          </template>

          <template #firmware_version-data="{ row }">
            <span>{{ row.firmware_version || 'N/A' }}</span>
          </template>

          <template #lastEventActions-data="{ row }">
            <div class="flex justify-center items-center">
              <UButton
                  icon="i-heroicons-document-text"
                  size="sm"
                  color="gray"
                  variant="ghost"
                  :aria-label="latestDataLabel"
                  @click.stop="showLastEventModal(row.last_event)"
              />
            </div>
          </template>
        </UTable>
      </div>

      <div v-if="totalPages > 1" class="pagination-controls flex justify-center items-center mt-4 shrink-0 gap-2">
        <UPagination v-model="currentPage" :page-count="itemsPerPage" :total="filteredDevices.length" :max="5"/>
        <div class="flex items-center gap-1 text-sm">
          <UInput v-model.number="pageInput" type="number" size="xs" class="w-16 text-center" :min="1" :max="totalPages" @keyup.enter="goToPage" @blur="goToPage" />
          <span>/ {{ totalPages }}</span>
        </div>
      </div>
    </section>

    <USlideover v-model="isMobileMenuOpen" side="left" :ui="{ width: 'max-w-xs w-full sm:w-72' }">
      <UCard class="flex flex-col flex-1 h-full" :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800', body: { padding: '', base: 'flex-1 overflow-y-auto' } }">
        <template #header>
          <div class="flex items-center justify-between p-4">
            <h3 class="text-lg font-semibold text-gray-800 dark:text-dark-text-primary">Wrist Strap Menu</h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" @click="isMobileMenuOpen = false"/>
          </div>
        </template>
        <div class="p-4">
          <UVerticalNavigation :links="localizedNavigationItems" :ui="{ base: 'group relative flex items-start gap-x-3', padding: 'px-3 py-3', label: 'text-base whitespace-pre-line break-words text-left', icon: { base: 'flex-shrink-0 w-5 h-5 mt-0.5' }}" @click="isMobileMenuOpen = false" />
        </div>
      </UCard>
    </USlideover>

    <UModal v-model="isFormModalOpen">
      <UForm v-if="formState" :state="formState" @submit="isEditing ? handleUpdateDevice() : handleSaveNewDevice()">
        <UCard :ui="{ divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
          <template #header>
            <h3 class="text-lg font-semibold">{{ isEditing ? editDeviceModalTitle : addDeviceModalTitle }}</h3>
          </template>
          <div class="p-4 space-y-4">
            <UFormGroup :label="deviceNameLabel" name="name" required><UInput v-model="formState.name" /></UFormGroup>
            <UFormGroup :label="newDeviceTypeLabel" name="device_type" required>
              <USelectMenu
                  v-model="formState.device_type"
                  :options="deviceTypeOptionsForModal"
                  value-attribute="value"
                  option-attribute="label"
                  :placeholder="selectDeviceTypePlaceholder"
                  :disabled="isEditing"
              />
            </UFormGroup>
            <UFormGroup :label="areaLabel" name="installationArea" required><USelectMenu v-model="formState.installationArea" :options="allAreas" /></UFormGroup>
            <UFormGroup :label="macAddressLabel" name="mac_address"><UInput v-model="formState.mac_address" :disabled="isEditing"/></UFormGroup>
            <UFormGroup :label="firmwareVersionLabel" name="firmware_version"><UInput v-model="formState.firmware_version" /></UFormGroup>
          </div>
          <template #footer>
            <div class="flex justify-end gap-3">
              <UButton :label="cancelLabel" color="gray" @click="isFormModalOpen = false"/>
              <UButton :label="saveLabel" type="submit" color="primary" :loading="isSaving"/>
            </div>
          </template>
        </UCard>
      </UForm>
    </UModal>

    <UModal v-model="isConfirmDeleteModalOpen">
      <UCard :ui="{ divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
        <template #header>
          <h3 class="text-lg font-semibold text-red-600 dark:text-red-400">{{ confirmDeleteTitle }}</h3>
        </template>
        <div class="p-4">
          <p>{{ confirmDeleteMessage }}</p>
        </div>
        <template #footer>
          <div class="flex justify-end gap-3">
            <UButton :label="cancelLabel" color="gray" @click="isConfirmDeleteModalOpen = false" />
            <UButton :label="deleteLabel" color="red" @click="confirmDeleteDevices" :loading="isSaving" />
          </div>
        </template>
      </UCard>
    </UModal>

    <UModal v-model="isLastEventModalOpen">
      <UCard :ui="{ divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-base font-semibold leading-6 text-gray-900 dark:text-white">
              {{ lastEventModalTitle }}
            </h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" class="-my-1" @click="isLastEventModalOpen = false"/>
          </div>
        </template>
        <div class="p-4">
          <pre class="text-xs p-3 bg-gray-900 text-white rounded-md overflow-auto">{{ prettifiedLastEvent }}</pre>
        </div>
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { useLanguage } from '~/composables/useLanguage';
import { useLogger } from '~/composables/useLogger';
import { useActionStatusModal } from '~/composables/useActionStatusModal';
import { useDeviceRealtimeStore } from '~/stores/deviceRealtime';
import type { LogStatus, EventType } from '~/config/constants';
import { useLocalization } from '~/composables/useLocalization';
import { useRuntimeConfig, useNuxtApp, useToast } from '#imports';

type AppBadgeColor = 'green' | 'red' | 'amber' | 'gray' | 'blue' | 'purple' | 'indigo' | 'orange' | 'yellow';

const { currentLanguage } = useLanguage();
const logger = useLogger();
const toast = useToast();
const { $api } = useNuxtApp();
const { show: showActionStatusModal } = useActionStatusModal();
const deviceRealtimeStore = useDeviceRealtimeStore();
const runtimeConfig = useRuntimeConfig();
const { getLocalizedStatus, getFormattedDeviceType } = useLocalization();

// --- General State & Navigation ---
const isMobileMenuOpen = ref(false);
const rawNavigationItems = ref([
  {id: 'home', label_en: 'Home', label_vi: 'Trang chủ', icon: 'i-heroicons-home-solid', to: '/'},
  {id: 'device-list', label_en: 'Device List', label_vi: 'Danh sách thiết bị', icon: 'i-heroicons-queue-list-solid', to: '/device-list'},
  {id: 'device-management', label_en: 'Device Management', label_vi: 'Quản lý thiết bị', icon: 'i-heroicons-cog-8-tooth-solid', to: '/device-management'},
  {id: 'production-plan', label_en: 'Production Plan\n& Working Time', label_vi: 'Kế hoạch & Thời gian\nsản xuất', icon: 'i-heroicons-calendar-days-solid', to: '/production-plan'},
  {id: 'data-visualization', label_en: 'Data Visualization', label_vi: 'Trực quan hóa dữ liệu', icon: 'i-heroicons-chart-pie-solid', to: '/data-visualization'},
  {id: 'data-analysis', label_en: 'Data Analysis', label_vi: 'Phân tích dữ liệu', icon: 'i-heroicons-presentation-chart-line-solid', to: '/data-analysis'},
]);
const localizedNavigationItems = computed(() => rawNavigationItems.value.map(item => ({ id: item.id, label: currentLanguage.value === 'vi' ? item.label_vi : item.label_en, icon: item.icon, to: item.to })));

// --- Localization Computed Properties ---
const pageTitle = computed(() => currentLanguage.value === 'vi' ? 'Quản lý Thiết bị' : 'Device Management');
const addDeviceLabel = computed(() => currentLanguage.value === 'vi' ? 'Thêm mới' : 'Add Device');
const removeDeviceLabel = computed(() => currentLanguage.value === 'vi' ? 'Xóa' : 'Remove');
const exportExcelLabel = computed(() => currentLanguage.value === 'vi' ? 'Xuất Excel' : 'Export Excel');
const generalSearchPlaceholder = computed(() => currentLanguage.value === 'vi' ? 'Tìm tên, MAC...' : 'Search name, MAC...');
const noDevicesMessage = computed(() => currentLanguage.value === 'vi' ? 'Không có thiết bị nào phù hợp.' : 'No devices match your criteria.');
const filterByAreaPlaceholder = computed(() => currentLanguage.value === 'vi' ? 'Lọc theo khu vực' : 'Filter by Area');
const filterByStatusPlaceholder = computed(() => currentLanguage.value === 'vi' ? 'Lọc theo trạng thái' : 'Filter by Status');
const filterByDatePlaceholder = computed(() => currentLanguage.value === 'vi' ? 'Lọc theo ngày' : 'Filter by Date');
const addDeviceModalTitle = computed(() => currentLanguage.value === 'vi' ? 'Thêm thiết bị mới' : 'Add New Device');
const editDeviceModalTitle = computed(() => currentLanguage.value === 'vi' ? 'Chỉnh sửa thông tin thiết bị' : 'Edit Device Information');
const deviceNameLabel = computed(() => currentLanguage.value === 'vi' ? 'Tên thiết bị' : 'Device Name');
const areaLabel = computed(() => currentLanguage.value === 'vi' ? 'Khu vực lắp đặt' : 'Installation Area');
const macAddressLabel = computed(() => currentLanguage.value === 'vi' ? 'Địa chỉ MAC' : 'MAC Address');
const firmwareVersionLabel = computed(() => currentLanguage.value === 'vi' ? 'Phiên bản Firmware' : 'Firmware Version');
const installationDateLabel = computed(() => currentLanguage.value === 'vi' ? 'Ngày lắp đặt' : 'Installation Date');
const statusLabel = computed(() => currentLanguage.value === 'vi' ? 'Trạng thái' : 'Status');
const cancelLabel = computed(() => currentLanguage.value === 'vi' ? 'Hủy' : 'Cancel');
const saveLabel = computed(() => currentLanguage.value === 'vi' ? 'Lưu' : 'Save');
const deleteLabel = computed(() => currentLanguage.value === 'vi' ? 'Xóa' : 'Delete');
const newDeviceTypeLabel = computed(() => currentLanguage.value === 'vi' ? 'Loại thiết bị' : 'Device Type');
const selectDeviceTypePlaceholder = computed(() => currentLanguage.value === 'vi' ? 'Chọn một loại...' : 'Select a type...');
const confirmDeleteTitle = computed(() => currentLanguage.value === 'vi' ? 'Xác nhận Xóa' : 'Confirm Deletion');
const confirmDeleteMessage = computed(() => {
  const count = selectedDevices.value.length;
  return currentLanguage.value === 'vi'
      ? `Bạn có chắc chắn muốn xóa ${count} thiết bị đã chọn không? Hành động này không thể hoàn tác.`
      : `Are you sure you want to delete the ${count} selected device(s)? This action cannot be undone.`;
});
const successTitle = computed(() => currentLanguage.value === 'vi' ? 'Thành công' : 'Success');
const addSuccessMessage = computed(() => currentLanguage.value === 'vi' ? 'Thiết bị đã được thêm thành công.' : 'Device has been added successfully.');
const updateSuccessMessage = computed(() => currentLanguage.value === 'vi' ? 'Thiết bị đã được cập nhật thành công.' : 'Device has been updated successfully.');
const deleteSuccessMessage = computed(() => currentLanguage.value === 'vi' ? 'Các thiết bị đã được xóa thành công.' : 'The selected devices have been deleted successfully.');
const latestDataLabel = computed(() => currentLanguage.value === 'vi' ? 'Dữ liệu gần nhất' : 'Latest Data');
const lastEventModalTitle = computed(() => currentLanguage.value === 'vi' ? 'Dữ liệu Sự kiện Cuối' : 'Last Event Data');

// --- Device Data & Table State ---
interface EventDetails { type: EventType | null; status?: LogStatus | null; timestamp: number; value: any; }
interface Device { id: string; name: string; installationArea: string; installationDate: number; status: LogStatus | 'Unknown' | null; mac_address: string; firmware_version?: string | null; device_type: string; last_event: EventDetails | null; createdAt: number; }
const allDevices = ref<Device[]>([]);
const allAreas = runtimeConfig.public.installationAreas;
const allStatuses = runtimeConfig.public.logStatuses;
const allDeviceTypes = runtimeConfig.public.deviceTypes;
const deviceTypeOptionsForModal = computed(() => allDeviceTypes.map((type: string) => ({ label: getFormattedDeviceType(type), value: type })));
const pending = ref(false);

const localizedColumns = computed(() => [
  {key: 'name', label: deviceNameLabel.value, sortable: true},
  {key: 'mac_address', label: macAddressLabel.value, sortable: false},
  {key: 'installationArea', label: areaLabel.value, sortable: true},
  {key: 'firmware_version', label: firmwareVersionLabel.value, sortable: true},
  {key: 'installationDate', label: installationDateLabel.value, sortable: true},
  {key: 'status', label: statusLabel.value, sortable: true},
  {key: 'lastEventActions', label: latestDataLabel.value, sortable: false, class: 'w-16 text-center'},
]);

const liveDeviceData = computed(() => {
  const realtimeSnapshots = deviceRealtimeStore.latestDeviceSnapshots;
  if (realtimeSnapshots.size === 0) {
    return allDevices.value;
  }
  return allDevices.value.map(device => {
    const snapshot = realtimeSnapshots.get(device.id);
    if (snapshot) {
      return {
        ...device,
        status: (snapshot.last_event?.status || 'Unknown') as LogStatus | 'Unknown',
        last_event: snapshot.last_event
      };
    }
    return device;
  });
});

// --- Filtering, Sorting & Pagination ---
const searchTerm = ref('');
const selectedFilterArea = ref<string | undefined>(undefined);
const selectedFilterStatus = ref<LogStatus | 'Unknown' | undefined>(undefined);
const selectedFilterDate = ref<number | undefined>(undefined);
const sort = ref<{ column: string; direction: 'asc' | 'desc' }>({column: 'name', direction: 'asc'});

const filteredDevices = computed(() => {
  let results = [...liveDeviceData.value];
  if (searchTerm.value) { const term = searchTerm.value.toLowerCase(); results = results.filter(device => (device.name.toLowerCase().includes(term)) || (device.mac_address.toLowerCase().includes(term))); }
  if (selectedFilterArea.value) results = results.filter(device => device.installationArea === selectedFilterArea.value);
  if (selectedFilterStatus.value) results = results.filter(device => device.status === selectedFilterStatus.value);
  if (selectedFilterDate.value) results = results.filter(device => new Date(device.installationDate).toDateString() === new Date(selectedFilterDate.value!).toDateString());
  results.sort((a, b) => { let valA = a[sort.value.column as keyof Device]; let valB = b[sort.value.column as keyof Device]; if (sort.value.column === 'installationDate') { return sort.value.direction === 'asc' ? (valA as number) - (valB as number) : (valB as number) - (valA as number); } if (typeof valA === 'string' && typeof valB === 'string') { return sort.value.direction === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA); } return 0; });
  return results;
});

const deviceTableContainerRef = ref<HTMLElement | null>(null);
const tableRef = ref<any>(null);
const itemsPerPage = ref(15); // Start with a reasonable default
const currentPage = ref(1);
const pageInput = ref(currentPage.value);
let resizeObserver: ResizeObserver | null = null;

const totalPages = computed(() => Math.ceil(filteredDevices.value.length / itemsPerPage.value) || 1);
const paginatedDevices = computed(() => { const start = (currentPage.value - 1) * itemsPerPage.value; const end = start + itemsPerPage.value; return filteredDevices.value.slice(start, end); });
watch(currentPage, (newPage) => { pageInput.value = newPage; });
const goToPage = () => { let page = Number(pageInput.value); if (isNaN(page) || page < 1) page = 1; if (page > totalPages.value) page = totalPages.value; currentPage.value = page; };
watch([searchTerm, selectedFilterArea, selectedFilterStatus, selectedFilterDate, sort], () => { currentPage.value = 1; });

// --- Table Data Formatting ---
const formatTimestamp = (timestamp: number) => new Date(timestamp).toLocaleDateString(currentLanguage.value === 'vi' ? 'vi-VN' : 'en-US');

const areaColumnFilterOptions = computed(() => [{ label: filterByAreaPlaceholder.value, value: undefined }, ...allAreas.map(a => ({ label: a, value: a }))]);
const statusColumnFilterOptions = computed(() => [{ label: filterByStatusPlaceholder.value, value: undefined }, ...allStatuses.map(s => ({ label: getLocalizedStatus(s), value: s }))]);
const dateColumnFilterOptions = computed(() => { const uniqueDates = [...new Set(allDevices.value.map(d => new Date(d.installationDate).toDateString()))]; return [{ label: filterByDatePlaceholder.value, value: undefined }, ...uniqueDates.map(d => ({ label: new Date(d).toLocaleDateString(), value: new Date(d).getTime() }))]; });

const getStatusColor = (status: LogStatus | 'Unknown' | null): AppBadgeColor => {
  if (!status) return 'gray';
  const colorName = runtimeConfig.public.statusColors[status] || 'gray';
  return colorName === 'slate' ? 'gray' : colorName as AppBadgeColor;
};

// --- Modal & Action State ---
const selectedDevices = ref<Device[]>([]);
const isFormModalOpen = ref(false);
const isConfirmDeleteModalOpen = ref(false);
const isEditing = ref(false);
const isSaving = ref(false);
const formState = ref<any>({});
const isLastEventModalOpen = ref(false);
const selectedLastEvent = ref<EventDetails | null>(null);
const prettifiedLastEvent = computed(() => JSON.stringify(selectedLastEvent.value, null, 2));

// --- Modal Logic ---
const openAddModal = () => { isEditing.value = false; formState.value = { name: '', device_type: allDeviceTypes[0], installationArea: allAreas[0], mac_address: '', firmware_version: '' }; isFormModalOpen.value = true; };
const handleRowClick = (row: Device) => { isEditing.value = true; formState.value = JSON.parse(JSON.stringify(row)); isFormModalOpen.value = true; };
const showLastEventModal = (lastEvent: EventDetails | null) => {
  if (!lastEvent) {
    toast.add({ title: 'Info', description: 'No last event data available for this device.', color: 'blue' });
    return;
  }
  selectedLastEvent.value = lastEvent;
  isLastEventModalOpen.value = true;
};

// --- CRUD ---
const handleSaveNewDevice = async () => { isSaving.value = true; const payload = { name: formState.value.name, installation_area: formState.value.installationArea, mac_address: formState.value.mac_address || "00:00:00:00:00:00", firmware_version: formState.value.firmware_version || "", device_type: formState.value.device_type, installation_date: new Date().toISOString() }; try { await $api('/api/v1/devices/', { method: 'POST', body: payload }); toast.add({ title: successTitle.value, description: addSuccessMessage.value, color: 'green' }); isFormModalOpen.value = false; await fetchDevices(); } catch (error) { logger.error('[Device Management] Failed to add device:', error); toast.add({ title: 'Error', description: 'Could not add the new device.', color: 'red' }); } finally { isSaving.value = false; } };
const handleUpdateDevice = async () => { if (!formState.value.id) return; isSaving.value = true; const payload = { name: formState.value.name, installation_area: formState.value.installationArea, firmware_version: formState.value.firmware_version, }; try { await $api(`/api/v1/devices/${formState.value.id}`, { method: 'PUT', body: payload }); toast.add({ title: successTitle.value, description: updateSuccessMessage.value, color: 'green' }); isFormModalOpen.value = false; await fetchDevices(); } catch (error) { logger.error('[Device Management] Failed to update device:', error); toast.add({ title: 'Error', description: 'Could not update the device.', color: 'red' }); } finally { isSaving.value = false; } };
const handleRemoveDevice = () => { if (selectedDevices.value.length > 0) { isConfirmDeleteModalOpen.value = true; } };
const confirmDeleteDevices = async () => { isSaving.value = true; const idsToDelete = selectedDevices.value.map(d => d.id); try { await Promise.all( idsToDelete.map(id => $api(`/api/v1/devices/${id}`, { method: 'DELETE' })) ); allDevices.value = allDevices.value.filter(device => !idsToDelete.includes(device.id)); selectedDevices.value = []; isConfirmDeleteModalOpen.value = false; toast.add({ title: successTitle.value, description: deleteSuccessMessage.value, color: 'green' }); } catch (error) { logger.error('[Device Management] Failed to delete devices:', error); toast.add({ title: 'Error', description: 'Could not delete one or more devices.', color: 'red' }); } finally { isSaving.value = false; } };
const handleExportExcel = async () => { const XLSX = await import('xlsx'); const dataToExport = filteredDevices.value.map(device => ({ [deviceNameLabel.value]: device.name, [macAddressLabel.value]: device.mac_address, [areaLabel.value]: device.installationArea, [firmwareVersionLabel.value]: device.firmware_version || 'N/A', [installationDateLabel.value]: formatTimestamp(device.installationDate), [statusLabel.value]: getLocalizedStatus(device.status), })); if (dataToExport.length === 0) { toast.add({ title: 'No Data', description: 'There is no data to export.', color: 'orange' }); return; } const worksheet = XLSX.utils.json_to_sheet(dataToExport); const colWidths = Object.keys(dataToExport[0]).map(key => ({ wch: Math.max(key.length, 25) })); worksheet['!cols'] = colWidths; const workbook = XLSX.utils.book_new(); XLSX.utils.book_append_sheet(workbook, worksheet, "Device List"); const today = new Date(); const dateStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`; const fileName = `Device_List_${dateStr}.xlsx`; XLSX.writeFile(workbook, fileName); };

async function fetchDevices() {
  pending.value = true;
  try {
    const response: any[] = await $api('/api/v1/devices/');
    allDevices.value = response.map((device: any) => ({
      id: device._id,
      name: device.name,
      installationArea: device.installation_area,
      installationDate: new Date(device.installation_date).getTime(),
      status: (device.last_event?.status || 'Unknown') as LogStatus | 'Unknown',
      mac_address: device.mac_address,
      firmware_version: device.firmware_version,
      device_type: device.device_type,
      last_event: device.last_event,
      createdAt: new Date(device.createdAt).getTime(),
    }));
  } catch (error) {
    logger.error('[Device Management] Failed to fetch devices:', error);
    toast.add({ title: 'Error', description: 'Could not fetch devices.', color: 'red' });
  } finally {
    pending.value = false;
  }
}

const calculateDynamicItemsPerPage = () => {
  // Ensure the container element is available
  if (!deviceTableContainerRef.value) return;

  const tableContainer = deviceTableContainerRef.value;
  if (tableContainer.clientHeight === 0) return;

  // Subtract the header height to find the available space for rows
  const thead = tableContainer.querySelector('thead');
  const theadHeight = thead ? thead.clientHeight : 0;
  const availableBodyHeight = tableContainer.clientHeight - theadHeight;

  // We need at least one rendered row to measure its height
  const firstRowEl = tableContainer.querySelector('tbody tr');
  if (!firstRowEl) {
    // Can't calculate without a row to measure
    return;
  }

  const rowHeight = firstRowEl.getBoundingClientRect().height;
  if (rowHeight <= 0) return; // Avoid division by zero

  const numRowsThatFit = Math.floor(availableBodyHeight / rowHeight);
  const newItemsPerPage = Math.max(1, numRowsThatFit);

  if (itemsPerPage.value !== newItemsPerPage) {
    itemsPerPage.value = newItemsPerPage;
  }
};

onMounted(() => {
  fetchDevices().then(async () => {
    // Wait for the DOM to update with the fetched data
    await nextTick();

    // Now perform the initial calculation and set up the observer
    calculateDynamicItemsPerPage();
    if (deviceTableContainerRef.value) {
      resizeObserver = new ResizeObserver(calculateDynamicItemsPerPage);
      resizeObserver.observe(deviceTableContainerRef.value);
    }
  });
});

onBeforeUnmount(() => {
  if (resizeObserver) {
    resizeObserver.disconnect();
  }
});

// Recalculate when filters change the number of available rows
watch(filteredDevices, async () => {
  // Wait for the DOM to potentially re-render with the new filtered list
  await nextTick();
  calculateDynamicItemsPerPage();
});


// --- Page Head ---
useHead({title: pageTitle.value});
watch(pageTitle, (newTitle) => { useHead({title: newTitle}); });
</script>

<style scoped>
/* All custom scrollbar styles have been removed */
.custom-scrollbar {
  scrollbar-width: none; /* For Firefox */
}
.custom-scrollbar::-webkit-scrollbar {
  display: none; /* For Chrome, Safari, and Opera */
}
</style>