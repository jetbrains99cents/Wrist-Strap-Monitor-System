<template>
  <div class="pdf-viewer-wrapper w-full h-full flex flex-col overflow-hidden">
    <div
        ref="pdfViewportRef"
        class="pdf-viewport flex-grow w-full h-full overflow-hidden cursor-grab active:cursor-grabbing relative bg-gray-300 dark:bg-gray-700"
        @mousedown.prevent="handleMouseDown"
        @mousemove.prevent="handleMouseMove"
        @mouseup="handleMouseUp"
        @mouseleave="handleMouseLeave"
        @wheel.prevent="handleWheelZoom"
    >
      <canvas
          ref="pdfCanvasElementRef"
          class="pdf-canvas"
          :style="{ transform: `translate(${panX}px, ${panY}px)` }"
      ></canvas>
    </div>

    <div v-if="loading && !errorMsg" class="loading-indicator">Loading PDF...</div>
    <div v-if="isRenderingPage && !loading" class="loading-indicator bottom-16">Rendering Page @
      {{ currentPdfJsRenderScale.toFixed(1) }}x ...
    </div>
    <div v-if="errorMsg" class="error-indicator">Error: {{ errorMsg }}</div>
  </div>
</template>

<script setup lang="ts">
import {ref, onMounted, onUnmounted, watch, nextTick, computed} from 'vue';
import * as pdfjsLib from 'pdfjs-dist/build/pdf.mjs';
import PdfjsWorkerPath from 'pdfjs-dist/build/pdf.worker.min.mjs?url';

const props = defineProps({
  src: {type: String, required: true},
  initialPdfRenderScale: {type: Number, default: 1.0},
  pdfMaxRenderScale: {type: Number, default: 5.0},
  pdfMinRenderScale: {type: Number, default: 0.2},
  pdfZoomStep: {type: Number, default: 0.2}
});

const emit = defineEmits<{
  (e: 'rendered'): void;
  (e: 'loaded'): void;
  (e: 'panstart'): void;
  (e: 'panend'): void;
}>();

const pdfViewportRef = ref<HTMLElement | null>(null);
const pdfCanvasElementRef = ref<HTMLCanvasElement | null>(null);
let pdfDoc: pdfjsLib.PDFDocumentProxy | null = null;
let renderTask: pdfjsLib.RenderTask | null = null;

const loading = ref(true);
const isRenderingPage = ref(false);
const errorMsg = ref<string | null>(null);
const numPages = ref(0);
const currentPage = ref(1);
const currentPdfJsRenderScale = ref(props.initialPdfRenderScale);

const isDragging = ref(false);
const panX = ref(0);
const panY = ref(0);
const startPanX = ref(0);
const startPanY = ref(0);
const dragStartX = ref(0);
const dragStartY = ref(0);

let renderDebounceTimer: ReturnType<typeof setTimeout> | null = null;

const actualCanvasWidth_internal = ref(0);
const actualCanvasHeight_internal = ref(0);

async function renderPage(pageNum: number, pdfScaleToRender: number) {
  const canvasEl = pdfCanvasElementRef.value;
  const viewportEl = pdfViewportRef.value;

  if (!canvasEl || !viewportEl) {
    errorMsg.value = "Render prerequisites: Missing canvas or viewport element.";
    isRenderingPage.value = false;
    return;
  }
  const currentDocInstance = pdfDoc;
  if (!currentDocInstance) {
    errorMsg.value = "Render prerequisites: pdfDoc is null in renderPage.";
    isRenderingPage.value = false;
    return;
  }
  if (renderTask) {
    try {
      renderTask.cancel();
    } catch (e) { /* ignore */
    }
    renderTask = null;
  }

  isRenderingPage.value = true;
  errorMsg.value = null;

  try {
    const page = await currentDocInstance.getPage(pageNum);
    const viewport = page.getViewport({scale: pdfScaleToRender});
    const context = canvasEl.getContext('2d');

    if (!context) {
      errorMsg.value = 'Failed to get canvas 2D context';
      isRenderingPage.value = false;
      return;
    }

    canvasEl.height = viewport.height;
    canvasEl.width = viewport.width;
    actualCanvasWidth_internal.value = canvasEl.width;
    actualCanvasHeight_internal.value = canvasEl.height;
    currentPdfJsRenderScale.value = pdfScaleToRender;

    const renderContext = {canvasContext: context, viewport: viewport};
    renderTask = page.render(renderContext);
    await renderTask.promise;
    renderTask = null;
    await nextTick();

    if (viewportEl.offsetWidth > canvasEl.width) {
      panX.value = (viewportEl.offsetWidth - canvasEl.width) / 2;
    } else {
      panX.value = Math.max(viewportEl.offsetWidth - canvasEl.width, Math.min(panX.value, 0));
    }
    if (viewportEl.offsetHeight > canvasEl.height) {
      panY.value = (viewportEl.offsetHeight - canvasEl.height) / 2;
    } else {
      panY.value = Math.max(viewportEl.offsetHeight - canvasEl.height, Math.min(panY.value, 0));
    }

    emit('rendered');
  } catch (err: any) {
    if (renderTask) renderTask = null;
    if (err.name === 'RenderingCancelledException' || (typeof err.message === 'string' && err.message.includes('Rendering cancelled'))) {
      // This is expected
    } else {
      errorMsg.value = err.message || `Failed to render page ${pageNum}`;
    }
  } finally {
    isRenderingPage.value = false;
  }
}

