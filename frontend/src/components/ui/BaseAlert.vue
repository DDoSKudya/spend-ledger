<script setup lang="ts">
import { computed } from "vue";

import type { AlertVariant } from "@/types/models";

const props = withDefaults(
  defineProps<{
    variant?: AlertVariant;
  }>(),
  {
    variant: "error",
  },
);

const variantClass = computed(() => (props.variant === "success" ? "alert--success" : "alert--error"));
</script>

<template>
  <p
    class="alert"
    :class="variantClass"
  >
    <slot />
  </p>
</template>
