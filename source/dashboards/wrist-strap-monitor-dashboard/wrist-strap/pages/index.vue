<template>
  <div class="flex flex-1 min-h-0 overflow-hidden">
    <aside
        class="hidden md:flex md:flex-col bg-gray-100 dark:bg-dark-surface border-r border-gray-200 dark:border-dark-border p-4 w-60 lg:w-64 overflow-y-auto shrink-0"
        aria-label="Desktop Dashboard Navigation"
    >
      <UVerticalNavigation :links="localizedNavigationItems" :ui="{ base: 'group relative flex items-start gap-x-3', padding: 'px-3 py-2.5', label: 'text-base whitespace-pre-line break-words text-left', icon: { base: 'flex-shrink-0 w-5 h-5 mt-0.5' } }" />
    </aside>

    <section class="flex-1 flex flex-col overflow-hidden">
      <div class="md:hidden p-3 sm:p-4 sticky top-0 bg-white dark:bg-dark-bg z-20 border-b dark:border-dark-border">
        <UButton icon="i-heroicons-bars-3-20-solid" color="gray" variant="ghost" aria-label="Open navigation menu" @click="isMobileMenuOpen = true" />
      </div>

      <div class="pdf-main-area flex flex-col flex-1 overflow-y-auto">
        <div
            v-if="pdfViewerComponentRef"
            class="pdf-controls-bar sticky top-0 z-10 p-2 flex flex-wrap justify-center items-center gap-x-2 gap-y-1 bg-gray-100 dark:bg-dark-surface border-b dark:border-dark-border shadow-sm shrink-0"
        >
          <div class="flex items-center gap-1">
            <UToggle v-model="isPanMode" on-icon="i-heroicons-arrows-pointing-out-20-solid" off-icon="i-heroicons-cursor-arrow-rays-20-solid" :aria-label="interactionModeToggleAriaLabel" />
            <span class="text-xs text-gray-600 dark:text-gray-400 whitespace-nowrap"> {{ viewModeBaseLabel }}: {{ currentInteractionModeLabel }} </span>
          </div>
          <UButton size="sm" @click="pdfViewerComponentRef?.zoomIn()" :disabled="pdfViewerComponentRef?.isRendering?.value"> <UIcon name="i-heroicons-magnifying-glass-plus-20-solid" class="h-4 w-4 mr-1" /> {{ zoomInLabel }} </UButton>
          <UButton size="sm" @click="pdfViewerComponentRef?.zoomOut()" :disabled="pdfViewerComponentRef?.isRendering?.value"> <UIcon name="i-heroicons-magnifying-glass-minus-20-solid" class="h-4 w-4 mr-1" /> {{ zoomOutLabel }} </UButton>
          <UButton size="sm" @click="pdfViewerComponentRef?.resetZoomAndPan()" :disabled="pdfViewerComponentRef?.isRendering?.value"> <UIcon name="i-heroicons-arrows-pointing-out-20-solid" class="h-4 w-4 mr-1" /> {{ resetViewLabel }} </UButton>
          <div class="flex items-center gap-1 text-xs text-gray-600 dark:text-gray-400">
            <span>{{ scaleLabel }}:</span> <UInput v-model.number="zoomInputPercentage" type="number" size="xs" class="w-20 text-center" @change="applyManualZoomToViewer" @keyup.enter="applyManualZoomToViewer" :min="minZoomPercentage" :max="maxZoomPercentage" :disabled="pdfViewerComponentRef?.isRendering?.value"/> <span>%</span>
          </div>
          <span v-if="pdfViewerComponentRef?.totalPages?.value > 1" class="text-xs text-gray-600 dark:text-gray-400"> {{ pageLabel }}: {{ pdfViewerComponentRef?.currentPageNum?.value }} / {{ pdfViewerComponentRef?.totalPages?.value }} </span>
          <span v-if="pdfViewerComponentRef?.currentScale?.value && Number.isFinite(pdfViewerComponentRef.currentScale.value)" class="text-xs text-gray-500 dark:text-gray-400 hidden sm:inline"> {{ renderLabel }}: {{ pdfViewerComponentRef.currentScale.value.toFixed(1) }}x </span>
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
                border: '3px solid red',
                boxSizing: 'border-box',
                pointerEvents: 'none',
                zIndex: 10
              }"
              aria-hidden="true"
          />
        </div>
      </div>
    </section>
    <USlideover v-model="isMobileMenuOpen" side="left" :ui="{ width: 'max-w-xs w-full sm:w-72', zIndex: 'z-50' }"> <UCard class="flex flex-col flex-1 h-full" :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800', body: { padding: '', base: 'flex-1 overflow-y-auto' } }"> <template #header> <div class="flex items-center justify-between p-4"> <h3 class="text-lg font-semibold text-gray-800 dark:text-dark-text-primary">Wrist Strap Menu</h3> <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" @click="isMobileMenuOpen = false"/> </div> </template> <div class="p-4"> <UVerticalNavigation :links="localizedNavigationItems" :ui="{ base: 'group relative flex items-start gap-x-3', padding: 'px-3 py-3', label: 'text-base whitespace-pre-line break-words text-left', icon: { base: 'flex-shrink-0 w-5 h-5 mt-0.5' }}" @click="isMobileMenuOpen = false"/> </div> </UCard> </USlideover>
    <UModal v-model="isGridCellModalOpen"> <UCard :ui="{ divide: 'divide-y divide-gray-100 dark:divide-gray-800' }"> <template #header> <div class="flex items-center justify-between"> <h3 class="text-base font-semibold leading-6 text-gray-900 dark:text-white"> Cell Information </h3> <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" class="-my-1" @click="isGridCellModalOpen = false"/> </div> </template> <div v-if="modalCellData" class="p-4"> <p>You selected cell at: </p> <p>Row: {{ modalCellData.row + 1 }}, Column: {{ modalCellData.col + 1 }}</p> <p>ID (example): {{ modalCellData.id }}</p> <p class="mt-4">Use this modal to set purposes for this square.</p> <p v-if="modalCellData.status" class="mt-2">Device Status: {{ modalCellData.status }}</p> </div> <div v-else class="p-4"> <p>No cell data available.</p> </div> <template #footer> <UButton label="Close" color="gray" @click="isGridCellModalOpen = false"/> <UButton label="Save" color="primary" @click="handleSaveCellData"/> </template> </UCard> </UModal>
  </div>
