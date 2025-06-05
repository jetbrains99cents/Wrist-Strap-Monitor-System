<template>
  <div class="flex flex-1 min-h-0 overflow-hidden">
    <aside
        class="hidden md:flex md:flex-col bg-gray-100 dark:bg-dark-surface border-r border-gray-200 dark:border-dark-border p-4 w-60 lg:w-64 overflow-y-auto shrink-0"
        aria-label="Desktop Dashboard Navigation"
    >
      <UVerticalNavigation :links="localizedNavigationItems"
                           :ui="{ base: 'group relative flex items-start gap-x-3', padding: 'px-3 py-2.5', label: 'text-base whitespace-pre-line break-words text-left', icon: { base: 'flex-shrink-0 w-5 h-5 mt-0.5' } }"/>
    </aside>

    <section class="flex-1 flex flex-col overflow-hidden">
      <div class="md:hidden p-3 sm:p-4 sticky top-0 bg-white dark:bg-dark-bg z-20 border-b dark:border-dark-border">
        <UButton icon="i-heroicons-bars-3-20-solid" color="gray" variant="ghost" :aria-label="openMenuAriaLabel"
                 @click="isMobileMenuOpen = true"/>
      </div>

      <div class="pdf-main-area flex flex-col flex-1 overflow-y-auto">
        <div
            v-if="pdfViewerComponentRef"
            class="pdf-controls-bar sticky top-0
            z-10 p-2 flex flex-wrap justify-center items-center gap-x-2 gap-y-1 bg-gray-100 dark:bg-dark-surface border-b dark:border-dark-border shadow-sm shrink-0"
        >
          <div class="flex items-center gap-1">
            <UToggle v-model="isPanMode" on-icon="i-heroicons-arrows-pointing-out-20-solid"
                     off-icon="i-heroicons-cursor-arrow-rays-20-solid" :aria-label="interactionModeToggleAriaLabel"/>
            <span class="text-xs text-gray-600 dark:text-gray-400 whitespace-nowrap"> {{
                viewModeBaseLabel
              }}: {{ currentInteractionModeLabel }} </span>
          </div>
          <UButton size="sm" @click="pdfViewerComponentRef?.zoomIn()"
                   :disabled="pdfViewerComponentRef?.isRendering?.value">
            <UIcon name="i-heroicons-magnifying-glass-plus-20-solid" class="h-4 w-4 mr-1"/>
            {{ zoomInLabel }}
          </UButton>
          <UButton size="sm" @click="pdfViewerComponentRef?.zoomOut()"
                   :disabled="pdfViewerComponentRef?.isRendering?.value">
            <UIcon name="i-heroicons-magnifying-glass-minus-20-solid" class="h-4 w-4 mr-1"/>
            {{ zoomOutLabel }}
          </UButton>
          <UButton size="sm" @click="pdfViewerComponentRef?.resetZoomAndPan()"
                   :disabled="pdfViewerComponentRef?.isRendering?.value">
            <UIcon name="i-heroicons-arrows-pointing-out-20-solid" class="h-4 w-4 mr-1"/>
            {{ resetViewLabel }}
          </UButton>
          <div class="flex items-center gap-1 text-xs text-gray-600 dark:text-gray-400">
            <span>{{ scaleLabel }}:</span>
            <UInput v-model.number="zoomInputPercentage" type="number" size="xs" class="w-20 text-center"
                    @change="applyManualZoomToViewer" @keyup.enter="applyManualZoomToViewer" :min="minZoomPercentage"
                    :max="maxZoomPercentage" :disabled="pdfViewerComponentRef?.isRendering?.value"/>
            <span>%</span>
          </div>
          <span v-if="pdfViewerComponentRef?.totalPages?.value > 1" class="text-xs text-gray-600 dark:text-gray-400"> {{
              pageLabel
            }}: {{ pdfViewerComponentRef?.currentPageNum?.value }} / {{
              pdfViewerComponentRef?.totalPages?.value
            }} </span>
          <span
              v-if="pdfViewerComponentRef?.currentScale?.value && Number.isFinite(pdfViewerComponentRef.currentScale.value)"
              class="text-xs text-gray-500 dark:text-gray-400 hidden sm:inline"> {{
              renderLabel
            }}: {{ pdfViewerComponentRef.currentScale.value.toFixed(1) }}x </span>
        </div>

        <div ref="pdfViewAndGridAreaRef" class="flex-grow relative overflow-hidden">
          <PdfViewer
              ref="pdfViewerComponentRef"
              src="/factory-layout.pdf"
              alt="Factory Production Layout"
              class="w-full h-full"
              :interaction-mode="interactionMode"
              @rendered="handlePdfRendered"
              @loaded="handlePdfLoaded"
              @panstart="isPdfCurrentlyPanning = true"
              @panend="isPdfCurrentlyPanning = false"
          />
          <GridOverlay
              v-if="computedGridOverlayProps.visible"
              :rows="computedGridOverlayProps.rows"
              :cols="computedGridOverlayProps.cols"
              :cell-width="computedGridOverlayProps.cellWidth"
              :cell-height="computedGridOverlayProps.cellHeight"
              :selected-cell="selectedGridCell"
              :is-pdf-panning="isPdfCurrentlyPanning"
              :interaction-mode="interactionMode"
              :cell-statuses="cellStatusesForOverlay"
              @cell-click="handleGridCellClick"
              :tooltip-name-label="tooltipNameLabel"
              :tooltip-area-label="tooltipAreaLabel"
              :tooltip-last-event-status-label="tooltipLastEventStatusLabel"
              :tooltip-last-event-type-label="tooltipLastEventTypeLabel"
              :tooltip-created-at-label="tooltipCreatedAtLabel"
              :tooltip-installed-at-label="tooltipInstalledAtLabel"
              :tooltip-cell-label="tooltipCellLabel"
              :tooltip-row-label="modalRowLabel"
              :tooltip-col-label="modalColLabel"
              :style="{
                position: 'absolute',
                top: `${computedGridOverlayProps.y}px`,
                left: `${computedGridOverlayProps.x}px`,
                width: `${computedGridOverlayProps.width}px`,
                height: `${computedGridOverlayProps.height}px`,
                boxSizing: 'border-box',
                pointerEvents: 'none',
                zIndex: 10
              }"
              aria-hidden="true"
          />
        </div>
      </div>
    </section>
    <USlideover v-model="isMobileMenuOpen" side="left" :ui="{ width: 'max-w-xs w-full sm:w-72', zIndex: 'z-50' }">
      <UCard class="flex flex-col flex-1 h-full"
             :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800', body: { padding: '', base: 'flex-1 overflow-y-auto' } }">
        <template #header>
          <div class="flex items-center justify-between p-4"><h3
              class="text-lg font-semibold text-gray-800 dark:text-dark-text-primary">{{ mobileMenuTitleLabel }}</h3>
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

    <UModal v-model="isGridCellModalOpen">
      <UCard :ui="{ divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-base font-semibold leading-6 text-gray-900 dark:text-white">
              {{ cellAssignmentModalTitleLabel }} </h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" class="-my-1"
                     @click="closeAndResetModal"/>
          </div>
        </template>

        <div v-if="modalCellData" class="p-4 space-y-3">
          <p class="text-sm">
            <span class="font-medium text-gray-700 dark:text-gray-200">{{ selectedCellInfoLabel }}:</span>
            <span class="ml-1">{{ modalRowLabel }}: {{ modalCellData.row }}, {{ modalColLabel }}: {{
                modalCellData.col
              }}</span>
          </p>

          <template v-if="modalCellData.device">
            <UDivider :label="currentDeviceOnCellLabel"
                      :ui="{ label: 'text-xs font-medium text-gray-500 dark:text-gray-400', border: { base: 'border-gray-200 dark:border-gray-700'}}"/>
            <div class="grid grid-cols-[max-content_1fr] gap-x-3 gap-y-1.5 text-sm">
              <span class="text-gray-600 dark:text-gray-400 text-left font-medium">{{ modalDeviceNameLabel }}:</span>
              <span class="dark:text-white font-semibold">{{ modalCellData.device.device_name }}</span>
              <span class="text-gray-600 dark:text-gray-400 text-left font-medium">{{ modalDeviceAreaLabel }}:</span>
              <span class="dark:text-white">{{ modalCellData.device.installation_area }}</span>
              <span class="text-gray-600 dark:text-gray-400 text-left font-medium">{{
                  modalDeviceLastEventStatusLabel
                }}:</span> <span class="dark:text-white">{{
                getLocalizedStatus(modalCellData.device.last_event.status)
              }}</span>
              <span class="text-gray-600 dark:text-gray-400 text-left font-medium">{{ modalLastEventTypeLabel }}:</span>
              <span class="dark:text-white">{{ modalCellData.device.last_event.type }}</span>
              <span class="text-gray-600 dark:text-gray-400 text-left font-medium">{{
                  modalFirmwareVersionLabel
                }}:</span> <span class="dark:text-white">{{ modalCellData.device.firmware_version || 'N/A' }}</span>
              <span class="text-gray-600 dark:text-gray-400 text-left font-medium">{{ modalWifiSsidLabel }}:</span>
              <span class="dark:text-white">{{ modalCellData.device.wifi_ssid || 'N/A' }}</span>
              <span class="text-gray-600 dark:text-gray-400 text-left font-medium">{{
                  modalScaleAtCreationLabel
                }}:</span> <span class="dark:text-white">{{
                modalCellData.device.scale_at_creation_time.toFixed(1)
              }}x</span>
              <span class="text-gray-600 dark:text-gray-400 text-left font-medium">{{ modalCreatedAtLabel }}:</span>
              <span class="dark:text-white">{{ formatDateForDisplay(modalCellData.device.created_at) }}</span>
              <span class="text-gray-600 dark:text-gray-400 text-left font-medium">{{ modalInstalledAtLabel }}:</span>
              <span class="dark:text-white">{{ formatDateForDisplay(modalCellData.device.installed_at) }}</span>
            </div>
          </template>
          <p v-else class="text-sm text-gray-500 dark:text-gray-400">{{ noDeviceAssignedToCellLabel }}</p>

          <UDivider :ui="{border: {base: 'border-gray-200 dark:border-gray-700'}}"/>

          <div v-if="!isCreatingNewDeviceInModal">
            <div class="flex justify-between items-center mb-2">
              <label for="existing-device-select" class="block text-sm font-medium text-gray-700 dark:text-gray-200">{{
                  assignExistingDeviceLabel
                }}</label>
              <UButton size="xs" variant="outline" @click="isCreatingNewDeviceInModal = true">
                {{ createNewDeviceButtonLabel }}
              </UButton>
            </div>
            <USelectMenu
                id="existing-device-select"
                v-model="modalSelectedDeviceId"
                :options="availableDeviceOptionsForModal"
                value-attribute="id"
                option-attribute="name"
                :placeholder="selectDevicePlaceholderLabel"
                searchable
                :search-attributes="['name']"
                size="md"
            >
              <template #label>
                  <span v-if="modalSelectedDeviceId && availableDevices.find(d => d.id === modalSelectedDeviceId)"
                        class="text-sm">
                    {{ availableDevices.find(d => d.id === modalSelectedDeviceId)?.name }}
                  </span>
                <span v-else class="text-sm text-gray-400 dark:text-gray-500">{{ selectDevicePlaceholderLabel }}</span>
              </template>
              <template #option="{ option }">
                <span class="text-sm">{{ option.name }}</span>
              </template>
            </USelectMenu>
          </div>

          <div v-else class="space-y-3">
            <div class="flex justify-between items-center mb-2">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">{{
                  createNewDeviceTitleLabel
                }}</label>
              <UButton size="xs" variant="link" @click="isCreatingNewDeviceInModal = false">
                {{ selectExistingDeviceButtonLabel }}
              </UButton>
            </div>
            <UFormGroup :label="newDeviceNameLabel" name="newDeviceName" required :ui="{label: { base: 'text-sm' }}">
              <UInput v-model="newDeviceForm.name" :placeholder="newDeviceNamePlaceholderLabel" size="md"/>
            </UFormGroup>
            <UFormGroup :label="newDeviceAreaLabel" name="newDeviceArea" required :ui="{label: { base: 'text-sm' }}">
              <USelectMenu
                  v-model="newDeviceForm.installation_area"
                  :options="areaOptionsForModal"
                  :placeholder="selectAreaPlaceholderLabel"
                  searchable
                  size="md"
              />
            </UFormGroup>
          </div>

        </div>
        <div v-else class="p-4">
          <p class="text-sm">{{ noCellDataAvailableLabel }}</p>
        </div>

        <template #footer>
          <div class="flex justify-between w-full">
            <UButton :label="closeButtonLabel" color="gray" variant="outline" @click="closeAndResetModal"/>
            <UButton :label="saveAssignmentButtonLabel" color="primary" @click="handleSaveCellAssignment"/>
          </div>
        </template>
      </UCard>
    </UModal>

  </div>
