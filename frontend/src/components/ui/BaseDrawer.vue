<script setup lang="ts">
const visible = defineModel<boolean>({ default: false });

withDefaults(
  defineProps<{
    title?: string;
  }>(),
  {
    title: "",
  },
);

defineEmits<{
  close: [];
}>();
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="visible"
        class="drawer-backdrop"
        @click.self="$emit('close')"
      >
        <aside
          class="drawer"
          role="dialog"
          aria-modal="true"
          @click.stop
        >
          <header class="drawer__head">
            <h2
              v-if="title"
              class="drawer__title"
            >
              {{ title }}
            </h2>
            <button
              type="button"
              class="btn btn--ghost btn--icon"
              aria-label="Close"
              @click="$emit('close')"
            >
              ×
            </button>
          </header>
          <div class="drawer__body">
            <slot />
          </div>
        </aside>
      </div>
    </Transition>
  </Teleport>
</template>