</template>

<script setup lang="ts">
import {ref, computed, watch, onMounted } from 'vue';
import {useLanguage} from '~/composables/useLanguage';
import PdfViewer from '~/components/pdf/PdfViewer.vue';
import GridOverlay from '~/components/interactive/GridOverlay.vue';

type InteractionMode = 'pan' | 'select';

interface DeviceData {
  id: string;
  name: string;
  pdfX: number;
  pdfY: number;
  status: 'connected' | 'error' | 'disconnected';
}

interface PredefinedArea {
  id: string;
  name: string;
  description?: string;
  pdfX: number; // Coordinate in PDF's point system, relative to definitionScale
  pdfY: number; // Coordinate in PDF's point system, relative to definitionScale
  definitionScale?: number; // The scale at which pdfX/pdfY were defined (defaults to 1.0 if undefined)
  status: 'connected' | 'error' | 'disconnected';
}

interface PdfViewerExposed {
  zoomIn: () => void; zoomOut: () => void; resetZoomAndPan: () => void;
  setPdfScale: (scale: number) => void; goToPage: (page: number) => void; reloadPdf: () => void;
  currentScale: { value: number }; currentPageNum: { value: number }; totalPages: { value: number };
  isRendering: { value: boolean }; isLoading: { value: boolean };
  minScale: number; maxScale: number;
  getCanvasActualWidth: () => number; getCanvasActualHeight: () => number;
  getCanvasPanX: () => number; getCanvasPanY: () => number;
  getPdfPageOriginalWidth: () => number; getPdfPageOriginalHeight: () => number;
  initialPdfRenderScale?: number; // Added for robust zoom reset
}

