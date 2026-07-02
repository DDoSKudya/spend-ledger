<script setup lang="ts">
import { computed } from "vue";

import type { ButtonVariant } from "@/types/models";

const props = withDefaults(
  defineProps<{
    type?: "button" | "submit" | "reset";
    variant?: ButtonVariant;
    disabled?: boolean;
    block?: boolean;
  }>(),
  {
    type: "button",
    variant: "primary",
    disabled: false,
    block: false,
  },
);

const variantClass = computed(() => {
  const map: Record<ButtonVariant, string> = {
    primary: "btn--primary",
    secondary: "btn--secondary",
    ghost: "btn--ghost",
    danger: "btn--danger",
  };
  return map[props.variant];
});
</script>

<template>
  <button
    :type="type"
    class="btn"
    :class="[variantClass, block && 'btn--block']"
    :disabled="disabled"
  >
    <slot />
  </button>
</template>