</template>

<script setup lang="ts">
import {ref, computed, watch, onMounted, nextTick} from 'vue';
import {useLanguage} from '~/composables/useLanguage';
import PdfViewer from '~/components/pdf/PdfViewer.vue';
import GridOverlay from '~/components/interactive/GridOverlay.vue';

type InteractionMode = 'pan' | 'select';

// --- Data Structures ---
type LogStatus =
    "Connected"
    | "Disconnected"
    | "Voltage reading failed"
    | "Info"
    | "Warning"
    | "Error"
    | "Critical"
    | "Configured"
    | "Reset";
type EventCategory = "Connection" | "Sensor Reading" | "Alert" | "User action" | "System";

interface EventDetails {
  type: EventCategory;
  status?: LogStatus;
  value: string | Record<string, any>;
}

interface DeviceData {
  id: string;
  device_name: string;
  coordinates: { row: number; col: number };
  installation_area: string;
  mac_address?: string;
  wifi_ssid?: string;
  firmware_version?: string;
  last_event: EventDetails;
  scale_at_creation_time: number;
  created_at: string;
  installed_at: string;
}

interface GridCellStatus {
  status: LogStatus;
  deviceId: string;
  deviceName: string;
  installationArea?: string;
  lastEventType?: EventCategory;
  createdAtFormatted?: string;
  installedAtFormatted?: string;
}