const {currentLanguage} = useLanguage ? useLanguage() : { currentLanguage: ref('en')};
const isMobileMenuOpen = ref(false);
const pdfViewerComponentRef = ref<PdfViewerExposed | null>(null);
const isPdfCurrentlyPanning = ref(false);
const zoomInputPercentage = ref(100);
const currentPageInput = ref(1);
const totalPagesForPdf = ref(0);

const isPanMode = ref(true);
const interactionMode = computed<InteractionMode>(() => isPanMode.value ? 'pan' : 'select');

const viewModeBaseLabel = computed(() => currentLanguage.value === 'vi' ? 'Chế độ xem' : 'View Mode');
const currentInteractionModeLabel = computed(() => { return interactionMode.value === 'pan' ? (currentLanguage.value === 'vi' ? 'Vuốt bản đồ' : 'Pan Map') : (currentLanguage.value === 'vi' ? 'Chọn khu vực' : 'Select Area'); });
const interactionModeToggleAriaLabel = computed(() => { return isPanMode.value ? (currentLanguage.value === 'vi' ? 'Chuyển sang Chọn khu vực' : 'Switch to Select Area Mode') : (currentLanguage.value === 'vi' ? 'Chuyển sang Vuốt bản đồ' : 'Switch to Pan Map Mode'); });
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
        console.log(`[index.vue/applyManualZoom] Calling setPdfScale with: ${newScale}`);
        viewer.setPdfScale(newScale);
      } else {
        console.warn(`[index.vue/applyManualZoom] Zoom input (${currentZoomInputVal}%) resulted in invalid scale (${newScale}). Resetting input.`);
        if (viewer.currentScale?.value && Number.isFinite(viewer.currentScale.value) && viewer.currentScale.value > 0) {
          zoomInputPercentage.value = Math.round(viewer.currentScale.value * 100);
        } else {
          zoomInputPercentage.value = Math.round((viewer.initialPdfRenderScale || 1.0) * 100) ;
        }
      }
    } else {
      console.warn(`[index.vue/applyManualZoom] Zoom input is not a valid number: ${currentZoomInputVal}. Resetting input.`);
      if (viewer.currentScale?.value && Number.isFinite(viewer.currentScale.value) && viewer.currentScale.value > 0) {
        zoomInputPercentage.value = Math.round(viewer.currentScale.value * 100);
      } else {
        zoomInputPercentage.value = Math.round((viewer.initialPdfRenderScale || 1.0) * 100) ;
      }
    }
  }
};

const handlePdfRendered = () => { console.log('[index.vue] PDF Page Rendered'); };
const handlePdfLoaded = () => {
  console.log('[index.vue] PDF Loaded');
  if (pdfViewerComponentRef.value) {
    const currentScaleVal = pdfViewerComponentRef.value.currentScale.value;
    if(Number.isFinite(currentScaleVal) && currentScaleVal > 0) {
      zoomInputPercentage.value = Math.round(currentScaleVal * 100);
    } else { // Fallback if PDFViewer reports an invalid current scale on load
      console.warn("[index.vue/handlePdfLoaded] PDFViewer reported invalid current scale on load. Resetting zoom input to initial prop or 100%.");
      zoomInputPercentage.value = Math.round((pdfViewerComponentRef.value.initialPdfRenderScale || 1.0) * 100);
    }
    totalPagesForPdf.value = pdfViewerComponentRef.value.totalPages.value;
    currentPageInput.value = pdfViewerComponentRef.value.currentPageNum.value;
  }
};

watch(() => pdfViewerComponentRef.value?.currentScale?.value, (newScale) => {
  if (typeof newScale === 'number' && Number.isFinite(newScale) && newScale > 0) {
    zoomInputPercentage.value = Math.round(newScale * 100);
  } else {
    console.warn(`[index.vue/watchCurrentScale] Watched currentScale from PDFViewer became invalid: ${newScale}. Input not updated.`);
  }
});
watch(() => pdfViewerComponentRef.value?.currentPageNum?.value, (newPage) => { if (typeof newPage === 'number') currentPageInput.value = newPage; });
watch(() => pdfViewerComponentRef.value?.totalPages?.value, (newTotal) => { if (typeof newTotal === 'number') totalPagesForPdf.value = newTotal; });

