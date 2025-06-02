// overlay.js
// Responsible for drawing a tiling-style grid plus hover highlighting, selection,
// and now saved-cell blinking with a bright yellow LED-like effect.

const baseTileSize = 100;
let lastHoveredTile = null;
let selectionRect = null; // holds the current selection rectangle (if any)

/**
 * Draw the entire grid.
 * Optional parameters:
 *   - hoverTile: the cell currently hovered
 *   - selectionRect: an active selection rectangle (if any)
 *   - savedCells: an object holding saved cell data (mapData)
 *   - blinkVisible: a boolean indicating if saved cells should be drawn (for blinking effect)
 *   - currentViewport: the current PDF viewport (used to convert intrinsic coordinates to canvas coordinates)
 */
export function drawGrid(overlayCanvas, scale, hoverTile = null, selectionRect = null, savedCells = null, blinkVisible = false, currentViewport = null) {
  const ctx = overlayCanvas.getContext('2d');
  const width = overlayCanvas.width;
  const height = overlayCanvas.height;

  ctx.clearRect(0, 0, width, height);

  // Grid configuration
  const gridColor = 'rgba(0, 0, 255, 0.5)';  // blue lines
  let tileSize = baseTileSize / scale;
  if (tileSize < 5) tileSize = 5; // clamp minimum tile size

  ctx.strokeStyle = gridColor;
  ctx.lineWidth = 1;

  // Draw vertical grid lines
  for (let x = 0; x <= width; x += tileSize) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, height);
    ctx.stroke();
  }
  // Draw horizontal grid lines
  for (let y = 0; y <= height; y += tileSize) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(width, y);
    ctx.stroke();
  }

  // Draw selection rectangle (if any)
  if (selectionRect) {
    const startRow = Math.min(selectionRect.start.row, selectionRect.end.row);
    const endRow = Math.max(selectionRect.start.row, selectionRect.end.row);
    const startCol = Math.min(selectionRect.start.col, selectionRect.end.col);
    const endCol = Math.max(selectionRect.start.col, selectionRect.end.col);
    ctx.fillStyle = 'rgba(0, 255, 0, 0.3)'; // semi-transparent green

    for (let row = startRow; row <= endRow; row++) {
      for (let col = startCol; col <= endCol; col++) {
        const tileX = col * tileSize;
        const tileY = row * tileSize;
        ctx.fillRect(tileX, tileY, tileSize, tileSize);
      }
    }
  }

  // Draw saved cell highlights with blinking LED effect.
  // If blinkVisible is true, draw a bright yellow rectangle over each saved cell.
  if (savedCells && currentViewport) {
    if (blinkVisible) {
      // Get intrinsic dimensions from currentViewport.
      const intrinsicWidth = currentViewport.viewBox[2] - currentViewport.viewBox[0];
      const intrinsicHeight = currentViewport.viewBox[3] - currentViewport.viewBox[1];
      for (let key in savedCells) {
        const cellData = savedCells[key];
        // Convert saved intrinsic coordinates to canvas coordinates.
        const canvasX = (cellData.intrinsicX / intrinsicWidth) * width;
        const canvasY = (cellData.intrinsicY / intrinsicHeight) * height;
        console.debug("Drawing saved cell (LED) for key", key, "at canvas coordinates:", canvasX, canvasY);
        ctx.fillStyle = "rgba(255, 255, 0, 1)"; // bright yellow (LED-like)
        ctx.fillRect(canvasX, canvasY, tileSize, tileSize);
      }
    }
  }

  // Draw hover highlight if there is no active selection.
  if (hoverTile && !selectionRect) {
    const { col, row } = hoverTile;
    const tileX = col * tileSize;
    const tileY = row * tileSize;
    ctx.fillStyle = 'rgba(255, 255, 0, 0.3)'; // transparent yellow (for hover)
    ctx.fillRect(tileX, tileY, tileSize, tileSize);
  }
}

/**
 * Calculate which tile is hovered.
 */
export function handleMouseHover(overlayCanvas, scale, mouseX, mouseY) {
  const rect = overlayCanvas.getBoundingClientRect();
  const x = mouseX - rect.left;
  const y = mouseY - rect.top;
  let tileSize = baseTileSize / scale;
  if (tileSize < 5) tileSize = 5;
  const col = Math.floor(x / tileSize);
  const row = Math.floor(y / tileSize);

  if (!selectionRect && (!lastHoveredTile || lastHoveredTile.col !== col || lastHoveredTile.row !== row)) {
    lastHoveredTile = { col, row };
    drawGrid(overlayCanvas, scale, lastHoveredTile, selectionRect);
    return lastHoveredTile;
  }
  return null;
}

/** Reset hover (no tile highlighted) */
export function resetHover(overlayCanvas, scale) {
  lastHoveredTile = null;
  drawGrid(overlayCanvas, scale, null, selectionRect);
}

/** Set the current selection rectangle and re-draw */
export function setSelectionRect(overlayCanvas, scale, rect) {
  selectionRect = rect;
  drawGrid(overlayCanvas, scale, null, selectionRect);
}

/** Clear any active selection rectangle */
export function clearSelectionRect(overlayCanvas, scale) {
  selectionRect = null;
  drawGrid(overlayCanvas, scale);
}

/**
 * Given a mouse event coordinate, compute the tile (row, col)
 */
export function getTileAtPoint(overlayCanvas, scale, mouseX, mouseY) {
  const rect = overlayCanvas.getBoundingClientRect();
  const x = mouseX - rect.left;
  const y = mouseY - rect.top;
  let tileSize = baseTileSize / scale;
  if (tileSize < 5) tileSize = 5;
  const col = Math.floor(x / tileSize);
  const row = Math.floor(y / tileSize);
  return { row, col };
}
