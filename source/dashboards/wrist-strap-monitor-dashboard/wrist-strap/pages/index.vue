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
        <UButton icon="i-heroicons-bars-3-20-solid" color="gray" variant="ghost" aria-label="Open navigation menu"
                 @click="isMobileMenuOpen = true"/>
      </div>

      <div class="pdf-main-area flex flex-col flex-1 overflow-y-auto">
        <div
            v-if="pdfViewerComponentRef"
            class="pdf-controls-bar sticky top-0 z-10 p-2 flex flex-wrap justify-center items-center gap-x-2 gap-y-1 bg-gray-100 dark:bg-dark-surface border-b dark:border-dark-border shadow-sm shrink-0"
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
              :cell-statuses="cellStatusesForOverlay" @cell-click="handleGridCellClick"
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
              class="text-lg font-semibold text-gray-800 dark:text-dark-text-primary">Wrist Strap Menu</h3>
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
          <div class="flex items-center justify-between"><h3
              class="text-base font-semibold leading-6 text-gray-900 dark:text-white"> Cell Information </h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" class="-my-1"
                     @click="isGridCellModalOpen = false"/>
          </div>
        </template>
        <div v-if="modalCellData" class="p-4">
          <p>You selected cell at: </p>
          <p>Row: {{ modalCellData.row + 1 }}, Column: {{ modalCellData.col + 1 }}</p>
          <p>Device Name: {{ modalCellData.deviceName || 'N/A' }}</p>
          <p class="mt-4">Use this modal to set purposes for this square.</p>
          <p v-if="modalCellData.status" class="mt-2">Device Status: {{ modalCellData.status }}</p>
        </div>
        <div v-else class="p-4"><p>No cell data available.</p></div>
        <template #footer>
          <UButton label="Close" color="gray" @click="isGridCellModalOpen = false"/>
          <UButton label="Save" color="primary" @click="handleSaveCellData"/>
        </template>
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import {ref, computed, watch, onMounted, nextTick } from 'vue';
// import {useLanguage} from '~/composables/useLanguage'; // Assuming this is project-specific
import PdfViewer from '~/components/pdf/PdfViewer.vue';
import GridOverlay from '~/components/interactive/GridOverlay.vue';

type InteractionMode = 'pan' | 'select';

