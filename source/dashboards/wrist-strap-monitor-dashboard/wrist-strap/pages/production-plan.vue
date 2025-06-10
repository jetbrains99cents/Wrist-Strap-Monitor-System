<template>
  <div class="flex flex-1 min-h-0 overflow-hidden">
    <aside
        class="hidden md:flex md::flex-col bg-gray-100 dark:bg-dark-surface border-r border-gray-200 dark:border-dark-border p-4 w-60 lg:w-64 overflow-y-auto shrink-0"
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

    <section class="flex-1 flex flex-col overflow-hidden p-3 sm:p-4 md:p-6">
      <div class="md:hidden mb-4 shrink-0">
        <UButton
            icon="i-heroicons-bars-3-20-solid"
            color="gray"
            variant="ghost"
            aria-label="Open navigation menu"
            @click="isMobileMenuOpen = true"
        />
      </div>

      <div v-if="isLoadingSettings" class="flex flex-col items-center justify-center flex-grow">
        <UIcon name="i-heroicons-arrow-path-20-solid" class="animate-spin w-10 h-10 text-primary-500" />
        <p class="mt-4 text-gray-500 dark:text-gray-400">Loading settings...</p>
      </div>

      <div v-else class="space-y-8 overflow-y-auto custom-scrollbar pr-2 flex-grow pt-2">
        <UCard :ui="{ header: { padding: 'px-4 py-3 sm:px-6' }, body: { padding: 'p-4 sm:p-6' } }">
          <template #header>
            <h2 class="text-lg font-medium text-gray-900 dark:text-white">{{ workingTimeAlertTitle }}</h2>
          </template>
          <div class="space-y-6">
            <div v-for="(shift, index) in settings.workingTime" :key="`wt-shift-${index}`" class="p-4 border border-gray-200 dark:border-gray-700 rounded-md space-y-2">
              <div class="flex items-center gap-x-2">
                <span class="text-md font-medium text-gray-700 dark:text-gray-300">{{ shiftSettingLabel }}:</span>
                <UInput v-model="shift.name" :placeholder="`Shift ${index + 1} Name`" class="flex-grow" />
              </div>
              <h3 class="text-md font-medium text-gray-700 dark:text-gray-300 mb-3">
                {{ noAlertFromLabel }}
              </h3>
              <div class="flex flex-wrap items-center gap-x-3 gap-y-2">
                <div class="flex items-center gap-x-1">
                  <USelectMenu v-model="shift.from.hour" :options="hourOptions" :aria-label="`${shiftSettingLabel} ${index + 1} ${fromHourLabel}`" class="w-20" />
                  <span class="text-gray-500 dark:text-gray-400">:</span>
                  <USelectMenu v-model="shift.from.minute" :options="minuteOptions" :aria-label="`${shiftSettingLabel} ${index + 1} ${fromMinuteLabel}`" class="w-20" />
                  <URadioGroup v-model="shift.from.period" :options="amPmOptions" :ui="{ fieldset: 'flex gap-1 ml-1', legend: 'sr-only' }" :aria-label="`${shiftSettingLabel} ${index + 1} ${fromTimePeriodLabel}`" />
                </div>
                <span class="text-center text-gray-500 dark:text-gray-400 mx-1">{{ toLabel }}</span>
                <div class="flex items-center gap-x-1">
                  <USelectMenu v-model="shift.to.hour" :options="hourOptions" :aria-label="`${shiftSettingLabel} ${index + 1} ${toHourLabel}`" class="w-20" />
                  <span class="text-gray-500 dark:text-gray-400">:</span>
                  <USelectMenu v-model="shift.to.minute" :options="minuteOptions" :aria-label="`${shiftSettingLabel} ${index + 1} ${toMinuteLabel}`" class="w-20" />
                  <URadioGroup v-model="shift.to.period" :options="amPmOptions" :ui="{ fieldset: 'flex gap-1 ml-1', legend: 'sr-only' }" :aria-label="`${shiftSettingLabel} ${index + 1} ${toTimePeriodLabel}`" />
                </div>
              </div>
            </div>
          </div>
        </UCard>

        <UCard :ui="{ header: { padding: 'px-4 py-3 sm:px-6' }, body: { padding: 'p-4 sm:p-6' } }">
          <template #header>
            <h2 class="text-lg font-medium text-gray-900 dark:text-white">{{ productionPlanAlertTitle }}</h2>
          </template>
          <div class="space-y-6">
            <div v-for="(shift, index) in settings.productionPlan" :key="`pp-shift-${index}`" class="p-4 border border-gray-200 dark:border-gray-700 rounded-md space-y-3">
              <div class="flex items-center gap-x-2">
                <span class="text-md font-medium text-gray-700 dark:text-gray-300">{{ shiftSettingLabel }}:</span>
                <UInput v-model="shift.name" :placeholder="`Production Shift ${index + 1} Name`" class="flex-grow" />
              </div>
              <div class="flex items-center gap-x-2">
                <span class="text-sm text-gray-600 dark:text-gray-400 w-16 text-right">{{ dateLabel }}:</span>
                <UInput
                    type="date"
                    v-model="shift.date"
                    color="gray"
                    variant="outline"
                    class="w-[180px]"
                    :aria-label="`${shiftSettingLabel} ${index + 1} ${dateLabel}`"
                />
              </div>

              <div class="flex flex-wrap items-center gap-x-3 gap-y-2">
                <span class="text-sm text-gray-600 dark:text-gray-400 w-16 text-right">{{ noAlertFromLabel }}</span>
                <div class="flex items-center gap-x-1">
                  <USelectMenu v-model="shift.from.hour" :options="hourOptions" :aria-label="`${shiftSettingLabel} ${index + 1} ${fromHourLabel}`" class="w-20" />
                  <span class="text-gray-500 dark:text-gray-400">:</span>
                  <USelectMenu v-model="shift.from.minute" :options="minuteOptions" :aria-label="`${shiftSettingLabel} ${index + 1} ${fromMinuteLabel}`" class="w-20" />
                  <URadioGroup v-model="shift.from.period" :options="amPmOptions" :ui="{ fieldset: 'flex gap-1 ml-1', legend: 'sr-only' }" :aria-label="`${shiftSettingLabel} ${index + 1} ${fromTimePeriodLabel}`" />
                </div>
                <span class="text-center text-gray-500 dark:text-gray-400 mx-1">{{ toLabel }}</span>
                <div class="flex items-center gap-x-1">
                  <USelectMenu v-model="shift.to.hour" :options="hourOptions" :aria-label="`${shiftSettingLabel} ${index + 1} ${toHourLabel}`" class="w-20" />
                  <span class="text-gray-500 dark:text-gray-400">:</span>
                  <USelectMenu v-model="shift.to.minute" :options="minuteOptions" :aria-label="`${shiftSettingLabel} ${index + 1} ${toMinuteLabel}`" class="w-20" />
                  <URadioGroup v-model="shift.to.period" :options="amPmOptions" :ui="{ fieldset: 'flex gap-1 ml-1', legend: 'sr-only' }" :aria-label="`${shiftSettingLabel} ${index + 1} ${toTimePeriodLabel}`" />
                </div>
              </div>
            </div>
          </div>
        </UCard>
      </div>

      <div class="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700 shrink-0">
        <UButton :label="saveSettingsLabel" icon="i-heroicons-check-circle-20-solid" size="lg" @click="saveSettings" :loading="isSavingSettings" />
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

    <UModal v-model="isSaveSuccessDialogOpen">
      <UCard :ui="{ divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-base font-semibold leading-6 text-gray-900 dark:text-white">
              {{ saveSuccessTitle }}
            </h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" class="-my-1" @click="isSaveSuccessDialogOpen = false" />
          </div>
        </template>
        <div class="p-4">
          <p>{{ saveSuccessMessage }}</p>
        </div>
        <template #footer>
          <UButton :label="closeButtonLabel" @click="isSaveSuccessDialogOpen = false" />
        </template>
      </UCard>
    </UModal>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useLanguage } from '~/composables/useLanguage';