interface SelectableDevice {
  id: string;
  name: string;
}

interface ModalDisplayData {
  row: number;
  col: number;
  device?: DeviceData;
}


interface PdfViewerExposed {
  zoomIn: () => void;
  zoomOut: () => void;
  resetZoomAndPan: () => void;
  setPdfScale: (scale: number) => void;
  goToPage: (page: number) => void;
  reloadPdf: () => void;
  currentScale: { value: number };
  currentPageNum: { value: number };
  totalPages: { value: number };
  isRendering: { value: boolean };
  isLoading: { value: boolean };
  minScale: number;
  maxScale: number;
  getCanvasActualWidth: () => number;
  getCanvasActualHeight: () => number;
  getCanvasPanX: () => number;
  getCanvasPanY: () => number;
  getPdfPageOriginalWidth: () => number;
  getPdfPageOriginalHeight: () => number;
  initialPdfRenderScale?: number;
}

const {currentLanguage} = useLanguage();


const isMobileMenuOpen = ref(false);
const pdfViewerComponentRef = ref<PdfViewerExposed | null>(null);
const isPdfCurrentlyPanning = ref(false);
const zoomInputPercentage = ref(100);
const currentPageInput = ref(1);
const totalPagesForPdf = ref(0);

const isPanMode = ref(true);
const interactionMode = computed<InteractionMode>(() => isPanMode.value ? 'pan' : 'select');

