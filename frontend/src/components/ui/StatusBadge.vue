<script setup lang="ts">
import type { ExportStatus } from "@/types/models";

defineProps<{
  status: ExportStatus | string;
}>();
</script>

<template>
  <span
    class="badge"
    :class="`badge--${status}`"
  >{{ status }}</span>
</template>
