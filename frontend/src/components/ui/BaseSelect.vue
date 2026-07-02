<script setup lang="ts">
defineOptions({ inheritAttrs: false });

import type { SelectOption } from "@/types/models";

withDefaults(
  defineProps<{
    modelValue?: string | number;
    label?: string;
    options?: SelectOption[];
  }>(),
  {
    modelValue: "",
    label: "",
    options: () => [],
  },
);

const emit = defineEmits<{
  "update:modelValue": [value: string];
}>();

function onChange(event: Event): void {
  const target = event.target as HTMLSelectElement;
  emit("update:modelValue", target.value);
}
</script>

<template>
  <label
    class="field-wrap"
    v-bind="$attrs"
  >
    <span
      v-if="label"
      class="field-label"
    >{{ label }}</span>
    <select
      class="field px-3 py-2.5"
      :value="modelValue"
      @change="onChange"
    >
      <slot />
      <option
        v-for="option in options"
        :key="option.value"
        :value="option.value"
      >
        {{ option.label }}
      </option>
    </select>
  </label>
</template>
