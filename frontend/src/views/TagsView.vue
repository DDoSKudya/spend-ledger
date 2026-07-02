<script setup lang="ts">
import { onMounted } from "vue";

import NamedResourcePanel from "@/components/resources/NamedResourcePanel.vue";
import { useTags } from "@/composables/useTags";

const { items, loading, load, create, update, remove } = useTags();

onMounted(() => load());
</script>

<template>
  <NamedResourcePanel
    title="Tags"
    description="Flexible labels for filtering."
    input-label="New tag"
    input-placeholder="e.g. Travel"
    empty-title="No tags yet"
    empty-text="Tags help filter expenses and exports."
    delete-title="Delete tag"
    :items="items"
    :loading="loading"
    :on-create="create"
    :on-update="update"
    :on-remove="remove"
  />
</template>
