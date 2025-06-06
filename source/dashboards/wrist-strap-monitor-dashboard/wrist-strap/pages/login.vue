<template>
  <div class="flex flex-col min-h-screen bg-gray-50 dark:bg-dark-bg">
    <!-- Header -->
    <header class="p-4 border-b border-gray-200 dark:border-dark-border">
      <div class="container mx-auto flex justify-between items-center">
        <div class="flex items-center gap-3">
          <UIcon name="i-heroicons-shield-check-solid" class="w-8 h-8 text-primary"/>
          <h1 class="text-xl font-bold text-gray-800 dark:text-dark-text-primary">{{ pageTitle }}</h1>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 flex items-center justify-center p-4">
      <UCard class="w-full max-w-md" :ui="{ ring: 'ring-1 ring-gray-200 dark:ring-gray-700' }">
        <div v-if="!isAwaitingCode" class="space-y-6">
          <h2 class="text-2xl font-semibold text-center">{{ loginTitle }}</h2>
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
          <h2 class="text-2xl font-semibold text-center">{{ verificationTitle }}</h2>
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
    </main>

    <!-- Footer -->
    <footer class="p-4 text-center text-sm text-gray-500 dark:text-gray-400 border-t border-gray-200 dark:border-dark-border">
      <p>&copy; {{ new Date().getFullYear() }} IoT Platform. All rights reserved.</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { useLanguage } from '~/composables/useLanguage';
import { useUserStore } from '~/composables/stores/userStore';

// Use a clean layout without the main dashboard's sidebars
definePageMeta({ layout: 'empty' });

const { currentLanguage } = useLanguage();
const userStore = useUserStore();
const toast = useToast();
const router = useRouter();

// UI state management
const isLoading = ref(false);
const isBackupMode = ref(false);
const isAwaitingCode = ref(false);

// Form state
const state = reactive({
  email: '',
  code: '',
});

// --- Client-Side Hashing for Backup Codes ---
// This function securely hashes the backup code before sending it to the backend.
async function sha256(message: string): Promise<string> {
  const msgBuffer = new TextEncoder().encode(message);
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

// --- API Interaction Logic ---

// Step 1: Request a verification code (or check if user exists for backup flow)
async function handleRequestCode() {
  isLoading.value = true;
  try {
    // In a real app, this would be an API call:
    // await $fetch('/api/auth/request-code', { method: 'POST', body: { email: state.email } });

    // For now, we simulate the API call and move to the next step
    console.log(`Simulating API call: Requesting code for email: ${state.email}`);
    await new Promise(resolve => setTimeout(resolve, 1000));

    isAwaitingCode.value = true;
    if (!isBackupMode.value) {
      toast.add({ title: 'Code Sent', description: 'A verification code has been sent to your email.', color: 'green' });
    }
  } catch (error) {
    toast.add({ title: 'Error', description: 'Could not request verification code. Please try again.', color: 'red' });
  } finally {
    isLoading.value = false;
  }
}

// Step 2: Verify the code provided by the user
async function handleVerifyCode() {
  isLoading.value = true;
  try {
    let payload;
    if (isBackupMode.value) {
      // Hash the backup code before sending it to the server for comparison
      const hashedCode = await sha256(state.code);
      payload = { email: state.email, backupCodeHash: hashedCode };
      console.log('Simulating API call: Verifying with hashed backup code:', payload);
    } else {
      payload = { email: state.email, code: state.code };
      console.log('Simulating API call: Verifying with standard one-time code:', payload);
    }

    // In a real app, you would make the API call and get a JWT and user data back
    // const { user, token } = await $fetch('/api/auth/verify-code', { method: 'POST', body: payload });
    // await userStore.finishLogin(user, token);

    // For now, we simulate a successful login
    await new Promise(resolve => setTimeout(resolve, 1000));
    await userStore.mockLogin(state.email);

    toast.add({ title: 'Login Successful!', color: 'green' });
    router.push('/'); // Redirect to the main dashboard

  } catch (error) {
    toast.add({ title: 'Verification Failed', description: 'The code is incorrect. Please try again.', color: 'red' });
  } finally {
    isLoading.value = false;
  }
}

// Toggles the UI to enter a backup code directly
function toggleMode() {
  isBackupMode.value = true;
  isAwaitingCode.value = true; // Go directly to the code entry screen
}

// Resets the entire flow to the initial email entry screen
function resetFlow() {
  isAwaitingCode.value = false;
  isBackupMode.value = false;
  state.code = '';
}

// --- All UI text is translated based on the current language ---
const pageTitle = computed(() => currentLanguage.value === 'vi' ? 'Xác thực Truy cập' : 'Access Authentication');
const loginTitle = computed(() => currentLanguage.value === 'vi' ? 'Chào mừng' : 'Welcome');
const loginSubtitle = computed(() => currentLanguage.value === 'vi' ? 'Vui lòng nhập email của bạn để tiếp tục.' : 'Please enter your email to continue.');
const emailInputLabel = computed(() => currentLanguage.value === 'vi' ? 'Địa chỉ Email' : 'Email Address');
const emailPlaceholder = computed(() => currentLanguage.value === 'vi' ? 'ban@email.com' : 'you@example.com');
const continueButtonLabel = computed(() => currentLanguage.value === 'vi' ? 'Tiếp tục' : 'Continue');
const useBackupCodeLabel = computed(() => currentLanguage.value === 'vi' ? 'Sử dụng mã dự phòng?' : 'Use a backup code?');
const verificationTitle = computed(() => currentLanguage.value === 'vi' ? 'Nhập mã xác thực' : 'Enter Verification Code');
const verificationCodePrompt = computed(() => currentLanguage.value === 'vi' ? 'Chúng tôi đã gửi một mã đến {email}.' : 'We sent a code to {email}.');
const backupCodePrompt = computed(() => currentLanguage.value === 'vi' ? 'Vui lòng nhập một trong các mã dự phòng của bạn.' : 'Please enter one of your backup codes.');
const codeInputLabel = computed(() => isBackupMode.value ? (currentLanguage.value === 'vi' ? 'Mã dự phòng' : 'Backup Code') : (currentLanguage.value === 'vi' ? 'Mã xác thực' : 'Verification Code'));
const codePlaceholder = computed(() => '******');
const verifyButtonLabel = computed(() => currentLanguage.value === 'vi' ? 'Xác thực' : 'Verify');
const backToEmailLabel = computed(() => currentLanguage.value === 'vi' ? 'Quay lại' : 'Go Back');
</script>
