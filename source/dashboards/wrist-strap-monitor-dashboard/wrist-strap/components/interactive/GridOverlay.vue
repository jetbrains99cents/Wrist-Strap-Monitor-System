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
        :style="{ display: 'contents' }"
    >
      <UTooltip
          v-for="c_idx in cols"
          :key="`tooltip-cell-${r_idx - 1}-${c_idx - 1}`"
          :text="getCellTooltip(r_idx - 1, c_idx - 1)"
          :popper="{ placement: 'top', arrow: true }"
          :ui="{
          base: 'invisible md:visible h-auto max-w-xs px-3 py-2 rounded-lg shadow-lg text-sm font-medium whitespace-pre-line',
          background: 'bg-white dark:bg-gray-900',
          color: 'text-gray-900 dark:text-white',
          ring: 'ring-1 ring-gray-200 dark:ring-gray-800',
          arrow: {
            base: 'before:bg-gray-200 dark:before:bg-gray-800',
          }
        }"
      >
        <div
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
      </UTooltip>
    </div>
  </div>
</template>

<script setup lang="ts">
import {computed} from 'vue';

type InteractionMode = 'pan' | 'select';

// --- Data Structures (Matching index.vue) ---
type LogStatus =
    "Connected"
    | "Disconnected"
    | "Voltage reading failed"
    | "Info"
    | "Warning"
    | "Error"
    | "Critical"
    | "Configured"
    | "Reset";
type EventCategory = "Connection" | "Sensor Reading" | "Alert" | "User action" | "System";

interface GridCellStatusInfo {
  status: LogStatus;
  deviceId: string;
  deviceName: string;
  installationArea?: string;
  lastEventType?: EventCategory;
  createdAtFormatted?: string;
  installedAtFormatted?: string;
}


interface Props {
  rows: number;
  cols: number;
  cellWidth: number;
  cellHeight: number;
  selectedCell: { row: number; col: number } | null;
  isPdfPanning: boolean;
  interactionMode: InteractionMode;
  cellStatuses: Record<string, GridCellStatusInfo>;
  // MODIFIED: Added props for translated labels
  tooltipNameLabel: string;
  tooltipAreaLabel: string;
  tooltipLastEventStatusLabel: string;
  tooltipLastEventTypeLabel: string;
  tooltipCreatedAtLabel: string;
  tooltipInstalledAtLabel: string;
  tooltipCellLabel: string;
  tooltipRowLabel: string; // Added for empty cell tooltip
  tooltipColLabel: string; // Added for empty cell tooltip
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
    'border': true,
    'box-border': true,
  };

  if (isSelected(r, c)) {
    classes['border-yellow-500'] = true;
    classes['dark:border-yellow-300'] = true;
    classes['bg-yellow-400'] = true;
    classes['dark:bg-yellow-500'] = true;
    classes['opacity-60'] = true;
    classes['blinking-cell'] = true;
  } else if (status) {
    const statusClass = status.toLowerCase().replace(/\s+/g, '-');
    classes[`cell-status-${statusClass}`] = true;
    classes['border-gray-500'] = true;
    classes['dark:border-gray-600'] = true;
    classes['opacity-50'] = true;
    classes['blinking-cell'] = true;
  } else {
    classes['border-blue-500'] = true;
    classes['dark:border-yellow-400'] = true;
    classes['opacity-10'] = true;

    if (props.interactionMode === 'select' && !props.isPdfPanning) {
      classes['hover:opacity-30'] = true;
      classes['hover:bg-gray-500'] = true;
      classes['hover:bg-opacity-10'] = true;
    }
  }
  return classes;
}

// MODIFIED: getCellTooltip to use props for labels
const getCellTooltip = (r: number, c: number): string => {
  const key = `${r}-${c}`;
  const cellInfo = props.cellStatuses[key];
  if (cellInfo && cellInfo.deviceName) {
    let tooltipLines: string[] = [];
    tooltipLines.push(`${props.tooltipNameLabel}: ${cellInfo.deviceName}`);
    if (cellInfo.installationArea) {
      tooltipLines.push(`${props.tooltipAreaLabel}: ${cellInfo.installationArea}`);
    }
    if (cellInfo.status) {
      // The status itself might need to be localized in index.vue before being passed
      // or a getLocalizedStatus function passed as prop/imported here.
      // For now, assuming cellInfo.status is already the display-ready string.
      tooltipLines.push(`${props.tooltipLastEventStatusLabel}: ${cellInfo.status}`);
    }
    if (cellInfo.lastEventType) {
      tooltipLines.push(`${props.tooltipLastEventTypeLabel}: ${cellInfo.lastEventType}`);
    }
    if (cellInfo.createdAtFormatted) {
      tooltipLines.push(`${props.tooltipCreatedAtLabel}: ${cellInfo.createdAtFormatted}`);
    }
    if (cellInfo.installedAtFormatted) {
      tooltipLines.push(`${props.tooltipInstalledAtLabel}: ${cellInfo.installedAtFormatted}`);
    }
    return tooltipLines.join('\n');
  }
  return `${props.tooltipCellLabel}: ${props.tooltipRowLabel} ${r}, ${props.tooltipColLabel} ${c}`;
};

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
.cell-status-connected {
  background-color: #22c55e;
}

.cell-status-warning {
  background-color: #eab308;
}

.cell-status-error {
  background-color: #f59e0b;
}

.cell-status-disconnected {
  background-color: #ef4444;
}

.cell-status-info {
  background-color: #3b82f6;
}

.cell-status-voltage-reading-failed {
  background-color: #ef4444;
}

.cell-status-configured {
  background-color: #a855f7;
}

.cell-status-reset {
  background-color: #6366f1;
}

.cell-status-critical {
  background-color: #dc2626;
}


/* Blinking Animation */
@keyframes blink {
  0%, 100% {
    opacity: inherit;
  }
  50% {
    opacity: 0.2;
  }
}

.blinking-cell {
  animation: blink 1.5s infinite ease-in-out;
}
</style>