interface GridCellDeviceData {
  name: string;
  row: number;    // Grid row index (NOW 1-based in JSON)
  col: number;    // Grid column index (NOW 1-based in JSON)
  status: 'connected' | 'error' | 'disconnected' | 'warning';
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

// Mocking useLanguage for standalone example
const useLanguage = () => ({ currentLanguage: ref('en') });
const {currentLanguage} = useLanguage ? useLanguage() : {currentLanguage: ref('en')};


const isMobileMenuOpen = ref(false);
const pdfViewerComponentRef = ref<PdfViewerExposed | null>(null);
const isPdfCurrentlyPanning = ref(false);
const zoomInputPercentage = ref(100);
const currentPageInput = ref(1);
const totalPagesForPdf = ref(0);

const isPanMode = ref(true);
const interactionMode = computed<InteractionMode>(() => isPanMode.value ? 'pan' : 'select');

const viewModeBaseLabel = computed(() => currentLanguage.value === 'vi' ? 'Chế độ xem' : 'View Mode');
const currentInteractionModeLabel = computed(() => {
  return interactionMode.value === 'pan' ? (currentLanguage.value === 'vi' ? 'Vuốt bản đồ' : 'Pan Map') : (currentLanguage.value === 'vi' ? 'Chọn khu vực' : 'Select Area');
});
const interactionModeToggleAriaLabel = computed(() => {
  return isPanMode.value ? (currentLanguage.value === 'vi' ? 'Chuyển sang Chọn khu vực' : 'Switch to Select Area Mode') : (currentLanguage.value === 'vi' ? 'Chuyển sang Vuốt bản đồ' : 'Switch to Pan Map Mode');
});
const scaleLabel = computed(() => currentLanguage.value === 'vi' ? 'Tỉ lệ thu phóng' : 'Scale');
const pageLabel = computed(() => currentLanguage.value === 'vi' ? 'Trang' : 'Page');
const renderLabel = computed(() => currentLanguage.value === 'vi' ? 'Kết xuất' : 'Render');

const minZoomPercentage = computed(() => pdfViewerComponentRef.value ? Math.round(pdfViewerComponentRef.value.minScale * 100) : 20);
const maxZoomPercentage = computed(() => pdfViewerComponentRef.value ? Math.round(pdfViewerComponentRef.value.maxScale * 100) : 500);
const zoomInLabel = computed(() => currentLanguage.value === 'vi' ? 'Phóng to' : 'Zoom In');
const zoomOutLabel = computed(() => currentLanguage.value === 'vi' ? 'Thu nhỏ' : 'Zoom Out');
const resetViewLabel = computed(() => currentLanguage.value === 'vi' ? 'Đặt lại' : 'Reset View');

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
  { id: 'home', label_en: 'Home', label_vi: 'Trang chủ', icon: 'i-heroicons-home-solid', to: '/' },
  { id: 'device-list', label_en: 'Device List', label_vi: 'Danh sách thiết bị', icon: 'i-heroicons-queue-list-solid', to: '/device-list'},
  { id: 'device-management', label_en: 'Device Management', label_vi: 'Quản lý thiết bị', icon: 'i-heroicons-cog-8-tooth-solid', to: '/device-management'},
  { id: 'production-plan', label_en: 'Production Plan\n& Working Time', label_vi: 'Kế hoạch & Thời gian\nsản xuất', icon: 'i-heroicons-calendar-days-solid', to: '/production-plan'},
  { id: 'data-visualization', label_en: 'Data Visualization', label_vi: 'Trực quan hóa dữ liệu', icon: 'i-heroicons-chart-pie-solid', to: '/data-visualization'},
  { id: 'data-analysis', label_en: 'Data Analysis', label_vi: 'Phân tích dữ liệu', icon: 'i-heroicons-presentation-chart-line-solid', to: '/data-analysis'},
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
const modalCellData = ref<{ id: string; row: number; col: number; status?: string; deviceName?: string } | null>(null);


// MODIFIED: deviceDataStreamJson now uses 1-based indexing for row and col
const deviceDataStreamJson = `[
  { "name": "device_cell_1_1", "row": 1, "col": 1, "status": "connected" },
  { "name": "device_cell_1_2", "row": 1, "col": 2, "status": "disconnected" },
  { "name": "device_cell_2_1", "row": 2, "col": 1, "status": "warning" },
  { "name": "device_cell_2_2", "row": 2, "col": 2, "status": "connected" },
  { "name": "device_cell_6_6_error", "row": 6, "col": 6, "status": "error" }
]`;

const deviceDataStream = ref<GridCellDeviceData[]>([]);

onMounted(() => {
  console.log("[index.vue/onMounted] Component mounted.");
  console.log("--- Device Data Stream JSON (1-based Grid Coords) ---");
  console.log(deviceDataStreamJson);
  try {
    deviceDataStream.value = JSON.parse(deviceDataStreamJson);
    console.log("--- Parsed Device Data Stream (1-based Grid Coords) ---");
    console.log(JSON.stringify(deviceDataStream.value, null, 2));
  } catch (e) {
    console.error("Failed to parse deviceDataStreamJson:", e);
  }
  console.log("-----------------------------------------------------------");
});


const computedGridOverlayProps = computed(() => {
  const viewer = pdfViewerComponentRef.value;
  if (!viewer || typeof viewer.getCanvasActualWidth !== 'function' || typeof viewer.getCanvasActualHeight !== 'function' ||
      typeof viewer.getCanvasPanX !== 'function' || typeof viewer.getCanvasPanY !== 'function') {
    return {
      visible: false, x: 0, y: 0, width: 0, height: 0, rows: 0, cols: 0, cellWidth: BASE_CELL_SIZE_PX, cellHeight: BASE_CELL_SIZE_PX
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
      visible: false, x: 0, y: 0, width: 0, height: 0, rows: 0, cols: 0, cellWidth: BASE_CELL_SIZE_PX, cellHeight: BASE_CELL_SIZE_PX
    };
  }
  const cols = Math.max(0,Math.floor(actualWidthVal / BASE_CELL_SIZE_PX));
  const rows = Math.max(0,Math.floor(actualHeightVal / BASE_CELL_SIZE_PX));
  if (cols <= 0 || rows <= 0) {
    return {
      visible: false, x: panXVal, y: panYVal, width: actualWidthVal, height: actualHeightVal, rows: 0, cols: 0, cellWidth: BASE_CELL_SIZE_PX, cellHeight: BASE_CELL_SIZE_PX
    };
  }
  return {
    visible: true, x: panXVal, y: panYVal, width: actualWidthVal, height: actualHeightVal, rows: rows, cols: cols, cellWidth: BASE_CELL_SIZE_PX, cellHeight: BASE_CELL_SIZE_PX
  };
});

// MODIFIED: cellStatusesForOverlay to handle 1-based JSON data
const cellStatusesForOverlay = computed(() => {
  const statuses: Record<string, { status: string, deviceId: string, deviceName: string }> = {};
  const priorities: Record<string, number> = { error: 4, disconnected: 3, warning: 2, connected: 1 };

  const gridProps = computedGridOverlayProps.value;
  if (!gridProps.visible || gridProps.rows === 0 || gridProps.cols === 0) {
    return {};
  }

  console.log(`\n--- [cellStatusesForOverlay - Modified for 1-based JSON] Processing ---`);
  console.log(`   Visible Grid Dimensions: ${gridProps.rows} Rows, ${gridProps.cols} Cols`);

  for (const device of deviceDataStream.value) {
    // device.row and device.col are now 1-based from JSON
    const oneBasedRow = device.row;
    const oneBasedCol = device.col;
    const status = device.status;
    const name = device.name;

    // Validate 1-based row/col from data
    if (typeof oneBasedRow !== 'number' || typeof oneBasedCol !== 'number' || oneBasedRow < 1 || oneBasedCol < 1) {
      console.warn(`  [Device: ${name}] Invalid 1-based row/col in data: R${oneBasedRow},C${oneBasedCol}. Skipping.`);
      continue;
    }

    // Convert to 0-based for internal keying and boundary checks
    const zeroBasedRow = oneBasedRow - 1;
    const zeroBasedCol = oneBasedCol - 1;

    console.log(`  Device: ${name}, JSON Coords (1-based): (R:${oneBasedRow}, C:${oneBasedCol}), Status: ${status}`);
    console.log(`    Converted to 0-based for internal use: (R:${zeroBasedRow}, C:${zeroBasedCol})`);


    // Check if the 0-based row/col is within the currently VISIBLE grid dimensions
    if (zeroBasedCol < gridProps.cols && zeroBasedRow < gridProps.rows) {
      const key = `${zeroBasedRow}-${zeroBasedCol}`; // Key is 0-based
      const existingEntry = statuses[key];
      const newPriority = priorities[status as keyof typeof priorities] || 0;
      const existingPriority = existingEntry ? (priorities[existingEntry.status as keyof typeof priorities] || 0) : 0;

      if (newPriority >= existingPriority) {
        statuses[key] = { status: status, deviceId: name, deviceName: name };
        console.log(`    -> Grid Cell (0-based key) ${key} UPDATED by Device '${name}' with status '${status}'.`);
      } else {
        console.log(`    -> Grid Cell (0-based key) ${key} NOT updated. Existing status '${existingEntry.status}' from '${existingEntry.deviceName}' has higher priority.`);
      }
    } else {
      console.log(`    -> Device '${name}' (defined for 0-based R${zeroBasedRow},C${zeroBasedCol}) is OUTSIDE current visible grid (Max 0-based R${gridProps.rows -1}, C${gridProps.cols -1}).`);
    }
  }
  console.log("--- [cellStatusesForOverlay - Modified for 1-based JSON] Finished. Statuses generated:", Object.keys(statuses).length > 0 ? JSON.stringify(statuses) : "None");
  return statuses;
});


const handleGridCellClick = (cell: { row: number; col: number; }) => { // cell is 0-based from GridOverlay
  if (interactionMode.value !== 'select') return;
  if (isPdfCurrentlyPanning.value) return;

  const zeroBasedCellKey = `${cell.row}-${cell.col}`; // cell.row and cell.col are 0-based
  console.log(`[index.vue/handleGridCellClick] Clicked cell (0-based from event): R${cell.row},C${cell.col}. Key: ${zeroBasedCellKey}.`);
  const statusInfo = cellStatusesForOverlay.value[zeroBasedCellKey];
  console.log(`[index.vue/handleGridCellClick] StatusInfo for key '${zeroBasedCellKey}':`, statusInfo ? JSON.parse(JSON.stringify(statusInfo)) : 'undefined');


  if (selectedGridCell.value?.row === cell.row && selectedGridCell.value?.col === cell.col) {
    selectedGridCell.value = null;
    isGridCellModalOpen.value = false;
  } else {
    selectedGridCell.value = cell; // Store 0-based row/col
    modalCellData.value = {
      id: statusInfo?.deviceId || `cell_R${cell.row + 1}_C${cell.col + 1}`, // Use deviceId or generate a 1-based ID for display
      row: cell.row, // Store 0-based row for internal consistency if needed elsewhere
      col: cell.col, // Store 0-based col
      status: statusInfo?.status,
      deviceName: statusInfo?.deviceName
    };
    console.log('[index.vue/handleGridCellClick] Modal data set to:', JSON.parse(JSON.stringify(modalCellData.value)));
    isGridCellModalOpen.value = true;
  }
};

const handleSaveCellData = () => {
  if (modalCellData.value) {
    console.log('Saving cell data:', modalCellData.value);
  }
  isGridCellModalOpen.value = false;
};

// useHead({ title: 'Factory Layout (PDF) - Wrist Strap Dashboard | IoT Hub', meta: [ {name: 'description', content: 'Interactive overview of the factory production layout using PDF with grid overlay.'} ] });

</script>

<style scoped>
.pdf-main-area {
}
</style>
