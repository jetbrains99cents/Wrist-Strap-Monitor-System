<template>
  <div class="pdf-viewer-wrapper w-full h-full flex flex-col overflow-hidden">
    <div
        ref="pdfViewportRef"
        class="pdf-viewport flex-grow w-full h-full overflow-hidden relative bg-gray-300 dark:bg-gray-700"
        :class="{ 'cursor-grab active:cursor-grabbing': interactionMode === 'pan', 'cursor-default': interactionMode !== 'pan' }"
        @mousedown="handleMouseDown"
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
      {{ Number.isFinite(currentPdfJsRenderScale) ? currentPdfJsRenderScale.toFixed(1) : 'N/A' }}x ...
    </div>
    <div v-if="errorMsg" class="error-indicator">Error: {{ errorMsg }}</div>
  </div>
</template>

<script setup lang="ts">
import {ref, onMounted, onUnmounted, watch, nextTick, computed} from 'vue';
import * as pdfjsLib from 'pdfjs-dist/build/pdf.mjs';
import PdfjsWorkerPath from 'pdfjs-dist/build/pdf.worker.min.mjs?url';
import { useLogger } from '~/composables/useLogger';

type InteractionMode = 'pan' | 'select';

const logger = useLogger();

const props = defineProps({
  src: {type: String, required: true},
  initialPdfRenderScale: {type: Number, default: 1.0},
  pdfMaxRenderScale: {type: Number, default: 20.0},
  pdfMinRenderScale: {type: Number, default: 0.2},
  pdfZoomStep: {type: Number, default: 0.2},
  interactionMode: {type: String as () => InteractionMode, default: 'pan'}
});

