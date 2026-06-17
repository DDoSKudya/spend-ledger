<script setup>
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import { toggleItem } from "@/utils/selection";

const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
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

const emit = defineEmits(["update:modelValue", "apply", "reset"]);

function update(field, value) {
  emit("update:modelValue", { ...props.modelValue, [field]: value });
}

function toggleTag(tagId) {
  update("tag_ids", toggleItem(props.modelValue.tag_ids, tagId));
}

const sortOptions = [
  { value: "expense_date:desc", label: "Date (newest)" },
  { value: "expense_date:asc", label: "Date (oldest)" },
  { value: "amount:desc", label: "Amount (high)" },
  { value: "amount:asc", label: "Amount (low)" },
];
</script>

<template>
  <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
    <BaseInput
      :model-value="modelValue.search"
      label="Search"
      placeholder="Description"
      @update:model-value="update('search', $event)"
    />

    <BaseSelect
      :model-value="modelValue.category_id"
      label="Category"
      @update:model-value="update('category_id', $event)"
    >
      <option value="">
        All categories
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
      :model-value="modelValue.date_from"
      label="From"
      type="date"
      @update:model-value="update('date_from', $event)"
    />

    <BaseInput
      :model-value="modelValue.date_to"
      label="To"
      type="date"
      @update:model-value="update('date_to', $event)"
    />

    <BaseSelect
      :model-value="modelValue.sort"
      label="Sort"
      :options="sortOptions"
      @update:model-value="update('sort', $event)"
    />

    <div class="sm:col-span-2">
      <p class="mb-2 text-sm text-slate-700">
        Tags (any)
      </p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="tag in tags"
          :key="tag.id"
          type="button"
          class="rounded-full border px-3 py-1 text-sm transition"
          :class="modelValue.tag_ids.includes(tag.id)
            ? 'border-slate-800 bg-slate-800 text-white'
            : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'"
          @click="toggleTag(tag.id)"
        >
          {{ tag.name }}
        </button>
      </div>
    </div>

    <div class="flex items-end gap-2 sm:col-span-2">
      <BaseButton @click="emit('apply')">
        Apply filters
      </BaseButton>
      <BaseButton
        variant="secondary"
        @click="emit('reset')"
      >
        Reset
      </BaseButton>
    </div>
  </div>
</template>
