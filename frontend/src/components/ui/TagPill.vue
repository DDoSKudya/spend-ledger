<script setup lang="ts">
withDefaults(
  defineProps<{
    label: string;
    active?: boolean;
    readonly?: boolean;
  }>(),
  {
    active: false,
    readonly: false,
  },
);

defineEmits<{
  toggle: [];
}>();
</script>

<template>
  <span
    v-if="readonly"
    class="chip chip--on chip--readonly"
  >{{ label }}</span>
  <button
    v-else
    type="button"
    class="chip"
    :class="{ 'chip--on': active }"
    @click="$emit('toggle')"
  >
    {{ label }}
  </button>
</template>