import { useLogger } from '~/composables/useLogger';
import { useNuxtApp } from '#app';
// REMOVED: Problematic import for useToast
// import { useToast } from '#app/composables/toast'; // This line was causing the error

const logger = useLogger();
const { currentLanguage } = useLanguage();
const toast = useToast();
const { $api } = useNuxtApp();

const isMobileMenuOpen = ref(false);
const isSaveSuccessDialogOpen = ref(false);
const isLoadingSettings = ref(false); // NEW: For initial settings load state
const isSavingSettings = ref(false); // NEW: For save button loading state

const rawNavigationItems = ref([
  { id: 'home', label_en: 'Home', label_vi: 'Trang chủ', icon: 'i-heroicons-home-solid', to: '/' },
  { id: 'device-list', label_en: 'Device List', label_vi: 'Danh sách thiết bị', icon: 'i-heroicons-queue-list-solid', to: '/device-list' },
  { id: 'device-management', label_en: 'Device Management', label_vi: 'Quản lý thiết bị', icon: 'i-heroicons-cog-8-tooth-solid', to: '/device-management' },
  { id: 'production-plan', label_en: 'Production Plan\n& Working Time', label_vi: 'Kế hoạch & Thời gian\nsản xuất', icon: 'i-heroicons-calendar-days-solid', to: '/production-plan' },
  { id: 'data-visualization', label_en: 'Data Visualization', label_vi: 'Trực quan hóa dữ liệu', icon: 'i-heroicons-chart-pie-solid', to: '/data-visualization' },
  { id: 'data-analysis', label_en: 'Data Analysis', label_vi: 'Phân tích dữ liệu', icon: 'i-heroicons-presentation-chart-line-solid', to: '/data-analysis' },
]);
const localizedNavigationItems = computed(() => rawNavigationItems.value.map(item => ({
  id: item.id,
  label: currentLanguage.value === 'vi' ? item.label_vi : item.label_en,
  icon: item.icon,
  to: item.to,
})));

