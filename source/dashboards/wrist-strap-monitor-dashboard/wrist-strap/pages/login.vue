<template>
  <div class="flex flex-1 items-center justify-center p-4">
    <UCard class="w-full max-w-md" :ui="{ ring: 'ring-1 ring-gray-200 dark:ring-gray-700' }">
      <div class="text-center mb-8">
        <div class="inline-flex justify-center items-center">
          <UIcon name="i-heroicons-shield-check-solid" class="w-12 h-12 text-primary"/>
        </div>
        <h2 class="text-2xl font-semibold mt-4">{{ cardTitle }}</h2>
      </div>

      <!-- Login Success View -->
      <div v-if="isLoginSuccess" class="space-y-4 text-center">
        <UIcon name="i-heroicons-check-circle-20-solid" class="w-16 h-16 text-green-500 mx-auto"/>
        <p class="text-lg font-medium">{{ successTitle }}</p>
        <p class="text-gray-500 dark:text-gray-400">{{ redirectMessage.replace('{countdown}', countdown.toString()) }}</p>
      </div>

      <!-- Main Login Flow -->
      <div v-else>
        <!-- Email Entry View -->
        <div v-if="!isAwaitingCode" class="space-y-6">
          <p class="text-center text-gray-500 dark:text-gray-400">{{ loginSubtitle }}</p>

          <UForm :state="state" @submit="handleRequestCode">
            <UFormGroup :label="emailInputLabel" name="email">
              <UInput
                  v-model="state.email"
                  type="email"
                  :placeholder="emailPlaceholder"
                  size="xl"
                  icon="i-heroicons-envelope-20-solid"
                  required
              />
            </UFormGroup>
            <UButton type="submit" block size="xl" class="mt-4" :loading="isLoading">{{ continueButtonLabel }}</UButton>
          </UForm>

          <div class="text-center">
            <UButton variant="link" @click="toggleMode">{{ useBackupCodeLabel }}</UButton>
          </div>
        </div>

        <!-- Code Verification View -->
        <div v-else class="space-y-6">
          <p class="text-center text-gray-500 dark:text-gray-400">
            <span v-if="isBackupMode">{{ backupCodePrompt }}</span>
            <span v-else>{{ verificationCodePrompt.replace('{email}', state.email) }}</span>
          </p>

          <UForm :state="state" @submit="handleVerifyCode">
            <UFormGroup :label="codeInputLabel" name="code">
              <UInput
                  v-model="state.code"
                  :placeholder="codePlaceholder"
                  size="xl"
                  icon="i-heroicons-key-20-solid"
                  required
              />
            </UFormGroup>
            <UButton type="submit" block size="xl" class="mt-4" :loading="isLoading">{{ verifyButtonLabel }}</UButton>
          </UForm>

          <div class="text-center">
            <UButton variant="link" @click="resetFlow">{{ backToEmailLabel }}</UButton>
          </div>
        </div>
      </div>
    </UCard>

    <UModal v-model="isErrorModalOpen">
      <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-base font-semibold leading-6 text-gray-900 dark:text-white">
              {{ errorModalTitle }}
            </h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" class="-my-1" @click="isErrorModalOpen = false" />
          </div>
        </template>
        <div class="p-4">
          <p class="text-sm text-gray-700 dark:text-gray-300">{{ errorModalMessage }}</p>
        </div>
        <template #footer>
          <UButton :label="closeButtonLabel" color="gray" variant="solid" @click="isErrorModalOpen = false" />
        </template>
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onUnmounted } from 'vue';
import { useLanguage } from '~/composables/useLanguage';
import { useUserStore } from '~/stores/userStore';
import { useLogger } from '~/composables/useLogger';

// --- Type Definitions for API response ---
interface User {
  id: number;
  email: string;
  name: string;
  roles: string[];
  granted: boolean;
}

interface AuthResponse {
  access_token: string;
  user: User;
}

const { currentLanguage } = useLanguage();
const userStore = useUserStore();
const toast = useToast();
const router = useRouter();
const logger = useLogger();

const config = useRuntimeConfig();
const apiBaseUrl = config.public.apiBase;

// UI state management
const isLoading = ref(false);
const isBackupMode = ref(false);
const isAwaitingCode = ref(false);
const isLoginSuccess = ref(false);
const countdown = ref(5);
let countdownInterval: ReturnType<typeof setInterval> | null = null;

// Form state
const state = reactive({
  email: '',
  code: '',
});

// Error Modal State
const isErrorModalOpen = ref(false);
const errorModalTitle = ref('');
const errorModalMessage = ref('');

