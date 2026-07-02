<script setup lang="ts">
import { computed } from "vue";
import { RouterView, useRoute } from "vue-router";

import ConfirmDialog from "@/components/ConfirmDialog.vue";
import ToastHost from "@/components/ToastHost.vue";

const route = useRoute();

const shellKey = computed(() => route.meta.shell ?? route.matched[0]?.path ?? route.path);
</script>

<template>
  <RouterView v-slot="{ Component }">
    <Transition
      name="shell"
      mode="out-in"
    >
      <component
        :is="Component"
        :key="shellKey"
      />
    </Transition>
  </RouterView>
  <ConfirmDialog />
  <ToastHost />
</template>
