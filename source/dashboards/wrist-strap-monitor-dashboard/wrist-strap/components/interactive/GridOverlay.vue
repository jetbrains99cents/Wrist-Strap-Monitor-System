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
      /* Opacity is now handled by individual cell classes more directly */
    }"
  >
    <div
        v-for="r_idx in rows"
        :key="`row-${r_idx}`"
        class="grid-row-group"
        :style="{ display: 'contents' }"
    >
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
  cellStatuses: Record<string, { status: string, deviceId?: string, deviceName?: string }>; // Key: "row-col"
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
  const status = cellInfo?.status;

  let classes: Record<string, boolean | string> = {
    'border': true, // Apply border to all cells
    'box-border': true,
  };

  if (isSelected(r,c)) {
    classes['border-yellow-500'] = true; // Specific border for selected
    classes['dark:border-yellow-300'] = true;
    classes['bg-yellow-400'] = true;    // Background for selected
    classes['dark:bg-yellow-500'] = true;
    classes['opacity-60'] = true;       // Opacity for selected
  } else if (status) {
    classes[`cell-status-${status}`] = true; // Applies specific background color via CSS
    classes['border-gray-500'] = true;       // Border for status cells
    classes['dark:border-gray-600'] = true;
    classes['opacity-50'] = true;            // Consistent opacity for all status cells
                                             // (e.g., 50% transparent to see PDF behind)
  } else {
    // Cells without status, and not selected (these are the faint grid lines)
    classes['border-blue-500'] = true;
    classes['dark:border-yellow-400'] = true;
    classes['opacity-10'] = true; // Make grid lines very faint
    // Optionally, add a hover effect for empty, interactive cells
    if (props.interactionMode === 'select' && !props.isPdfPanning) {
      classes['hover:opacity-30'] = true;
      classes['hover:bg-gray-500'] = true; // Faint hover background
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

.grid-cell[style*="pointer-events: auto"] {
  cursor: pointer;
}

/* Status specific backgrounds */
/* These colors will be moderated by the 'opacity-50' class from getCellClasses */
.cell-status-connected {
  background-color: #22c55e; /* green-500 */
}
.cell-status-error { /* This will be yellow, suitable for "warning/problematic" */
  background-color: #eab308; /* yellow-500 */
}
.cell-status-disconnected {
  background-color: #ef4444; /* red-500 */
}
</style>