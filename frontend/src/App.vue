<script setup lang="ts">
import { computed } from "vue";
import { RouterView, useRoute } from "vue-router";

import ConfirmDialog from "@/components/ConfirmDialog.vue";
import ToastHost from "@/components/ToastHost.vue";

const route = useRoute();

const viewKey = computed(() => {
  const shell = route.meta.shell ?? route.matched[0]?.path ?? route.path;
  // App shell hosts its own RouterView; auth routes need a per-path key so
  // register → login remounts instead of reusing the same transition slot.
  if (shell === "app") {
    return shell;
  }
  return route.fullPath;
});
</script>

<template>
  <RouterView v-slot="{ Component }">
    <Transition
      name="shell"
      mode="out-in"
    >
      <component
        :is="Component"
        :key="viewKey"
      />
    </Transition>
  </RouterView>
  <ConfirmDialog />
  <ToastHost />
</template>
