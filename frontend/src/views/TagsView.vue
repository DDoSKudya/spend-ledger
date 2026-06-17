<script setup>
import { PencilSquareIcon, PlusIcon, TrashIcon } from "@heroicons/vue/24/outline";
import { onMounted, ref } from "vue";

import { getErrorMessage } from "@/api/errors";
import AppLayout from "@/components/layout/AppLayout.vue";
import BaseAlert from "@/components/ui/BaseAlert.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import { useTags } from "@/composables/useTags";

const { items, loading, load, create, update, remove } = useTags();

const error = ref("");
const newName = ref("");
const editingId = ref(null);
const editingName = ref("");

onMounted(async () => {
  try {
    await load();
  } catch (err) {
    error.value = getErrorMessage(err);
  }
});

async function handleCreate() {
  if (!newName.value.trim()) {
    return;
  }

  error.value = "";
  try {
    await create(newName.value.trim());
    newName.value = "";
  } catch (err) {
    error.value = getErrorMessage(err);
  }
}

function startEdit(tag) {
  editingId.value = tag.id;
  editingName.value = tag.name;
}

function cancelEdit() {
  editingId.value = null;
  editingName.value = "";
}

async function handleUpdate(id) {
  if (!editingName.value.trim()) {
    return;
  }

  error.value = "";
  try {
    await update(id, editingName.value.trim());
    cancelEdit();
  } catch (err) {
    error.value = getErrorMessage(err);
  }
}

async function handleDelete(tag) {
  if (!window.confirm(`Delete tag "${tag.name}"?`)) {
    return;
  }

  error.value = "";
  try {
    await remove(tag.id);
  } catch (err) {
    error.value = getErrorMessage(err);
  }
}
</script>

<template>
  <AppLayout>
    <h1 class="mb-6 text-2xl font-semibold">
      Tags
    </h1>

    <BaseAlert
      v-if="error"
      variant="error"
      class="mb-4"
    >
      {{ error }}
    </BaseAlert>

    <BaseCard class="mb-6">
      <form
        class="flex flex-col gap-3 sm:flex-row sm:items-end"
        @submit.prevent="handleCreate"
      >
        <BaseInput
          v-model="newName"
          label="New tag"
          placeholder="e.g. weekly"
          required
        />
        <BaseButton type="submit">
          <PlusIcon class="size-4" />
          Add
        </BaseButton>
      </form>
    </BaseCard>

    <BaseCard>
      <div
        v-if="loading"
        class="flex justify-center py-8"
      >
        <LoadingSpinner />
      </div>

      <ul
        v-else-if="items.length"
        class="divide-y divide-slate-100"
      >
        <li
          v-for="tag in items"
          :key="tag.id"
          class="flex flex-col gap-3 py-3 sm:flex-row sm:items-center sm:justify-between"
        >
          <template v-if="editingId === tag.id">
            <BaseInput
              v-model="editingName"
              class="flex-1"
            />
            <div class="flex gap-2">
              <BaseButton @click="handleUpdate(tag.id)">
                Save
              </BaseButton>
              <BaseButton
                variant="secondary"
                @click="cancelEdit"
              >
                Cancel
              </BaseButton>
            </div>
          </template>

          <template v-else>
            <span>{{ tag.name }}</span>
            <div class="flex gap-2">
              <BaseButton
                variant="secondary"
                @click="startEdit(tag)"
              >
                <PencilSquareIcon class="size-4" />
                Rename
              </BaseButton>
              <BaseButton
                variant="danger"
                @click="handleDelete(tag)"
              >
                <TrashIcon class="size-4" />
                Delete
              </BaseButton>
            </div>
          </template>
        </li>
      </ul>

      <p
        v-else
        class="py-8 text-center text-slate-500"
      >
        No tags yet. Add tags to group and filter expenses.
      </p>
    </BaseCard>
  </AppLayout>
</template>
