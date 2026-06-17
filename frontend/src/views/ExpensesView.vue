<script setup>
import { PencilSquareIcon, PlusIcon, TrashIcon } from "@heroicons/vue/24/outline";
import { onMounted, ref } from "vue";

import { getErrorMessage } from "@/api/errors";
import ExpenseFilters from "@/components/expenses/ExpenseFilters.vue";
import ExpenseForm from "@/components/expenses/ExpenseForm.vue";
import AppLayout from "@/components/layout/AppLayout.vue";
import BaseAlert from "@/components/ui/BaseAlert.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import { useCategories } from "@/composables/useCategories";
import { useExpenses } from "@/composables/useExpenses";
import { useTags } from "@/composables/useTags";
import { formatDate, formatMoney } from "@/utils/format";

const {
  items,
  total,
  pages,
  loading,
  filters,
  load,
  create,
  update,
  remove,
  setPage,
  resetFilters,
} = useExpenses();

const { items: categories, load: loadCategories } = useCategories();
const { items: tags, load: loadTags } = useTags();

const error = ref("");
const showForm = ref(false);
const editingExpense = ref(null);

onMounted(async () => {
  try {
    await Promise.all([loadCategories(), loadTags(), load()]);
  } catch (err) {
    error.value = getErrorMessage(err);
  }
});

function openCreate() {
  editingExpense.value = null;
  showForm.value = true;
}

function openEdit(expense) {
  editingExpense.value = expense;
  showForm.value = true;
}

function closeForm() {
  showForm.value = false;
  editingExpense.value = null;
}

async function handleSave(payload) {
  error.value = "";
  try {
    if (editingExpense.value) {
      await update(editingExpense.value.id, payload);
    } else {
      await create(payload);
    }
    closeForm();
  } catch (err) {
    error.value = getErrorMessage(err);
  }
}

async function handleDelete(expense) {
  if (!window.confirm(`Delete expense "${expense.description || expense.amount}"?`)) {
    return;
  }

  error.value = "";
  try {
    await remove(expense.id);
  } catch (err) {
    error.value = getErrorMessage(err);
  }
}

async function handleApply() {
  error.value = "";
  try {
    filters.value.page = 1;
    await load();
  } catch (err) {
    error.value = getErrorMessage(err);
  }
}

async function handleReset() {
  error.value = "";
  try {
    await resetFilters();
  } catch (err) {
    error.value = getErrorMessage(err);
  }
}

async function handlePageChange(page) {
  error.value = "";
  try {
    await setPage(page);
  } catch (err) {
    error.value = getErrorMessage(err);
  }
}
</script>

<template>
  <AppLayout>
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold">
          Expenses
        </h1>
        <p class="text-sm text-slate-600">
          {{ total }} total
        </p>
      </div>
      <BaseButton @click="openCreate">
        <PlusIcon class="size-4" />
        Add expense
      </BaseButton>
    </div>

    <BaseAlert
      v-if="error"
      variant="error"
      class="mb-4"
    >
      {{ error }}
    </BaseAlert>

    <BaseCard class="mb-6">
      <ExpenseFilters
        v-model="filters"
        :categories="categories"
        :tags="tags"
        @apply="handleApply"
        @reset="handleReset"
      />
    </BaseCard>

    <BaseCard
      v-if="showForm"
      class="mb-6"
    >
      <h2 class="mb-4 text-lg font-medium">
        {{ editingExpense ? "Edit expense" : "New expense" }}
      </h2>
      <ExpenseForm
        :expense="editingExpense"
        :categories="categories"
        :tags="tags"
        @save="handleSave"
        @cancel="closeForm"
      />
    </BaseCard>

    <BaseCard>
      <div
        v-if="loading"
        class="flex justify-center py-8"
      >
        <LoadingSpinner />
      </div>

      <div
        v-else-if="items.length === 0"
        class="py-8 text-center text-slate-500"
      >
        No expenses yet. Add one above to start tracking spending.
      </div>

      <div
        v-else
        class="overflow-x-auto"
      >
        <table class="min-w-full text-left text-sm">
          <thead class="border-b border-slate-200 text-slate-600">
            <tr>
              <th class="px-2 py-3 font-medium">
                Date
              </th>
              <th class="px-2 py-3 font-medium">
                Amount
              </th>
              <th class="px-2 py-3 font-medium">
                Category
              </th>
              <th class="px-2 py-3 font-medium">
                Description
              </th>
              <th class="px-2 py-3 font-medium">
                Tags
              </th>
              <th class="px-2 py-3 font-medium" />
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="expense in items"
              :key="expense.id"
              class="border-b border-slate-100"
            >
              <td class="px-2 py-3">
                {{ formatDate(expense.expense_date) }}
              </td>
              <td class="px-2 py-3 font-medium">
                {{ formatMoney(expense.amount) }}
              </td>
              <td class="px-2 py-3">
                {{ expense.category.name }}
              </td>
              <td class="px-2 py-3">
                {{ expense.description || "—" }}
              </td>
              <td class="px-2 py-3">
                <span
                  v-for="tag in expense.tags"
                  :key="tag.id"
                  class="mr-1 inline-block rounded-full bg-slate-100 px-2 py-0.5 text-xs"
                >
                  {{ tag.name }}
                </span>
              </td>
              <td class="px-2 py-3 text-right">
                <div class="flex justify-end gap-2">
                  <BaseButton
                    variant="secondary"
                    @click="openEdit(expense)"
                  >
                    <PencilSquareIcon class="size-4" />
                    Edit
                  </BaseButton>
                  <BaseButton
                    variant="danger"
                    @click="handleDelete(expense)"
                  >
                    <TrashIcon class="size-4" />
                    Delete
                  </BaseButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div
        v-if="pages > 1"
        class="mt-4 flex items-center justify-between"
      >
        <p class="text-sm text-slate-600">
          Page {{ filters.page }} of {{ pages }}
        </p>
        <div class="flex gap-2">
          <BaseButton
            variant="secondary"
            :disabled="filters.page <= 1"
            @click="handlePageChange(filters.page - 1)"
          >
            Previous
          </BaseButton>
          <BaseButton
            variant="secondary"
            :disabled="filters.page >= pages"
            @click="handlePageChange(filters.page + 1)"
          >
            Next
          </BaseButton>
        </div>
      </div>
    </BaseCard>
  </AppLayout>
</template>
