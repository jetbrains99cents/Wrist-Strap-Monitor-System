<template>
  <div
      class="grid-overlay-root"
      :style="{
      display: 'grid',
      gridTemplateColumns: `repeat(${cols}, ${cellWidth}px)`,
      gridTemplateRows: `repeat(${rows}, ${cellHeight}px)`,
      width: `${cols * cellWidth}px`,
      height: `${rows * cellHeight}px`,
      pointerEvents: 'none',
    }"
  >
    <div
        v-for="r_idx in rows"
        :key="`row-${r_idx}`"
        class="grid-row-group"
        :style="{ display: 'contents' }" >
      <div
          v-for="c_idx in cols"
          :key="`cell-${r_idx - 1}-${c_idx - 1}`"
          class="grid-cell box-border"
          :class="getCellClasses(r_idx - 1, c_idx - 1)"
          :style="{
           width: `${cellWidth}px`,
           height: `${cellHeight}px`,
           pointerEvents: (isPdfPanning || interactionMode === 'pan') ? 'none' : 'auto',
         }"
          role="button"
          tabindex="0"
          :aria-label="`Grid cell row ${r_idx} column ${c_idx}`"
          @click="onCellClick(r_idx - 1, c_idx - 1)"
          @keydown.enter="onCellClick(r_idx - 1, c_idx - 1)"
          @keydown.space="onCellClick(r_idx - 1, c_idx - 1)"
      >
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {computed} from 'vue';

type InteractionMode = 'pan' | 'select';

interface Props {
  rows: number;
  cols: number;
  cellWidth: number;
  cellHeight: number;
  selectedCell: { row: number; col: number } | null;
  isPdfPanning: boolean;
  interactionMode: InteractionMode;
  // cellStatuses key is "row-col", e.g., "0-0", "1-2"
  // Value contains status and optionally device info
  cellStatuses: Record<string, { status: string, deviceId?: string, deviceName?: string }>;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  (e: 'cell-click', payload: { row: number; col: number }): void;
}>();

const onCellClick = (rowIndex: number, colIndex: number) => {
  if (props.interactionMode !== 'select' || props.isPdfPanning) return;
  emit('cell-click', {row: rowIndex, col: colIndex});
};

const isSelected = (rowIndex: number, colIndex: number) => {
  return props.selectedCell && props.selectedCell.row === rowIndex && props.selectedCell.col === colIndex;
};

const getCellClasses = (r: number, c: number) => {
  const key = `${r}-${c}`;
  const cellInfo = props.cellStatuses[key];
  const status = cellInfo?.status; // e.g., 'connected', 'disconnected', 'warning', 'error'

  let classes: Record<string, boolean | string> = {
    'border': true, // Apply border to all cells
    'box-border': true,
  };

  if (isSelected(r,c)) {
    classes['border-yellow-500'] = true;
    classes['dark:border-yellow-300'] = true;
    classes['bg-yellow-400'] = true;
    classes['dark:bg-yellow-500'] = true;
    classes['opacity-60'] = true; // Opacity for selected cell
    classes['blinking-cell'] = true; // Selected cells also blink
  } else if (status) {
    // Dynamically apply status class, e.g., 'cell-status-connected'
    classes[`cell-status-${status}`] = true;
    classes['border-gray-500'] = true;
    classes['dark:border-gray-600'] = true;
    classes['opacity-50'] = true; // Consistent opacity for all status cells
    classes['blinking-cell'] = true; // Add blinking class to all status cells
  } else {
    // Cells without status, and not selected (these are the faint grid lines)
    classes['border-blue-500'] = true;
    classes['dark:border-yellow-400'] = true;
    classes['opacity-10'] = true; // Make grid lines very faint

    if (props.interactionMode === 'select' && !props.isPdfPanning) {
      classes['hover:opacity-30'] = true;
      classes['hover:bg-gray-500'] = true;
      classes['hover:bg-opacity-10'] = true;
    }
  }
  return classes;
}

</script>

<style scoped>
.grid-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
  transition: background-color 0.15s ease-in-out, opacity 0.15s ease-in-out, border-color 0.15s ease-in-out;
}

.grid-cell[style*="pointer-events: auto"] { /* Style cells that are clickable */
  cursor: pointer;
}

/* Status specific backgrounds */
/* These colors will be moderated by the 'opacity-50' or 'opacity-60' class from getCellClasses */
.cell-status-connected {
  background-color: #22c55e; /* tailwind green-500 */
}
.cell-status-warning {
  background-color: #eab308; /* tailwind yellow-500 */
}
.cell-status-error {
  background-color: #f59e0b; /* tailwind amber-500 */
}
.cell-status-disconnected {
  background-color: #ef4444; /* tailwind red-500 */
}

/* Blinking Animation */
@keyframes blink {
  0%, 100% { opacity: inherit; }
  50% { opacity: 0.2; }
}

.blinking-cell {
  animation: blink 1000ms infinite ease-in-out; /* MODIFIED: Animation duration changed to 300ms */
}
</style>
