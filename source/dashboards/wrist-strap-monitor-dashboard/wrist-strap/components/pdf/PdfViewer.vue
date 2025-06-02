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

async function renderPage(pageNum: number, pdfScaleToRender: number) {
  const canvasEl = pdfCanvasElementRef.value;
  const viewportEl = pdfViewportRef.value;

  if (!canvasEl || !viewportEl) {
    errorMsg.value = "Render prerequisites: Missing canvas or viewport element.";
    loading.value = false; // Though loading is more for loadPdf
    isRenderingPage.value = false;
    return;
  }

  const currentDocInstance = pdfDoc;
  if (!currentDocInstance) {
    errorMsg.value = "Render prerequisites: pdfDoc is null in renderPage.";
    loading.value = false; // Though loading is more for loadPdf
    isRenderingPage.value = false;
    return;
  }

  if (renderTask) {
    try { renderTask.cancel(); } catch (e) { /* ignore */ }
    renderTask = null;
  }

  isRenderingPage.value = true;
  errorMsg.value = null; // Clear previous render-specific errors

  try {
    const page = await currentDocInstance.getPage(pageNum);
    const viewport = page.getViewport({ scale: pdfScaleToRender });
    const context = canvasEl.getContext('2d');

    if (!context) {
      errorMsg.value = 'Failed to get canvas 2D context'; // Set error directly
      console.error(errorMsg.value);
      isRenderingPage.value = false; // Reset flag as render won't proceed
      return; // Exit function
    }

    canvasEl.height = viewport.height;
    canvasEl.width = viewport.width;
    currentPdfJsRenderScale.value = pdfScaleToRender;

    const renderContext = { canvasContext: context, viewport: viewport };
    renderTask = page.render(renderContext);

    await renderTask.promise;
    renderTask = null;

    await nextTick();
    panX.value = Math.max(0, (viewportEl.offsetWidth - canvasEl.width) / 2);
    panY.value = Math.max(0, (viewportEl.offsetHeight - canvasEl.height) / 2);

  } catch (err: any) {
    if(renderTask) renderTask = null;
    if (err.name === 'RenderingCancelledException' || (typeof err.message === 'string' && err.message.includes('Rendering cancelled'))) {
      // This is expected if a new render was initiated and cancelled this one
    } else {
      errorMsg.value = err.message || `Failed to render page ${pageNum}`;
      console.error('PDF Rendering Error:', err);
    }
  } finally {
    isRenderingPage.value = false; // Ensure this is always set
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
    try { renderTask.cancel(); } catch (e) { /* ignore */ }
    renderTask = null;
  }

  if (pdfDoc) {
    try { await pdfDoc.destroy(); } catch (e) { console.error('Error destroying previous pdfDoc:', e); }
    pdfDoc = null;
  }

  numPages.value = 0;
  currentPage.value = 1;
  currentPdfJsRenderScale.value = props.initialPdfRenderScale;
  panX.value = 0;
  panY.value = 0;

  try {
    if (typeof window !== 'undefined' && !pdfjsLib.GlobalWorkerOptions.workerSrc) {
      pdfjsLib.GlobalWorkerOptions.workerSrc = PdfjsWorkerPath;
    }

    const loadedDoc = await pdfjsLib.getDocument(props.src).promise;

    if (!loadedDoc) {
      pdfDoc = null; // Ensure component state is null
      errorMsg.value = "PDF document loading failed: getDocument resolved to a nullish value.";
      console.error(errorMsg.value);
      // No throw needed; the function will proceed to 'finally' where loading is set to false.
      // The rest of the try block is effectively skipped as pdfDoc remains null or further checks fail.
    } else {
      // This block executes only if loadedDoc is valid
      pdfDoc = loadedDoc;
      numPages.value = loadedDoc.numPages; // Use the validated local const

      if (numPages.value > 0) {
        await renderPage(currentPage.value, currentPdfJsRenderScale.value);
      } else {
        errorMsg.value = "The PDF document has no pages to display.";
      }
    }
  } catch (err: any) {
    pdfDoc = null; // Ensure component-level pdfDoc is null if any error occurs
    errorMsg.value = err.message || 'Failed to load PDF document';
    console.error('loadPdf: Error:', err);
  } finally {
    loading.value = false; // This will always run
  }
}

// --- Mouse Panning Logic --- (remains unchanged)
const handleMouseDown = (event: MouseEvent) => {
  if (!pdfViewportRef.value || !(event.target === pdfViewportRef.value || event.target === pdfCanvasElementRef.value)) return;
  if (event.button !== 0) return;
  isDragging.value = true;
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
  panX.value = startPanX.value + dx;
  panY.value = startPanY.value + dy;
};

const handleMouseUp = () => {
  if (!isDragging.value) return;
  isDragging.value = false;
  if (pdfViewportRef.value) pdfViewportRef.value.style.cursor = 'grab';
};

const handleMouseLeave = () => {
  if (isDragging.value) {
    handleMouseUp();
  }
};

// --- Zoom Logic --- (remains unchanged)
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
  panX.value = 0;
  panY.value = 0;
  if (pdfDoc) {
    renderPage(currentPage.value, props.initialPdfRenderScale);
  } else {
    currentPdfJsRenderScale.value = props.initialPdfRenderScale;
  }
};

const applyManualScale = (newScale: number) => {
  const targetScale = parseFloat(Math.max(props.pdfMinRenderScale, Math.min(props.pdfMaxRenderScale, newScale)).toFixed(2));
  changeZoom(targetScale);
};

// --- Page Navigation & Lifecycle --- (remains unchanged)
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
    try { renderTask.cancel(); } catch (e) { /* ignore */ }
    renderTask = null;
  }
  if (pdfDoc) {
    try {
      pdfDoc.destroy();
    } catch(e) { console.error('Error destroying PDF document on unmount:', e); }
    pdfDoc = null;
  }
});

// --- Expose --- (remains unchanged)
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
  isRendering: computed(() => isRenderingPage.value),
  isLoading: computed(() => loading.value),
  minScale: props.pdfMinRenderScale,
  maxScale: props.pdfMaxRenderScale,
});
</script>

<style scoped>
.pdf-viewer-wrapper {
  background-color: #f0f0f0; /* Fallback if not overridden by dark mode */
}

html.dark .pdf-viewer-wrapper {
  background-color: #2d3748; /* Dark mode background */
}

.pdf-canvas {
  display: block; /* Removes extra space below canvas */
  /* transform-origin: 0 0; */ /* Better to control precisely with panX/panY from center logic */
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
  font-family: 'ABeeZee', sans-serif; /* Ensure font is available */
  text-align: center;
  pointer-events: none; /* Allow interaction with underlying elements if necessary */
}

.error-indicator {
  background-color: rgba(220, 38, 38, 0.9); /* Red for error messages */
}

/* This style is applied when isRenderingPage is true AND loading is false */
.loading-indicator.bottom-16 {
  bottom: 4rem; /* Adjust as needed, roughly 64px from bottom */
  top: auto;
  transform: translateX(-50%); /* Keep it centered horizontally */
  left: 50%;
}
</style>