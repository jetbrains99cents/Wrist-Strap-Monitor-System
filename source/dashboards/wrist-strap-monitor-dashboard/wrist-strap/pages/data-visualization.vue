<template>
  <div class="flex flex-1 min-h-0 overflow-hidden">
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
              clearable
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

      <div class="chart-display-wrapper flex flex-col flex-grow min-h-0">
        <div class="chart-display-area flex-grow min-h-0 relative bg-white dark:bg-dark-surface-alt rounded-lg shadow">
          <div v-if="isLoadingChart"
               class="absolute inset-0 flex items-center justify-center bg-opacity-50 bg-gray-200 dark:bg-opacity-50 dark:bg-gray-800 z-10 rounded-lg">
            <UIcon name="i-heroicons-arrow-path" class="animate-spin h-12 w-12 text-primary-500"/>
          </div>
          <div v-else-if="!selectedMetric || !chartData || chartData.datasets.length === 0 || chartData.datasets[0].data.length === 0"
               class="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
            <p>{{ selectedMetric ? noDataAvailableLabel : selectMetricPrompt }}</p>
          </div>
          <div v-else class="chart-container w-full h-full overflow-x-auto custom-scrollbar">
            <Line v-if="selectedMetric === 'deviceStatusTrends'" :data="chartData"
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
import {useLogger} from '~/composables/useLogger';
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
  Colors,
  Filler // --- MODIFICATION: Import 'Filler' for area charts
} from 'chart.js'
import type {ChartOptions, Plugin} from 'chart.js';
import zoomPlugin from 'chartjs-plugin-zoom';
import {useNuxtApp, useRuntimeConfig, useToast, useColorMode} from "#imports";
import tailwindColors from '#tailwind-config/theme';
import { useLocalization } from '~/composables/useLocalization';

// SECTION: Chart.js Setup
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
    Title, Tooltip, Legend, LineElement, BarElement, CategoryScale,
    LinearScale, PointElement, ArcElement, Colors, Filler, // --- MODIFICATION: Register 'Filler'
    customCanvasBackgroundColor, zoomPlugin
);
// !SECTION

// SECTION: Composables and Basic State
const {currentLanguage} = useLanguage();
const colorMode = useColorMode();
const logger = useLogger();
const { $api } = useNuxtApp();
const runtimeConfig = useRuntimeConfig();
const toast = useToast();
const { getLocalizedStatus } = useLocalization();

const isMobileMenuOpen = ref(false);
const chartComponentRef = ref<any | null>(null);
// !SECTION

// SECTION: Navigation and Localization
const rawNavigationItems = ref([
  {id: 'home', label_en: 'Home', label_vi: 'Trang chủ', icon: 'i-heroicons-home-solid', to: '/'},
  {id: 'device-list', label_en: 'Device List', label_vi: 'Danh sách thiết bị', icon: 'i-heroicons-queue-list-solid', to: '/device-list' },
  {id: 'device-management', label_en: 'Device Management', label_vi: 'Quản lý thiết bị', icon: 'i-heroicons-cog-8-tooth-solid', to: '/device-management' },
  {id: 'production-plan', label_en: 'Production Plan\n& Working Time', label_vi: 'Kế hoạch & Thời gian\nsản xuất', icon: 'i-heroicons-calendar-days-solid', to: '/production-plan' },
  {id: 'data-visualization', label_en: 'Data Visualization', label_vi: 'Trực quan hóa dữ liệu', icon: 'i-heroicons-chart-pie-solid', to: '/data-visualization' },
  {id: 'data-analysis', label_en: 'Data Analysis', label_vi: 'Phân tích dữ liệu', icon: 'i-heroicons-presentation-chart-line-solid', to: '/data-analysis' },
]);
const localizedNavigationItems = computed(() => rawNavigationItems.value.map(item => ({ id: item.id, label: currentLanguage.value === 'vi' ? item.label_vi : item.label_en, icon: item.icon, to: item.to, })));

