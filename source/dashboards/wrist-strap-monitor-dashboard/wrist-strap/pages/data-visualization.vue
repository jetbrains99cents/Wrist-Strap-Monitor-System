<template>
  <div class="flex flex-1 min-h-0 overflow-hidden">
    <!-- Desktop Sidebar -->
    <aside
        class="hidden md:flex md:flex-col bg-gray-100 dark:bg-dark-surface border-r border-gray-200 dark:border-dark-border p-4 w-60 lg:w-64 overflow-y-auto shrink-0"
        aria-label="Desktop Dashboard Navigation"
    >
      <UVerticalNavigation
          :links="localizedNavigationItems"
          :ui="{
            base: 'group relative flex items-start gap-x-3',
            padding: 'px-3 py-2.5',
            label: 'text-base whitespace-pre-line break-words text-left',
            icon: { base: 'flex-shrink-0 w-5 h-5 mt-0.5' }
          }"
      />
    </aside>

    <!-- Main Content Area -->
    <section class="flex-1 flex flex-col overflow-hidden p-4 sm:p-6 md:p-8">
      <div class="md:hidden mb-4 shrink-0">
        <UButton
            icon="i-heroicons-bars-3-20-solid"
            color="gray"
            variant="ghost"
            aria-label="Open navigation menu"
            @click="isMobileMenuOpen = true"
        />
      </div>

      <!-- Filter Bar -->
      <div class="filter-bar shrink-0 mb-6 p-4 bg-gray-50 dark:bg-dark-surface rounded-lg shadow">
        <div class="flex flex-col sm:flex-row flex-wrap items-center gap-4">
          <div class="flex items-center gap-3">
            <span class="text-base font-medium text-gray-700 dark:text-gray-300">{{ dateRangeLabel }}:</span>
            <UButtonGroup size="md" orientation="horizontal">
              <UButton :label="todayLabel" @click="setDateRange('today')"
                       :variant="selectedDateRange === 'today' ? 'solid' : 'outline'"/>
              <UButton :label="last7DaysLabel" @click="setDateRange('7days')"
                       :variant="selectedDateRange === '7days' ? 'solid' : 'outline'"/>
              <UButton :label="last30DaysLabel" @click="setDateRange('30days')"
                       :variant="selectedDateRange === '30days' ? 'solid' : 'outline'"/>
              <UButton :label="allTimeLabel" @click="setDateRange('all')"
                       :variant="selectedDateRange === 'all' ? 'solid' : 'outline'"/>
            </UButtonGroup>
          </div>

          <USelectMenu
              v-model="selectedArea"
              :options="areaOptions"
              value-attribute="value"
              option-attribute="label"
              :placeholder="areaFilterPlaceholder"
              class="min-w-[200px]"
              size="md"
              aria-label="Area Filter"
          />
          <USelectMenu
              v-model="selectedMetric"
              :options="metricOptions"
              value-attribute="value"
              option-attribute="label"
              :placeholder="metricFilterPlaceholder"
              class="min-w-[240px]"
              size="md"
              aria-label="Metric Filter"
          />
        </div>
      </div>

      <!-- Key Metrics -->
      <div class="key-metrics shrink-0 mb-6">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <UCard
              v-for="metric in keyMetrics"
              :key="metric.id"
              :ui="{
              base: 'transition-all duration-200 ease-in-out',
              background: 'bg-white dark:bg-gray-900 hover:bg-gray-50 dark:hover:bg-slate-800',
              ring: 'ring-1 ring-gray-200 dark:ring-gray-800 hover:ring-primary-500 dark:hover:ring-primary-400',
              body: { padding: 'p-5 sm:p-6' }
            }"
          >
            <p class="text-base text-gray-500 dark:text-gray-400 mb-1">{{ metric.label }}</p>
            <p class="text-3xl font-semibold text-gray-900 dark:text-white">{{ metric.value }}</p>
          </UCard>
        </div>
      </div>

      <!-- Chart Display Area and Controls -->
      <div class="chart-display-wrapper flex flex-col flex-grow min-h-0">
        <div class="chart-display-area flex-grow min-h-0 relative bg-white dark:bg-dark-surface-alt rounded-lg shadow">
          <div v-if="isLoadingChart"
               class="absolute inset-0 flex items-center justify-center bg-opacity-50 bg-gray-200 dark:bg-opacity-50 dark:bg-gray-800 z-10 rounded-lg">
            <UIcon name="i-heroicons-arrow-path" class="animate-spin h-12 w-12 text-primary-500"/>
          </div>
          <div v-else-if="!selectedMetric || !chartData || chartData.datasets.length === 0"
               class="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
            <p>{{ selectedMetric ? noDataAvailableLabel : selectMetricPrompt }}</p>
          </div>
          <div v-else class="chart-container w-full h-full overflow-x-auto custom-scrollbar">
            <Line v-if="selectedMetric === 'connectionStatusTimeline'" :data="chartData"
                  :options="dynamicChartOptions as ChartOptions<'line'>" :ref="(el: any) => chartComponentRef = el"/>
            <Line v-else-if="selectedMetric === 'voltageReadings'" :data="chartData"
                  :options="dynamicChartOptions as ChartOptions<'line'>" :ref="(el: any) => chartComponentRef = el"/>
            <Bar v-else-if="selectedMetric === 'alertFrequencies'" :data="chartData"
                 :options="dynamicChartOptions as ChartOptions<'bar'>" :ref="(el: any) => chartComponentRef = el"/>
            <Bar v-else-if="selectedMetric === 'deviceDistribution'" :data="chartData"
                 :options="dynamicChartOptions as ChartOptions<'bar'>" :ref="(el: any) => chartComponentRef = el"/>
            <Pie v-else-if="selectedMetric === 'deviceStatusOverview'" :data="chartData"
                 :options="dynamicChartOptions as ChartOptions<'pie'>" :ref="(el: any) => chartComponentRef = el"/>
          </div>
        </div>
        <!-- Chart Controls -->
        <div class="chart-controls mt-4 flex justify-center gap-3 shrink-0">
          <UButton
              @click="togglePan"
              :variant="isPanEnabled ? 'solid' : 'outline'"
              :label="isPanEnabled ? panDisableLabel : panEnableLabel"
              :icon="isPanEnabled ? 'i-heroicons-arrows-pointing-out' : 'i-heroicons-arrows-pointing-in'"
          />
          <UButton
              @click="toggleZoom"
              :variant="isZoomEnabled ? 'solid' : 'outline'"
              :label="isZoomEnabled ? zoomDisableLabel : zoomEnableLabel"
              :icon="isZoomEnabled ? 'i-heroicons-magnifying-glass-minus-solid' : 'i-heroicons-magnifying-glass-plus-solid'"
          />
          <UButton
              @click="resetChartZoom"
              :label="resetZoomLabel"
              icon="i-heroicons-arrow-path-rounded-square"
              variant="outline"
          />
        </div>
      </div>
    </section>

    <!-- Mobile Sidebar -->
    <USlideover v-model="isMobileMenuOpen" side="left" :ui="{ width: 'max-w-xs w-full sm:w-72' }">
      <UCard class="flex flex-col flex-1 h-full"
             :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800', body: { padding: '', base: 'flex-1 overflow-y-auto' } }">
        <template #header>
          <div class="flex items-center justify-between p-4">
            <h3 class="text-lg font-semibold text-gray-800 dark:text-dark-text-primary">{{ mobileMenuTitle }}</h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" @click="isMobileMenuOpen = false"/>
          </div>
        </template>
        <div class="p-4">
          <UVerticalNavigation
              :links="localizedNavigationItems"
              :ui="{ base: 'group relative flex items-start gap-x-3', padding: 'px-3 py-3', label: 'text-base whitespace-pre-line break-words text-left', icon: { base: 'flex-shrink-0 w-5 h-5 mt-0.5' }}"
              @click="isMobileMenuOpen = false"
          />
        </div>
      </UCard>
    </USlideover>
  </div>
