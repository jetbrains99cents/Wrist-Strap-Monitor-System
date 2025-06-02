<template>
  <div class="interactive-svg-viewer-wrapper">
    <div ref="panzoomContainer" class="panzoom-container w-full h-full overflow-hidden cursor-grab active:cursor-grabbing">
      <!-- SVG content will be inserted here -->
    </div>
    <div class="controls p-2 flex justify-center gap-2 bg-gray-100 dark:bg-dark-surface rounded-b-lg">
      <UButton size="sm" icon="i-heroicons-zoom-in-20-solid" @click="zoomIn" :aria-label="zoomInLabel" />
      <UButton size="sm" icon="i-heroicons-zoom-out-20-solid" @click="zoomOut" :aria-label="zoomOutLabel" />
      <UButton size="sm" icon="i-heroicons-arrows-pointing-out-20-solid" @click="resetPanzoom" :aria-label="resetViewLabel" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue';
import Panzoom from '@panzoom/panzoom'; // Import only the Panzoom function
import { useLanguage } from '~/composables/useLanguage';

const { currentLanguage } = useLanguage();

const props = defineProps({
  src: {
    type: String,
    required: true,
  },
  alt: {
    type: String,
    default: 'Interactive Layout',
  },
  maxScale: {
    type: Number,
    default: 4,
  },
  minScale: {
    type: Number,
    default: 0.3,
  }
});

const panzoomContainer = ref<HTMLElement | null>(null);
let panzoomInstance: ReturnType<typeof Panzoom> | null = null; // Correct type using ReturnType

const loadSvg = async () => {
  try {
    const response = await fetch(props.src);
    if (!response.ok) throw new Error('Failed to load SVG');
    const svgText = await response.text();
    if (panzoomContainer.value) {
      panzoomContainer.value.innerHTML = svgText;
      await nextTick();
      initializePanzoom();
    }
  } catch (error) {
    console.error('Error loading SVG:', error);
  }
};

const initializePanzoom = () => {
  if (panzoomContainer.value && !panzoomInstance) {
    panzoomInstance = Panzoom(panzoomContainer.value, {
      maxScale: props.maxScale,
      minScale: props.minScale,
      contain: 'outside',
      canvas: true,
      step: 0.2,
      cursor: '',
      setTransform: (elem, { x, y, scale }) => {
        elem.style.transform = `translate(${x}px, ${y}px) scale(${scale})`;
      }
    });
    panzoomContainer.value.addEventListener('wheel', handleWheelZoom, { passive: false });
  }
};

const handleWheelZoom = (event: WheelEvent) => {
  if (panzoomInstance) {
    event.preventDefault();
    panzoomInstance.zoomWithWheel(event);
  }
};

onMounted(() => {
  loadSvg();
});

onUnmounted(() => {
  if (panzoomInstance) {
    panzoomInstance.destroy();
    panzoomInstance = null;
  }
  if (panzoomContainer.value) {
    panzoomContainer.value.removeEventListener('wheel', handleWheelZoom);
  }
});

// Control functions for buttons
const zoomIn = () => panzoomInstance?.zoomIn();
const zoomOut = () => panzoomInstance?.zoomOut();
const resetPanzoom = () => panzoomInstance?.reset();

// Localized labels for controls
const zoomInLabel = computed(() => currentLanguage.value === 'vi' ? 'Phóng to' : 'Zoom In');
const zoomOutLabel = computed(() => currentLanguage.value === 'vi' ? 'Thu nhỏ' : 'Zoom Out');
const resetViewLabel = computed(() => currentLanguage.value === 'vi' ? 'Đặt lại' : 'Reset View');
</script>

<style scoped>
.interactive-svg-viewer-wrapper {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  border: 1px solid #ccc;
  border-radius: 0.5rem;
  overflow: hidden;
}

.panzoom-container {
  flex-grow: 1;
  position: relative;
}

.controls {
  flex-shrink: 0;
}
</style>