<template>
  <div class="flex flex-1 items-center justify-center p-4">
    <UCard class="w-full max-w-md" :ui="{ ring: 'ring-1 ring-gray-200 dark:ring-gray-700' }">
      <div class="text-center mb-8">
        <div class="inline-flex justify-center items-center">
          <UIcon name="i-heroicons-shield-check-solid" class="w-12 h-12 text-primary"/>
        </div>
        <h2 class="text-2xl font-semibold mt-4">{{ cardTitle }}</h2>
      </div>

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
import { ref, reactive, computed, watch, onMounted } from 'vue';
import { useLanguage } from '~/composables/useLanguage';
import { useUserStore } from '~/stores/userStore';

const { currentLanguage } = useLanguage();
const userStore = useUserStore();
const toast = useToast();
const router = useRouter();

const config = useRuntimeConfig();
const apiBaseUrl = config.public.apiBase;

// UI state management
const isLoading = ref(false);
const isBackupMode = ref(false);
const isAwaitingCode = ref(false);

// Form state
const state = reactive({
  email: '',
  code: '',
});

// Error Modal State
const isErrorModalOpen = ref(false);
const errorModalTitle = ref('');
const errorModalMessage = ref('');

// --- Debug Logging for State Changes ---
onMounted(() => {
  console.log('[Login Page] Component mounted.');
  console.log('[Login Page] Initial State:', {
    email: state.email,
    code: state.code,
    isLoading: isLoading.value,
    isBackupMode: isBackupMode.value,
    isAwaitingCode: isAwaitingCode.value,
  });
});

watch(() => state.email, (newValue) => {
  console.log(`[Login Page] Email input changed: "${newValue}"`);
});

watch(() => state.code, (newValue) => {
  console.log(`[Login Page] Code input changed: "${newValue}"`);
});

watch(isLoading, (newValue) => {
  console.log(`[Login Page] isLoading state changed to: ${newValue}`);
});

watch(isBackupMode, (newValue) => {
  console.log(`[Login Page] isBackupMode state changed to: ${newValue}`);
});

watch(isAwaitingCode, (newValue) => {
  console.log(`[Login Page] isAwaitingCode state changed to: ${newValue}`);
});

// --- Client-Side Hashing for Backup Codes ---
async function sha256(message: string): Promise<string> {
  console.log('[Login Page] Hashing backup code...');
  if (!crypto.subtle) {
    const errorMsg = 'Cryptography API (crypto.subtle) is not available. Ensure you are on a secure context (HTTPS) or a compatible browser.';
    // FIX: Corrected console.error to use backticks for template literal
    console.error(`[Login Page] Hashing Error: ${errorMsg}`);
    throw new Error(errorMsg);
  }
  try {
    const msgBuffer = new TextEncoder().encode(message);
    const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashedCode = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    console.log(`[Login Page] Hashing complete. Input: "${message.substring(0, 3)}...", Hashed: "${hashedCode.substring(0, 10)}..."`);
    return hashedCode;
  } catch (error) {
    console.error('[Login Page] Error during SHA-256 hashing:', error);
    throw new Error(`Failed to hash code: ${error instanceof Error ? error.message : String(error)}`);
  }
}