const rawNavigationItems = ref([
  { id: 'home', label_en: 'Home', label_vi: 'Trang chủ', icon: 'i-heroicons-home-solid', to: '/' },
  { id: 'device-list', label_en: 'Device List', label_vi: 'Danh sách thiết bị', icon: 'i-heroicons-queue-list-solid', to: '/device-list'},
  { id: 'device-management', label_en: 'Device Management', label_vi: 'Quản lý thiết bị', icon: 'i-heroicons-cog-8-tooth-solid', to: '/device-management'},
  { id: 'production-plan', label_en: 'Production Plan\n& Working Time', label_vi: 'Kế hoạch & Thời gian\nsản xuất', icon: 'i-heroicons-calendar-days-solid', to: '/production-plan'},
  { id: 'data-visualization', label_en: 'Data Visualization', label_vi: 'Trực quan hóa dữ liệu', icon: 'i-heroicons-chart-pie-solid', to: '/data-visualization'},
  { id: 'data-analysis', label_en: 'Data Analysis', label_vi: 'Phân tích dữ liệu', icon: 'i-heroicons-presentation-chart-line-solid', to: '/data-analysis'},
]);
const localizedNavigationItems = computed(() => rawNavigationItems.value.map(item => ({ id: item.id, label: currentLanguage.value === 'vi' ? item.label_vi : item.label_en, icon: item.icon, to: item.to, })));

const pdfViewAndGridAreaRef = ref<HTMLElement | null>(null);
const BASE_CELL_SIZE_PX = 50;
const selectedGridCell = ref<{ row: number; col: number } | null>(null);
const isGridCellModalOpen = ref(false);
const modalCellData = ref<{ id: string; row: number; col: number; status?: string } | null>(null);

const mockDeviceDataJson = `[
  { "id": "device_temp_001", "name": "Temperature Sensor A1", "pdfX": 150, "pdfY": 220, "status": "connected" },
  { "id": "device_motor_002", "name": "Motor Control B3", "pdfX": 350, "pdfY": 400, "status": "error" },
  { "id": "device_light_003", "name": "Lighting Unit C5", "pdfX": 550, "pdfY": 150, "status": "disconnected" }
]`;
const mockDeviceData = ref<DeviceData[]>(JSON.parse(mockDeviceDataJson));

const predefinedAreasJson = `[
  { "id": "area_zone_alpha", "name": "Alpha Zone", "description": "Primary assembly line", "pdfX": 50, "pdfY": 50, "definitionScale": 1.0, "status": "connected" },
  { "id": "area_storage_bay_1", "name": "Storage Bay 1 (Defined at 0.5x scale)", "pdfX": 300, "pdfY": 225, "definitionScale": 0.5, "status": "error" },
  { "id": "area_qc_station", "name": "QC Station (Native PDF scale)", "pdfX": 100, "pdfY": 500, "status": "disconnected" }
]`;
const predefinedAreasData: PredefinedArea[] = JSON.parse(predefinedAreasJson);

onMounted(() => {
  // PdfViewer's onMounted calls loadPdf, which then emits 'loaded'
  // We ensure handlePdfLoaded is called which syncs zoomInputPercentage
  console.log("[index.vue/onMounted] Component mounted.");
  console.log("--- Predefined Areas JSON String (Raw Input) ---");
  console.log(predefinedAreasJson);
  console.log("---------------------------------------------");
});


