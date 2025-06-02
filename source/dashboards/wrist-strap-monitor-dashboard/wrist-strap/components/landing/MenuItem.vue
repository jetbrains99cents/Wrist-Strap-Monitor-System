<template>
  <div
      class="menu-item-card menu-item flex flex-col items-center justify-center text-center p-3 m-2 rounded-lg shadow-md hover:shadow-xl transition-shadow cursor-pointer"
      style="width: 130px; height: 140px;"
      @click="handleClick"
  >
    <img
        v-if="iconSrc"
        :src="iconSrc"
        :alt="label"
        class="w-12 h-12 mb-1 object-contain"
        :onerror="`this.onerror=null; this.src='https://placehold.co/48x48/cccccc/000000?text=${label.substring(0,1)}';`"
    />
    <div v-else class="menu-item-icon-placeholder-bg menu-item-icon-placeholder-text w-12 h-12 mb-1 rounded flex items-center justify-center text-xl">
      {{ label.substring(0,1) }}
    </div>
    <h3 class="menu-item-label menu-item-text m-0 text-sm font-medium leading-tight">
      {{ label }}
    </h3>
    <p v-if="description" class="menu-item-description-text text-xs mt-1">
      {{ description }}
    </p>
  </div>
</template>

<script setup lang="ts">
interface Props {
  label: string;
  iconSrc?: string;
  description?: string;
  targetRoute?: string;
}

const props = defineProps<Props>();
const emit = defineEmits(['item-click']);

const handleClick = () => {
  emit('item-click', props.label);
  if (props.targetRoute) {
    // Using Nuxt's built-in navigation
    navigateTo(props.targetRoute);
  }
};
</script>

<style scoped>
.menu-item {
  font-family: 'ABeeZee', sans-serif; /* Ensure font is applied if needed */
  display: flex; /* Already applied by Tailwind class 'flex' */
  flex-direction: column; /* Already applied by Tailwind class 'flex-col' */
  align-items: center; /* Already applied by Tailwind class 'items-center' */
  justify-content: center; /* Already applied by Tailwind class 'justify-center' */
  box-sizing: border-box; /* Tailwind includes this in its base styles */
}
.menu-item-label {
  white-space: pre-line; /* Allows \n to create new lines */
  word-break: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
  max-width: 100%;
}
</style>