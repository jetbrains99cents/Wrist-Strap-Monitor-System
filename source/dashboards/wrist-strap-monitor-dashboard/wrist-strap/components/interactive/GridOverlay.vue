<template>
  <div
      class="grid-overlay-root"
      :style="{
      display: 'grid',
      gridTemplateColumns: `repeat(${cols}, ${cellWidth}px)`,
      gridTemplateRows: `repeat(${rows}, ${cellHeight}px)`,
      width: `${cols * cellWidth}px`,
      height: `${rows * cellHeight}px`,
      pointerEvents: 'auto',
    }"
      @mouseleave="onOverlayMouseLeave"
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
          :title="getCellTooltipText(r_idx - 1, c_idx - 1)"
          @click="onCellClick(r_idx - 1, c_idx - 1)"
          @keydown.enter="onCellClick(r_idx - 1, c_idx - 1)"
          @keydown.space="onCellClick(r_idx - 1, c_idx - 1)"
          @mouseenter="onCellMouseEnter(r_idx - 1, c_idx - 1, $event)"
          @mouseleave="onCellMouseLeave"
      >
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// --- Type Definitions ---
type InteractionMode = 'pan' | 'select';
type LogStatus =
    "Connected"
    | "Disconnected"
    | "Voltage reading ok"
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
  color: string; // Expects a color NAME, e.g., 'amber'
  installationArea?: string;
  lastEventType?: EventCategory | null;
  createdAtFormatted?: string;
  installedAtFormatted?: string;
  localizedStatus: string;
  localizedEventType: string;
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
  tooltipNameLabel: string;
  tooltipAreaLabel: string;
  tooltipLastEventStatusLabel: string;
  tooltipLastEventTypeLabel: string;
  tooltipCreatedAtLabel: string;
  tooltipInstalledAtLabel: string;
  tooltipCellLabel: string;
  tooltipRowLabel: string;
  tooltipColLabel: string;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  (e: 'cell-click', payload: { row: number; col: number }): void;
  (e: 'cell-mouse-enter', payload: { row: number; col: number; event: MouseEvent }): void;
  (e: 'cell-mouse-leave'): void;
}>();

// --- MODIFICATION: This "translator" function now lives inside the component ---
const mapColorNameToTailwindClass = (colorName?: string): string => {
  if (!colorName) return 'bg-slate-400 dark:bg-slate-700';

  const colorClassMap: Record<string, string> = {
    green: 'bg-green-500',
    red: 'bg-red-500',
    amber: 'bg-amber-500',
    yellow: 'bg-yellow-500',
    blue: 'bg-blue-500',
    orange: 'bg-orange-500',
    purple: 'bg-purple-500',
    indigo: 'bg-indigo-500',
    slate: 'bg-slate-400 dark:bg-slate-700'
  };
  return colorClassMap[colorName.toLowerCase()] || 'bg-slate-400 dark:bg-slate-700';
};


const onCellClick = (rowIndex: number, colIndex: number) => {
  if (props.interactionMode !== 'select' || props.isPdfPanning) return;
  emit('cell-click', {row: rowIndex, col: colIndex});
};

const onCellMouseEnter = (rowIndex: number, colIndex: number, event: MouseEvent) => {
  if (props.interactionMode !== 'select' || props.isPdfPanning) return;
  emit('cell-mouse-enter', {row: rowIndex, col: colIndex, event});
};

const onCellMouseLeave = () => {
  emit('cell-mouse-leave');
};

const onOverlayMouseLeave = () => {
  emit('cell-mouse-leave');
}

const isSelected = (rowIndex: number, colIndex: number) => {
  return props.selectedCell && props.selectedCell.row === rowIndex && props.selectedCell.col === colIndex;
};

const getCellClasses = (r: number, c: number) => {
  const key = `${r}-${c}`;
  const cellInfo = props.cellStatuses[key];

  let classes: Record<string, any> = {
    'border': true,
    'box-border': true,
  };

  if (isSelected(r, c)) {
    classes['border-yellow-500 dark:border-yellow-300'] = true;
    classes['bg-yellow-400 dark:bg-yellow-500'] = true;
    classes['opacity-60'] = true;
  } else if (cellInfo) {
    // --- MODIFICATION: Use the internal translator to get the correct CSS class ---
    const bgColorClass = mapColorNameToTailwindClass(cellInfo.color);
    classes[bgColorClass] = true;

    classes['border-gray-500 dark:border-gray-600'] = true;
    classes['opacity-50'] = true;
  } else {
    classes['border-blue-500 dark:border-yellow-400'] = true;
    classes['opacity-10'] = true;

    if (props.interactionMode === 'select' && !props.isPdfPanning) {
      classes['hover:opacity-30 hover:bg-gray-500 hover:bg-opacity-10'] = true;
    }
  }
  return classes;
}

const getCellTooltipText = (r: number, c: number): string => {
  const key = `${r}-${c}`;
  const cellInfo = props.cellStatuses[key];
  if (cellInfo && cellInfo.deviceName) {
    let tooltipLines: string[] = [];
    tooltipLines.push(`${props.tooltipNameLabel}: ${cellInfo.deviceName}`);

    if (cellInfo.installationArea) {
      tooltipLines.push(`${props.tooltipAreaLabel}: ${cellInfo.installationArea}`);
    }

    if (cellInfo.localizedStatus) {
      tooltipLines.push(`${props.tooltipLastEventStatusLabel}: ${cellInfo.localizedStatus}`);
    }

    if (cellInfo.localizedEventType) {
      tooltipLines.push(`${props.tooltipLastEventTypeLabel}: ${cellInfo.localizedEventType}`);
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
</style>