<script setup lang="ts">
import { useToast } from "@/composables/useToast";

const { toasts } = useToast();
</script>

<template>
  <div
    class="toasts"
    aria-live="polite"
  >
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="toast"
        :class="`toast--${toast.variant}`"
      >
        {{ toast.message }}
      </div>
    </TransitionGroup>
  </div>
</template>