const pageTitle = computed(() => currentLanguage.value === 'vi' ? 'Kế hoạch Sản xuất & Thời gian Làm việc' : 'Production Plan & Working Time');
const workingTimeAlertTitle = computed(() => currentLanguage.value === 'vi' ? 'Cài đặt thông báo - Thời gian làm việc' : 'Alert setting - Working time');
const productionPlanAlertTitle = computed(() => currentLanguage.value === 'vi' ? 'Cài đặt thông báo - Kế hoạch sản xuất' : 'Alert setting - Production plan');
const shiftSettingLabel = computed(() => currentLanguage.value === 'vi' ? 'Cài đặt ca' : 'Shift Setting');
const noAlertFromLabel = computed(() => currentLanguage.value === 'vi' ? 'Không thông báo từ:' : 'No alert from:');
const toLabel = computed(() => currentLanguage.value === 'vi' ? 'đến' : 'to');
const saveSettingsLabel = computed(() => currentLanguage.value === 'vi' ? 'Lưu cài đặt' : 'Save Settings');
const mobileMenuTitle = computed(() => currentLanguage.value === 'vi' ? 'Menu' : 'Menu');
const fromHourLabel = computed(() => currentLanguage.value === 'vi' ? 'Giờ bắt đầu' : 'From Hour');
const fromMinuteLabel = computed(() => currentLanguage.value === 'vi' ? 'Phút bắt đầu' : 'From Minute');
const fromTimePeriodLabel = computed(() => currentLanguage.value === 'vi' ? 'Buổi bắt đầu' : 'From Period');
const toHourLabel = computed(() => currentLanguage.value === 'vi' ? 'Giờ kết thúc' : 'To Hour');
const toMinuteLabel = computed(() => currentLanguage.value === 'vi' ? 'Phút kết thúc' : 'To Minute');
const toTimePeriodLabel = computed(() => currentLanguage.value === 'vi' ? 'Buổi kết thúc' : 'To Period');
const dateLabel = computed(() => currentLanguage.value === 'vi' ? 'Ngày' : 'Date');
const saveSuccessTitle = computed(() => currentLanguage.value === 'vi' ? 'Thành công' : 'Success');
const saveSuccessMessage = computed(() => currentLanguage.value === 'vi' ? 'Cài đặt đã được lưu.' : 'Settings have been saved.');
const closeButtonLabel = computed(() => currentLanguage.value === 'vi' ? 'Đóng' : 'Close');

useHead({ title: pageTitle });
watch(pageTitle, (newTitle) => {
  useHead({ title: `${newTitle} - Wrist Strap Dashboard | IoT Hub` });
});

// MODIFIED: Interfaces for Settings, including `name` field
interface SelectOption { label: string; value: string; } // NEW: Define SelectOption interface
interface SelectTimeSetting { hour: SelectOption; minute: SelectOption; period: 'AM' | 'PM'; } // MODIFIED: hour/minute are now SelectOption
interface WorkingShiftSetting { name: string; from: SelectTimeSetting; to: SelectTimeSetting; }
interface ProductionShiftDateTimeSetting { name: string; date: string | undefined; from: SelectTimeSetting; to: SelectTimeSetting; }

const createDefaultSelectTime = (): SelectTimeSetting => ({
  hour: { label: '00', value: '00' }, // MODIFIED: Initialize as SelectOption object
  minute: { label: '00', value: '00' }, // MODIFIED: Initialize as SelectOption object
  period: 'AM'
});
// MODIFIED: Default shifts now include specified names
const createDefaultWorkingShift = (index: number): WorkingShiftSetting => ({ name: `Shift ${index + 1}`, from: createDefaultSelectTime(), to: createDefaultSelectTime() });
const createDefaultProductionShiftDateTime = (index: number): ProductionShiftDateTimeSetting => ({ name: `Plan ${index + 1}`, date: undefined, from: createDefaultSelectTime(), to: createDefaultSelectTime() });