// --- Translations ---
const openMenuAriaLabel = computed(() => currentLanguage.value === 'vi' ? 'Mở menu điều hướng' : 'Open navigation menu');
const mobileMenuTitleLabel = computed(() => currentLanguage.value === 'vi' ? 'Menu bản đồ' : 'Map menu');
const viewModeBaseLabel = computed(() => currentLanguage.value === 'vi' ? 'Chế độ xem' : 'View mode');
const currentInteractionModeLabel = computed(() => {
  return interactionMode.value === 'pan' ? (currentLanguage.value === 'vi' ? 'Kéo bản đồ' : 'Pan map') : (currentLanguage.value === 'vi' ? 'Chọn ô' : 'Select cell');
});
const interactionModeToggleAriaLabel = computed(() => {
  return isPanMode.value ? (currentLanguage.value === 'vi' ? 'Chuyển sang chế độ chọn ô' : 'Switch to select cell mode') : (currentLanguage.value === 'vi' ? 'Chuyển sang chế độ kéo bản đồ' : 'Switch to pan map mode');
});
const scaleLabel = computed(() => currentLanguage.value === 'vi' ? 'Tỉ lệ' : 'Scale');
const pageLabel = computed(() => currentLanguage.value === 'vi' ? 'Trang' : 'Page');
const renderLabel = computed(() => currentLanguage.value === 'vi' ? 'Kết xuất' : 'Render');
const zoomInLabel = computed(() => currentLanguage.value === 'vi' ? 'Phóng to' : 'Zoom in');
const zoomOutLabel = computed(() => currentLanguage.value === 'vi' ? 'Thu nhỏ' : 'Zoom out');
const resetViewLabel = computed(() => currentLanguage.value === 'vi' ? 'Đặt lại chế độ xem' : 'Reset view');

const cellAssignmentModalTitleLabel = computed(() => currentLanguage.value === 'vi' ? 'Thông tin & Gán thiết bị cho Ô' : 'Cell Information & Device Assignment');
const youSelectedCellAtLabel = computed(() => currentLanguage.value === 'vi' ? 'Bạn đã chọn ô tại' : 'You selected cell at');
const modalRowLabel = computed(() => currentLanguage.value === 'vi' ? 'Hàng' : 'Row');
const modalColLabel = computed(() => currentLanguage.value === 'vi' ? 'Cột' : 'Column');
const assignExistingDeviceLabel = computed(() => currentLanguage.value === 'vi' ? 'Gán thiết bị hiện có' : 'Assign existing device');
const createNewDeviceButtonLabel = computed(() => currentLanguage.value === 'vi' ? 'Hoặc tạo thiết bị mới' : 'Or create new device');
const selectDevicePlaceholderLabel = computed(() => currentLanguage.value === 'vi' ? 'Chọn một thiết bị...' : 'Select a device...');
const currentDeviceOnCellLabel = computed(() => currentLanguage.value === 'vi' ? 'Thiết bị hiện tại' : 'Current device');
const createNewDeviceTitleLabel = computed(() => currentLanguage.value === 'vi' ? 'Tạo thiết bị mới' : 'Create new device');
const selectExistingDeviceButtonLabel = computed(() => currentLanguage.value === 'vi' ? 'Hoặc chọn thiết bị hiện có' : 'Or select existing device');
const newDeviceNameLabel = computed(() => currentLanguage.value === 'vi' ? 'Tên thiết bị mới' : 'New device name');
const newDeviceNamePlaceholderLabel = computed(() => currentLanguage.value === 'vi' ? 'Ví dụ: Device 123' : 'Example: Device 123');
const newDeviceAreaLabel = computed(() => currentLanguage.value === 'vi' ? 'Khu vực lắp đặt' : 'Installation area');
const selectAreaPlaceholderLabel = computed(() => currentLanguage.value === 'vi' ? 'Chọn khu vực...' : 'Select area...');
const noCellDataAvailableLabel = computed(() => currentLanguage.value === 'vi' ? 'Không có dữ liệu ô.' : 'No cell data available.');
const closeButtonLabel = computed(() => currentLanguage.value === 'vi' ? 'Đóng' : 'Close');
const saveAssignmentButtonLabel = computed(() => currentLanguage.value === 'vi' ? 'Lưu gán' : 'Save assignment');
const modalDeviceLastEventStatusLabel = computed(() => currentLanguage.value === 'vi' ? 'Trạng thái sự kiện cuối' : 'Last event status');
const currentInstallationAreaLabel = computed(() => currentLanguage.value === 'vi' ? 'Khu vực lắp đặt hiện tại' : 'Current installation area');
const modalMacAddressLabel = computed(() => currentLanguage.value === 'vi' ? 'Địa chỉ MAC' : 'MAC address');
const modalFirmwareVersionLabel = computed(() => currentLanguage.value === 'vi' ? 'Phiên bản Firmware' : 'Firmware version');
const modalWifiSsidLabel = computed(() => currentLanguage.value === 'vi' ? 'Wi-Fi SSID' : 'Wi-Fi SSID');
const modalScaleAtCreationLabel = computed(() => currentLanguage.value === 'vi' ? 'Tỉ lệ khi tạo' : 'Scale at creation');
const modalCreatedAtLabel = computed(() => currentLanguage.value === 'vi' ? 'Ngày tạo' : 'Created at');
const modalInstalledAtLabel = computed(() => currentLanguage.value === 'vi' ? 'Ngày lắp đặt' : 'Installed at');
const modalLastEventTypeLabel = computed(() => currentLanguage.value === 'vi' ? 'Loại sự kiện cuối' : 'Last event type');
const noDeviceAssignedToCellLabel = computed(() => currentLanguage.value === 'vi' ? 'Chưa có thiết bị nào được gán cho ô này.' : 'No device assigned to this cell.');
const selectedCellInfoLabel = computed(() => currentLanguage.value === 'vi' ? 'Thông tin ô đã chọn' : 'Selected cell info');
const modalDeviceNameLabel = computed(() => currentLanguage.value === 'vi' ? 'Tên thiết bị' : 'Device name');
const modalDeviceAreaLabel = computed(() => currentLanguage.value === 'vi' ? 'Khu vực lắp đặt' : 'Installation area');