// --- Client-Side Hashing for Backup Codes ---
async function sha256(message: string): Promise<string> {
  if (!crypto.subtle) {
    throw new Error('Cryptography API (crypto.subtle) is not available. Ensure you are on a secure context (HTTPS) or a compatible browser.');
  }
  const msgBuffer = new TextEncoder().encode(message);
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

// Helper to get a user-friendly error message
const getErrorMessage = (error: any): { title: string, description: string, isCritical: boolean } => {
  logger.error('[Login Page] Analyzing error:', error);

  if (error instanceof Error && (error.message.includes('Failed to fetch') || error.message.includes('network error'))) {
    return { title: 'Connection Error', description: 'Could not reach the API server.', isCritical: true };
  }
  if (error.response?._data) {
    const status = error.response.status;
    const backendMessage = error.response._data.detail || 'Unknown error';
    if (status === 401 || status === 403) {
      return { title: 'Authentication Failed', description: backendMessage, isCritical: true };
    }
    if (status === 404) {
      return { title: 'Not Found', description: 'API endpoint not found.', isCritical: true };
    }
  }
  return { title: 'Unknown Error', description: 'An unexpected error occurred.', isCritical: true };
};

const closeButtonLabel = computed(() => currentLanguage.value === 'vi' ? 'Đóng' : 'Close');

// --- API Interaction Logic ---
async function handleRequestCode() {
  isLoading.value = true;
  try {
    const url = `${apiBaseUrl}/api/v1/auth/request-code`;
    await $fetch(url, { method: 'POST', body: { email: state.email } });

    isAwaitingCode.value = true;
    if (!isBackupMode.value) {
      toast.add({ title: 'Code Sent', color: 'green' });
    }
  } catch (error) {
    const errorInfo = getErrorMessage(error);
    errorModalTitle.value = errorInfo.title;
    errorModalMessage.value = errorInfo.description;
    isErrorModalOpen.value = true;
  } finally {
    isLoading.value = false;
  }
}

async function handleVerifyCode() {
  isLoading.value = true;
  try {
    let payload;
    const url = `${apiBaseUrl}/api/v1/auth/verify-code`;

    if (isBackupMode.value) {
      const hashedCode = await sha256(state.code);
      payload = { email: state.email, backupCodeHash: hashedCode };
    } else {
      payload = { email: state.email, code: state.code };
      throw new Error('OTP authentication is not yet implemented.');
    }

    const response = await $fetch<AuthResponse>(url, { method: 'POST', body: payload });

    if (!response?.user || !response.access_token) {
      throw new Error('Invalid API response content for verification.');
    }

    logger.log('[Login Page] Login successful. User data received:', JSON.parse(JSON.stringify(response.user)));

    await userStore.finishLogin(response.user, response.access_token);

    isLoginSuccess.value = true;
    countdownInterval = setInterval(() => {
      countdown.value--;
      if (countdown.value <= 0) {
        if (countdownInterval) clearInterval(countdownInterval);
        router.push('/');
      }
    }, 1000);

  } catch (error) {
    const errorInfo = getErrorMessage(error);
    errorModalTitle.value = errorInfo.title;
    errorModalMessage.value = errorInfo.description;
    isErrorModalOpen.value = true;
  } finally {
    isLoading.value = false;
  }
}

function toggleMode() {
  isBackupMode.value = true;
  isAwaitingCode.value = true;
}

function resetFlow() {
  isAwaitingCode.value = false;
  isBackupMode.value = false;
  state.code = '';
}

onUnmounted(() => {
  if (countdownInterval) {
    clearInterval(countdownInterval);
  }
});

// --- Translations ---
const cardTitle = computed(() => currentLanguage.value === 'vi' ? 'Xác thực đăng nhập' : 'Login Authentication');
const loginSubtitle = computed(() => currentLanguage.value === 'vi' ? 'Vui lòng nhập email của bạn để tiếp tục.' : 'Please enter your email to continue.');
const emailInputLabel = computed(() => currentLanguage.value === 'vi' ? 'Địa chỉ email' : 'Email Address');
const emailPlaceholder = computed(() => currentLanguage.value === 'vi' ? 'ban@email.com' : 'you@example.com');
const continueButtonLabel = computed(() => currentLanguage.value === 'vi' ? 'Tiếp tục' : 'Continue');
const useBackupCodeLabel = computed(() => currentLanguage.value === 'vi' ? 'Sử dụng mã dự phòng?' : 'Use a backup code?');
const verificationCodePrompt = computed(() => currentLanguage.value === 'vi' ? 'Mã xác thực đã được gửi đến {email}.' : 'We have sent a verification code to {email}.');
const backupCodePrompt = computed(() => currentLanguage.value === 'vi' ? 'Vui lòng nhập một trong các mã dự phòng của bạn.' : 'Please enter one of your backup codes.');
const codeInputLabel = computed(() => isBackupMode.value ? (currentLanguage.value === 'vi' ? 'Mã dự phòng' : 'Backup Code') : (currentLanguage.value === 'vi' ? 'Mã xác thực' : 'Verification Code'));
const codePlaceholder = computed(() => '******');
const verifyButtonLabel = computed(() => currentLanguage.value === 'vi' ? 'Xác thực' : 'Verify');
const backToEmailLabel = computed(() => currentLanguage.value === 'vi' ? 'Quay lại' : 'Go Back');
const successTitle = computed(() => currentLanguage.value === 'vi' ? 'Đăng nhập thành công!' : 'Login Successful!');
const redirectMessage = computed(() => currentLanguage.value === 'vi' ? 'Đang chuyển hướng trong {countdown} giây...' : 'Redirecting in {countdown} seconds...');
</script>