</template>

<script setup lang="ts">
import {ref, computed, watch, onMounted} from 'vue';
import {useLanguage} from '~/composables/useLanguage';
import {useColorMode} from '@vueuse/core';
import {Line, Bar, Pie} from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  ArcElement,
  Colors
} from 'chart.js'
import type {ChartOptions, Plugin, ChartType} from 'chart.js';
import zoomPlugin from 'chartjs-plugin-zoom';

const customCanvasBackgroundColor: Plugin = {
  id: 'customCanvasBackgroundColor',
  beforeDraw: (chart: ChartJS, args: any, pluginOptions: { color?: string }) => {
    const {ctx} = chart;
    const color = pluginOptions.color || 'rgba(255,255,255,1)';

    ctx.save();
    ctx.globalCompositeOperation = 'destination-over';
    ctx.fillStyle = color;
    ctx.fillRect(0, 0, chart.width, chart.height);
    ctx.restore();
  }
};

ChartJS.register(
    Title,
    Tooltip,
    Legend,
    LineElement,
    BarElement,
    CategoryScale,
    LinearScale,
    PointElement,
    ArcElement,
    Colors,
    customCanvasBackgroundColor,
    zoomPlugin
);


const {currentLanguage} = useLanguage();
const colorMode = useColorMode();

