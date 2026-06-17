<script setup>
defineProps({
  variant: {
    type: String,
    default: "error",
  },
});

const variants = {
  error: "border-red-200 bg-red-50 text-red-800",
  success: "border-green-200 bg-green-50 text-green-800",
  info: "border-slate-200 bg-slate-50 text-slate-700",
};
</script>

<template>
  <p
    class="rounded-lg border px-4 py-3 text-sm"
    :class="variants[variant]"
  >
    <slot />
  </p>
</template>