// Tooltip Labels
const tooltipNameLabel = computed(() => currentLanguage.value === 'vi' ? 'Tên' : 'Name');
const tooltipAreaLabel = computed(() => currentLanguage.value === 'vi' ? 'Khu vực' : 'Area');
const tooltipLastEventStatusLabel = computed(() => currentLanguage.value === 'vi' ? 'Trạng thái sự kiện cuối' : 'Last Event Status');
const tooltipLastEventTypeLabel = computed(() => currentLanguage.value === 'vi' ? 'Loại sự kiện cuối' : 'Last Event Type');
const tooltipCreatedAtLabel = computed(() => currentLanguage.value === 'vi' ? 'Ngày tạo' : 'Created At');
const tooltipInstalledAtLabel = computed(() => currentLanguage.value === 'vi' ? 'Ngày lắp đặt' : 'Installed At');
const tooltipCellLabel = computed(() => currentLanguage.value === 'vi' ? 'Ô' : 'Cell');


const minZoomPercentage = computed(() => pdfViewerComponentRef.value ? Math.round(pdfViewerComponentRef.value.minScale * 100) : 20);
const maxZoomPercentage = computed(() => pdfViewerComponentRef.value ? Math.round(pdfViewerComponentRef.value.maxScale * 100) : 500);

const applyManualZoomToViewer = () => {
  const viewer = pdfViewerComponentRef.value;
  if (viewer) {
    const currentZoomInputVal = zoomInputPercentage.value;
    if (typeof currentZoomInputVal === 'number' && !isNaN(currentZoomInputVal)) {
      const newScale = currentZoomInputVal / 100;
      if (Number.isFinite(newScale) && newScale > 0) {
        viewer.setPdfScale(newScale);
      } else {
        if (viewer.currentScale?.value && Number.isFinite(viewer.currentScale.value) && viewer.currentScale.value > 0) {
          zoomInputPercentage.value = Math.round(viewer.currentScale.value * 100);
        } else {
          zoomInputPercentage.value = Math.round((viewer.initialPdfRenderScale || 1.0) * 100);
        }
      }
    } else {
      if (viewer.currentScale?.value && Number.isFinite(viewer.currentScale.value) && viewer.currentScale.value > 0) {
        zoomInputPercentage.value = Math.round(viewer.currentScale.value * 100);
      } else {
        zoomInputPercentage.value = Math.round((viewer.initialPdfRenderScale || 1.0) * 100);
      }
    }
  }
};

const handlePdfRendered = () => {
  console.log('[index.vue] PDF Page Rendered');
};
const handlePdfLoaded = async () => {
  console.log('[index.vue] PDF Loaded event received.');
  await nextTick();
  if (pdfViewerComponentRef.value) {
    const currentScaleVal = pdfViewerComponentRef.value.currentScale.value;
    if (Number.isFinite(currentScaleVal) && currentScaleVal > 0) {
      zoomInputPercentage.value = Math.round(currentScaleVal * 100);
    } else {
      zoomInputPercentage.value = Math.round((pdfViewerComponentRef.value.initialPdfRenderScale || 1.0) * 100);
    }
    totalPagesForPdf.value = pdfViewerComponentRef.value.totalPages.value;
    currentPageInput.value = pdfViewerComponentRef.value.currentPageNum.value;
  }
};

watch(() => pdfViewerComponentRef.value?.currentScale?.value, (newScale) => {
  if (typeof newScale === 'number' && Number.isFinite(newScale) && newScale > 0) {
    if (Math.round(newScale * 100) !== zoomInputPercentage.value) {
      zoomInputPercentage.value = Math.round(newScale * 100);
    }
  }
});
watch(() => pdfViewerComponentRef.value?.currentPageNum?.value, (newPage) => {
  if (typeof newPage === 'number') currentPageInput.value = newPage;
});
watch(() => pdfViewerComponentRef.value?.totalPages?.value, (newTotal) => {
  if (typeof newTotal === 'number') totalPagesForPdf.value = newTotal;
});

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

const pdfViewAndGridAreaRef = ref<HTMLElement | null>(null);
const BASE_CELL_SIZE_PX = 50;
const selectedGridCell = ref<{ row: number; col: number } | null>(null);
const isGridCellModalOpen = ref(false);
const modalCellData = ref<ModalDisplayData | null>(null);


// --- Modal Device Assignment State ---
const isCreatingNewDeviceInModal = ref(false);
const modalSelectedDeviceId = ref<string | undefined>(undefined);
const newDeviceForm = ref({
  name: '',
  installation_area: undefined as string | undefined,
  // mac_address removed
});
const availableDevices = ref<SelectableDevice[]>([]);
const availableInstallationAreas = ref<string[]>(["POL", "FLW", "CG A", "CG B", "QA Main", "Storage X", "Production Line 1", "Production Line 2", "Maintenance Bay", "Office Area"]);

const areaOptionsForModal = computed(() => {
  return availableInstallationAreas.value.map(area => ({label: area, value: area}));
});

const availableDeviceOptionsForModal = computed(() => {
  return availableDevices.value.map(d => ({id: d.id, name: d.name}));
});


const deviceDataStream = ref<DeviceData[]>([]);