const isMobileMenuOpen = ref(false);
const chartComponentRef = ref<any | null>(null);

const rawNavigationItems = ref([
  {id: 'home', label_en: 'Home', label_vi: 'Trang chủ', icon: 'i-heroicons-home-solid', to: '/'},
  {
    id: 'device-list',
    label_en: 'Device List',
    label_vi: 'Danh sách thiết bị',
    icon: 'i-heroicons-queue-list-solid',
    to: '/device-list'
  },
  {
    id: 'device-management',
    label_en: 'Device Management',
    label_vi: 'Quản lý thiết bị',
    icon: 'i-heroicons-cog-8-tooth-solid',
    to: '/device-management'
  },
  {
    id: 'production-plan',
    label_en: 'Production Plan\n& Working Time',
    label_vi: 'Kế hoạch & Thời gian\nsản xuất',
    icon: 'i-heroicons-calendar-days-solid',
    to: '/production-plan'
  },
  {
    id: 'data-visualization',
    label_en: 'Data Visualization',
    label_vi: 'Trực quan hóa dữ liệu',
    icon: 'i-heroicons-chart-pie-solid',
    to: '/data-visualization'
  },
  {
    id: 'data-analysis',
    label_en: 'Data Analysis',
    label_vi: 'Phân tích dữ liệu',
    icon: 'i-heroicons-presentation-chart-line-solid',
    to: '/data-analysis'
  },
]);
const localizedNavigationItems = computed(() => rawNavigationItems.value.map(item => ({
  id: item.id,
  label: currentLanguage.value === 'vi' ? item.label_vi : item.label_en,
  icon: item.icon,
  to: item.to,
})));

const pageTitle = computed(() => currentLanguage.value === 'vi' ? 'Trực quan hóa Dữ liệu' : 'Data Visualization');
const dateRangeLabel = computed(() => currentLanguage.value === 'vi' ? 'Phạm vi Ngày' : 'Date Range');
const todayLabel = computed(() => currentLanguage.value === 'vi' ? 'Hôm nay' : 'Today');
const last7DaysLabel = computed(() => currentLanguage.value === 'vi' ? '7 ngày qua' : 'Last 7 Days');
const last30DaysLabel = computed(() => currentLanguage.value === 'vi' ? '30 ngày qua' : 'Last 30 Days');
const allTimeLabel = computed(() => currentLanguage.value === 'vi' ? 'Tất cả' : 'All Time');
const areaFilterPlaceholder = computed(() => currentLanguage.value === 'vi' ? 'Tất cả khu vực' : 'All Areas');
const metricFilterPlaceholder = computed(() => currentLanguage.value === 'vi' ? 'Chọn loại số liệu' : 'Select Metric Type');
const mobileMenuTitle = computed(() => currentLanguage.value === 'vi' ? 'Menu' : 'Menu');

const totalActiveDevicesLabel = computed(() => currentLanguage.value === 'vi' ? 'Tổng thiết bị hoạt động' : 'Total Active Devices');
const overallUptimeLabel = computed(() => currentLanguage.value === 'vi' ? '% Thời gian hoạt động' : 'Overall Uptime %');
const totalAlertsLabel = computed(() => currentLanguage.value === 'vi' ? 'Tổng cảnh báo' : 'Total Alerts');
const averageVoltageLabel = computed(() => currentLanguage.value === 'vi' ? 'Điện áp trung bình' : 'Average Voltage');