const computedGridOverlayProps = computed(() => {
  const viewer = pdfViewerComponentRef.value;
  if (!viewer || typeof viewer.getCanvasActualWidth !== 'function' || typeof viewer.getCanvasActualHeight !== 'function' ||
      typeof viewer.getCanvasPanX !== 'function' || typeof viewer.getCanvasPanY !== 'function') {
    return { visible: false, x: 0, y: 0, width: 0, height: 0, rows: 0, cols: 0, cellWidth: BASE_CELL_SIZE_PX, cellHeight: BASE_CELL_SIZE_PX };
  }
  const panXVal = viewer.getCanvasPanX();
  const panYVal = viewer.getCanvasPanY();
  const actualWidthVal = viewer.getCanvasActualWidth();
  const actualHeightVal = viewer.getCanvasActualHeight();

  if (!Number.isFinite(actualWidthVal) || actualWidthVal <= 0 ||
      !Number.isFinite(actualHeightVal) || actualHeightVal <= 0 ||
      !Number.isFinite(panXVal) || !Number.isFinite(panYVal) ||
      BASE_CELL_SIZE_PX <= 0) {
    console.warn("[index.vue/computedGridOverlayProps] Invalid dimensions/pan from viewer for grid overlay.", {actualWidthVal, actualHeightVal, panXVal, panYVal});
    return { visible: false, x: 0, y: 0, width: 0, height: 0, rows: 0, cols: 0, cellWidth: BASE_CELL_SIZE_PX, cellHeight: BASE_CELL_SIZE_PX };
  }
  const cols = Math.floor(actualWidthVal / BASE_CELL_SIZE_PX);
  const rows = Math.floor(actualHeightVal / BASE_CELL_SIZE_PX);
  if (cols <= 0 || rows <= 0) {
    return { visible: false, x: 0, y: 0, width: 0, height: 0, rows: 0, cols: 0, cellWidth: BASE_CELL_SIZE_PX, cellHeight: BASE_CELL_SIZE_PX };
  }
  return { visible: true, x: panXVal, y: panYVal, width: actualWidthVal, height: actualHeightVal, rows: rows, cols: cols, cellWidth: BASE_CELL_SIZE_PX, cellHeight: BASE_CELL_SIZE_PX };
});