const formatDateForDisplay = (isoString: string): string => {
  if (!isoString) return 'N/A';
  try {
    const date = new Date(isoString);
    return date.toLocaleDateString(currentLanguage.value === 'vi' ? 'vi-VN' : 'en-US', {
      year: 'numeric', month: '2-digit', day: '2-digit'
    });
  } catch (e) {
    return 'Invalid Date';
  }
};

const formatDateForTooltip = (isoString: string): string => {
  if (!isoString) return 'N/A';
  try {
    const date = new Date(isoString);
    return date.toLocaleDateString(currentLanguage.value === 'vi' ? 'vi-VN' : 'en-US', {
      year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    });
  } catch (e) {
    return 'Invalid Date';
  }
};

const generateDeviceData = (count = 40): DeviceData[] => {
  console.groupCollapsed(`[generateDeviceData] Generating ${count} mock grid devices`);
  const data: DeviceData[] = [];
  const statuses: LogStatus[] = ["Connected", "Error", "Disconnected", "Warning", "Info", "Voltage reading failed", "Configured", "Reset"];
  const eventTypes: EventCategory[] = ["Connection", "Sensor Reading", "Alert", "User action", "System"];

  const maxRows = 20;
  const maxCols = 30;
  const usedCells = new Set<string>();
  const now = new Date();

  for (let i = 1; i <= count; i++) {
    let row, col;
    do {
      row = Math.floor(Math.random() * maxRows);
      col = Math.floor(Math.random() * maxCols);
    } while (usedCells.has(`${row}-${col}`));
    usedCells.add(`${row}-${col}`);

    const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)];
    let eventStatus: LogStatus | undefined = statuses[Math.floor(Math.random() * statuses.length)];
    let eventValue: string | Record<string, any> = `Event value for ${eventType} at ${new Date().toLocaleTimeString()}`;
    if (eventType === 'Connection') eventStatus = Math.random() > 0.5 ? "Connected" : "Disconnected";
    else if (eventType === 'System') eventStatus = Math.random() > 0.5 ? "Configured" : "Reset";
    else if (eventType === 'Sensor Reading') eventStatus = Math.random() > 0.05 ? "Info" : "Voltage reading failed";


    const deviceName = `Device ${i}`;
    const installedDate = new Date(now.getTime() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000);
    const deviceId = `dev-instance-${Date.now().toString(36).slice(-4)}-${i}`;

    const deviceEntry: DeviceData = {
      id: deviceId,
      device_name: deviceName,
      coordinates: {row, col},
      installation_area: availableInstallationAreas.value[Math.floor(Math.random() * availableInstallationAreas.value.length)],
      // mac_address removed from direct generation here, can be added in save if needed
      wifi_ssid: `FACTORY_WIFI_${String.fromCharCode(65 + (i % 3))}`,
      firmware_version: `1.${i % 5}.${i % 9}`,
      last_event: {
        type: eventType,
        status: eventStatus,
        value: eventValue,
      },
      scale_at_creation_time: parseFloat((Math.random() * 4 + 1).toFixed(1)),
      created_at: new Date(installedDate.getTime() - Math.floor(Math.random() * 5) * 24 * 60 * 60 * 1000).toISOString(),
      installed_at: installedDate.toISOString(),
    };
    data.push(deviceEntry);
    console.log(`  Created Grid Device: ID=${deviceEntry.id}, Name=${deviceEntry.device_name}, Area=${deviceEntry.installation_area}, Coords=R${row}C${col}, Last Event Status=${eventStatus}`);
  }
  console.log(`Generated ${data.length} mock devices for deviceDataStream.`);
  console.groupEnd();
  return data;
};


onMounted(() => {
  console.log("[index.vue/onMounted] Component mounted.");
  deviceDataStream.value = generateDeviceData();
  console.log("[onMounted] Initial grid devices (first 3):", JSON.parse(JSON.stringify(deviceDataStream.value.slice(0, 3))));

  availableDevices.value = [
    {id: 'unique-master-dev-001', name: 'ESP32 Sensor Alpha'},
    {id: 'unique-master-dev-002', name: 'ESP32 Sensor Beta'},
    {id: 'unique-master-dev-003', name: 'Temperature Probe Gamma'},
    {id: 'unique-master-dev-004', name: 'Lighting Controller Delta'},
    {id: 'unique-master-dev-005', name: 'Motion Sensor Epsilon'},
    ...deviceDataStream.value.slice(0, 5).map(d => ({id: d.id, name: d.device_name})),
  ];
  const uniqueDeviceIds = new Set<string>();
  availableDevices.value = availableDevices.value.filter(device => {
    if (uniqueDeviceIds.has(device.id)) {
      return false;
    }
    uniqueDeviceIds.add(device.id);
    return true;
  });

  console.log("[onMounted] Initialized availableInstallationAreas:", JSON.parse(JSON.stringify(availableInstallationAreas.value)));
  console.log("[onMounted] Initialized availableDevices (master list):", JSON.parse(JSON.stringify(availableDevices.value)));
});