async function loadPdf() {
  if (!props.src) {
    errorMsg.value = "No PDF source provided.";
    loading.value = false;
    return;
  }
  loading.value = true;
  errorMsg.value = null;

  if (renderTask) {
    try {
      renderTask.cancel();
    } catch (e) { /* ignore */
    }
    renderTask = null;
  }
  if (pdfDoc) {
    try {
      await pdfDoc.destroy();
    } catch (e) {
      console.error('Error destroying previous pdfDoc:', e);
    }
    pdfDoc = null;
  }

  numPages.value = 0;
  currentPage.value = 1;
  currentPdfJsRenderScale.value = props.initialPdfRenderScale;
  panX.value = 0;
  panY.value = 0;
  actualCanvasWidth_internal.value = 0;
  actualCanvasHeight_internal.value = 0;

  try {
    if (typeof window !== 'undefined' && !pdfjsLib.GlobalWorkerOptions.workerSrc) {
      pdfjsLib.GlobalWorkerOptions.workerSrc = PdfjsWorkerPath;
    }
    const loadedDoc = await pdfjsLib.getDocument(props.src).promise;
    if (!loadedDoc) {
      pdfDoc = null;
      errorMsg.value = "PDF document loading failed.";
    } else {
      pdfDoc = loadedDoc;
      numPages.value = loadedDoc.numPages;
      if (numPages.value > 0) {
        await renderPage(currentPage.value, currentPdfJsRenderScale.value);
      } else {
        errorMsg.value = "The PDF document has no pages to display.";
        actualCanvasWidth_internal.value = 0;
        actualCanvasHeight_internal.value = 0;
      }
    }
  } catch (err: any) {
    pdfDoc = null;
    errorMsg.value = err.message || 'Failed to load PDF document';
    actualCanvasWidth_internal.value = 0;
    actualCanvasHeight_internal.value = 0;
  } finally {
    loading.value = false;
    if (!errorMsg.value && pdfDoc) {
      emit('loaded');
    }
  }
}

const handleMouseDown = (event: MouseEvent) => {
  if (!pdfViewportRef.value || !(event.target === pdfViewportRef.value || event.target === pdfCanvasElementRef.value)) return;
  if (event.button !== 0) return;
  isDragging.value = true;
  emit('panstart');
  dragStartX.value = event.clientX;
  dragStartY.value = event.clientY;
  startPanX.value = panX.value;
  startPanY.value = panY.value;
  if (pdfViewportRef.value) pdfViewportRef.value.style.cursor = 'grabbing';
};

const handleMouseMove = (event: MouseEvent) => {
  if (!isDragging.value) return;
  const dx = event.clientX - dragStartX.value;
  const dy = event.clientY - dragStartY.value;
  const canvasEl = pdfCanvasElementRef.value;
  const viewportEl = pdfViewportRef.value;

  if (canvasEl && viewportEl) {
    let newPanX = startPanX.value + dx;
    let newPanY = startPanY.value + dy;

    if (canvasEl.width <= viewportEl.offsetWidth) { // Canvas is narrower or same width
      newPanX = Math.max(0, Math.min(newPanX, viewportEl.offsetWidth - canvasEl.width));
    } else { // Canvas is wider
      newPanX = Math.max(viewportEl.offsetWidth - canvasEl.width, Math.min(newPanX, 0));
    }
    panX.value = newPanX;

    if (canvasEl.height <= viewportEl.offsetHeight) { // Canvas is shorter or same height
      newPanY = Math.max(0, Math.min(newPanY, viewportEl.offsetHeight - canvasEl.height));
    } else { // Canvas is taller
      newPanY = Math.max(viewportEl.offsetHeight - canvasEl.height, Math.min(newPanY, 0));
    }
    panY.value = newPanY;
  } else {
    panX.value = startPanX.value + dx;
    panY.value = startPanY.value + dy;
  }
};

const handleMouseUp = () => {
  if (!isDragging.value) return;
  isDragging.value = false;
  emit('panend');
  if (pdfViewportRef.value) pdfViewportRef.value.style.cursor = 'grab';
};