const noDataAvailableLabel = computed(() => currentLanguage.value === 'vi' ? 'Không có dữ liệu cho các tiêu chí đã chọn.' : 'No data available for the selected criteria.');
const selectMetricPrompt = computed(() => currentLanguage.value === 'vi' ? 'Vui lòng chọn một loại số liệu để hiển thị biểu đồ.' : 'Please select a metric type to display a chart.');

const connectionStatusTimelineLabel = computed(() => currentLanguage.value === 'vi' ? 'Dòng thời gian trạng thái kết nối' : 'Connection Status Timeline');
const voltageReadingsLabel = computed(() => currentLanguage.value === 'vi' ? 'Giá trị điện áp' : 'Voltage Readings');
const alertFrequenciesLabel = computed(() => currentLanguage.value === 'vi' ? 'Tần suất cảnh báo' : 'Alert Frequencies');
const deviceDistributionLabel = computed(() => currentLanguage.value === 'vi' ? 'Phân bố thiết bị' : 'Device Distribution');
const deviceStatusOverviewLabel = computed(() => currentLanguage.value === 'vi' ? 'Tổng quan trạng thái thiết bị' : 'Device Status Overview');

// MODIFIED: Chart control button labels casing
const panEnableLabel = computed(() => currentLanguage.value === 'vi' ? 'Bật kéo' : 'Enable pan');
const panDisableLabel = computed(() => currentLanguage.value === 'vi' ? 'Tắt kéo' : 'Disable pan');
const zoomEnableLabel = computed(() => currentLanguage.value === 'vi' ? 'Bật thu phóng' : 'Enable zoom');
const zoomDisableLabel = computed(() => currentLanguage.value === 'vi' ? 'Tắt thu phóng' : 'Disable zoom');
const resetZoomLabel = computed(() => currentLanguage.value === 'vi' ? 'Đặt lại thu phóng' : 'Reset zoom');


useHead({title: pageTitle});
watch(pageTitle, (newTitle) => {
  useHead({title: `${newTitle} - Wrist Strap Dashboard | IoT Hub`});
});

type DateRangeType = 'today' | '7days' | '30days' | 'all';
type MetricTypeWithoutNull =
    'connectionStatusTimeline'
    | 'voltageReadings'
    | 'alertFrequencies'
    | 'deviceDistribution'
    | 'deviceStatusOverview';
type MetricType = MetricTypeWithoutNull | undefined;


const selectedDateRange = ref<DateRangeType>('7days');
const selectedArea = ref<string | undefined>(undefined);
const selectedMetric = ref<MetricType>('connectionStatusTimeline');

const mockAreaList = [
  {label: 'POL', value: 'pol'},
  {label: 'FLW', value: 'flw'},
  {label: 'CG', value: 'cg'},
  {label: 'Assembly Line A', value: 'assembly-a'},
];

const areaOptions = computed(() => [
  {label: areaFilterPlaceholder.value, value: undefined},
  ...mockAreaList
]);

const metricOptions = computed(() => [
  {label: connectionStatusTimelineLabel.value, value: 'connectionStatusTimeline' as MetricTypeWithoutNull},
  {label: voltageReadingsLabel.value, value: 'voltageReadings' as MetricTypeWithoutNull},
  {label: alertFrequenciesLabel.value, value: 'alertFrequencies' as MetricTypeWithoutNull},
  {label: deviceDistributionLabel.value, value: 'deviceDistribution' as MetricTypeWithoutNull},
  {label: deviceStatusOverviewLabel.value, value: 'deviceStatusOverview' as MetricTypeWithoutNull},
]);

const keyMetrics = ref([
  {id: 'activeDevices', label: totalActiveDevicesLabel, value: '0'},
  {id: 'uptime', label: overallUptimeLabel, value: '0%'},
  {id: 'alerts', label: totalAlertsLabel, value: '0'},
  {id: 'avgVoltage', label: averageVoltageLabel, value: '0V'},
]);

const isLoadingChart = ref(false);
const chartData = ref<{ labels: string[]; datasets: any[] }>({labels: [], datasets: []});

const isPanEnabled = ref(true);
const isZoomEnabled = ref(true);

