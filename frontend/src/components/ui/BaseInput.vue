<script setup lang="ts">
defineOptions({ inheritAttrs: false });

withDefaults(
  defineProps<{
    modelValue?: string | number;
    label?: string;
    type?: string;
    placeholder?: string;
    required?: boolean;
  }>(),
  {
    modelValue: "",
    label: "",
    type: "text",
    placeholder: "",
    required: false,
  },
);

const emit = defineEmits<{
  "update:modelValue": [value: string];
}>();

function onInput(event: Event): void {
  const target = event.target as HTMLInputElement;
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
    <input
      class="field px-3 py-2.5"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :required="required"
      @input="onInput"
    >
  </label>
</template>
