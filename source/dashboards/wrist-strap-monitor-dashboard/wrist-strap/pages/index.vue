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

    <section class="flex-1 flex flex-col overflow-hidden">
      <div class="md:hidden p-3 sm:p-4 sticky top-0 bg-white dark:bg-dark-bg z-20 border-b dark:border-dark-border">
        <UButton
            icon="i-heroicons-bars-3-20-solid"
            color="gray"
            variant="ghost"
            aria-label="Open navigation menu"
            @click="isMobileMenuOpen = true"
        />
      </div>

      <div class="pdf-main-area flex flex-col flex-1 overflow-y-auto">
        <div
            v-if="pdfViewerComponentRef"
            class="pdf-controls-bar sticky top-0 z-10 p-2 flex justify-center items-center gap-2 bg-gray-100 dark:bg-dark-surface border-b dark:border-dark-border shadow-sm shrink-0"
        >
          <UButton size="sm" icon="i-heroicons-magnifying-glass-plus-20-solid" @click="pdfViewerComponentRef?.zoomIn()"
                   :aria-label="zoomInLabel" :disabled="pdfViewerComponentRef?.isRendering?.value"/>
          <UButton size="sm" icon="i-heroicons-magnifying-glass-minus-20-solid"
                   @click="pdfViewerComponentRef?.zoomOut()" :aria-label="zoomOutLabel"
                   :disabled="pdfViewerComponentRef?.isRendering?.value"/>
          <UButton size="sm" icon="i-heroicons-arrows-pointing-out-20-solid"
                   @click="pdfViewerComponentRef?.resetZoomAndPan()" :aria-label="resetViewLabel"
                   :disabled="pdfViewerComponentRef?.isRendering?.value"/>
          <div class="flex items-center gap-1 text-xs text-gray-600 dark:text-gray-400">
            <span>Scale:</span>
            <UInput v-model.number="zoomInputPercentage" type="number" size="xs" class="w-20 text-center"
                    @change="applyManualZoomToViewer" @keyup.enter="applyManualZoomToViewer" :min="minZoomPercentage"
                    :max="maxZoomPercentage" :disabled="pdfViewerComponentRef?.isRendering?.value"/>
            <span>%</span>
          </div>
          <div class="flex items-center gap-1 text-xs text-gray-600 dark:text-gray-400">
            <span>Pg:</span>
            <UInput v-model.number="currentPageInput" type="number" size="xs" class="w-16 text-center"
                    @change="changePdfPage" @keyup.enter="changePdfPage" :min="1" :max="totalPagesForPdf"
                    :disabled="!pdfViewerComponentRef || totalPagesForPdf <= 1 || pdfViewerComponentRef?.isRendering?.value"/>
            <span>/ {{ totalPagesForPdf || '?' }}</span>
          </div>
          <span v-if="pdfViewerComponentRef?.currentScale?.value"
                class="text-xs text-gray-500 dark:text-gray-400 hidden sm:inline">
            Render: {{ pdfViewerComponentRef.currentScale.value.toFixed(1) }}x
          </span>
        </div>

        <div ref="pdfViewAndGridAreaRef" class="flex-grow relative overflow-hidden">
          <PdfViewer
              ref="pdfViewerComponentRef"
              src="/factory-layout.pdf"
              alt="Factory Production Layout"
              class="w-full h-full"
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
              @cell-click="handleGridCellClick"
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

    <USlideover v-model="isMobileMenuOpen" side="left" :ui="{ width: 'max-w-xs w-full sm:w-72', zIndex: 'z-50' }">
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

    <UModal v-model="isGridCellModalOpen">
      <UCard :ui="{ divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-base font-semibold leading-6 text-gray-900 dark:text-white">
              Cell Information
            </h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" class="-my-1"
                     @click="isGridCellModalOpen = false"/>
          </div>
        </template>
        <div v-if="modalCellData" class="p-4">
          <p>You selected cell at: </p>
          <p>Row: {{ modalCellData.row + 1 }}, Column: {{ modalCellData.col + 1 }}</p>
          <p>ID (example): {{ modalCellData.id }}</p>
          <p class="mt-4">Use this modal to set purposes for this square.</p>
        </div>
        <div v-else class="p-4">
          <p>No cell data available.</p>
        </div>
        <template #footer>
          <UButton label="Close" color="gray" @click="isGridCellModalOpen = false"/>
          <UButton label="Save" color="primary" @click="handleSaveCellData"/>
        </template>
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import {ref, computed, watch, onMounted} from 'vue';
import {useLanguage} from '~/composables/useLanguage';
import PdfViewer from '~/components/pdf/PdfViewer.vue';
import GridOverlay from '~/components/interactive/GridOverlay.vue';

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
}

const {currentLanguage} = useLanguage();
const isMobileMenuOpen = ref(false);
const pdfViewerComponentRef = ref<PdfViewerExposed | null>(null);
const isPdfCurrentlyPanning = ref(false);
const zoomInputPercentage = ref(100);
const currentPageInput = ref(1);
const totalPagesForPdf = ref(0);

