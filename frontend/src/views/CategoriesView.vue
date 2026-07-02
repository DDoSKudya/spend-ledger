<script setup lang="ts">
import { onMounted } from "vue";

import NamedResourcePanel from "@/components/resources/NamedResourcePanel.vue";
import { useCategories } from "@/composables/useCategories";

const { items, loading, load, create, update, remove } = useCategories();

onMounted(() => load());
</script>

<template>
  <NamedResourcePanel
    title="Categories"
    description="Group your spending."
    input-label="New category"
    input-placeholder="e.g. Food"
    empty-title="No categories yet"
    empty-text="Add one to classify expenses."
    delete-title="Delete category"
    :items="items"
    :loading="loading"
    :on-create="create"
    :on-update="update"
    :on-remove="remove"
  />
</template>
