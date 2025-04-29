import * as pdfjsLib from '../libs/pdfjs/pdf.mjs';
import {
  drawGrid,
  handleMouseHover,
  resetHover,
  setSelectionRect,
  clearSelectionRect,
  getTileAtPoint
} from './overlay.js';

// PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = '../libs/pdfjs/pdf.worker.mjs';

console.debug("Starting app.js execution");

// Define base tile size (used for grid and intrinsic coordinate conversion)
const baseTileSize = 100;

// DOM references
const pdfContainer = document.getElementById('pdfContainer');
const pdfCanvas = document.getElementById('pdfCanvas');
const overlayCanvas = document.getElementById('overlayCanvas');
const ctx = pdfCanvas.getContext('2d');

const zoomOutBtn = document.getElementById('zoomOutBtn');
const zoomInBtn = document.getElementById('zoomInBtn');
const zoomInfo = document.getElementById('zoomInfo');

const renderOverlay = document.getElementById('renderOverlay');
const cellTooltip = document.getElementById('cellTooltip');

const cellModal = document.getElementById('cellModal');
const modalClose = document.getElementById('modalClose');
const modalCloseBtn = document.getElementById('modalCloseBtn');
const modalSave = document.getElementById('modalSave');
const modalCellInfo = document.getElementById('modalCellInfo');
const cellSettingInput = document.getElementById('cellSettingInput');
const saveCellDataCheckbox = document.getElementById('saveCellDataCheckbox');

// Global variable to store the current cell being edited.
let currentCell = null;

// Global object to store map data (cell-level data).
// Keys are generated from intrinsic (scale-invariant) coordinates.
let mapData = {};

// We'll store the current PDF viewport so we can access intrinsic dimensions.
let currentViewport = null;

// Global variables for blinking saved cells.
let blinkFlag = false;
let blinkInterval = null;

// Load existing map data from storage into mapData.
function loadMapData() {
  console.debug("loadMapData() called");
  fetch('../storage/map_data.json')
    .then(response => {
      console.debug("Fetching map_data.json, status:", response.status);
      return response.json();
    })
    .then(data => {
      mapData = data;
      console.debug("Loaded map data from file:", mapData);
    })
    .catch(err => {
      console.error("Error loading map_data.json:", err);
      mapData = {};
    });
}
loadMapData();

// Default values for PDF and zoom.
let pdfUrl = '../resources/factory_layout.pdf';
let scale = 4.0; // Default to 400%

let pdfDoc = null;
let currentPage = 1;
let rendering = false;

// Panning variables
let isDragging = false;
let startX, startY;
let offsetX = 0;
let offsetY = 0;

// Selection variables
let isSelecting = false;
let selectionStartTile = null;

// Variables to detect click for modal opening
let clickStartX = 0;
let clickStartY = 0;

/**
 * Load settings from config.json.
 */
function loadConfig() {
  console.debug("loadConfig() called");
  fetch('../config/config.json')
    .then(response => {
      console.debug("Fetching config.json, status:", response.status);
      return response.json();
    })
    .then(config => {
      if (config['default-zoom'] && !isNaN(config['default-zoom'])) {
        scale = config['default-zoom'] / 100;
        console.debug("Default zoom set from config:", scale);
      }
      if (config['factory-layout-path']) {
        pdfUrl = `../${config['factory-layout-path']}`;
        console.debug("PDF URL set from config:", pdfUrl);
      }
    })
    .catch(err => {
      console.error("Failed to load config.json. Using default settings.", err);
    })
    .finally(() => {
      loadPDF();
    });
}
loadConfig();

function loadPDF() {
  console.debug("loadPDF() called");
  pdfjsLib.getDocument(pdfUrl).promise
    .then(pdf => {
      pdfDoc = pdf;
      console.debug("PDF loaded, total pages:", pdf.numPages);
      renderPDF(scale);
    })
    .catch(err => {
      console.error("Failed to load PDF:", err);
    });
}

/**
 * Render the PDF at the given scale and save the current viewport.
 */
function renderPDF(newScale) {
  console.debug("renderPDF() called with newScale:", newScale);
  if (!pdfDoc || rendering) return;
  rendering = true;
  showOverlay();

  pdfDoc.getPage(currentPage).then(page => {
    const viewport = page.getViewport({ scale: newScale });
    currentViewport = viewport;
    pdfCanvas.width = viewport.width;
    pdfCanvas.height = viewport.height;
    overlayCanvas.width = viewport.width;
    overlayCanvas.height = viewport.height;
    console.debug("Rendering page with viewport:", viewport);
    return page.render({ canvasContext: ctx, viewport }).promise;
  }).then(() => {
    rendering = false;
    hideOverlay();
    scale = newScale;
    zoomInfo.value = `${Math.round(scale * 100)}%`;
    // Redraw grid including saved cells (blinkFlag may be false).
    drawGrid(overlayCanvas, scale, null, null, mapData, blinkFlag, currentViewport);
    console.debug("renderPDF() completed at scale:", scale);
  }).catch(err => {
    rendering = false;
    hideOverlay();
    console.error("Render error:", err);
  });
}