const pageTitle = computed(() => currentLanguage.value === 'vi' ? 'Trực quan hóa dữ liệu' : 'Data Visualization');
const dateRangeLabel = computed(() => currentLanguage.value === 'vi' ? 'Phạm vi ngày' : 'Date Range');
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
// --- MODIFICATION: Changed label for the new chart ---
const deviceFleetHealthLabel = computed(() => currentLanguage.value === 'vi' ? 'Sức khỏe hệ thống (Theo thời gian)' : 'Device Fleet Health (Timeline)');
const voltageReadingsLabel = computed(() => currentLanguage.value === 'vi' ? 'Giá trị điện áp' : 'Voltage Readings');
const alertFrequenciesLabel = computed(() => currentLanguage.value === 'vi' ? 'Tần suất cảnh báo' : 'Alert Frequencies');
const deviceDistributionLabel = computed(() => currentLanguage.value === 'vi' ? 'Phân bố thiết bị' : 'Device Distribution');
const deviceStatusOverviewLabel = computed(() => currentLanguage.value === 'vi' ? 'Tổng quan trạng thái thiết bị' : 'Device Status Overview');
const panEnableLabel = computed(() => currentLanguage.value === 'vi' ? 'Bật kéo' : 'Enable pan');
const panDisableLabel = computed(() => currentLanguage.value === 'vi' ? 'Tắt kéo' : 'Disable pan');
const zoomEnableLabel = computed(() => currentLanguage.value === 'vi' ? 'Bật thu phóng' : 'Enable zoom');
const zoomDisableLabel = computed(() => currentLanguage.value === 'vi' ? 'Tắt thu phóng' : 'Disable zoom');
const resetZoomLabel = computed(() => currentLanguage.value === 'vi' ? 'Đặt lại thu phóng' : 'Reset zoom');

const datasetLabelTranslations = computed((): { [key: string]: string } => {
  if (currentLanguage.value !== 'vi') return {};
  return {
    '# of Devices': 'Số lượng thiết bị',
    'Device Count': 'Số lượng thiết bị',
    'Connection Status': 'Trạng thái kết nối',
    'Voltage': 'Điện áp',
    'Alerts': 'Cảnh báo',
    'Connection Events': 'Sự kiện kết nối',
    'Average Voltage': 'Điện áp trung bình',
    'Devices by Area': 'Thiết bị theo khu vực'
  };
});

useHead({title: pageTitle});
watch(pageTitle, (newTitle) => { useHead({title: `${newTitle} - Wrist Strap Dashboard | IoT Hub`}); });
// !SECTION

// SECTION: Filters and Data State
type DateRangeType = 'today' | '7days' | '30days' | 'all';
// --- MODIFICATION: Changed metric type value ---
type MetricTypeWithoutNull = 'deviceStatusTrends' | 'voltageReadings' | 'alertFrequencies' | 'deviceDistribution' | 'deviceStatusOverview';
type MetricType = MetricTypeWithoutNull | undefined;

const selectedDateRange = ref<DateRangeType>('7days');
const selectedArea = ref<string | undefined>(undefined);
const selectedMetric = ref<MetricType>('deviceStatusTrends');

const areaOptions = computed(() => [
  {label: areaFilterPlaceholder.value, value: undefined},
  ...runtimeConfig.public.installationAreas.map((area: string) => ({ label: area, value: area }))
]);