const dynamicChartOptions = computed(() => {
  const isDark = colorMode.value === 'dark';
  const textColor = isDark ? 'rgba(229, 231, 235, 1)' : 'rgba(31, 41, 55, 1)';
  const gridColor = isDark ? 'rgba(55, 65, 81, 0.5)' : 'rgba(229, 231, 235, 0.7)';
  const scaleBorderColor = isDark ? 'rgb(55, 65, 81)' : 'rgb(209, 213, 219)';
  const titleFontSize = 18;
  const tickFontSize = 13;
  const legendFontSize = 14;
  const chartCanvasBackgroundColor = isDark ? 'rgb(30 41 59)' : 'rgb(255 255 255)';

  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      customCanvasBackgroundColor: {
        color: chartCanvasBackgroundColor
      },
      colors: {
        enabled: false
      },
      legend: {
        position: 'top' as const,
        labels: {
          color: textColor,
          font: {
            size: legendFontSize
          }
        }
      },
      title: {
        display: true,
        text: selectedMetric.value ? (metricOptions.value.find(opt => opt.value === selectedMetric.value)?.label || 'Chart') : 'Chart',
        color: textColor,
        font: {
          size: titleFontSize,
          weight: 'bold' as const
        },
        padding: {
          top: 10,
          bottom: 20
        }
      },
      tooltip: {
        bodyColor: textColor,
        titleColor: textColor,
        backgroundColor: isDark ? 'rgba(55, 65, 81, 0.95)' : 'rgba(249, 250, 251, 0.95)',
        borderColor: gridColor,
        borderWidth: 1,
        padding: 10,
        titleFont: {
          size: 14,
        },
        bodyFont: {
          size: 13
        }
      },
      zoom: {
        pan: {
          enabled: isPanEnabled.value,
          mode: 'xy' as const,
          threshold: 5,
        },
        zoom: {
          wheel: {
            enabled: isZoomEnabled.value,
          },
          pinch: {
            enabled: isZoomEnabled.value
          },
          mode: 'xy' as const,
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: textColor,
          font: {
            size: tickFontSize
          },
          maxRotation: 45,
          minRotation: 45,
          autoSkip: false,
          padding: 5,
        },
        grid: {
          color: gridColor,
        },
        border: {
          display: true,
          color: scaleBorderColor
        }
      },
      y: {
        beginAtZero: true,
        ticks: {
          color: textColor,
          font: {
            size: tickFontSize
          }
        },
        grid: {
          color: gridColor,
        },
        border: {
          display: true,
          color: scaleBorderColor
        }
      }
    }
  };
});


const setDateRange = (range: DateRangeType) => {
  selectedDateRange.value = range;
};

const generateLabelsForDateRange = (range: DateRangeType): string[] => {
  const now = new Date();
  const labels: string[] = [];
  const formatDate = (d: Date) => d.toLocaleDateString(currentLanguage.value === 'vi' ? 'vi-VN' : 'en-US', {
    month: 'short',
    day: 'numeric'
  });
  const formatHour = (h: number) => `${h.toString().padStart(2, '0')}:00`;

  switch (range) {
    case 'today':
      for (let i = 0; i < 24; i++) {
        labels.push(formatHour(i));
      }
      break;
    case '7days':
      for (let i = 6; i >= 0; i--) {
        const d = new Date(now);
        d.setDate(now.getDate() - i);
        labels.push(formatDate(d));
      }
      break;
    case '30days':
      for (let i = 29; i >= 0; i--) {
        const d = new Date(now);
        d.setDate(now.getDate() - i);
        labels.push(formatDate(d));
      }
      break;
    case 'all':
    default:
      return ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  }
  return labels;
};


