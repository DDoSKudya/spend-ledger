<script setup lang="ts">
import { computed, ref, watch } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import TagPill from "@/components/ui/TagPill.vue";
import type { Category, Expense, ExpensePayload, Tag } from "@/types/models";
import { todayIso } from "@/utils/format";
import { toggleItem } from "@/utils/selection";

interface ExpenseFormState {
  amount: string | number;
  category_id: string;
  description: string;
  expense_date: string;
  tag_ids: string[];
}

const props = withDefaults(
  defineProps<{
    expense?: Expense | null;
    categories?: Category[];
    tags?: Tag[];
  }>(),
  {
    expense: null,
    categories: () => [],
    tags: () => [],
  },
);

const emit = defineEmits<{
  save: [payload: ExpensePayload];
  cancel: [];
}>();

function emptyForm(): ExpenseFormState {
  return {
    amount: "",
    category_id: "",
    description: "",
    expense_date: todayIso(),
    tag_ids: [],
  };
}

const form = ref<ExpenseFormState>(emptyForm());
const isEdit = computed(() => props.expense !== null);

watch(
  () => props.expense,
  (expense) => {
    form.value = expense
      ? {
          amount: expense.amount,
          category_id: expense.category.id,
          description: expense.description ?? "",
          expense_date: expense.expense_date,
          tag_ids: expense.tags.map((tag) => tag.id),
        }
      : emptyForm();
  },
  { immediate: true },
);

function toggleTag(tagId: string): void {
  form.value.tag_ids = toggleItem(form.value.tag_ids, tagId);
}

function submit(): void {
  emit("save", {
    amount: form.value.amount,
    category_id: form.value.category_id,
    description: form.value.description || null,
    expense_date: form.value.expense_date,
    tag_ids: form.value.tag_ids,
  });
}
</script>

<template>
  <form
    class="form-grid form-grid--2"
    @submit.prevent="submit"
  >
    <BaseInput
      v-model="form.amount"
      label="Amount"
      type="number"
      step="0.01"
      min="0.01"
      required
    />
    <BaseInput
      v-model="form.expense_date"
      label="Date"
      type="date"
      required
    />

    <BaseSelect
      v-model="form.category_id"
      label="Category"
      required
    >
      <option
        value=""
        disabled
      >
        Select category
      </option>
      <option
        v-for="category in categories"
        :key="category.id"
        :value="category.id"
      >
        {{ category.name }}
      </option>
    </BaseSelect>

    <BaseInput
      v-model="form.description"
      label="Description"
      placeholder="Optional"
    />

    <div class="sm:col-span-2">
      <span class="field-label">Tags</span>
      <div class="mt-2 flex flex-wrap gap-2">
        <TagPill
          v-for="tag in tags"
          :key="tag.id"
          :label="tag.name"
          :active="form.tag_ids.includes(tag.id)"
          @toggle="toggleTag(tag.id)"
        />
      </div>
    </div>

    <div class="flex gap-2 sm:col-span-2">
      <BaseButton type="submit">
        {{ isEdit ? "Save changes" : "Create expense" }}
      </BaseButton>
      <BaseButton
        type="button"
        variant="secondary"
        @click="emit('cancel')"
      >
        Cancel
      </BaseButton>
    </div>
  </form>
</template>
