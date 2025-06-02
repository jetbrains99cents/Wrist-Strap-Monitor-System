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
      opacity: 0.7,
    }"
  >
    <div
        v-for="row in rows"
        :key="`row-${row}`"
        class="grid-row-group"
        :style="{ display: 'contents' }"
    >
      <div
          v-for="col in cols"
          :key="`cell-${row - 1}-${col - 1}`"
          class="grid-cell border border-blue-500 dark:border-yellow-400 box-border"
          :class="{
          'bg-yellow-400 bg-opacity-30 dark:bg-yellow-500 dark:bg-opacity-40': isSelected(row - 1, col - 1)
        }"
          :style="{
           width: `${cellWidth}px`,
           height: `${cellHeight}px`,
           pointerEvents: isPdfPanning ? 'none' : 'auto', // Dynamic pointer-events
         }"
          role="button"
          tabindex="0"
          :aria-label="`Grid cell row ${row} column ${col}`"
          @click="onCellClick(row - 1, col - 1)"
          @keydown.enter="onCellClick(row - 1, col - 1)"
          @keydown.space="onCellClick(row - 1, col - 1)"
      >
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {computed} from 'vue';

interface Props {
  rows: number;
  cols: number;
  cellWidth: number;
  cellHeight: number;
  selectedCell: { row: number; col: number } | null;
  isPdfPanning: boolean; // New prop
}

const props = defineProps<Props>();

const emit = defineEmits<{
  (e: 'cell-click', payload: { row: number; col: number }): void;
}>();

const onCellClick = (rowIndex: number, colIndex: number) => {
  if (props.isPdfPanning) return; // Prevent click if PDF is being panned
  emit('cell-click', {row: rowIndex, col: colIndex});
};

const isSelected = (rowIndex: number, colIndex: number) => {
  return props.selectedCell && props.selectedCell.row === rowIndex && props.selectedCell.col === colIndex;
};
</script>

<style scoped>
.grid-overlay-root {
  /* This element is positioned by index.vue via the :style prop on the component tag. */
}

.grid-cell {
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
}

.grid-cell:hover {
  background-color: rgba(75, 85, 99, 0.1);
}

html.dark .grid-cell:hover {
  background-color: rgba(200, 200, 200, 0.1);
}
</style>