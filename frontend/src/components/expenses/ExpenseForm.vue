<script setup>
import { computed, ref, watch } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import { todayIso } from "@/utils/format";
import { toggleItem } from "@/utils/selection";

const props = defineProps({
  expense: {
    type: Object,
    default: null,
  },
  categories: {
    type: Array,
    default: () => [],
  },
  tags: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["save", "cancel"]);

const form = ref(emptyForm());

const isEdit = computed(() => props.expense !== null);

watch(
  () => props.expense,
  (expense) => {
    if (!expense) {
      form.value = emptyForm();
      return;
    }

    form.value = {
      amount: expense.amount,
      category_id: expense.category.id,
      description: expense.description ?? "",
      expense_date: expense.expense_date,
      tag_ids: expense.tags.map((tag) => tag.id),
    };
  },
  { immediate: true },
);

function emptyForm() {
  return {
    amount: "",
    category_id: "",
    description: "",
    expense_date: todayIso(),
    tag_ids: [],
  };
}

function toggleTag(tagId) {
  form.value.tag_ids = toggleItem(form.value.tag_ids, tagId);
}

function submit() {
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
    class="grid gap-4 sm:grid-cols-2"
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
      <p class="mb-2 text-sm text-slate-700">
        Tags
      </p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="tag in tags"
          :key="tag.id"
          type="button"
          class="rounded-full border px-3 py-1 text-sm transition"
          :class="form.tag_ids.includes(tag.id)
            ? 'border-slate-800 bg-slate-800 text-white'
            : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'"
          @click="toggleTag(tag.id)"
        >
          {{ tag.name }}
        </button>
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