const handleMouseLeave = () => {
  if (isDragging.value) {
    isDragging.value = false;
    emit('panend');
    if (pdfViewportRef.value) pdfViewportRef.value.style.cursor = 'grab';
  }
};

const changeZoom = (newScale: number) => {
  const targetScale = parseFloat(Math.max(props.pdfMinRenderScale, Math.min(props.pdfMaxRenderScale, newScale)).toFixed(2));
  if (targetScale !== currentPdfJsRenderScale.value) {
    if (renderDebounceTimer) clearTimeout(renderDebounceTimer);
    renderDebounceTimer = setTimeout(() => {
      if (pdfDoc) {
        renderPage(currentPage.value, targetScale);
      }
    }, 100);
  }
};

const handleWheelZoom = (event: WheelEvent) => {
  event.preventDefault();
  let newScaleDelta = props.pdfZoomStep * (event.ctrlKey ? 1.5 : 1);
  if (event.deltaY < 0) {
    changeZoom(currentPdfJsRenderScale.value + newScaleDelta);
  } else {
    changeZoom(currentPdfJsRenderScale.value - newScaleDelta);
  }
};

const triggerZoomIn = () => changeZoom(currentPdfJsRenderScale.value + props.pdfZoomStep);
const triggerZoomOut = () => changeZoom(currentPdfJsRenderScale.value - props.pdfZoomStep);
const triggerFullReset = () => {
  if (pdfDoc) {
    currentPage.value = 1;
    renderPage(currentPage.value, props.initialPdfRenderScale);
  } else {
    currentPdfJsRenderScale.value = props.initialPdfRenderScale;
    panX.value = 0;
    panY.value = 0;
    actualCanvasWidth_internal.value = 0;
    actualCanvasHeight_internal.value = 0;
  }
};
const applyManualScale = (newScale: number) => {
  const targetScale = parseFloat(Math.max(props.pdfMinRenderScale, Math.min(props.pdfMaxRenderScale, newScale)).toFixed(2));
  changeZoom(targetScale);
};
const triggerGoToPage = (pageNumber: number) => {
  if (pageNumber >= 1 && pageNumber <= numPages.value && pageNumber !== currentPage.value && pdfDoc) {
    currentPage.value = pageNumber;
  }
};

onMounted(() => {
  loadPdf();
});
watch(() => props.src, (newSrc, oldSrc) => {
  if (newSrc && newSrc !== oldSrc) {
    loadPdf();
  }
});
watch(currentPage, (newPage, oldPage) => {
  if (newPage !== oldPage && newPage >= 1 && newPage <= numPages.value && pdfDoc) {
    renderPage(newPage, currentPdfJsRenderScale.value);
  }
});
onUnmounted(() => {
  if (renderDebounceTimer) clearTimeout(renderDebounceTimer);
  if (renderTask) {
    try {
      renderTask.cancel();
    } catch (e) { /* ignore */
    }
    renderTask = null;
  }
  if (pdfDoc) {
    try {
      pdfDoc.destroy();
    } catch (e) {
      console.error('Error destroying PDF document on unmount:', e);
    }
    pdfDoc = null;
  }
});

defineExpose({
  zoomIn: triggerZoomIn,
  zoomOut: triggerZoomOut,
  resetZoomAndPan: triggerFullReset,
  setPdfScale: applyManualScale,
  goToPage: triggerGoToPage,
  reloadPdf: loadPdf,
  currentScale: computed(() => currentPdfJsRenderScale.value),
  currentPageNum: computed(() => currentPage.value),
  totalPages: computed(() => numPages.value),
  isRendering: computed(() => isRenderingPage.value || loading.value),
  isLoading: computed(() => loading.value),
  minScale: props.pdfMinRenderScale,
  maxScale: props.pdfMaxRenderScale,
  getCanvasActualWidth: () => actualCanvasWidth_internal.value,
  getCanvasActualHeight: () => actualCanvasHeight_internal.value,
  getCanvasPanX: () => panX.value,
  getCanvasPanY: () => panY.value,
});
</script>

<style scoped>
.pdf-viewer-wrapper {
  background-color: #f0f0f0;
}

html.dark .pdf-viewer-wrapper {
  background-color: #2d3748;
}

.pdf-canvas {
  display: block;
}

.loading-indicator, .error-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 1rem 1.5rem;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  border-radius: 0.5rem;
  z-index: 10;
  font-family: 'ABeeZee', sans-serif;
  text-align: center;
  pointer-events: none;
}

.error-indicator {
  background-color: rgba(220, 38, 38, 0.9);
}

.loading-indicator.bottom-16 {
  bottom: 4rem;
  top: auto;
  transform: translateX(-50%);
  left: 50%;
}
</style>