const minZoomPercentage = computed(() => pdfViewerComponentRef.value ? Math.round(pdfViewerComponentRef.value.minScale * 100) : 20);
const maxZoomPercentage = computed(() => pdfViewerComponentRef.value ? Math.round(pdfViewerComponentRef.value.maxScale * 100) : 500);
const zoomInLabel = computed(() => currentLanguage.value === 'vi' ? 'Phóng to' : 'Zoom In');
const zoomOutLabel = computed(() => currentLanguage.value === 'vi' ? 'Thu nhỏ' : 'Zoom Out');
const resetViewLabel = computed(() => currentLanguage.value === 'vi' ? 'Đặt lại' : 'Reset View');

const applyManualZoomToViewer = () => {
  if (pdfViewerComponentRef.value) pdfViewerComponentRef.value.setPdfScale(zoomInputPercentage.value / 100);
};
const changePdfPage = () => {
  if (pdfViewerComponentRef.value) pdfViewerComponentRef.value.goToPage(currentPageInput.value);
};

const handlePdfRendered = () => {
  const viewer = pdfViewerComponentRef.value;
  if (viewer && typeof viewer.getCanvasActualWidth === 'function') {
    const w = viewer.getCanvasActualWidth();
    const h = viewer.getCanvasActualHeight();
    const px = viewer.getCanvasPanX();
    const py = viewer.getCanvasPanY();
    // console.log(`[index.vue] PDF RENDERED - Direct access via functions: W=${w}, H=${h}, PanX=${px}, PanY=${py}`);
  }
  if (pdfViewerComponentRef.value?.currentScale?.value) {
    zoomInputPercentage.value = Math.round(pdfViewerComponentRef.value.currentScale.value * 100);
  }
  if (pdfViewerComponentRef.value?.currentPageNum?.value) {
    currentPageInput.value = pdfViewerComponentRef.value.currentPageNum.value;
  }
};

const handlePdfLoaded = () => {
  const viewer = pdfViewerComponentRef.value;
  if (viewer && typeof viewer.getCanvasActualWidth === 'function') {
    const w = viewer.getCanvasActualWidth();
    const h = viewer.getCanvasActualHeight();
    // console.log(`[index.vue] PDF LOADED - Direct access via functions: W=${w}, H=${h}`);
  }
  if (pdfViewerComponentRef.value?.totalPages?.value) {
    totalPagesForPdf.value = pdfViewerComponentRef.value.totalPages.value;
    currentPageInput.value = 1;
  }
  if (pdfViewerComponentRef.value?.currentScale?.value) {
    zoomInputPercentage.value = Math.round(pdfViewerComponentRef.value.currentScale.value * 100);
  }
};

watch(() => pdfViewerComponentRef.value?.currentScale?.value, (newScale) => {
  if (typeof newScale === 'number') zoomInputPercentage.value = Math.round(newScale * 100);
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
const modalCellData = ref<{ id: string; row: number; col: number } | null>(null);

const computedGridOverlayProps = computed(() => {
  const viewer = pdfViewerComponentRef.value;
  if (!viewer ||
      typeof viewer.getCanvasActualWidth !== 'function' ||
      typeof viewer.getCanvasActualHeight !== 'function' ||
      typeof viewer.getCanvasPanX !== 'function' ||
      typeof viewer.getCanvasPanY !== 'function') {
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

  if (typeof actualWidthVal !== 'number' || actualWidthVal <= 0 ||
      typeof actualHeightVal !== 'number' || actualHeightVal <= 0 ||
      typeof panXVal !== 'number' ||
      typeof panYVal !== 'number' ||
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

  const cols = Math.floor(actualWidthVal / BASE_CELL_SIZE_PX);
  const rows = Math.floor(actualHeightVal / BASE_CELL_SIZE_PX);

  if (cols <= 0 || rows <= 0) {
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

  return {
    visible: true, x: panXVal, y: panYVal, width: actualWidthVal, height: actualHeightVal,
    rows: rows, cols: cols, cellWidth: BASE_CELL_SIZE_PX, cellHeight: BASE_CELL_SIZE_PX,
  };
});

onMounted(() => {
  // console.log('[index.vue] Component MOUNTED. pdfViewerComponentRef:', pdfViewerComponentRef.value);
});

const handleGridCellClick = (cell: { row: number; col: number }) => {
  if (isPdfCurrentlyPanning.value) return; // Prevent cell click if panning
  if (selectedGridCell.value?.row === cell.row && selectedGridCell.value?.col === cell.col) {
    selectedGridCell.value = null;
  } else {
    selectedGridCell.value = cell;
    modalCellData.value = {id: `cell-${cell.row}-${cell.col}`, row: cell.row, col: cell.col};
    isGridCellModalOpen.value = true;
  }
};

const handleSaveCellData = () => {
  if (modalCellData.value) {
    // console.log('Saving data for cell:', modalCellData.value);
  }
  isGridCellModalOpen.value = false;
};

useHead({
  title: 'Factory Layout (PDF) - Wrist Strap Dashboard | IoT Hub',
  meta: [{
    name: 'description',
    content: 'Interactive overview of the factory production layout using PDF with grid overlay.'
  }]
});
</script>

<style scoped> .pdf-main-area { /* Styles for the main PDF area */
} </style>