const settings = ref<{ workingTime: WorkingShiftSetting[]; productionPlan: ProductionShiftDateTimeSetting[]; }>({
  workingTime: Array(3).fill(null).map((_, i) => createDefaultWorkingShift(i)),
  productionPlan: Array(3).fill(null).map((_, i) => createDefaultProductionShiftDateTime(i)),
});

// MODIFIED: hourOptions and minuteOptions now explicitly define label/value properties,
// though they were likely already structured this way for USelectMenu.
const hourOptions = Array.from({ length: 12 }, (_, i) => {
  const val = (i + 1).toString().padStart(2, '0');
  return { label: val, value: val };
});
const minuteOptions = Array.from({ length: 60 }, (_, i) => {
  const val = i.toString().padStart(2, '0');
  return { label: val, value: val };
});
const amPmOptions = [ { label: 'AM', value: 'AM' }, { label: 'PM', value: 'PM' }];

// The mockApiSettingsJson is now primarily for initial UI development or fallback.
// The actual loading will come from the API.
const mockApiSettingsJson = `{
  "workingTime": [
    { "name": "Shift 1", "from": { "hour": "08", "minute": "00", "period": "AM" }, "to": { "hour": "12", "minute": "00", "period": "PM" } },
    { "name": "Shift 2", "from": { "hour": "01", "minute": "00", "period": "PM" }, "to": { "hour": "05", "minute": "00", "period": "PM" } },
    { "name": "Shift 3", "from": { "hour": "06", "minute": "00", "period": "PM" }, "to": { "hour": "10", "minute": "00", "period": "PM" } }
  ],
  "productionPlan": [
    { "name": "Plan 1", "date": "2025-07-10", "from": { "hour": "07", "minute": "30", "period": "AM" }, "to": { "hour": "11", "minute": "30", "period": "AM" } },
    { "name": "Plan 2", "date": "2025-07-11", "from": { "hour": "02", "minute": "15", "period": "PM" }, "to": { "hour": "06", "minute": "45", "period": "PM" } },
    { "name": "Plan 3", "date": null, "from": { "hour": "12", "minute": "00", "period": "AM" }, "to": { "hour": "12", "minute": "00", "period": "AM" } }
  ]
}`;