// Zoom In/Out Buttons
zoomInBtn.addEventListener('click', () => {
  console.debug("Zoom In button clicked");
  if (!rendering) {
    renderPDF(scale * 1.25);
  }
});

zoomOutBtn.addEventListener('click', () => {
  console.debug("Zoom Out button clicked");
  if (!rendering) {
    renderPDF(scale * 0.8);
  }
});

// Mouse Wheel Zoom
pdfContainer.addEventListener('wheel', (e) => {
  e.preventDefault();
  console.debug("Mouse wheel event, deltaY:", e.deltaY);
  if (rendering) return;
  let newScale = scale;
  if (e.deltaY < 0) {
    newScale *= 1.1;
  } else {
    newScale *= 0.9;
  }
  newScale = Math.max(0.2, Math.min(newScale, 10.0));
  renderPDF(newScale);
}, { passive: false });

// Manual Zoom Input
zoomInfo.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    console.debug("Manual zoom input Enter pressed");
    applyManualZoom();
  }
});

zoomInfo.addEventListener('blur', () => {
  console.debug("Manual zoom input blur event");
  applyManualZoom();
});

function applyManualZoom() {
  console.debug("applyManualZoom() called");
  let inputValue = zoomInfo.value.replace('%', '').trim();
  let newZoom = parseFloat(inputValue);
  if (!isNaN(newZoom) && newZoom > 0 && newZoom <= 1000) {
    renderPDF(newZoom / 100);
    console.debug("Manual zoom applied:", newZoom / 100);
  } else {
    zoomInfo.value = `${Math.round(scale * 100)}%`;
    console.debug("Manual zoom invalid, reset to current scale");
  }
}

// Panning Logic
pdfContainer.addEventListener('mousedown', (e) => {
  console.debug("Panning: mousedown event");
  isDragging = true;
  startX = e.clientX - offsetX;
  startY = e.clientY - offsetY;
  pdfContainer.style.cursor = 'grabbing';
});

pdfContainer.addEventListener('mousemove', (e) => {
  if (!isDragging) return;
  offsetX = e.clientX - startX;
  offsetY = e.clientY - startY;
  updatePosition();
});

pdfContainer.addEventListener('mouseup', () => {
  console.debug("Panning: mouseup event");
  isDragging = false;
  pdfContainer.style.cursor = 'grab';
});

pdfContainer.addEventListener('mouseleave', () => {
  console.debug("Panning: mouseleave event");
  isDragging = false;
  pdfContainer.style.cursor = 'grab';
});

// Modified Hover Logic on Grid Overlay
overlayCanvas.addEventListener('mousemove', (e) => {
  if (isDragging || rendering) return;
  const hovered = getTileAtPoint(overlayCanvas, scale, e.clientX, e.clientY);
  if (hovered) {
    cellTooltip.textContent = `Cell: row=${hovered.row}, col=${hovered.col} | Zoom: ${(scale * 100).toFixed(0)}%`;
    cellTooltip.style.left = (e.pageX + 10) + 'px';
    cellTooltip.style.top = (e.pageY + 10) + 'px';
    cellTooltip.style.visibility = 'visible';
  }
  // Always redraw grid with saved cells and blinking.
  drawGrid(overlayCanvas, scale, hovered, null, mapData, blinkFlag, currentViewport);
});

overlayCanvas.addEventListener('mouseleave', () => {
  if (!isDragging && !rendering) {
    resetHover(overlayCanvas, scale);
    cellTooltip.style.visibility = 'hidden';
    drawGrid(overlayCanvas, scale, null, null, mapData, blinkFlag, currentViewport);
    console.debug("Mouse left overlayCanvas, resetting hover");
  }
});

// Detect Click to Open Modal
overlayCanvas.addEventListener('mousedown', (e) => {
  console.debug("Overlay mousedown event");
  clickStartX = e.clientX;
  clickStartY = e.clientY;
  if (!isDragging && !rendering) {
    isSelecting = true;
    selectionStartTile = getTileAtPoint(overlayCanvas, scale, e.clientX, e.clientY);
    console.debug("Selection start tile:", selectionStartTile);
  }
});

overlayCanvas.addEventListener('mouseup', () => {
  console.debug("Overlay mouseup event");
  isSelecting = false;
});

overlayCanvas.addEventListener('click', (e) => {
  const clickThreshold = 5;
  if (Math.abs(e.clientX - clickStartX) < clickThreshold && Math.abs(e.clientY - clickStartY) < clickThreshold) {
    const clickedTile = getTileAtPoint(overlayCanvas, scale, e.clientX, e.clientY);
    console.debug("Overlay click event, clicked tile:", clickedTile);
    openCellModal(clickedTile);
  }
});

