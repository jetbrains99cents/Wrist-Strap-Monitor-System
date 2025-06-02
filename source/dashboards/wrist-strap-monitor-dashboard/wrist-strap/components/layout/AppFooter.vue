<template>
  <footer
      class="app-footer fixed bottom-0 left-0 right-0 z-10 self-stretch overflow-hidden
           flex flex-col items-center p-3 gap-3
           md:flex-row md:items-center md:justify-between md:p-4 md:gap-5
           max-w-full text-left text-lg font-abeezee"
  >
    <div
        class="app-footer-version-text overflow-hidden flex flex-row items-center justify-center md:justify-start"
    >
      <h3
          class="m-0 relative text-sm" >
        v1.0 - Updated at 27/12/2025
      </h3>
    </div>

    <div
        class="w-auto flex flex-col items-center gap-3
             sm:flex-row sm:justify-end sm:gap-x-4 md:gap-x-6"
    >
      <div class="flex items-center">
        <UButton
            :label="backToHubLabel"
            icon="i-heroicons-arrow-uturn-left-20-solid"
            color="gray"
            variant="ghost"
            @click="navigateToLandingPage"
            size="sm"
            class="font-abeezee"
        />
      </div>

      <div class="flex items-center gap-1.5 md:gap-2">
        <span class="text-xs sm:text-sm hidden xs:inline md:hidden lg:inline">{{ languageLabelText }}:</span> <div
          class="shrink-0 flex flex-row items-center justify-around gap-1 sm:gap-2"
          role="group"
          aria-label="Language Selection"
      >
        <button
            aria-label="Switch to Vietnamese"
            @click="selectedLang = 'vi'"
            class="focus:outline-none transition-opacity p-0.5"
            :class="currentLanguage.value === 'vi' ? 'opacity-100' : 'opacity-50 hover:opacity-80'"
        >
          <img
              class="h-[30px] w-[30px] rounded-sm cursor-pointer object-cover"
              loading="lazy"
              alt="Vietnamese Flag"
              src="/vietnamese-flag.svg"
              onerror="this.onerror=null; this.src='https://placehold.co/30x30/cccccc/000000?text=VI';"
          />
        </button>
        <button
            aria-label="Switch to English"
            @click="selectedLang = 'en'"
            class="focus:outline-none transition-opacity p-0.5"
            :class="currentLanguage.value === 'en' ? 'opacity-100' : 'opacity-50 hover:opacity-80'"
        >
          <img
              class="h-[30px] w-[30px] rounded-sm cursor-pointer object-cover"
              loading="lazy"
              alt="English Flag"
              src="/english-flag.svg"
              onerror="this.onerror=null; this.src='https://placehold.co/30x30/cccccc/000000?text=EN';"
          />
        </button>
      </div>
        <span class="text-xs sm:text-sm font-semibold w-auto min-w-[60px] text-left hidden xs:inline md:hidden lg:inline">{{ currentLanguageName }}</span>
      </div>

      <div class="flex items-center gap-1.5 md:gap-2">
        <span class="text-xs sm:text-sm hidden xs:inline md:hidden lg:inline">{{ themeLabelText }}:</span><div
          class="shrink-0 flex flex-row items-center justify-center"
          role="group"
          aria-label="Theme Selection"
      >
        <UToggle
            v-model="isDark"
            on-icon="i-heroicons-moon-20-solid"
            off-icon="i-heroicons-sun-20-solid"
            aria-label="Theme Switch"
            size="sm"
        />
      </div>
        <span class="text-xs sm:text-sm font-semibold w-auto min-w-[40px] text-left hidden xs:inline md:hidden lg:inline">{{ currentThemeName }}</span>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
// Script remains the same as your last version
import { ref, computed } from 'vue';
import { useLanguage } from '~/composables/useLanguage';

const { currentLanguage, setLanguage: setLang } = useLanguage();
const colorMode = useColorMode();

const landingPageUrl = computed(() => { /* ... as before ... */
  if (typeof window !== 'undefined') {
    return window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.hostname.startsWith('192.168.') || window.location.hostname.startsWith('172.')
        ? `${window.location.protocol}//${window.location.hostname}:3000`
        : 'YOUR_PRODUCTION_LANDING_PAGE_URL';
  }
  return 'http://localhost:3000';
});
const navigateToLandingPage = () => { navigateTo(landingPageUrl.value, { external: true }); };
const backToHubLabel = computed(() => { return currentLanguage.value === 'vi' ? 'Về trang chủ IoT Hub' : 'Back to IoT Hub'; });
const selectedLang = computed({ get: () => currentLanguage.value, set: (val: 'en' | 'vi') => setLang(val) });
const languageLabelText = computed(() => { return currentLanguage.value === 'vi' ? 'Ngôn ngữ' : 'Language'; });
const currentLanguageName = computed(() => { return currentLanguage.value === 'vi' ? 'Tiếng Việt' : 'English'; });
const isDark = computed<boolean>({ get() { return colorMode.value === 'dark'; }, set(newValue: boolean) { colorMode.preference = newValue ? 'dark' : 'light'; }});
const themeLabelText = computed(() => { return currentLanguage.value === 'vi' ? 'Giao diện' : 'Theme'; });
const currentThemeName = computed(() => { if (currentLanguage.value === 'vi') { return isDark.value ? 'Tối' : 'Sáng'; } return isDark.value ? 'Dark' : 'Light'; });
</script>

<style scoped>
.font-abeezee {
  font-family: 'ABeeZee', sans-serif;
}
</style>