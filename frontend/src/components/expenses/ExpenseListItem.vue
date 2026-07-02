<script setup lang="ts">
import { PencilSquareIcon, TrashIcon } from "@heroicons/vue/24/outline";

import BaseButton from "@/components/ui/BaseButton.vue";
import TagPill from "@/components/ui/TagPill.vue";
import type { Expense } from "@/types/models";
import { formatDate, formatMoney } from "@/utils/format";

defineProps<{
  expense: Expense;
}>();

const emit = defineEmits<{
  edit: [expense: Expense];
  delete: [expense: Expense];
}>();
</script>

<template>
  <article class="expense-item">
    <time class="expense-item__date">{{ formatDate(expense.expense_date) }}</time>
    <div class="expense-item__amount">
      {{ formatMoney(expense.amount) }}
    </div>
    <div class="expense-item__meta">
      <div class="expense-item__category">
        {{ expense.category.name }}
      </div>
      <div class="expense-item__desc">
        {{ expense.description || "No description" }}
      </div>
      <div
        v-if="expense.tags.length"
        class="expense-item__tags"
      >
        <TagPill
          v-for="tag in expense.tags"
          :key="tag.id"
          :label="tag.name"
          readonly
        />
      </div>
    </div>
    <div class="expense-item__actions">
      <BaseButton
        variant="ghost"
        class="btn--icon"
        aria-label="Edit"
        @click="emit('edit', expense)"
      >
        <PencilSquareIcon class="icon-md" />
      </BaseButton>
      <BaseButton
        variant="ghost"
        class="btn--icon"
        aria-label="Delete"
        @click="emit('delete', expense)"
      >
        <TrashIcon class="icon-md" />
      </BaseButton>
    </div>
  </article>
</template>