// Helper to get a user-friendly error message
const getErrorMessage = (error: any): { title: string, description: string, isCritical: boolean } => {
  console.log('[Login Page] Analyzing error:', error);

  // Network/Connection errors (e.g., server down, no internet)
  if (error instanceof Error && (error.message.includes('Failed to fetch') || error.message.includes('network error') || error.message.includes('connection refused'))) {
    return {
      title: currentLanguage.value === 'vi' ? 'Lỗi kết nối' : 'Connection Error',
      description: currentLanguage.value === 'vi' ? 'Không thể kết nối đến máy chủ API. Vui lòng kiểm tra kết nối internet hoặc trạng thái máy chủ.' : 'Could not reach the API server. Please check your internet connection or server status.',
      isCritical: true,
    };
  }
  // Cryptography API error
  if (error instanceof Error && error.message.includes('Cryptography API (crypto.subtle)')) {
    return {
      title: currentLanguage.value === 'vi' ? 'Lỗi bảo mật' : 'Security Error',
      description: currentLanguage.value === 'vi' ? 'API mật mã không khả dụng. Hãy đảm bảo bạn đang truy cập qua HTTPS hoặc trình duyệt tương thích.' : 'Cryptography API not available. Ensure you are on HTTPS or a compatible browser.',
      isCritical: true,
    };
  }
  // API response errors (e.g., 4xx, 5xx) - using Nuxt's $fetch error structure
  if (error && typeof error === 'object' && 'response' in error && error.response) {
    const status = error.response.status;
    const backendMessage = error.response.data?.detail || error.response.data?.message;

    if (status === 401 || status === 403) {
      return {
        title: currentLanguage.value === 'vi' ? 'Xác thực thất bại' : 'Authentication Failed',
        description: currentLanguage.value === 'vi' ? `Email hoặc mã xác thực không đúng. ${backendMessage ? `Chi tiết: ${backendMessage}` : ''}` : `Incorrect email or verification code. ${backendMessage ? `Details: ${backendMessage}` : ''}`,
        isCritical: false,
      };
    } else if (status >= 500) {
      return {
        title: currentLanguage.value === 'vi' ? 'Lỗi máy chủ' : 'Server Error',
        description: currentLanguage.value === 'vi' ? `Máy chủ gặp sự cố. Vui lòng thử lại sau. ${backendMessage ? `Chi tiết: ${backendMessage}` : ''}` : `The server encountered an error. Please try again later. ${backendMessage ? `Details: ${backendMessage}` : ''}`,
        isCritical: true,
      };
    } else if (status >= 400) {
      return {
        title: currentLanguage.value === 'vi' ? 'Lỗi yêu cầu' : 'Request Error',
        description: currentLanguage.value === 'vi' ? `Yêu cầu không hợp lệ. ${backendMessage ? `Chi tiết: ${backendMessage}` : ''}` : `Invalid request. ${backendMessage ? `Details: ${backendMessage}` : ''}`,
        isCritical: false,
      };
    }
  }

  // Fallback for unexpected API responses that didn't throw an error but contained invalid data
  if (error instanceof Error && error.message.includes('Invalid API response content')) {
    return {
      title: currentLanguage.value === 'vi' ? 'Lỗi phản hồi API' : 'API Response Error',
      description: currentLanguage.value === 'vi' ? 'Máy chủ đã trả về phản hồi không hợp lệ. Vui lòng thử lại hoặc liên hệ hỗ trợ.' : 'The server returned an invalid response. Please try again or contact support.',
      isCritical: false,
    };
  }
  // Specific error for OTP not implemented on backend
  if (error instanceof Error && error.message.includes('OTP authentication is not yet implemented')) {
    return {
      title: currentLanguage.value === 'vi' ? 'Xác thực OTP' : 'OTP Authentication',
      description: currentLanguage.value === 'vi' ? 'Tính năng xác thực bằng mã OTP chưa được triển khai trên máy chủ.' : 'OTP authentication feature is not yet implemented on the server.',
      isCritical: false,
    };
  }

  // Fallback for any other unexpected errors
  return {
    title: currentLanguage.value === 'vi' ? 'Lỗi không xác định' : 'Unknown Error',
    description: currentLanguage.value === 'vi' ? `Đã xảy ra lỗi không xác định. Vui lòng thử lại. ${error instanceof Error ? error.message : String(error)}` : `An unknown error occurred. Please try again. ${error instanceof Error ? error.message : String(error)}`,
    isCritical: true,
  };
};

const closeButtonLabel = computed(() => currentLanguage.value === 'vi' ? 'Đóng' : 'Close');