const computedGridOverlayProps = computed(() => {
  const viewer = pdfViewerComponentRef.value;
  if (!viewer || typeof viewer.getCanvasActualWidth !== 'function' || typeof viewer.getCanvasActualHeight !== 'function' ||
      typeof viewer.getCanvasPanX !== 'function' || typeof viewer.getCanvasPanY !== 'function') {
    return {
      visible: false,
      x: 0,
      y: 0,
      width: 0,
      height: 0,
      rows: 0,
      cols: 0,
      cellWidth: BASE_CELL_SIZE_PX,
      cellHeight: BASE_CELL_SIZE_PX
    };
  }
  const panXVal = viewer.getCanvasPanX();
  const panYVal = viewer.getCanvasPanY();
  const actualWidthVal = viewer.getCanvasActualWidth();
  const actualHeightVal = viewer.getCanvasActualHeight();

  if (!Number.isFinite(actualWidthVal) || actualWidthVal <= 0 ||
      !Number.isFinite(actualHeightVal) || actualHeightVal <= 0 ||
      !Number.isFinite(panXVal) || !Number.isFinite(panYVal) ||
      BASE_CELL_SIZE_PX <= 0) {
    return {
      visible: false,
      x: 0,
      y: 0,
      width: 0,
      height: 0,
      rows: 0,
      cols: 0,
      cellWidth: BASE_CELL_SIZE_PX,
      cellHeight: BASE_CELL_SIZE_PX
    };
  }
  const cols = Math.max(0, Math.floor(actualWidthVal / BASE_CELL_SIZE_PX));
  const rows = Math.max(0, Math.floor(actualHeightVal / BASE_CELL_SIZE_PX));
  if (cols <= 0 || rows <= 0) {
    return {
      visible: false,
      x: panXVal,
      y: panYVal,
      width: actualWidthVal,
      height: actualHeightVal,
      rows: 0,
      cols: 0,
      cellWidth: BASE_CELL_SIZE_PX,
      cellHeight: BASE_CELL_SIZE_PX
    };
  }
  return {
    visible: true,
    x: panXVal,
    y: panYVal,
    width: actualWidthVal,
    height: actualHeightVal,
    rows: rows,
    cols: cols,
    cellWidth: BASE_CELL_SIZE_PX,
    cellHeight: BASE_CELL_SIZE_PX
  };
});

const cellStatusesForOverlay = computed((): Record<string, GridCellStatus> => {
  const statuses: Record<string, GridCellStatus> = {};
  const gridProps = computedGridOverlayProps.value;
  if (!gridProps.visible || gridProps.rows === 0 || gridProps.cols === 0) {
    return {};
  }
  // console.groupCollapsed(`[cellStatusesForOverlay] Processing ${deviceDataStream.value.length} devices for grid display.`);
  for (const device of deviceDataStream.value) {
    const row = device.coordinates.row;
    const col = device.coordinates.col;
    const status = device.last_event.status || 'warning';
    const name = device.device_name;
    const deviceGridId = device.id;

    if (typeof row !== 'number' || typeof col !== 'number' || row < 0 || col < 0) {
      // console.warn(`  Skipping device '${name}' (ID: ${deviceGridId}) due to invalid coordinates: R${row},C${col}.`);
      continue;
    }

    if (col < gridProps.cols && row < gridProps.rows) {
      const key = `${row}-${col}`;
      statuses[key] = {
        status,
        deviceId: deviceGridId,
        deviceName: name,
        installationArea: device.installation_area,
        lastEventType: device.last_event.type,
        createdAtFormatted: formatDateForTooltip(device.created_at), // Use new formatter for tooltips
        installedAtFormatted: formatDateForTooltip(device.installed_at) // Use new formatter for tooltips
      };
    }
  }
  // console.groupEnd();
  return statuses;
});

const resetModalState = () => {
  console.log("[resetModalState] Resetting modal state.");
  isCreatingNewDeviceInModal.value = false;
  modalSelectedDeviceId.value = undefined;
  newDeviceForm.value = {name: '', installation_area: undefined};
};

const closeAndResetModal = () => {
  console.log("[closeAndResetModal] Closing modal and resetting state.");
  isGridCellModalOpen.value = false;
  resetModalState();
};


const handleGridCellClick = (cell: { row: number; col: number; }) => {
  console.groupCollapsed(`[handleGridCellClick] Cell R${cell.row},C${cell.col} clicked.`);
  if (interactionMode.value !== 'select') {
    console.log("  Mode is not 'select'. Aborting.");
    console.groupEnd();
    return;
  }
  if (isPdfCurrentlyPanning.value) {
    console.log("  PDF is panning. Aborting.");
    console.groupEnd();
    return;
  }

  resetModalState();

  const existingDeviceOnCell = deviceDataStream.value.find(d => d.coordinates.row === cell.row && d.coordinates.col === cell.col);
  console.log("  Existing device on cell:", existingDeviceOnCell ? JSON.parse(JSON.stringify(existingDeviceOnCell)) : "None");

  modalCellData.value = {
    row: cell.row,
    col: cell.col,
    device: existingDeviceOnCell
  };

  if (existingDeviceOnCell) {
    const selectableMatch = availableDevices.value.find(ad => ad.id === existingDeviceOnCell.id);
    if (selectableMatch) {
      modalSelectedDeviceId.value = selectableMatch.id;
      console.log(`  Pre-selecting device from available list: ID='${selectableMatch.id}', Name='${selectableMatch.name}'`);
    } else {
      console.log(`  Device '${existingDeviceOnCell.device_name}' (ID: ${existingDeviceOnCell.id}) on cell is not in 'availableDevices'.`);
    }
  }

  isGridCellModalOpen.value = true;
  console.log("  Modal opened. Modal data:", JSON.parse(JSON.stringify(modalCellData.value)));
  console.groupEnd();
};

