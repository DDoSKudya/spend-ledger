<script setup lang="ts">
import { PencilSquareIcon, PlusIcon, TrashIcon } from "@heroicons/vue/24/outline";
import { ref } from "vue";

import { getErrorMessage } from "@/api/errors";
import BaseAlert from "@/components/ui/BaseAlert.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import { useConfirm } from "@/composables/useConfirm";
import { useToast } from "@/composables/useToast";
import type { NamedResource } from "@/types/models";

const props = defineProps<{
  title: string;
  description?: string;
  inputLabel: string;
  inputPlaceholder?: string;
  emptyTitle: string;
  emptyText?: string;
  deleteTitle: string;
  items: NamedResource[];
  loading?: boolean;
  onCreate: (name: string) => Promise<void>;
  onUpdate: (id: string, name: string) => Promise<void>;
  onRemove: (id: string) => Promise<void>;
}>();

const { confirm } = useConfirm();
const { show: showToast } = useToast();

const error = ref("");
const newName = ref("");
const editingId = ref<string | null>(null);
const editingName = ref("");

async function handleCreate(): Promise<void> {
  if (!newName.value.trim()) return;

  error.value = "";
  try {
    await props.onCreate(newName.value.trim());
    newName.value = "";
    showToast("Created");
  } catch (err) {
    error.value = getErrorMessage(err);
  }
}

function startEdit(item: NamedResource): void {
  editingId.value = item.id;
  editingName.value = item.name;
}

function cancelEdit(): void {
  editingId.value = null;
  editingName.value = "";
}

async function handleUpdate(id: string): Promise<void> {
  if (!editingName.value.trim()) return;

  error.value = "";
  try {
    await props.onUpdate(id, editingName.value.trim());
    cancelEdit();
    showToast("Saved");
  } catch (err) {
    error.value = getErrorMessage(err);
  }
}

async function handleDelete(item: NamedResource): Promise<void> {
  const accepted = await confirm({
    title: props.deleteTitle,
    message: `Delete "${item.name}"?`,
    confirmLabel: "Delete",
    danger: true,
  });
  if (!accepted) return;

  error.value = "";
  try {
    await props.onRemove(item.id);
    showToast("Deleted");
  } catch (err) {
    error.value = getErrorMessage(err);
  }
}
</script>

<template>
  <div>
    <header class="view-head">
      <div>
        <h1 class="view-head__title">
          {{ title }}
        </h1>
        <p
          v-if="description"
          class="view-head__meta"
        >
          {{ description }}
        </p>
      </div>
    </header>

    <Transition name="motion-alert">
      <BaseAlert
        v-if="error"
        variant="error"
        class="mb-4"
      >
        {{ error }}
      </BaseAlert>
    </Transition>

    <BaseCard class="mb-4">
      <form
        class="form-grid form-grid--2"
        @submit.prevent="handleCreate"
      >
        <BaseInput
          v-model="newName"
          :label="inputLabel"
          :placeholder="inputPlaceholder"
          required
        />
        <div class="flex items-end">
          <BaseButton type="submit">
            <PlusIcon class="icon-md" />
            Add
          </BaseButton>
        </div>
      </form>
    </BaseCard>

    <BaseCard>
      <Transition
        name="motion-body"
        mode="out-in"
      >
        <div
          v-if="loading"
          key="loading"
          class="flex justify-center py-10"
        >
          <LoadingSpinner />
        </div>

        <div
          v-else-if="items.length"
          key="list"
          class="resource-grid list-scroll"
        >
          <div
            v-for="item in items"
            :key="item.id"
            class="resource-card"
          >
            <template v-if="editingId === item.id">
              <BaseInput
                v-model="editingName"
                class="flex-1"
              />
              <div class="flex gap-1">
                <BaseButton @click="handleUpdate(item.id)">
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
              <span class="resource-card__name">{{ item.name }}</span>
              <div class="flex gap-1">
                <BaseButton
                  variant="ghost"
                  class="btn--icon"
                  aria-label="Rename"
                  @click="startEdit(item)"
                >
                  <PencilSquareIcon class="icon-md" />
                </BaseButton>
                <BaseButton
                  variant="ghost"
                  class="btn--icon"
                  aria-label="Delete"
                  @click="handleDelete(item)"
                >
                  <TrashIcon class="icon-md" />
                </BaseButton>
              </div>
            </template>
          </div>
        </div>

        <div
          v-else
          key="empty"
          class="empty"
        >
          <p class="empty__title">
            {{ emptyTitle }}
          </p>
          <p
            v-if="emptyText"
            class="empty__text"
          >
            {{ emptyText }}
          </p>
        </div>
      </Transition>
    </BaseCard>
  </div>
</template>
