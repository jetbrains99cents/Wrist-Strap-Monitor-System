<template>
  <div class="flex flex-1 min-h-0 overflow-hidden">
    <aside
        class="hidden md:flex md:flex-col bg-gray-100 dark:bg-dark-surface border-r border-ray-200 dark:border-dark-border p-4 w-60 lg:w-64 overflow-y-auto shrink-0"
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
          <div class="flex items-center gap-2">
            <UToggle v-model="isPanMode" on-icon="i-heroicons-arrows-pointing-out-20-solid"
                     off-icon="i-heroicons-cursor-arrow-rays-20-solid" :aria-label="interactionModeToggleAriaLabel"/>
            <span class="text-xs text-gray-500 dark:text-gray-400 hidden sm:inline">{{ shiftToSwitchLabel }}</span>
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
          <UButton size="sm" @click="handleResetView"
                   :disabled="pdfViewerComponentRef?.isRendering?.value">
            <UIcon name="i-heroicons-arrows-pointing-out-20-solid" class="h-4 w-4 mr-1"/>
            {{ resetViewLabel }}
          </UButton>
          <div class="flex items-center gap-1 text-xs text-gray-600 dark:text-gray-400">
            <span>{{ scaleLabel }}:</span>
            <UInput v-model.number="zoomInputPercentage" type="number" size="xs" class="w-20 text-center"
                    @change="applyManualZoomToViewer" @keyup.enter="applyManualZoomToViewer" :min="minZoomPercentage"
                    :disabled="pdfViewerComponentRef?.isRendering?.value"/>
            <span>%</span>
          </div>
          <UButtonGroup size="xs" orientation="horizontal">
            <UButton label="100%" @click="setQuickZoom(100)"
                     :variant="zoomInputPercentage === 100 ? 'solid' : 'outline'"/>
            <UButton label="200%" @click="setQuickZoom(200)"
                     :variant="zoomInputPercentage === 200 ? 'solid' : 'outline'"/>
            <UButton label="300%" @click="setQuickZoom(300)"
                     :variant="zoomInputPercentage === 300 ? 'solid' : 'outline'"/>
            <UButton label="400%" @click="setQuickZoom(400)"
                     :variant="zoomInputPercentage === 400 ? 'solid' : 'outline'"/>
            <UButton label="500%" @click="setQuickZoom(500)"
                     :variant="zoomInputPercentage === 500 ? 'solid' : 'outline'"/>
            <UButton label="800%" @click="setQuickZoom(800)"
                     :variant="zoomInputPercentage === 800 ? 'solid' : 'outline'"/>
            <UButton label="1000%" @click="setQuickZoom(1000)"
                     :variant="zoomInputPercentage === 1000 ? 'solid' : 'outline'"/>
            <UButton label="1200%" @click="setQuickZoom(1200)"
                     :variant="zoomInputPercentage === 1200 ? 'solid' : 'outline'"/>
            <UButton label="1600%" @click="setQuickZoom(1600)"
                     :variant="zoomInputPercentage === 1600 ? 'solid' : 'outline'"/>
          </UButtonGroup>

          <span v-if="pdfViewerComponentRef?.totalPages?.value > 1"
                class="text-xs text-gray-600 dark:text-gray-400 ml-2"> {{
              pageLabel
            }}: {{ pdfViewerComponentRef?.currentPageNum?.value }} / {{
              pdfViewerComponentRef?.totalPages?.value
            }} </span>
          <span
              v-if="pdfViewerComponentRef?.currentScale?.value && Number.isFinite(pdfViewerComponentRef.currentScale.value)"
              class="text-xs text-gray-500 dark:text-gray-400 hidden sm:inline ml-2"> {{
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
              @scale-updated="handlePdfScaleUpdated"/>
          <GridOverlay
              v-if="computedGridOverlayProps.visible"
              :rows="computedGridOverlayProps.rows"
              :cols="computedGridOverlayProps.cols"
              :cell-width="computedGridOverlayProps.cellWidth"
              :cell-height="computedGridOverlayProps.cellHeight"
              :selected-cell="selectedGridCell"
              :is-pdf-panning="isPdfCurrentlyPanning"
              :interaction-mode="interactionMode"
              :cell-statuses="cellStatusesForOverlay as any"
              @cell-click="handleGridCellClick"
              @cell-mouse-enter="handleCellMouseEnter"
              @cell-mouse-leave="handleCellMouseLeave"
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
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid"
                     @click="isMobileMenuOpen = false"/>
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
              <span class="dark:text-white font-semibold">{{ modalCellData.device.name }}</span>
              <span class="text-gray-600 dark:text-gray-400 text-left font-medium">{{ modalDeviceAreaLabel }}:</span>
              <span class="dark:text-white">{{ modalCellData.device.installation_area }}</span>
              <span class="text-gray-600 dark:text-gray-400 text-left font-medium">{{
                  modalDeviceLastEventStatusLabel
                }}:</span> <span class="dark:text-white">{{
                getLocalizedStatus(modalCellData.device.last_event?.status)
              }}</span>
              <span class="text-gray-600 dark:text-gray-400 text-left font-medium">{{ modalLastEventTypeLabel }}:</span>
              <span class="dark:text-white">{{ modalCellData.device.last_event?.type || 'N/A' }}</span>
              <span class="text-gray-600 dark:text-gray-400 text-left font-medium">{{
                  modalFirmwareVersionLabel
                }}:</span> <span class="dark:text-white">{{ modalCellData.device.firmware_version || 'N/A' }}</span>
              <span class="text-gray-600 dark:text-gray-400 text-left font-medium">{{
                  modalScaleAtCreationLabel
                }}:</span> <span class="dark:text-white">{{
                modalCellData.device.scale_at_creation_time ? modalCellData.device.scale_at_creation_time.toFixed(1) + 'x' : 'N/A'
              }}</span>
              <span class="text-gray-600 dark:text-gray-400 text-left font-medium">{{ modalCreatedAtLabel }}:</span>
              <span class="dark:text-white">{{ formatDateForDisplay(modalCellData.device.createdAt) }}</span>
              <span class="text-gray-600 dark:text-gray-400 text-left font-medium">{{ modalInstalledAtLabel }}:</span>
              <span class="dark:text-white">{{
                  formatDateForDisplay(modalCellData.device.installation_date)
                }}</span>
            </div>
          </template>
          <p v-else class="text-sm text-gray-500 dark:text-gray-400">{{ noDeviceAssignedToCellLabel }}</p>

          <UDivider :ui="{border: {base: 'border-gray-200 dark:border-gray-700'}}"/>

          <div v-if="!isCreatingNewDeviceInModal">
            <div class="flex justify-between items-center mb-2">
              <label for="existing-device-select"
                     class="block text-sm font-medium text-gray-700 dark:text-gray-200">{{
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
                <span v-else class="text-sm text-gray-400 dark:text-gray-500">{{
                    selectDevicePlaceholderLabel
                  }}</span>
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
                  value-attribute="value"
                  option-attribute="label"
                  :placeholder="selectAreaPlaceholderLabel"
                  searchable
                  size="md"
              />
            </UFormGroup>
            <UFormGroup :label="newDeviceMacAddressLabel" name="newDeviceMacAddress"
                        :ui="{label: { base: 'text-sm' }}">
              <UInput v-model="newDeviceForm.mac_address" :placeholder="newDeviceMacAddressPlaceholderLabel"
                      size="md"/>
            </UFormGroup>
            <UFormGroup :label="newDeviceFirmwareVersionLabel" name="newDeviceFirmwareVersion"
                        :ui="{label: { base: 'text-sm' }}">
              <UInput v-model="newDeviceForm.firmware_version" :placeholder="newDeviceFirmwareVersionPlaceholderLabel"
                      size="md"/>
            </UFormGroup>
          </div>

        </div>
        <div v-else class="p-4">
          <p class="text-sm">{{ noCellDataAvailableLabel }}</p>
        </div>

        <template #footer>
          <div class="flex justify-between items-center w-full">
            <UButton :label="closeButtonLabel" color="gray" variant="outline" @click="closeAndResetModal"/>

            <div class="flex items-center gap-x-2">
              <UButton
                  v-if="modalCellData && modalCellData.device"
                  :label="removeAssignmentButtonLabel"
                  color="red"
                  variant="solid"
                  @click="handleRemoveAssignment"
                  :loading="isSaving"
              />
              <UButton
                  :label="saveAssignmentButtonLabel"
                  color="primary"
                  @click="handleSaveCellAssignment"
                  :loading="isSaving"
              />
            </div>
          </div>
        </template>
      </UCard>
    </UModal>

  </div>
</template>

<script setup lang="ts">
import {ref, computed, onMounted, nextTick, onUnmounted, watch} from 'vue'; // Added watch
import {useLanguage} from '~/composables/useLanguage';
import {useLogger} from '~/composables/useLogger';
import PdfViewer from '~/components/pdf/PdfViewer.vue';
// The import is simplified back to the default, as we can no longer import types
import GridOverlay from '~/components/interactive/GridOverlay.vue';
import {definePageMeta, useNuxtApp, useRuntimeConfig, useToast} from "#imports";
import {useDeviceRealtimeStore} from '~/stores/deviceRealtime';

definePageMeta({
  middleware: 'auth'
});

// SECTION: Type Definitions (Local to this file)
// These types are defined here to match the structure of the types in GridOverlay.vue
type InteractionMode = 'pan' | 'select';

type LogStatus =
    "Connected"
    | "Disconnected"
    | "Voltage reading ok"
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
  status?: LogStatus | null;
  timestamp: number;
  value: string | Record<string, any> | number;
}

interface DeviceData {
  id: string;
  name: string;
  coordinates: { row: number; col: number } | null;
  installation_area: string;
  mac_address?: string;
  device_type: string;
  firmware_version?: string;
  last_event: EventDetails | null;
  scale_at_creation_time: number | null;
  createdAt: string;
  installation_date: string;
  updatedAt: string;
}

interface GridCellStatus {
  status: LogStatus;
  deviceId: string;
  deviceName: string;
  color: string; // <-- ADD THIS LINE
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
// !SECTION

// SECTION: Composables and Basic Refs
const logger = useLogger();
const {currentLanguage} = useLanguage();
const runtimeConfig = useRuntimeConfig();
const toast = useToast();
const {$api} = useNuxtApp();
const deviceRealtimeStore = useDeviceRealtimeStore();

const isMobileMenuOpen = ref(false);
const isSaving = ref(false);
// !SECTION

// SECTION: PDF Viewer State
const pdfViewerComponentRef = ref<PdfViewerExposed | null>(null);
const isPdfCurrentlyPanning = ref(false);
const zoomInputPercentage = ref(100);
const isPanMode = ref(true);
const interactionMode = computed<InteractionMode>(() => isPanMode.value ? 'pan' : 'select');
// !SECTION

// SECTION: i18n Computed Labels
const shiftToSwitchLabel = computed(() => currentLanguage.value === 'vi' ? '(Nhấn Shift để chuyển chế độ xem)' : '(Hold Shift to switch)');
const openMenuAriaLabel = computed(() => currentLanguage.value === 'vi' ? 'Mở menu điều hướng' : 'Open navigation menu');
const mobileMenuTitleLabel = computed(() => currentLanguage.value === 'vi' ? 'Menu bản đồ' : 'Map menu');
const viewModeBaseLabel = computed(() => currentLanguage.value === 'vi' ? 'Chế độ xem' : 'View mode');
const currentInteractionModeLabel = computed(() => interactionMode.value === 'pan' ? (currentLanguage.value === 'vi' ? 'Kéo bản đồ' : 'Pan map') : (currentLanguage.value === 'vi' ? 'Chọn ô' : 'Select cell'));
const interactionModeToggleAriaLabel = computed(() => isPanMode.value ? (currentLanguage.value === 'vi' ? 'Chuyển sang chế độ chọn ô' : 'Switch to select cell mode') : (currentLanguage.value === 'vi' ? 'Chuyển sang sang chế độ kéo bản đồ' : 'Switch to pan map mode'));
const scaleLabel = computed(() => currentLanguage.value === 'vi' ? 'Tỉ lệ' : 'Scale');
const pageLabel = computed(() => currentLanguage.value === 'vi' ? 'Trang' : 'Page');
const renderLabel = computed(() => currentLanguage.value === 'vi' ? 'Kết xuất' : 'Render');
const zoomInLabel = computed(() => currentLanguage.value === 'vi' ? 'Phóng to' : 'Zoom in');
const zoomOutLabel = computed(() => currentLanguage.value === 'vi' ? 'Thu nhỏ' : 'Zoom out');
const resetViewLabel = computed(() => currentLanguage.value === 'vi' ? 'Đặt lại chế độ xem' : 'Reset view');
const cellAssignmentModalTitleLabel = computed(() => currentLanguage.value === 'vi' ? 'Thông tin & Gán thiết bị cho Ô' : 'Cell Information & Device Assignment');
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
const newDeviceMacAddressLabel = computed(() => currentLanguage.value === 'vi' ? 'Địa chỉ MAC' : 'MAC Address');
const newDeviceMacAddressPlaceholderLabel = computed(() => currentLanguage.value === 'vi' ? 'Ví dụ: AA:BB:CC:DD:EE:FF' : 'Example: AA:BB:CC:DD:EE:FF');
const newDeviceFirmwareVersionLabel = computed(() => currentLanguage.value === 'vi' ? 'Phiên bản Firmware' : 'Firmware Version');
const newDeviceFirmwareVersionPlaceholderLabel = computed(() => currentLanguage.value === 'vi' ? 'Ví dụ: 1.0.0' : 'Example: 1.0.0');
const noCellDataAvailableLabel = computed(() => currentLanguage.value === 'vi' ? 'Không có dữ liệu ô.' : 'No cell data available.');
const closeButtonLabel = computed(() => currentLanguage.value === 'vi' ? 'Đóng' : 'Close');
const saveAssignmentButtonLabel = computed(() => currentLanguage.value === 'vi' ? 'Lưu gán' : 'Save assignment');
const removeAssignmentButtonLabel = computed(() => currentLanguage.value === 'vi' ? 'Xóa Gán' : 'Remove Assignment');
const modalDeviceLastEventStatusLabel = computed(() => currentLanguage.value === 'vi' ? 'Trạng thái sự kiện cuối' : 'Last event status');
const modalFirmwareVersionLabel = computed(() => currentLanguage.value === 'vi' ? 'Phiên bản Firmware' : 'Firmware version');
const modalScaleAtCreationLabel = computed(() => currentLanguage.value === 'vi' ? 'Tỉ lệ khi tạo' : 'Scale at creation');
const modalCreatedAtLabel = computed(() => currentLanguage.value === 'vi' ? 'Ngày tạo' : 'Created at');
const modalInstalledAtLabel = computed(() => currentLanguage.value === 'vi' ? 'Ngày lắp đặt' : 'Installed at');
const modalLastEventTypeLabel = computed(() => currentLanguage.value === 'vi' ? 'Loại sự kiện cuối' : 'Last event type');
const noDeviceAssignedToCellLabel = computed(() => currentLanguage.value === 'vi' ? 'Chưa có thiết bị nào được gán cho ô này.' : 'No device assigned to this cell.');
const selectedCellInfoLabel = computed(() => currentLanguage.value === 'vi' ? 'Thông tin ô đã chọn' : 'Selected cell info');
const modalDeviceNameLabel = computed(() => currentLanguage.value === 'vi' ? 'Tên thiết bị' : 'Device name');
const modalDeviceAreaLabel = computed(() => currentLanguage.value === 'vi' ? 'Khu vực lắp đặt' : 'Installation area');
const tooltipNameLabel = computed(() => currentLanguage.value === 'vi' ? 'Tên' : 'Name');
const tooltipAreaLabel = computed(() => currentLanguage.value === 'vi' ? 'Khu vực' : 'Area');
const tooltipLastEventStatusLabel = computed(() => currentLanguage.value === 'vi' ? 'Trạng thái sự kiện cuối' : 'Last Event Status');
const tooltipLastEventTypeLabel = computed(() => currentLanguage.value === 'vi' ? 'Loại sự kiện cuối' : 'Last Event Type');
const tooltipCreatedAtLabel = computed(() => currentLanguage.value === 'vi' ? 'Ngày tạo' : 'Created At');
const tooltipInstalledAtLabel = computed(() => currentLanguage.value === 'vi' ? 'Ngày lắp đặt' : 'Installed At');
const tooltipCellLabel = computed(() => currentLanguage.value === 'vi' ? 'Ô' : 'Cell');
// !SECTION

// SECTION: PDF Control Handlers
const minZoomPercentage = computed(() => pdfViewerComponentRef.value ? Math.round(pdfViewerComponentRef.value.minScale * 100) : 20);

const applyManualZoomToViewer = () => {
  const viewer = pdfViewerComponentRef.value;
  if (!viewer) return;
  const currentZoomInputVal = zoomInputPercentage.value;
  if (isNaN(currentZoomInputVal)) return;
  const newScale = Math.max(viewer.minScale, Math.min(currentZoomInputVal / 100, viewer.maxScale));
  if (Number.isFinite(newScale) && newScale > 0) {
    viewer.setPdfScale(newScale);
  }
};

const setQuickZoom = (percentage: number) => {
  if (pdfViewerComponentRef.value) {
    const scale = percentage / 100;
    pdfViewerComponentRef.value.setPdfScale(scale);
  }
};

const handleResetView = () => {
  pdfViewerComponentRef.value?.resetZoomAndPan();
};

const handlePdfRendered = () => logger.log('[index.vue] PDF Page Rendered');
const handlePdfLoaded = async () => {
  logger.log('[index.vue] PDF Loaded event received.');
  await nextTick();
  if (pdfViewerComponentRef.value) {
    handlePdfScaleUpdated(pdfViewerComponentRef.value.currentScale.value);
  }
};

const handlePdfScaleUpdated = (newScale: number) => {
  logger.log(`[index.vue] Received 'scale-updated' event with scale: ${newScale}`);
  if (typeof newScale === 'number' && Number.isFinite(newScale) && newScale > 0) {
    const newPercentage = Math.round(newScale * 100);
    if (newPercentage !== zoomInputPercentage.value) {
      zoomInputPercentage.value = newPercentage;
    }
  }
};
// !SECTION

// SECTION: Navigation Items
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
// !SECTION

// SECTION: Grid and Modal State
const pdfViewAndGridAreaRef = ref<HTMLElement | null>(null);
const BASE_CELL_SIZE_PX = 50;
const selectedGridCell = ref<{ row: number; col: number } | null>(null);
const isGridCellModalOpen = ref(false);
const modalCellData = ref<ModalDisplayData | null>(null);
const isCreatingNewDeviceInModal = ref(false);
const modalSelectedDeviceId = ref<string | undefined>(undefined);

const newDeviceForm = ref({
  name: '',
  installation_area: undefined as string | undefined,
  mac_address: '',
  firmware_version: ''
});

const deviceDataStream = ref<DeviceData[]>([]);
const availableDevices = computed<SelectableDevice[]>(() =>
    deviceDataStream.value.map(d => ({id: d.id, name: d.name})).sort((a, b) => a.name.localeCompare(b.name))
);
const availableInstallationAreas = ref<string[]>(runtimeConfig.public.installationAreas);
const areaOptionsForModal = computed(() => availableInstallationAreas.value.map(area => ({label: area, value: area})));
const availableDeviceOptionsForModal = computed(() => availableDevices.value);
// !SECTION

// SECTION: Utility and Formatting Functions
const formatDateForDisplay = (isoString: string): string => {
  if (!isoString) return 'N/A';
  try {
    return new Date(isoString).toLocaleDateString(currentLanguage.value === 'vi' ? 'vi-VN' : 'en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  } catch (e) {
    return 'Invalid Date';
  }
};

const formatDateForTooltip = (isoString: string): string => {
  if (!isoString) return 'N/A';
  try {
    return new Date(isoString).toLocaleDateString(currentLanguage.value === 'vi' ? 'vi-VN' : 'en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (e) {
    return 'Invalid Date';
  }
};

const getLocalizedStatus = (status?: LogStatus | null): string => {
  if (!status) return 'N/A';
  if (currentLanguage.value === 'vi') {
    const statusMap: Record<LogStatus, string> = {
      "Connected": "Đã kết nối",
      "Disconnected": "Mất kết nối",
      "Voltage reading ok": "Đọc điện áp OK",
      "Voltage reading failed": "Lỗi đọc điện áp",
      "Info": "Thông tin",
      "Warning": "Cảnh báo",
      "Error": "Lỗi",
      "Critical": "Nghiêm trọng",
      "Configured": "Đã cấu hình",
      "Reset": "Đã đặt lại"
    };
    return statusMap[status] || status;
  }
  return status;
};
// !SECTION


// SECTION: API Interaction
const fetchAndSetDevices = async () => {
  try {
    logger.log('[API] Fetching devices...');
    const response = await $api<any[]>('/api/v1/devices/');
    deviceDataStream.value = response.map((device: any): DeviceData => ({
      id: device._id,
      name: device.name,
      coordinates: device.coordinates,
      installation_area: device.installation_area,
      mac_address: device.mac_address,
      device_type: device.device_type,
      firmware_version: device.firmware_version,
      last_event: device.last_event,
      scale_at_creation_time: device.scale_at_creation_time,
      createdAt: device.createdAt,
      installation_date: device.installation_date,
      updatedAt: device.updatedAt,
    }));
    logger.log(`[API] Successfully fetched and mapped ${deviceDataStream.value.length} devices.`);
  } catch (error: any) {
    logger.error('[API] Failed to fetch devices:', error);
    toast.add({
      title: 'API Error',
      description: 'Could not fetch device data from the server.',
      color: 'red',
      icon: 'i-heroicons-x-circle'
    });
  }
};
// !SECTION


// SECTION: Lifecycle Hooks and Event Listeners
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Shift' && !event.repeat) {
    const target = event.target as HTMLElement;
    if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA' && !target.isContentEditable) {
      event.preventDefault();
      isPanMode.value = !isPanMode.value;
    }
  }
};

onMounted(async () => {
  logger.log('[index.vue] Initializing real-time listeners...');
  deviceRealtimeStore.initRealtimeListeners();

  await fetchAndSetDevices();
  window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  logger.log('[index.vue] Cleaning up real-time listeners...');
  deviceRealtimeStore.cleanupRealtimeListeners();

  window.removeEventListener('keydown', handleKeydown);
});
// !SECTION


// SECTION: Grid Overlay and Tooltip Logic
const computedGridOverlayProps = computed(() => {
  const viewer = pdfViewerComponentRef.value;
  if (!viewer) return {
    visible: false,
    x: 0,
    y: 0,
    width: 0,
    height: 0,
    rows: 0,
    cols: 0,
    cellWidth: 50,
    cellHeight: 50
  };
  const panXVal = viewer.getCanvasPanX();
  const panYVal = viewer.getCanvasPanY();
  const actualWidthVal = viewer.getCanvasActualWidth();
  const actualHeightVal = viewer.getCanvasActualHeight();
  if (!Number.isFinite(actualWidthVal) || actualWidthVal <= 0 || !Number.isFinite(actualHeightVal) || actualHeightVal <= 0) {
    return {
      visible: false,
      x: panXVal,
      y: panYVal,
      width: 0,
      height: 0,
      rows: 0,
      cols: 0,
      cellWidth: 50,
      cellHeight: 50
    };
  }
  const cols = Math.max(0, Math.floor(actualWidthVal / BASE_CELL_SIZE_PX));
  const rows = Math.max(0, Math.floor(actualHeightVal / BASE_CELL_SIZE_PX));
  return {
    visible: true,
    x: panXVal,
    y: panYVal,
    width: actualWidthVal,
    height: actualHeightVal,
    rows,
    cols,
    cellWidth: BASE_CELL_SIZE_PX,
    cellHeight: BASE_CELL_SIZE_PX
  };
});

const cellStatusesForOverlay = computed((): Record<string, GridCellStatus> => {
  logger.log('[Reactivity] `cellStatusesForOverlay` is re-computing...');

  const statuses: Record<string, GridCellStatus> = {};
  const gridProps = computedGridOverlayProps.value;
  const realtimeSnapshots = deviceRealtimeStore.latestDeviceSnapshots;

  // Get the color map from your nuxt.config.ts
  const colorMap = runtimeConfig.public.statusColors as Record<string, string>;

  if (!gridProps.visible) return {};

  for (const device of deviceDataStream.value) {
    if (device.coordinates) {
      const {row, col} = device.coordinates;
      if (row >= 0 && col >= 0 && row < gridProps.rows && col < gridProps.cols) {
        const key = `${row}-${col}`;

        const realtimeSnapshot = realtimeSnapshots.get(device.id);
        const lastEvent = realtimeSnapshot ? realtimeSnapshot.last_event : device.last_event;
        const currentStatus = lastEvent?.status || 'Disconnected';

        statuses[key] = {
          status: currentStatus,
          // Use the map to find the color, defaulting to 'slate' (Unknown) if not found
          color: colorMap[currentStatus] || 'slate', // <-- THIS IS THE KEY CHANGE
          deviceId: device.id,
          deviceName: device.name,
          installationArea: device.installation_area,
          lastEventType: lastEvent?.type,
          createdAtFormatted: formatDateForTooltip(device.createdAt),
          installedAtFormatted: formatDateForTooltip(device.installation_date),
        };
      }
    }
  }
  logger.log(`[Reactivity] Generated ${Object.keys(statuses).length} cell statuses.`);
  return statuses;
});

const sharedTooltipText = ref('');
const sharedTooltipVisible = ref(false);
const sharedTooltipStyle = ref<Record<string, string | number>>({});
let tooltipHideTimeout: ReturnType<typeof setTimeout> | null = null;

const handleCellMouseEnter = (payload: { row: number; col: number; event: MouseEvent }) => {
  if (tooltipHideTimeout) clearTimeout(tooltipHideTimeout);
  const cellKey = `${payload.row}-${payload.col}`;
  const cellData = cellStatusesForOverlay.value[cellKey];
  let text = `${tooltipCellLabel.value}: ${modalRowLabel.value} ${payload.row}, ${modalColLabel.value} ${payload.col}`;
  if (cellData) {
    text = `${tooltipNameLabel.value}: ${cellData.deviceName}`;
    if (cellData.installationArea) text += `\n${tooltipAreaLabel.value}: ${cellData.installationArea}`;
    if (cellData.status) text += `\n${tooltipLastEventStatusLabel.value}: ${getLocalizedStatus(cellData.status)}`;
  }
  sharedTooltipText.value = text;
  sharedTooltipStyle.value = {
    top: `${payload.event.clientY - 10}px`,
    left: `${payload.event.clientX + 15}px`,
    transform: 'translateY(-100%)',
    visibility: 'visible'
  };
  sharedTooltipVisible.value = true;
};

const handleCellMouseLeave = () => {
  tooltipHideTimeout = setTimeout(() => {
    sharedTooltipVisible.value = false;
  }, 100);
};
// !SECTION


// SECTION: Modal and Cell Assignment Logic
const resetModalState = () => {
  isCreatingNewDeviceInModal.value = false;
  modalSelectedDeviceId.value = undefined;
  newDeviceForm.value = {name: '', installation_area: undefined, mac_address: '', firmware_version: ''};
};

const closeAndResetModal = () => {
  isGridCellModalOpen.value = false;
  resetModalState();
};

const handleGridCellClick = (cell: { row: number; col: number; }) => {
  if (interactionMode.value !== 'select' || isPdfCurrentlyPanning.value) return;
  resetModalState();

  // MODIFICATION: Use the computed overlay data to get the most up-to-date device info
  const cellKey = `${cell.row}-${cell.col}`;
  const statusInfo = cellStatusesForOverlay.value[cellKey];
  const deviceId = statusInfo?.deviceId;

  const existingDeviceOnCell = deviceId ? deviceDataStream.value.find(d => d.id === deviceId) : undefined;

  modalCellData.value = {row: cell.row, col: cell.col, device: existingDeviceOnCell};

  if (existingDeviceOnCell) {
    // Also update the device's last_event in the modal with real-time data if available
    const realtimeSnapshot = deviceRealtimeStore.latestDeviceSnapshots.get(existingDeviceOnCell.id);
    if (realtimeSnapshot && modalCellData.value.device) {
      modalCellData.value.device.last_event = realtimeSnapshot.last_event;
    }
    modalSelectedDeviceId.value = existingDeviceOnCell.id;
  }
  isGridCellModalOpen.value = true;
};

const handleRemoveAssignment = async () => {
  const deviceToRemove = modalCellData.value?.device;
  if (!deviceToRemove) {
    toast.add({title: 'Error', description: 'No device is assigned to this cell.', color: 'orange'});
    return;
  }
  logger.log(`[API] Removing assignment for device ID: ${deviceToRemove.id}`);
  isSaving.value = true;
  try {
    await $api(`/api/v1/devices/${deviceToRemove.id}`, {
      method: 'PUT',
      body: {
        coordinates: null,
        scale_at_creation_time: null
      }
    });
    toast.add({title: 'Success', description: `Assignment removed for ${deviceToRemove.name}.`, color: 'green'});
    await fetchAndSetDevices();
    closeAndResetModal();
  } catch (error: any) {
    logger.error(`[API] Failed to remove assignment for device ${deviceToRemove.id}:`, error);
    toast.add({title: 'API Error', description: `Could not remove assignment.`, color: 'red'});
  } finally {
    isSaving.value = false;
  }
};


const handleSaveCellAssignment = async () => {
  logger.log('[Save Assignment] Function initiated.');

  if (!modalCellData.value) {
    logger.error('[Save Assignment] Exit: modalCellData is null.');
    return;
  }
  isSaving.value = true;

  const {row, col} = modalCellData.value;
  const scaleToSave = parseFloat((zoomInputPercentage.value / 100).toFixed(1));

  try {
    if (isCreatingNewDeviceInModal.value) {
      if (!newDeviceForm.value.name.trim() || !newDeviceForm.value.installation_area) {
        toast.add({
          title: 'Validation Error',
          description: 'Device Name and Installation Area are required.',
          color: 'orange'
        });
        logger.warn('[Save Assignment] Exit: New device form is invalid (missing name or area).');
        isSaving.value = false;
        return;
      }

      const payload = {
        name: newDeviceForm.value.name.trim(),
        mac_address: newDeviceForm.value.mac_address.trim() || '00:00:00:00:00:00',
        device_type: "WristStrapMonitorV1",
        installation_area: newDeviceForm.value.installation_area,
        coordinates: {row, col},
        scale_at_creation_time: scaleToSave,
        firmware_version: newDeviceForm.value.firmware_version || "",
        installation_date: new Date().toISOString()
      };

      logger.log('[API] Creating new device with payload:', payload);
      await $api('/api/v1/devices', {method: 'POST', body: payload});
      toast.add({title: 'Success', description: `Device ${payload.name} created and assigned.`, color: 'green'});

    } else {
      const newlySelectedDeviceId = modalSelectedDeviceId.value;
      const deviceCurrentlyOnCell = modalCellData.value.device;

      if (!newlySelectedDeviceId) {
        toast.add({title: 'Error', description: 'No device selected to assign.', color: 'orange'});
        logger.warn('[Save Assignment] Exit: No new device was selected from the dropdown.');
        isSaving.value = false;
        return;
      }
      if (newlySelectedDeviceId === deviceCurrentlyOnCell?.id) {
        toast.add({title: 'Info', description: 'No changes detected.', color: 'blue'});
        logger.log('[Save Assignment] Exit: The selected device is already assigned to this cell. No change needed.');
        isSaving.value = false;
        return;
      }

      if (deviceCurrentlyOnCell) {
        logger.log(`[API] Un-assigning old device: ${deviceCurrentlyOnCell.id}`);
        await $api(`/api/v1/devices/${deviceCurrentlyOnCell.id}`, {
          method: 'PUT',
          body: {coordinates: null, scale_at_creation_time: null}
        });
      }

      logger.log(`[API] Assigning new device: ${newlySelectedDeviceId} to cell R${row},C${col}`);
      await $api(`/api/v1/devices/${newlySelectedDeviceId}`, {
        method: 'PUT',
        body: {coordinates: {row, col}, scale_at_creation_time: scaleToSave}
      });
      const deviceName = availableDevices.value.find(d => d.id === newlySelectedDeviceId)?.name || 'device';
      toast.add({title: 'Success', description: `${deviceName} has been assigned to the cell.`, color: 'green'});
    }

    await fetchAndSetDevices();
    closeAndResetModal();

  } catch (error: any) {
    logger.error('[API] Failed to save cell assignment:', error);
    const errorMsg = error.data?.detail || 'An unknown error occurred.';
    toast.add({title: 'API Error', description: `Could not save assignment: ${errorMsg}`, color: 'red'});
  } finally {
    isSaving.value = false;
  }
};
// !SECTION

// SECTION: Reactivity Debugging
// MODIFICATION: Added a watcher to explicitly log when the real-time store changes.
watch(() => deviceRealtimeStore.latestDeviceSnapshots, (newSnapshots) => {
  logger.log(`[Reactivity] Watcher triggered: Real-time store updated. Total snapshots: ${newSnapshots.size}`);
}, { deep: true });
// !SECTION
</script>

<style scoped>
/* No custom CSS as all styling is done via Tailwind classes */
</style>