const getLocalizedStatus = (status?: LogStatus): string => {
  if (!status) return 'N/A';
  if (currentLanguage.value === 'vi') {
    switch (status) {
      case "Connected":
        return "Đã kết nối";
      case "Disconnected":
        return "Mất kết nối";
      case "Voltage reading failed":
        return "Lỗi đọc điện áp";
      case "Info":
        return "Thông tin";
      case "Warning":
        return "Cảnh báo";
      case "Error":
        return "Lỗi";
      case "Critical":
        return "Nghiêm trọng";
      case "Configured":
        return "Đã cấu hình";
      case "Reset":
        return "Đã đặt lại";
      default:
        return status;
    }
  }
  return status;
};

const handleSaveCellAssignment = () => {
  console.groupCollapsed("[handleSaveCellAssignment] Attempting to save cell assignment.");
  if (!modalCellData.value) {
    console.warn("  No modalCellData available. Aborting.");
    console.groupEnd();
    return;
  }

  const {row, col} = modalCellData.value;
  let newGridDeviceData: DeviceData;
  const nowISO = new Date().toISOString();
  const currentScale = pdfViewerComponentRef.value?.currentScale.value || 1.0;

  if (isCreatingNewDeviceInModal.value) {
    console.log("  Mode: Creating new device from form:", JSON.parse(JSON.stringify(newDeviceForm.value)));
    if (!newDeviceForm.value.name.trim()) {
      console.warn("  New device name is empty. Aborting.");
      alert(currentLanguage.value === 'vi' ? 'Tên thiết bị không được để trống.' : 'Device name cannot be empty.');
      console.groupEnd();
      return;
    }
    if (!newDeviceForm.value.installation_area) {
      console.warn("  New device installation area is not selected/empty. Aborting.");
      alert(currentLanguage.value === 'vi' ? 'Khu vực lắp đặt không được để trống.' : 'Installation area cannot be empty.');
      console.groupEnd();
      return;
    }
    const newDeviceUniqueId = `dev-${Date.now().toString(36)}-${Math.random().toString(36).substring(2, 9)}`;

    newGridDeviceData = {
      id: newDeviceUniqueId,
      device_name: newDeviceForm.value.name.trim(),
      coordinates: {row, col},
      installation_area: newDeviceForm.value.installation_area,
      // mac_address, wifi_ssid, firmware_version are defaults for a newly created device from modal
      mac_address: `NEW-MAC-${newDeviceUniqueId.slice(-4)}`,
      wifi_ssid: "WIFI_PENDING_CONFIG",
      firmware_version: "1.0.0-default",
      last_event: {
        type: 'System',
        status: 'Configured',
        value: 'Device newly created and placed on grid.'
      },
      scale_at_creation_time: currentScale,
      created_at: nowISO,
      installed_at: nowISO,
    };

    availableDevices.value.push({
      id: newGridDeviceData.id,
      name: newGridDeviceData.device_name,
    });
    console.log('  New device prepared for grid & added to availableDevices list:', JSON.parse(JSON.stringify(newGridDeviceData)));

  } else {
    console.log("  Mode: Assigning existing device from selectable list.");
    if (!modalSelectedDeviceId.value) {
      console.warn("  No existing device selected from list. Aborting.");
      alert(currentLanguage.value === 'vi' ? 'Vui lòng chọn một thiết bị hiện có.' : 'Please select an existing device.');
      console.groupEnd();
      return;
    }
    const selectedDeviceMaster = availableDevices.value.find(d => d.id === modalSelectedDeviceId.value);
    if (!selectedDeviceMaster) {
      console.warn(`  Selected device ID '${modalSelectedDeviceId.value}' not found in availableDevices. Aborting.`);
      console.groupEnd();
      return;
    }

    // Find if this device was already on the grid to carry over its existing details
    const existingDeviceOnAnyCell = deviceDataStream.value.find(d => d.id === selectedDeviceMaster.id);

    newGridDeviceData = {
      id: selectedDeviceMaster.id,
      device_name: selectedDeviceMaster.name,
      coordinates: {row, col},
      installation_area: existingDeviceOnAnyCell?.installation_area || modalCellData.value.device?.installation_area || "Default Assigned Area",
      mac_address: existingDeviceOnAnyCell?.mac_address, // Keep original MAC if exists
      wifi_ssid: existingDeviceOnAnyCell?.wifi_ssid || "FACTORY_WIFI_ASSIGNED",
      firmware_version: existingDeviceOnAnyCell?.firmware_version || "1.x.x",
      last_event: existingDeviceOnAnyCell?.last_event || {
        type: 'System',
        status: 'Info',
        value: `Device ${selectedDeviceMaster.name} assigned/moved to cell R${row},C${col}`
      },
      scale_at_creation_time: currentScale,
      created_at: existingDeviceOnAnyCell?.created_at || nowISO,
      installed_at: nowISO,
    };
    console.log('  Existing device selected, grid entry prepared/updated:', JSON.parse(JSON.stringify(newGridDeviceData)));
  }

  deviceDataStream.value = deviceDataStream.value.filter(d =>
      !((d.coordinates.row === row && d.coordinates.col === col) || d.id === newGridDeviceData.id)
  );

  deviceDataStream.value.push(newGridDeviceData);

  console.log(`  Device '${newGridDeviceData.device_name}' (ID: ${newGridDeviceData.id}) assignment processed for cell R${row},C${col}.`);
  console.log("  Current deviceDataStream (first 5):", JSON.parse(JSON.stringify(deviceDataStream.value.slice(0, 5), null, 2)));
  closeAndResetModal();
  console.groupEnd();
};

</script>

<style scoped>
.pdf-main-area {
}
</style>