const applyFilters = async () => {
  if (!selectedMetric.value) {
    chartData.value = {labels: [], datasets: []};
    return;
  }

  isLoadingChart.value = true;
  console.log("Applying filters:", {
    dateRange: selectedDateRange.value,
    area: selectedArea.value,
    metric: selectedMetric.value,
  });

  await new Promise(resolve => setTimeout(resolve, 500));

  keyMetrics.value = [
    {id: 'activeDevices', label: totalActiveDevicesLabel, value: Math.floor(Math.random() * 100 + 50).toString()},
    {id: 'uptime', label: overallUptimeLabel, value: `${Math.floor(Math.random() * 10 + 90)}%`},
    {id: 'alerts', label: totalAlertsLabel, value: Math.floor(Math.random() * 50).toString()},
    {id: 'avgVoltage', label: averageVoltageLabel, value: `${(Math.random() * 0.5 + 3.0).toFixed(1)}V`},
  ];

  const newLabels = generateLabelsForDateRange(selectedDateRange.value);
  let newDatasets: any[] = [];

  const generateMockData = (length: number, min: number, max: number, toFixed?: number) => {
    return Array.from({length}, () => {
      const val = Math.random() * (max - min) + min;
      return toFixed !== undefined ? val.toFixed(toFixed) : Math.floor(val);
    });
  };

  const nuxtGreen = 'rgb(16, 185, 129)';
  const nuxtGreenBg = 'rgba(16, 185, 129, 0.7)';
  const nuxtBlue = 'rgb(59, 130, 246)';
  const nuxtBlueBg = 'rgba(59, 130, 246, 0.7)';
  const nuxtYellow = 'rgb(234, 179, 8)';
  const nuxtYellowBg = 'rgba(234, 179, 8, 0.7)';
  const nuxtRed = 'rgb(239, 68, 68)';
  const nuxtRedBg = 'rgba(239, 68, 68, 0.7)';


  switch (selectedMetric.value) {
    case 'connectionStatusTimeline':
      newDatasets = [{
        label: localizedNavigationItems.value.find(item => item.to === '/data-visualization')?.label || connectionStatusTimelineLabel.value,
        data: generateMockData(newLabels.length, 50, 150),
        borderColor: nuxtGreen,
        backgroundColor: nuxtGreenBg,
        tension: 0.1,
        fill: true,
      }];
      break;
    case 'voltageReadings':
      newDatasets = [{
        label: voltageReadingsLabel.value,
        data: generateMockData(newLabels.length, 3.0, 3.5, 1),
        borderColor: nuxtBlue,
        backgroundColor: nuxtBlueBg,
        tension: 0.1,
        fill: false,
      }];
      break;
    case 'alertFrequencies':
      newDatasets = [{
        label: alertFrequenciesLabel.value,
        data: generateMockData(newLabels.length, 0, 20),
        borderColor: nuxtYellow,
        backgroundColor: nuxtYellowBg,
      }];
      break;
    case 'deviceDistribution':
      const areas = mockAreaList.map(a => a.label);
      newDatasets = [{
        label: deviceDistributionLabel.value,
        data: areas.map(() => Math.floor(Math.random() * 30 + 5)),
        backgroundColor: [nuxtGreenBg, nuxtBlueBg, nuxtYellowBg, nuxtRedBg, 'rgba(139, 92, 246, 0.7)'],
      }];
      chartData.value = {labels: areas, datasets: newDatasets};
      isLoadingChart.value = false;
      return;
    case 'deviceStatusOverview':
      const statuses = ['Online', 'Offline', 'Error/Warning'];
      newDatasets = [{
        label: deviceStatusOverviewLabel.value,
        data: statuses.map(() => Math.floor(Math.random() * 100)),
        backgroundColor: [nuxtGreenBg, nuxtRedBg, nuxtYellowBg],
      }];
      chartData.value = {labels: statuses, datasets: newDatasets};
      isLoadingChart.value = false;
      return;

    default:
      newDatasets = [];
  }
  chartData.value = {labels: newLabels, datasets: newDatasets};
  isLoadingChart.value = false;
};

const togglePan = () => {
  isPanEnabled.value = !isPanEnabled.value;
};

const toggleZoom = () => {
  isZoomEnabled.value = !isZoomEnabled.value;
};

const resetChartZoom = () => {
  if (chartComponentRef.value && chartComponentRef.value.chart) {
    (chartComponentRef.value.chart as any).resetZoom();
  } else {
    console.warn("Chart instance not available to reset zoom.");
  }
};


onMounted(() => {
  applyFilters();
});

watch([selectedDateRange, selectedArea, selectedMetric], () => {
  if (!isLoadingChart.value) {
    applyFilters();
  }
}, {deep: true});

</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1; /* light-gray-400 */
  border-radius: 4px;
}

html.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background: #4a5568; /* dark-gray-600 */
}

.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent; /* thumb track */
}

html.dark .custom-scrollbar {
  scrollbar-color: #4a5568 transparent; /* thumb track for dark mode */
}

.chart-container {
  position: relative;
}
</style>