// --- Scale-Invariant Mapping Helpers ---
// Compute intrinsic coordinates (PDF coordinate system) for a given cell.
function computeIntrinsicCoordinates(cell) {
  if (!currentViewport) {
    console.error("computeIntrinsicCoordinates: currentViewport not defined");
    return { intrinsicX: 0, intrinsicY: 0 };
  }
  let tileSize = baseTileSize / scale; // cell size in canvas pixels
  const tileX = cell.col * tileSize;
  const tileY = cell.row * tileSize;
  const canvasWidth = overlayCanvas.width;
  const canvasHeight = overlayCanvas.height;
  const intrinsicWidth = currentViewport.viewBox[2] - currentViewport.viewBox[0];
  const intrinsicHeight = currentViewport.viewBox[3] - currentViewport.viewBox[1];
  const intrinsicX = (tileX / canvasWidth) * intrinsicWidth;
  const intrinsicY = (tileY / canvasHeight) * intrinsicHeight;
  console.debug("Computed intrinsic coordinates:", { tileX, tileY, intrinsicX, intrinsicY });
  return { intrinsicX, intrinsicY };
}

// Generate a key from intrinsic coordinates by rounding.
function intrinsicKey(cell) {
  const { intrinsicX, intrinsicY } = computeIntrinsicCoordinates(cell);
  const key = `${Math.round(intrinsicX)}-${Math.round(intrinsicY)}`;
  console.debug("Generated intrinsic key:", key);
  return key;
}

// --- Modal Logic ---
// When opening a cell modal, reset input and checkbox.
// If saved data exists (via intrinsic key), pre-populate and check the checkbox.
function openCellModal(cell) {
  console.debug("openCellModal() called with cell:", cell);
  currentCell = cell;
  modalCellInfo.innerHTML = `
    Settings for cell: row=${cell.row}, col=${cell.col}<br>
    <strong>Current Zoom:</strong> ${(scale * 100).toFixed(0)}%
  `;
  cellSettingInput.value = "";
  saveCellDataCheckbox.checked = false;
  
  const key = intrinsicKey(cell);
  if (mapData[key] && mapData[key].data.setting !== undefined) {
    cellSettingInput.value = mapData[key].data.setting;
    saveCellDataCheckbox.checked = true;
    console.debug("Existing cell data loaded for key", key, ":", mapData[key]);
  }
  cellModal.style.display = "flex";
}

function closeCellModal() {
  console.debug("closeCellModal() called");
  cellModal.style.display = "none";
}

modalClose.addEventListener('click', closeCellModal);
modalCloseBtn.addEventListener('click', closeCellModal);

// When Save is clicked, if the checkbox is checked, update mapData with intrinsic coordinates,
// the current scale, and the setting. Then start blinking. (API call is attempted.)
modalSave.addEventListener('click', () => {
  console.debug("Modal Save clicked");
  if (saveCellDataCheckbox && saveCellDataCheckbox.checked) {
    const key = intrinsicKey(currentCell);
    const intrinsicCoords = computeIntrinsicCoordinates(currentCell);
    const newCellData = {
      intrinsicX: Math.round(intrinsicCoords.intrinsicX),
      intrinsicY: Math.round(intrinsicCoords.intrinsicY),
      scale: scale, // Save the current scale as well.
      data: { setting: cellSettingInput.value }
    };
    mapData[key] = newCellData;
    console.debug("Updated mapData with new cell data for key", key, ":", newCellData);
    // Start infinite blinking.
    startBlinking();
    // Attempt the API call.
    fetch('../api/saveMapData', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(mapData)
    })
    .then(response => {
      console.debug("API saveMapData response status:", response.status);
      if (response.ok) {
        console.log('Cell data saved successfully via API.');
      } else {
        console.error('Error saving cell data via API:', response.statusText);
      }
      console.log("Full map data:", mapData);
    })
    .catch(err => {
      console.error("API call failed; skipping API save. Full map data:", mapData, err);
    });
  } else {
    console.debug("Cell data not saved (checkbox unchecked).");
  }
  closeCellModal();
});

// --- Blinking Saved Cells Animation ---
// Toggle blinkFlag every 500ms indefinitely so that saved cells blink like a LED.
function startBlinking() {
  if (blinkInterval) clearInterval(blinkInterval);
  blinkInterval = setInterval(() => {
    blinkFlag = !blinkFlag;
    console.debug("Blink flag toggled:", blinkFlag);
    drawGrid(overlayCanvas, scale, null, null, mapData, blinkFlag, currentViewport);
  }, 500);
}

// Update Canvas Position for Panning
function updatePosition() {
  console.debug("updatePosition() called, offsetX:", offsetX, "offsetY:", offsetY);
  pdfCanvas.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
  overlayCanvas.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
  cellTooltip.style.visibility = 'hidden';
}

function showOverlay() {
  console.debug("showOverlay() called");
  renderOverlay.classList.add('active');
}

function hideOverlay() {
  console.debug("hideOverlay() called");
  renderOverlay.classList.remove('active');
}