onMounted(async () => {
  isLoadingSettings.value = true; // Set loading true
  logger.log("Attempting to load settings from API...");
  try {
    const loadedSettings = await $api('/api/v1/settings/'); // API call to fetch settings
    logger.log("Settings received from API:", JSON.parse(JSON.stringify(loadedSettings)));

    // Apply loaded settings to reactive ref
    // Ensure the arrays are initialized with correct length defaults before mapping
    const defaultWorkingTime = Array(3).fill(null).map((_, i) => createDefaultWorkingShift(i));
    const defaultProductionPlan = Array(3).fill(null).map((_, i) => createDefaultProductionShiftDateTime(i));

    if (loadedSettings.workingTime && Array.isArray(loadedSettings.workingTime)) {
      settings.value.workingTime = loadedSettings.workingTime.map((loadedShift: WorkingShiftSetting, index: number) => {
        // For `from.hour` and `from.minute`, convert loaded string value back to SelectOption object
        const fromHour = loadedShift.from.hour ? { label: loadedShift.from.hour, value: loadedShift.from.hour } : createDefaultSelectTime().hour;
        const fromMinute = loadedShift.from.minute ? { label: loadedShift.from.minute, value: loadedShift.from.minute } : createDefaultSelectTime().minute;
        const toHour = loadedShift.to.hour ? { label: loadedShift.to.hour, value: loadedShift.to.hour } : createDefaultSelectTime().hour;
        const toMinute = loadedShift.to.minute ? { label: loadedShift.to.minute, value: loadedShift.to.minute } : createDefaultSelectTime().minute;

        return {
          ...defaultWorkingTime[index],
          ...loadedShift,
          from: { ...loadedShift.from, hour: fromHour, minute: fromMinute },
          to: { ...loadedShift.to, hour: toHour, minute: toMinute }
        };
      });
      // Handle cases where loaded settings might have fewer or more items than default
      if (loadedSettings.workingTime.length < defaultWorkingTime.length) {
        settings.value.workingTime = [...settings.value.workingTime, ...defaultWorkingTime.slice(loadedSettings.workingTime.length)];
      }
    } else {
      settings.value.workingTime = defaultWorkingTime;
    }

    if (loadedSettings.productionPlan && Array.isArray(loadedSettings.productionPlan)) {
      settings.value.productionPlan = loadedSettings.productionPlan.map((loadedShift: ProductionShiftDateTimeSetting, index: number) => {
        // For `from.hour` and `from.minute`, convert loaded string value back to SelectOption object
        const fromHour = loadedShift.from.hour ? { label: loadedShift.from.hour, value: loadedShift.from.hour } : createDefaultSelectTime().hour;
        const fromMinute = loadedShift.from.minute ? { label: loadedShift.from.minute, value: loadedShift.from.minute } : createDefaultSelectTime().minute;
        const toHour = loadedShift.to.hour ? { label: loadedShift.to.hour, value: loadedShift.to.hour } : createDefaultSelectTime().hour;
        const toMinute = loadedShift.to.minute ? { label: loadedShift.to.minute, value: loadedShift.to.minute } : createDefaultSelectTime().minute;

        return {
          ...defaultProductionPlan[index],
          ...loadedShift,
          date: loadedShift.date === null ? undefined : loadedShift.date,
          from: { ...loadedShift.from, hour: fromHour, minute: fromMinute },
          to: { ...loadedShift.to, hour: toHour, minute: toMinute }
        };
      });
      if (loadedSettings.productionPlan.length < defaultProductionPlan.length) {
        settings.value.productionPlan = [...settings.value.productionPlan, ...defaultProductionPlan.slice(loadedSettings.productionPlan.length)];
      }
    } else {
      settings.value.productionPlan = defaultProductionPlan;
    }

    logger.log("Settings loaded and applied to UI:", JSON.parse(JSON.stringify(settings.value)));
  } catch (error) {
    logger.error("Failed to load settings from API:", error);
    toast.add({ title: 'Error', description: 'Could not load system settings. Please ensure settings are saved at least once.', color: 'red', icon: 'i-heroicons-exclamation-circle-20-solid' });
    // If API call fails, initialize with default UI settings
    settings.value.workingTime = Array(3).fill(null).map((_, i) => createDefaultWorkingShift(i));
    settings.value.productionPlan = Array(3).fill(null).map((_, i) => createDefaultProductionShiftDateTime(i));
  } finally {
    isLoadingSettings.value = false; // Set loading false
  }
});

const saveSettings = async () => {
  isSavingSettings.value = true; // Set saving true
  // Construct the payload in the format expected by backend's SystemSettingsCreateUpdate
  const apiPayload = {
    workingTime: settings.value.workingTime.map(shift => ({
      name: shift.name,
      // FIX: Ensure hour and minute values are extracted from the USelectMenu's bound object
      from: { hour: shift.from.hour.value, minute: shift.from.minute.value, period: shift.from.period },
      to: { hour: shift.to.hour.value, minute: shift.to.minute.value, period: shift.to.period },
    })),
    productionPlan: settings.value.productionPlan.map(shift => ({
      name: shift.name,
      date: shift.date === undefined || shift.date === '' ? null : shift.date, // Convert undefined/empty date to null for backend
      // FIX: Ensure hour and minute values are extracted from the USelectMenu's bound object
      from: { hour: shift.from.hour.value, minute: shift.from.minute.value, period: shift.from.period },
      to: { hour: shift.to.hour.value, minute: shift.to.minute.value, period: shift.to.period },
    })),
  };

  const settingsJson = JSON.stringify(apiPayload, null, 2);
  logger.log("Settings to be sent to API:", settingsJson);

  try {
    const response = await $api('/api/v1/settings/', {
      method: 'PUT',
      body: apiPayload,
    });
    logger.log("Settings saved successfully. API Response:", response);
    isSaveSuccessDialogOpen.value = true;
    toast.add({ title: saveSuccessTitle.value, description: saveSuccessMessage.value, color: 'green', icon: 'i-heroicons-check-circle-20-solid' });
  } catch (error) {
    logger.error("Failed to save settings:", error);
    toast.add({ title: 'Error', description: 'Could not save system settings.', color: 'red', icon: 'i-heroicons-exclamation-circle-20-solid' });
  } finally {
    isSavingSettings.value = false;
  }
};
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 8px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
html.dark .custom-scrollbar::-webkit-scrollbar-thumb { background: #4a5568; }
.custom-scrollbar { scrollbar-width: thin; scrollbar-color: #cbd5e1 transparent; }
html.dark .custom-scrollbar { scrollbar-color: #4a5568 transparent; }
</style>