const emit = defineEmits<{
  (e: 'rendered'): void;
  (e: 'loaded'): void;
  (e: 'panstart'): void;
  (e: 'panend'): void;
  (e: 'scale-updated', scale: number): void; // <-- ADDED
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
const currentPdfJsRenderScale = ref(props.initialPdfRenderScale > 0 && Number.isFinite(props.initialPdfRenderScale) ? props.initialPdfRenderScale : 1.0);

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
const pdfPageOriginalWidth_internal = ref(0);
const pdfPageOriginalHeight_internal = ref(0);

// Helper to ensure a scale is valid
const ensureValidScale = (scale: number, context: string): number => {
  let validScale = scale;
  if (isNaN(validScale) || !Number.isFinite(validScale) || validScale <= 0) {
    logger.warn(`[PdfViewer/${context}] Invalid scale detected: ${scale}. Falling back.`);
    if (Number.isFinite(currentPdfJsRenderScale.value) && currentPdfJsRenderScale.value > 0) {
      validScale = currentPdfJsRenderScale.value;
    } else if (Number.isFinite(props.initialPdfRenderScale) && props.initialPdfRenderScale > 0) {
      validScale = props.initialPdfRenderScale;
    } else {
      validScale = 1.0;
    }
    logger.warn(`[PdfViewer/${context}] Fallback scale: ${validScale}`);
  }
  let clampedScale = Math.max(props.pdfMinRenderScale, Math.min(props.pdfMaxRenderScale, validScale));
  return parseFloat(clampedScale.toFixed(2));
};


async function renderPage(pageNum: number, pdfScaleToRenderInput: number) {
  logger.log(`[PdfViewer/renderPage] Called with pageNum: ${pageNum}, pdfScaleToRenderInput: ${pdfScaleToRenderInput}`);
  const pdfScaleToRender = ensureValidScale(pdfScaleToRenderInput, "renderPage entry");
  logger.log(`[PdfViewer/renderPage] Validated pdfScaleToRender: ${pdfScaleToRender}`);

  if (pdfScaleToRender <= 0) {
    errorMsg.value = `[PdfViewer/renderPage] Critically invalid scale after validation: ${pdfScaleToRender}. Aborting render.`;
    logger.error(errorMsg.value);
    isRenderingPage.value = false;
    return;
  }

  const canvasEl = pdfCanvasElementRef.value;
  const viewportEl = pdfViewportRef.value;
  if (!canvasEl || !viewportEl) {
    errorMsg.value = "[PdfViewer/renderPage] Canvas or viewport element not found.";
    logger.error(errorMsg.value);
    isRenderingPage.value = false;
    return;
  }
  const currentDocInstance = pdfDoc;
  if (!currentDocInstance) {
    errorMsg.value = "[PdfViewer/renderPage] PDF document not loaded.";
    logger.error(errorMsg.value);
    isRenderingPage.value = false;
    return;
  }

  if (renderTask) {
    try {
      renderTask.cancel();
      logger.log("[PdfViewer/renderPage] Previous renderTask cancelled.");
    } catch (e) { /* ignore */
    }
    renderTask = null;
  }

  isRenderingPage.value = true;
  errorMsg.value = null;

  try {
    logger.log(`[PdfViewer/renderPage] Getting page ${pageNum}`);
    const page = await currentDocInstance.getPage(pageNum);
    logger.log(`[PdfViewer/renderPage] Getting viewport with scale: ${pdfScaleToRender}`);
    const viewport = page.getViewport({scale: pdfScaleToRender});
    logger.log(`[PdfViewer/renderPage] Viewport received: W=${viewport.width}, H=${viewport.height}, Scale=${viewport.scale}`);

    if (isNaN(viewport.width) || !Number.isFinite(viewport.width) || viewport.width <= 0 ||
        isNaN(viewport.height) || !Number.isFinite(viewport.height) || viewport.height <= 0) {
      errorMsg.value = `[PdfViewer/renderPage] PDF page generated invalid viewport WxH: ${viewport.width}x${viewport.height} at scale ${pdfScaleToRender}.`;
      logger.error(errorMsg.value, "Viewport object:", viewport);
      isRenderingPage.value = false;
      if (canvasEl) {
        canvasEl.width = (Number.isFinite(actualCanvasWidth_internal.value) && actualCanvasWidth_internal.value > 0) ? actualCanvasWidth_internal.value : 1;
        canvasEl.height = (Number.isFinite(actualCanvasHeight_internal.value) && actualCanvasHeight_internal.value > 0) ? actualCanvasHeight_internal.value : 1;
        logger.log(`[PdfViewer/renderPage] Canvas dimensions reset to avoid NaN: W=${canvasEl.width}, H=${canvasEl.height}`);
      }
      return;
    }

    const context = canvasEl.getContext('2d');
    if (!context) {
      errorMsg.value = '[PdfViewer/renderPage] Failed to get 2D context from canvas.';
      logger.error(errorMsg.value);
      isRenderingPage.value = false;
      return;
    }

    logger.log(`[PdfViewer/renderPage] Setting canvas dimensions: W=${viewport.width}, H=${viewport.height}`);
    canvasEl.height = viewport.height;
    canvasEl.width = viewport.width;

    logger.log(`[PdfViewer/renderPage] Updating internal reactive dimensions.`);
    actualCanvasWidth_internal.value = canvasEl.width;
    actualCanvasHeight_internal.value = canvasEl.height;
    currentPdfJsRenderScale.value = pdfScaleToRender; // Ensure this holds the actual scale rendered

    const renderContext = {canvasContext: context, viewport: viewport};
    logger.log("[PdfViewer/renderPage] Starting PDF.js page.render task.");
    renderTask = page.render(renderContext);
    await renderTask.promise;
    renderTask = null;
    logger.log("[PdfViewer/renderPage] PDF.js page.render task completed.");

    emit('scale-updated', currentPdfJsRenderScale.value); // <-- ADDED: Emit the updated scale
    logger.log(`[PdfViewer/renderPage] Emitted 'scale-updated' with scale: ${currentPdfJsRenderScale.value}`);


    await nextTick();

    let newPanX = panX.value;
    let newPanY = panY.value;

    if (viewportEl.offsetWidth > canvasEl.width) {
      newPanX = (viewportEl.offsetWidth - canvasEl.width) / 2;
    } else {
      newPanX = Math.max(viewportEl.offsetWidth - canvasEl.width, Math.min(newPanX, 0));
    }

    if (viewportEl.offsetHeight > canvasEl.height) {
      newPanY = (viewportEl.offsetHeight - canvasEl.height) / 2;
    } else {
      newPanY = Math.max(viewportEl.offsetHeight - canvasEl.height, Math.min(newPanY, 0));
    }

    panX.value = Number.isFinite(newPanX) ? newPanX : 0;
    panY.value = Number.isFinite(newPanY) ? newPanY : 0;
    logger.log(`[PdfViewer/renderPage] Pan updated: X=${panX.value}, Y=${panY.value}`);

    emit('rendered');
  } catch (err: any) {
    if (renderTask) renderTask = null;
    if (err.name === 'RenderingCancelledException') {
      logger.log("[PdfViewer/renderPage] Rendering cancelled.");
    } else {
      errorMsg.value = `[PdfViewer/renderPage] Error: ${err.message || 'Unknown error'}`;
      logger.error("[PdfViewer/renderPage] Exception:", err);
    }
  } finally {
    isRenderingPage.value = false;
    logger.log("[PdfViewer/renderPage] Finished.");
  }
}

async function loadPdf() {
  logger.log("[PdfViewer/loadPdf] Called with src:", props.src);
  if (!props.src) {
    errorMsg.value = "[PdfViewer/loadPdf] No PDF source.";
    logger.error(errorMsg.value);
    loading.value = false;
    return;
  }
  loading.value = true;
  errorMsg.value = null;
  if (renderTask) {
    try {
      renderTask.cancel();
    } catch (e) { /* ignore */ }
    renderTask = null;
  }
  if (pdfDoc) {
    try {
      await pdfDoc.destroy();
    } catch (e) { /* ignore */ }
    pdfDoc = null;
  }

  numPages.value = 0;
  currentPage.value = 1;
  currentPdfJsRenderScale.value = ensureValidScale(props.initialPdfRenderScale, "loadPdf initial scale");
  panX.value = 0;
  panY.value = 0;
  actualCanvasWidth_internal.value = 0;
  actualCanvasHeight_internal.value = 0;
  pdfPageOriginalWidth_internal.value = 0;
  pdfPageOriginalHeight_internal.value = 0;
  logger.log("[PdfViewer/loadPdf] Initial state reset. Current render scale set to:", currentPdfJsRenderScale.value);

  try {
    if (typeof window !== 'undefined' && !pdfjsLib.GlobalWorkerOptions.workerSrc) {
      pdfjsLib.GlobalWorkerOptions.workerSrc = PdfjsWorkerPath;
    }
    logger.log("[PdfViewer/loadPdf] Getting document...");
    const loadedDoc = await pdfjsLib.getDocument(props.src).promise;
    if (!loadedDoc) {
      pdfDoc = null;
      errorMsg.value = "[PdfViewer/loadPdf] Failed to load PDF document (loadedDoc is null).";
      logger.error(errorMsg.value);
    } else {
      pdfDoc = loadedDoc;
      numPages.value = loadedDoc.numPages;
      logger.log(`[PdfViewer/loadPdf] Document loaded. Pages: ${numPages.value}`);
      if (numPages.value > 0) {
        const firstPage = await pdfDoc.getPage(1);
        const viewportScale1 = firstPage.getViewport({scale: 1.0});
        logger.log(`[PdfViewer/loadPdf] Original viewport (scale 1.0): W=${viewportScale1.width}, H=${viewportScale1.height}`);

        const originalWidth = viewportScale1.width;
        const originalHeight = viewportScale1.height;

        if (!Number.isFinite(originalWidth) || originalWidth <= 0 || !Number.isFinite(originalHeight) || originalHeight <= 0) {
          errorMsg.value = `[PdfViewer/loadPdf] PDF page 1 has invalid original dimensions: W=${originalWidth}, H=${originalHeight}.`;
          logger.error(errorMsg.value);
          pdfPageOriginalWidth_internal.value = 0;
          pdfPageOriginalHeight_internal.value = 0;
        } else {
          pdfPageOriginalWidth_internal.value = originalWidth;
          pdfPageOriginalHeight_internal.value = originalHeight;
          logger.log(`[PdfViewer/loadPdf] Stored original PDF WxH: ${pdfPageOriginalWidth_internal.value}x${pdfPageOriginalHeight_internal.value}`);
          await renderPage(currentPage.value, currentPdfJsRenderScale.value);
          emit('scale-updated', currentPdfJsRenderScale.value); // <-- ADDED: Emit initial scale on load
          logger.log(`[PdfViewer/loadPdf] Emitted 'scale-updated' (initial) with scale: ${currentPdfJsRenderScale.value}`);
        }
      } else {
        errorMsg.value = "[PdfViewer/loadPdf] PDF has no pages.";
        logger.warn(errorMsg.value);
      }
    }
  } catch (err: any) {
    pdfDoc = null;
    errorMsg.value = `[PdfViewer/loadPdf] Exception: ${err.message || 'Unknown error'}`;
    logger.error("[PdfViewer/loadPdf] Exception:", err);
  } finally {
    loading.value = false;
    if (!errorMsg.value && pdfDoc) {
      emit('loaded');
      logger.log("[PdfViewer/loadPdf] 'loaded' event emitted.");
    }
    logger.log("[PdfViewer/loadPdf] Finished.");
  }
}

const changeZoom = (newScaleInput: number) => {
  logger.log(`[PdfViewer/changeZoom] Called with newScaleInput: ${newScaleInput}`);
  let validatedInputScale = newScaleInput;
  if (isNaN(validatedInputScale) || !Number.isFinite(validatedInputScale)) {
    logger.warn(`[PdfViewer/changeZoom] Initial newScaleInput (${newScaleInput}) is invalid. Using fallback via ensureValidScale.`);
    validatedInputScale = ensureValidScale(NaN, "changeZoom input correction");
  }

  let rawTargetScale = Math.max(props.pdfMinRenderScale, Math.min(props.pdfMaxRenderScale, validatedInputScale));
  let targetScale = parseFloat(rawTargetScale.toFixed(2));
  logger.log(`[PdfViewer/changeZoom] Clamped scale: ${rawTargetScale}, Parsed fixed(2): ${targetScale}`);

  if (isNaN(targetScale) || !Number.isFinite(targetScale) || targetScale <= 0) {
    logger.error(`[PdfViewer/changeZoom] Calculated targetScale is invalid: ${targetScale}. Applying robust fallback.`);
    targetScale = ensureValidScale(NaN, "changeZoom targetScale robust fallback");
    logger.error(`[PdfViewer/changeZoom] Robust fallback targetScale: ${targetScale}`);
  }

  const currentSafeRenderScale = (Number.isFinite(currentPdfJsRenderScale.value) && currentPdfJsRenderScale.value > 0)
      ? currentPdfJsRenderScale.value
      : ensureValidScale(NaN, "changeZoom currentSafeRenderScale fallback");

  logger.log(`[PdfViewer/changeZoom] Final targetScale: ${targetScale}, Current safe render scale: ${currentSafeRenderScale}`);
  if (targetScale !== currentSafeRenderScale) {
    if (renderDebounceTimer) clearTimeout(renderDebounceTimer);
    logger.log(`[PdfViewer/changeZoom] Debouncing renderPage with scale: ${targetScale}`);
    renderDebounceTimer = setTimeout(() => {
      if (pdfDoc) {
        renderPage(currentPage.value, targetScale);
      } else {
        logger.warn("[PdfViewer/changeZoom] PDF document not available for debounced render.");
      }
    }, 100);
  } else {
    logger.log("[PdfViewer/changeZoom] Target scale is same as current valid scale. No zoom change needed.");
  }
};

const documentMouseMoveHandler = (event: MouseEvent) => {
  if (!isDragging.value) return;
  event.preventDefault();
  const dx = event.clientX - dragStartX.value;
  const dy = event.clientY - dragStartY.value;
  panX.value = startPanX.value + dx;
  panY.value = startPanY.value + dy;
};

const documentMouseUpHandler = (event: MouseEvent) => {
  if (!isDragging.value) {
    document.removeEventListener('mousemove', documentMouseMoveHandler, true);
    document.removeEventListener('mouseup', documentMouseUpHandler, true);
    return;
  }
  isDragging.value = false;
  emit('panend');
  if (pdfViewportRef.value && props.interactionMode === 'pan') {
    pdfViewportRef.value.style.cursor = 'grab';
  }
  document.removeEventListener('mousemove', documentMouseMoveHandler, true);
  document.removeEventListener('mouseup', documentMouseUpHandler, true);
};

const handleMouseDown = (event: MouseEvent) => {
  if (props.interactionMode !== 'pan') return;
  if (!pdfViewportRef.value || !(event.target === pdfViewportRef.value || event.target === pdfCanvasElementRef.value)) return;
  event.preventDefault();
  if (event.button !== 0) return;

  isDragging.value = true;
  emit('panstart');
  dragStartX.value = event.clientX;
  dragStartY.value = event.clientY;
  startPanX.value = panX.value;
  startPanY.value = panY.value;
  if (pdfViewportRef.value) pdfViewportRef.value.style.cursor = 'grabbing';
  document.addEventListener('mousemove', documentMouseMoveHandler, true);
  document.addEventListener('mouseup', documentMouseUpHandler, true);
};

const handleMouseLeave = (event: MouseEvent) => {
  if (props.interactionMode !== 'pan') return;
  if (isDragging.value && event.buttons === 0) {
    documentMouseUpHandler(event);
  } else if (!isDragging.value && pdfViewportRef.value) {
    pdfViewportRef.value.style.cursor = 'grab';
  }
};

const handleWheelZoom = (event: WheelEvent) => {
  event.preventDefault();
  let newScaleDelta = props.pdfZoomStep * (event.ctrlKey ? 0.5 : 1); // Use 0.5 for finer control with Ctrl
  let currentScale = (Number.isFinite(currentPdfJsRenderScale.value) && currentPdfJsRenderScale.value > 0) ? currentPdfJsRenderScale.value : ensureValidScale(NaN, "wheelZoom currentScale");
  if (event.deltaY < 0) {
    changeZoom(currentScale + newScaleDelta);
  } else {
    changeZoom(currentScale - newScaleDelta);
  }
};

const triggerZoomIn = () => {
  let currentScale = (Number.isFinite(currentPdfJsRenderScale.value) && currentPdfJsRenderScale.value > 0) ? currentPdfJsRenderScale.value : ensureValidScale(NaN, "zoomIn currentScale");
  changeZoom(currentScale + props.pdfZoomStep);
};

const triggerZoomOut = () => {
  let currentScale = (Number.isFinite(currentPdfJsRenderScale.value) && currentPdfJsRenderScale.value > 0) ? currentPdfJsRenderScale.value : ensureValidScale(NaN, "zoomOut currentScale");
  changeZoom(currentScale - props.pdfZoomStep);
};

const triggerFullReset = () => {
  if (pdfDoc) {
    currentPage.value = 1;
    changeZoom(props.initialPdfRenderScale);
    panX.value = 0; // Also reset pan on full reset
    panY.value = 0;
  } else {
    currentPdfJsRenderScale.value = ensureValidScale(props.initialPdfRenderScale, "fullReset non-doc");
    panX.value = 0;
    panY.value = 0;
    actualCanvasWidth_internal.value = 0;
    actualCanvasHeight_internal.value = 0;
    pdfPageOriginalWidth_internal.value = 0;
    pdfPageOriginalHeight_internal.value = 0;
  }
};

const applyManualScale = (newScale: number) => {
  changeZoom(newScale);
};

const triggerGoToPage = (pageNumber: number) => {
  if (pageNumber >= 1 && pageNumber <= numPages.value && pageNumber !== currentPage.value && pdfDoc) {
    currentPage.value = pageNumber;
    renderPage(currentPage.value, currentPdfJsRenderScale.value);
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
  document.removeEventListener('mousemove', documentMouseMoveHandler, true);
  document.removeEventListener('mouseup', documentMouseUpHandler, true);
  if (renderDebounceTimer) clearTimeout(renderDebounceTimer);
  if (renderTask) {
    try {
      renderTask.cancel();
    } catch (e) { /* ignore */ }
    renderTask = null;
  }
  if (pdfDoc) {
    try {
      pdfDoc.destroy();
    } catch (e) {
      logger.error('Error destroying PDF document on unmount:', e);
    }
    pdfDoc = null;
  }
});

defineExpose({
  zoomIn: triggerZoomIn, zoomOut: triggerZoomOut, resetZoomAndPan: triggerFullReset,
  setPdfScale: applyManualScale, goToPage: triggerGoToPage, reloadPdf: loadPdf,
  currentScale: computed(() => currentPdfJsRenderScale.value),
  currentPageNum: computed(() => currentPage.value),
  totalPages: computed(() => numPages.value),
  isRendering: computed(() => isRenderingPage.value || loading.value),
  isLoading: computed(() => loading.value),
  minScale: props.pdfMinRenderScale, maxScale: props.pdfMaxRenderScale,
  getCanvasActualWidth: () => actualCanvasWidth_internal.value,
  getCanvasActualHeight: () => actualCanvasHeight_internal.value,
  getCanvasPanX: () => panX.value,
  getCanvasPanY: () => panY.value,
  getPdfPageOriginalWidth: () => pdfPageOriginalWidth_internal.value,
  getPdfPageOriginalHeight: () => pdfPageOriginalHeight_internal.value,
  initialPdfRenderScale: props.initialPdfRenderScale
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