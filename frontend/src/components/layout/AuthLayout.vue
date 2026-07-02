<script setup lang="ts">
import AppIcon from "@/components/AppIcon.vue";

defineProps<{
  title: string;
}>();
</script>

<template>
  <div class="auth-page">
    <div class="auth-panel">
      <div class="auth-panel__brand">
        <AppIcon icon-class="h-8 w-8" />
        <div>
          <div class="app-brand__name">
            Spend Ledger
          </div>
        </div>
      </div>

      <h1 class="auth-panel__title">
        {{ title }}
      </h1>
      <slot />
    </div>
  </div>
</template>
