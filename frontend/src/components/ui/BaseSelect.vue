<script setup>
defineOptions({ inheritAttrs: false });

defineProps({
  modelValue: {
    type: [String, Number],
    default: "",
  },
  label: {
    type: String,
    default: "",
  },
  options: {
    type: Array,
    default: () => [],
  },
});

defineEmits(["update:modelValue"]);
</script>

<template>
  <label
    class="flex flex-col gap-1 text-sm text-slate-700"
    v-bind="$attrs"
  >
    <span v-if="label">{{ label }}</span>
    <select
      class="rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 shadow-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
      :value="modelValue"
      @change="$emit('update:modelValue', $event.target.value)"
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
