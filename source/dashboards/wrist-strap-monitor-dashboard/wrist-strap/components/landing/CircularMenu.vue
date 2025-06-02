<template>
  <div class="circular-menu-container relative w-[650px] h-[650px] mx-auto my-10">
    <div class="menu-items-orbit-wrapper">
      <div
          v-for="(item, index) in localizedMenuItems" :key="item.id"
          class="menu-item-wrapper absolute"
          :style="calculateItemPosition(index, localizedMenuItems.length)" >
        <MenuItem
            :label="item.label" :icon-src="item.iconSrc"
            :target-route="item.targetRoute"
            @item-click="handleItemClick"
            class="transform"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'; // Import computed
import MenuItem from './MenuItem.vue';
import { useLanguage } from '~/composables/useLanguage'; // Or Nuxt might auto-import it

// Use the language composable
const { currentLanguage } = useLanguage();

interface RawMenuItem { // Renamed to RawMenuItem for clarity
  id: string;
  label_en: string; // English label
  label_vi: string; // Vietnamese label
  iconSrc?: string;
  targetRoute?: string;
}

// This interface will be for the computed property
interface DisplayMenuItem {
  id: string;
  label: string; // The currently selected language's label
  iconSrc?: string;
  targetRoute?: string;
}

// Updated menuItems data with both English and Vietnamese labels
const rawMenuItems = ref<RawMenuItem[]>([
  {
    id: 'rfid',
    label_en: 'RFID System',
    label_vi: 'Hệ thống RFID',
    iconSrc: '/rfid-scanner.svg',
    targetRoute: '/rfid-details'
  },
  {
    id: 'production-analytics',
    label_en: 'Production Analytics',
    label_vi: 'Phân tích dữ liệu sản xuất',
    iconSrc: '/production-analytics.svg',
    targetRoute: '/production-analytics'
  },
  {
    id: 'wrist-strap',
    label_en: 'Wrist Strap\nMonitor',
    label_vi: 'Giám sát\nhộp xả tĩnh điện',
    iconSrc: '/wrist-strap.svg',
    targetRoute: '/wrist-strap'
  },
  {
    id: 'led-fpc-assembling-machine',
    label_en: 'LED FPC\nAssembling\nMachine',
    label_vi: 'Máy gắn\nLED FPC\ntự động',
    iconSrc: '/led-fpc-assembling-machine.png',
    targetRoute: '/led-fpc-assembling-machine',
  },
  {
    id: 'aoi',
    label_en: 'AOI',
    label_vi: 'AOI', // Assuming AOI is the same
    iconSrc: '/aoi.png',
    targetRoute: '/aoi',
  },
  {
    id: 'jig-monitor',
    label_en: 'JIG Monitor',
    label_vi: 'Giám sát JIG',
    iconSrc: '/jig.svg',
    targetRoute: '/jig-monitor'
  },
  {
    id: 'agv-system',
    label_en: 'AGV System',
    label_vi: 'Robot chở hàng',
    iconSrc: '/agv.png',
    targetRoute: '/agv-system',
  },
  {
    id: 'thermometer',
    label_en: 'Thermometer\nMonitor',
    label_vi: 'Giám sát\nnhiệt độ, độ ẩm',
    iconSrc: '/thermometer.svg',
    targetRoute: '/thermometer-monitor'
  },
]);

// Computed property to get menu items with labels based on the current language
const localizedMenuItems = computed((): DisplayMenuItem[] => {
  return rawMenuItems.value.map(item => ({
    ...item,
    label: currentLanguage.value === 'vi' ? item.label_vi : item.label_en,
  }));
});

const calculateItemPosition = (index: number, totalItems: number) => {
  const angle = (index / totalItems) * 360;
  const radius = 270;
  const angleRad = (angle - 90) * (Math.PI / 180);
  const itemOffsetWidth = 130 / 2;
  const itemOffsetHeight = 140 / 2;

  const x = `calc(50% + ${radius * Math.cos(angleRad)}px - ${itemOffsetWidth}px)`;
  const y = `calc(50% + ${radius * Math.sin(angleRad)}px - ${itemOffsetHeight}px)`;

  return {
    left: x,
    top: y,
  };
};

const handleItemClick = (label: string) => {
  console.log(`Event received from MenuItem: ${label} was clicked.`);
};
</script>

<style scoped>
/* ... (styles remain the same) ... */
.circular-menu-container {
  font-family: 'ABeeZee', sans-serif;
  position: relative;
}

@keyframes spin-around {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes counter-spin-around {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(-360deg);
  }
}

.menu-items-orbit-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  animation: spin-around 240s linear infinite;
  transform-origin: center center;
  will-change: transform;
  backface-visibility: hidden;
}

.menu-item-wrapper {
  animation: counter-spin-around 240s linear infinite;
  transform-origin: center center;
  transition: transform 0.3s ease;
  will-change: transform;
  backface-visibility: hidden;
}

.circular-menu-container:hover .menu-items-orbit-wrapper,
.circular-menu-container:hover .menu-item-wrapper {
  animation-play-state: paused;
}

.menu-item-wrapper:hover {
  transform: scale(1.1);
  z-index: 10;
}
</style>