<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import TagPill from "@/components/ui/TagPill.vue";
import type { Category, ExpenseFilters, Tag } from "@/types/models";
import { toggleItem } from "@/utils/selection";

const filters = defineModel<ExpenseFilters>({ required: true });

defineProps<{
  categories?: Category[];
  tags?: Tag[];
}>();

const emit = defineEmits<{
  apply: [];
  reset: [];
}>();

function toggleTag(tagId: string): void {
  filters.value.tag_ids = toggleItem(filters.value.tag_ids, tagId);
}
</script>

<template>
  <details
    class="filters-panel lg:contents"
    open
  >
    <summary class="lg:hidden">
      Filters
    </summary>

    <div class="stack">
      <BaseInput
        v-model="filters.search"
        label="Search"
        placeholder="Description"
      />
      <BaseSelect
        v-model="filters.category_id"
        label="Category"
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
        v-model="filters.date_from"
        label="From"
        type="date"
      />
      <BaseInput
        v-model="filters.date_to"
        label="To"
        type="date"
      />

      <div>
        <span class="field-label">Tags</span>
        <div class="mt-2 flex flex-wrap gap-2">
          <TagPill
            v-for="tag in tags"
            :key="tag.id"
            :label="tag.name"
            :active="filters.tag_ids.includes(tag.id)"
            @toggle="toggleTag(tag.id)"
          />
        </div>
      </div>

      <div class="flex flex-wrap gap-2">
        <BaseButton @click="emit('apply')">
          Apply
        </BaseButton>
        <BaseButton
          variant="secondary"
          @click="emit('reset')"
        >
          Reset
        </BaseButton>
      </div>
    </div>
  </details>
</template>
