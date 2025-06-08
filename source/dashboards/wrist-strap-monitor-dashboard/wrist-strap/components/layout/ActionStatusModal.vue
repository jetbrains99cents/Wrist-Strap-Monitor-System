<template>
  <UModal v-model="state.isOpen" prevent-close>
    <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
      <div class="p-4 text-center">
        <div class="mb-4">
          <UIcon v-if="state.icon" :name="state.icon" :class="['w-16 h-16 mx-auto', state.color]" />
        </div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
          {{ state.title }}
        </h3>
        <p v-if="state.description" class="mt-2 text-sm text-gray-500 dark:text-gray-400">
          {{ state.description.replace('{countdown}', state.countdown.toString()) }}
        </p>
      </div>
    </UCard>
  </UModal>
</template>

<script setup lang="ts">
// This composable holds the global state for the modal
import {useActionStatusModal} from "~/composables/useActionStatusModal";

const { state } = useActionStatusModal();
</script>