const metricOptions = computed(() => [
  // --- MODIFICATION: Updated the first metric option ---
  {label: deviceFleetHealthLabel.value, value: 'deviceStatusTrends' as MetricTypeWithoutNull},
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
const chartData = ref<{ labels: (string | number)[]; datasets: any[] }>({labels: [], datasets: []});
// !SECTION

// SECTION: Chart Options and Controls
const isPanEnabled = ref(true);
const isZoomEnabled = ref(true);

const xAxisLabel = computed(() => {
  const metric = selectedMetric.value;
  // --- MODIFICATION: Updated label for the new metric ---
  if (currentLanguage.value !== 'vi') {
    switch (metric) {
      case 'deviceStatusTrends': return 'Time';
      case 'voltageReadings': return 'Time';
      case 'alertFrequencies': return 'Alert Type';
      case 'deviceDistribution': return 'Installation Area';
      case 'deviceStatusOverview': return 'Status';
      default: return '';
    }
  } else {
    switch (metric) {
      case 'deviceStatusTrends': return 'Thời gian';
      case 'voltageReadings': return 'Thời gian';
      case 'alertFrequencies': return 'Loại cảnh báo';
      case 'deviceDistribution': return 'Khu vực lắp đặt';
      case 'deviceStatusOverview': return 'Trạng thái';
      default: return '';
    }
  }
});

const yAxisLabel = computed(() => {
  const metric = selectedMetric.value;
  // --- MODIFICATION: Updated label for the new metric ---
  if (currentLanguage.value !== 'vi') {
    switch (metric) {
      case 'deviceStatusTrends': return 'Number of Devices';
      case 'voltageReadings': return 'Voltage (V)';
      case 'alertFrequencies': return 'Count';
      case 'deviceDistribution': return 'Number of Devices';
      case 'deviceStatusOverview': return 'Number of Devices';
      default: return '';
    }
  } else {
    switch (metric) {
      case 'deviceStatusTrends': return 'Số lượng thiết bị';
      case 'voltageReadings': return 'Điện áp (V)';
      case 'alertFrequencies': return 'Số lần';
      case 'deviceDistribution': return 'Số lượng thiết bị';
      case 'deviceStatusOverview': return 'Số lượng thiết bị';
      default: return '';
    }
  }
});

const dynamicChartOptions = computed(() => {
  const isDark = colorMode.value === 'dark';
  const textColor = isDark ? 'rgba(229, 231, 235, 1)' : 'rgba(31, 41, 55, 1)';
  const gridColor = isDark ? 'rgba(55, 65, 81, 0.5)' : 'rgba(229, 231, 235, 0.7)';
  const scaleBorderColor = isDark ? 'rgb(55, 65, 81)' : 'rgb(209, 213, 219)';
  const chartCanvasBackgroundColor = isDark ? 'rgb(30 41 59)' : 'rgb(255 255 255)';

  return {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      customCanvasBackgroundColor: { color: chartCanvasBackgroundColor },
      legend: { position: 'top' as const, labels: { color: textColor, font: { size: 14 } } },
      title: { display: true, text: selectedMetric.value ? (metricOptions.value.find(opt => opt.value === selectedMetric.value)?.label || 'Chart') : 'Chart', color: textColor, font: { size: 18, weight: 'bold' as const }, padding: { top: 10, bottom: 20 } },
      tooltip: { bodyColor: textColor, titleColor: textColor, backgroundColor: isDark ? 'rgba(55, 65, 81, 0.95)' : 'rgba(249, 250, 251, 0.95)', borderColor: gridColor, borderWidth: 1, padding: 10, titleFont: { size: 14, }, bodyFont: { size: 13 } },
      zoom: { pan: { enabled: isPanEnabled.value, mode: 'xy' as const, threshold: 5, }, zoom: { wheel: { enabled: isZoomEnabled.value, }, pinch: { enabled: isZoomEnabled.value }, mode: 'xy' as const, } }
    },
    scales: {
      x: {
        ticks: { color: textColor, font: { size: 13 }, maxRotation: 45, minRotation: 45, autoSkip: true, padding: 5, },
        grid: { color: gridColor, },
        border: { display: true, color: scaleBorderColor },
        title: { display: !!xAxisLabel.value, text: xAxisLabel.value, color: textColor, font: { size: 14, weight: 'bold' } }
      },
      y: {
        // --- MODIFICATION: Make the Y-axis stacked for the new chart ---
        stacked: selectedMetric.value === 'deviceStatusTrends',
        beginAtZero: true,
        ticks: { color: textColor, font: { size: 13 } },
        grid: { color: gridColor, },
        border: { display: true, color: scaleBorderColor },
        title: { display: !!yAxisLabel.value, text: yAxisLabel.value, color: textColor, font: { size: 14, weight: 'bold' } }
      }
    }
  };
});

const togglePan = () => { isPanEnabled.value = !isPanEnabled.value; };
const toggleZoom = () => { isZoomEnabled.value = !isZoomEnabled.value; };
const resetChartZoom = () => {
  if (chartComponentRef.value && chartComponentRef.value.chart) {
    (chartComponentRef.value.chart as any).resetZoom();
  }
};
// !SECTION

// SECTION: Data Fetching Logic
const setDateRange = (range: DateRangeType) => {
  selectedDateRange.value = range;
};

const applyFilters = async () => {
  if (!selectedMetric.value) {
    chartData.value = {labels: [], datasets: []};
    return;
  }

  isLoadingChart.value = true;
  logger.log("Applying filters:", { dateRange: selectedDateRange.value, area: selectedArea.value, metric: selectedMetric.value });

  try {
    const params: Record<string, any> = {
      dateRange: selectedDateRange.value,
    };
    if (selectedArea.value) {
      params.area = selectedArea.value;
    }

    const response = await $api<any>(`/api/v1/analytics/${selectedMetric.value}`, { params });

    if (response.keyMetrics) {
      keyMetrics.value = [
        {id: 'activeDevices', label: totalActiveDevicesLabel, value: response.keyMetrics.activeDevices?.toString() || '0'},
        {id: 'uptime', label: overallUptimeLabel, value: `${response.keyMetrics.uptimePercentage?.toFixed(1) || '0.0'}%`},
        {id: 'alerts', label: totalAlertsLabel, value: response.keyMetrics.totalAlerts?.toString() || '0'},
        {id: 'avgVoltage', label: averageVoltageLabel, value: `${response.keyMetrics.averageVoltage?.toFixed(2) || '0.00'}V`},
      ];
    }

    if (response.chartData) {
      const data = response.chartData;
      const colorNameMap = runtimeConfig.public.statusColors as Record<string, string>;

      // --- MODIFICATION: Reworked this block to handle different chart data structures ---
      if (selectedMetric.value === 'deviceStatusOverview' && data.datasets[0]) {
        // Handle colors and translations for the Pie Chart
        data.datasets[0].backgroundColor = data.labels.map((label: string) => {
          const colorName = colorNameMap[label] || 'slate';
          const colorPalette = (tailwindColors as any).colors[colorName];
          return colorPalette ? colorPalette['500'] : (tailwindColors as any).colors.slate['500'];
        });

        if (currentLanguage.value === 'vi') {
          data.labels = data.labels.map((label: string) => getLocalizedStatus(label));
        }

      } else if (selectedMetric.value === 'deviceStatusTrends' && data.datasets.length > 0) {
        // Handle colors and translations for the new Stacked Area Chart
        data.datasets.forEach((dataset: any) => {
          const originalLabel = dataset.label; // e.g., "Connected", "Disconnected"
          const colorName = colorNameMap[originalLabel] || 'slate';
          const colorPalette = (tailwindColors as any).colors[colorName];

          if (colorPalette) {
            dataset.backgroundColor = colorPalette['400']; // Area fill color
            dataset.borderColor = colorPalette['500'];     // Line color
          }

          dataset.fill = true; // This makes it an area chart
          dataset.tension = 0.4; // Smooths the lines

          if (currentLanguage.value === 'vi') {
            dataset.label = getLocalizedStatus(originalLabel);
          }
        });
      }

      // Universal translation for dataset labels if they exist
      if (currentLanguage.value === 'vi') {
        if (data.datasets[0] && data.datasets[0].label) {
          const originalLabel = data.datasets[0].label;
          data.datasets[0].label = datasetLabelTranslations.value[originalLabel] || originalLabel;
        }
        if (selectedMetric.value === 'alertFrequencies') {
          data.labels = data.labels.map((label: string) => getLocalizedStatus(label));
        }
      }

      chartData.value = data;
    } else {
      chartData.value = {labels: [], datasets: []};
    }

  } catch (error: any) {
    logger.error(`Failed to fetch analytics for metric: ${selectedMetric.value}`, error);
    toast.add({ title: 'API Error', description: 'Could not fetch analytics data from the server.', color: 'red', icon: 'i-heroicons-x-circle' });
    chartData.value = {labels: [], datasets: []};
  } finally {
    isLoadingChart.value = false;
  }
};
// !SECTION

// SECTION: Lifecycle and Watchers
onMounted(() => {
  applyFilters();
});

watch(
    [selectedDateRange, selectedArea, selectedMetric, currentLanguage],
    () => {
      if (!isLoadingChart.value) {
        applyFilters();
      }
    },
    {deep: true}
);
// !SECTION

</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 8px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
html.dark .custom-scrollbar::-webkit-scrollbar-thumb { background: #4a5568; }
.custom-scrollbar { scrollbar-width: thin; scrollbar-color: #cbd5e1 transparent; }
html.dark .custom-scrollbar { scrollbar-color: #4a5568 transparent; }
.chart-container { position: relative; }
</style>