const cellStatusesForOverlay = computed(() => {
  const statuses: Record<string, { status: string, sourceId?: string, sourceName?: string, sourceType?: 'device' | 'area' }> = {};
  const priorities: Record<string, number> = { error: 3, disconnected: 2, connected: 1 };

  const viewer = pdfViewerComponentRef.value;
  if (!viewer || !computedGridOverlayProps.value.visible ||
      typeof viewer.currentScale?.value !== 'number' ||
      !Number.isFinite(viewer.currentScale.value) ||
      viewer.currentScale.value <= 0) {
    console.warn("[index.vue/cellStatusesForOverlay] Viewer not ready or grid not visible or invalid currentScale.");
    return {};
  }

  const currentViewScale = viewer.currentScale.value; // This is the PDF.js render scale (e.g. 1.0, 1.5)

  // 1. Process Mock Device Data (assumes pdfX/pdfY are native PDF points, definitionScale = 1.0)
  for (const device of mockDeviceData.value) {
    const deviceNativePdfX = device.pdfX; // Already native
    const deviceNativePdfY = device.pdfY; // Already native

    const deviceCanvasX = deviceNativePdfX * currentViewScale;
    const deviceCanvasY = deviceNativePdfY * currentViewScale;

    const col = Math.floor(deviceCanvasX / BASE_CELL_SIZE_PX);
    const row = Math.floor(deviceCanvasY / BASE_CELL_SIZE_PX);

    if (col >= 0 && col < computedGridOverlayProps.value.cols && row >= 0 && row < computedGridOverlayProps.value.rows) {
      const key = `${row}-${col}`;
      const existingEntry = statuses[key];
      const newPriority = priorities[device.status] || 0;
      const existingPriority = existingEntry ? (priorities[existingEntry.status] || 0) : 0;

      if (newPriority > existingPriority) {
        statuses[key] = { status: device.status, sourceId: device.id, sourceName: device.name, sourceType: 'device' };
      }
    }
  }

  // 2. Process Predefined Areas (handles optional definitionScale)
  console.log("--- Processing Predefined Areas from JSON for Grid Overlay ---");
  for (const area of predefinedAreasData) {
    const itemDefinitionScale = area.definitionScale || 1.0;
    // Convert area's pdfX/pdfY to native PDF coordinates (scale 1.0)
    const areaNativePdfX = area.pdfX / itemDefinitionScale;
    const areaNativePdfY = area.pdfY / itemDefinitionScale;

    // Convert native PDF coordinates to current canvas pixel coordinates
    const areaCanvasX = areaNativePdfX * currentViewScale;
    const areaCanvasY = areaNativePdfY * currentViewScale;

    const col = Math.floor(areaCanvasX / BASE_CELL_SIZE_PX);
    const row = Math.floor(areaCanvasY / BASE_CELL_SIZE_PX);

    let color = 'unknown';
    switch (area.status) {
      case 'connected': color = 'green'; break;
      case 'error': color = 'yellow'; break;
      case 'disconnected': color = 'red'; break;
    }

    console.log(
        `Processing Predefined Area: ID='${area.id}', Name='${area.name}', `,
        `Original Coords=(X:${area.pdfX}, Y:${area.pdfY}) at DefinitionScale:${itemDefinitionScale}, `,
        `Native PDF Coords=(X:${areaNativePdfX.toFixed(2)}, Y:${areaNativePdfY.toFixed(2)}), `,
        `Status='${area.status}', DerivedColor='${color}', CurrentViewScale=${currentViewScale.toFixed(2)}, `,
        `Canvas Coords=(X:${areaCanvasX.toFixed(2)}, Y:${areaCanvasY.toFixed(2)}), `,
        `MappedToGridCell=(R:${row}, C:${col}) (Key: ${row}-${col})`
    );

    if (col >= 0 && col < computedGridOverlayProps.value.cols && row >= 0 && row < computedGridOverlayProps.value.rows) {
      const key = `${row}-${col}`;
      const existingEntry = statuses[key];
      const newPriority = priorities[area.status] || 0;
      const existingPriority = existingEntry ? (priorities[existingEntry.status] || 0) : 0;

      if (newPriority >= existingPriority) {
        statuses[key] = { status: area.status, sourceId: area.id, sourceName: area.name, sourceType: 'area' };
        console.log(`  > Grid Cell ${key} updated by Area '${area.name}' with status '${area.status}'.`);
      } else if (existingEntry) { // Check if existingEntry is defined before accessing its status
        console.log(`  > Grid Cell ${key} NOT updated by Area '${area.name}' (Existing status '${existingEntry.status}' from '${existingEntry.sourceType}' has higher priority).`);
      }
    } else {
      console.log(`  > Area '${area.name}' maps outside current grid view.`);
    }
  }
  console.log("-----------------------------------------------------------");

  const cellsForJsonDebug = [];
  for (const key in statuses) {
    if (Object.prototype.hasOwnProperty.call(statuses, key)) {
      const [rowStr, colStr] = key.split('-');
      const statusInfo = statuses[key];
      let color = 'unknown';
      switch (statusInfo.status) {
        case 'connected': color = 'green'; break;
        case 'error': color = 'yellow'; break;
        case 'disconnected': color = 'red'; break;
      }
      cellsForJsonDebug.push({
        row: parseInt(rowStr, 10),
        col: parseInt(colStr, 10),
        status: statusInfo.status,
        color: color,
        sourceId: statusInfo.sourceId,
        sourceName: statusInfo.sourceName,
        sourceType: statusInfo.sourceType
      });
    }
  }
  console.log("--- Final Combined Active Grid Cells (JSON String Debug) ---");
  console.log(JSON.stringify(cellsForJsonDebug, null, 2));
  console.log("---------------------------------------------------------");

  return statuses;
});


const handleGridCellClick = (cell: { row: number; col: number; }) => {
  if (interactionMode.value !== 'select') return;
  if (isPdfCurrentlyPanning.value) return;

  const cellKey = `${cell.row}-${cell.col}`;
  const statusInfo = cellStatusesForOverlay.value[cellKey];

  if (selectedGridCell.value?.row === cell.row && selectedGridCell.value?.col === cell.col) {
    selectedGridCell.value = null;
  } else {
    selectedGridCell.value = cell;
    modalCellData.value = {
      id: statusInfo?.sourceId || `cell-${cell.row}-${cell.col}`,
      row: cell.row,
      col: cell.col,
      status: statusInfo?.status
    };
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
.pdf-main-area { }
</style>