// --- API Interaction Logic ---
async function handleRequestCode() {
  console.log('[Login Page] handleRequestCode called. Attempting to request code.');
  isLoading.value = true;
  try {
    console.log(`[Login Page] Sending request to ${apiBaseUrl}/api/auth/require-code with email: "${state.email}"`);
    const response = await $fetch(`${apiBaseUrl}/api/auth/require-code`, { method: 'POST', body: { email: state.email } });
    console.log('[Login Page] API Response for /api/auth/require-code:', response);

    if (typeof response !== 'object' || response === null || !('success' in response && response.success === true)) {
      console.error('[Login Page] Backend responded successfully but with unexpected data for /require-code:', response);
      throw new Error('Invalid API response content for code request.');
    }

    isAwaitingCode.value = true;
    if (!isBackupMode.value) {
      toast.add({ title: currentLanguage.value === 'vi' ? 'Mã đã gửi' : 'Code Sent', description: currentLanguage.value === 'vi' ? 'Mã xác thực đã được gửi đến email của bạn.' : 'A verification code has been sent to your email.', color: 'green' });
      console.log('[Login Page] Toast: "Code Sent" displayed.');
    }
    console.log('[Login Page] Successfully processed code request.');
  } catch (error) {
    const errorInfo = getErrorMessage(error);
    if (errorInfo.isCritical) {
      errorModalTitle.value = errorInfo.title;
      errorModalMessage.value = errorInfo.description;
      isErrorModalOpen.value = true;
      console.error('[Login Page] Critical Error (Modal displayed):', error);
    } else {
      toast.add({ title: errorInfo.title, description: errorInfo.description, color: 'red' });
      console.error('[Login Page] Non-Critical Error (Toast displayed):', error);
    }
  } finally {
    isLoading.value = false;
    console.log('[Login Page] handleRequestCode finished.');
  }
}

async function handleVerifyCode() {
  console.log('[Login Page] handleVerifyCode called. Attempting to verify code.');
  isLoading.value = true;
  try {
    let payload;
    if (isBackupMode.value) {
      console.log('[Login Page] Verification in Backup Mode.');
      const hashedCode = await sha256(state.code);
      payload = { email: state.email, backupCodeHash: hashedCode };
      console.log(`[Login Page] Sending request to ${apiBaseUrl}/api/auth/verify-code with hashed backup code payload.`);
    } else {
      payload = { email: state.email, code: state.code };
      console.log('[Login Page] Verification in Standard OTP Mode. (Backend support for OTP not yet implemented).');
      console.log(`[Login Page] Sending request to ${apiBaseUrl}/api/auth/verify-code with standard OTP payload.`);
      throw new Error(currentLanguage.value === 'vi' ? 'Xác thực OTP chưa được triển khai.' : 'OTP authentication is not yet implemented.');
    }

    const { user, token } = await $fetch(`${apiBaseUrl}/api/auth/verify-code`, { method: 'POST', body: payload });
    console.log('[Login Page] API Response for /api/auth/verify-code:', { user, token: token ? '***TOKEN_RECEIVED***' : 'NO_TOKEN' });

    if (!user || typeof token !== 'string' || token.length < 50) {
      console.error('[Login Page] API returned an invalid successful login response: User or Token missing/invalid.', { user, token });
      throw new Error('Invalid API response content for verification.');
    }

    await userStore.finishLogin(user, token);
    console.log('[Login Page] User logged in via Pinia store.');

    toast.add({ title: currentLanguage.value === 'vi' ? 'Đăng nhập thành công!' : 'Login Successful!', color: 'green' });
    console.log('[Login Page] Toast: "Login Successful!" displayed.');
    console.log('[Login Page] Redirecting to home page (/).');
    router.push('/');

  } catch (error) {
    const errorInfo = getErrorMessage(error);
    if (errorInfo.isCritical) {
      errorModalTitle.value = errorInfo.title;
      errorModalMessage.value = errorInfo.description;
      isErrorModalOpen.value = true;
      console.error('[Login Page] Critical Error (Modal displayed):', error);
    } else {
      toast.add({ title: errorInfo.title, description: errorInfo.description, color: 'red' });
      console.error('[Login Page] Non-Critical Error (Toast displayed):', error);
    }
  } finally {
    isLoading.value = false;
    console.log('[Login Page] handleVerifyCode finished.');
  }
}

function toggleMode() {
  console.log('[Login Page] toggleMode called. Switching to backup code mode.');
  isBackupMode.value = true;
  isAwaitingCode.value = true;
  console.log(`[Login Page] State after toggleMode: isBackupMode=${isBackupMode.value}, isAwaitingCode=${isAwaitingCode.value}`);
}

function resetFlow() {
  console.log('[Login Page] resetFlow called. Returning to email entry.');
  isAwaitingCode.value = false;
  isBackupMode.value = false;
  state.code = '';
  console.log(`[Login Page] State after resetFlow: isBackupMode=${isBackupMode.value}, isAwaitingCode=${isAwaitingCode.value}, code cleared.`);
}

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
</script>