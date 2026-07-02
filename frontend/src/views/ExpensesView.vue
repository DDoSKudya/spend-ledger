<script setup lang="ts">
import { PlusIcon } from "@heroicons/vue/24/outline";
import { onMounted, ref } from "vue";

import { getErrorMessage } from "@/api/errors";
import ExpenseFilters from "@/components/expenses/ExpenseFilters.vue";
import ExpenseForm from "@/components/expenses/ExpenseForm.vue";
import ExpenseListItem from "@/components/expenses/ExpenseListItem.vue";
import BaseAlert from "@/components/ui/BaseAlert.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import { useConfirm } from "@/composables/useConfirm";
import { useCategories } from "@/composables/useCategories";
import { useExpenses } from "@/composables/useExpenses";
import { useTags } from "@/composables/useTags";
import { useToast } from "@/composables/useToast";
import type { Expense, ExpensePayload } from "@/types/models";

const {
  items, total, pages, loading, filters,
  load, create, update, remove, setPage, resetFilters,
} = useExpenses();

const { items: categories, load: loadCategories } = useCategories();
const { items: tags, load: loadTags } = useTags();
const { confirm } = useConfirm();
const { show: showToast } = useToast();

const error = ref("");
const showForm = ref(false);
const editingExpense = ref<Expense | null>(null);

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

function openEdit(expense: Expense): void {
  editingExpense.value = expense;
  showForm.value = true;
}

function closeForm() {
  showForm.value = false;
  editingExpense.value = null;
}

async function handleSave(payload: ExpensePayload): Promise<void> {
  error.value = "";
  try {
    if (editingExpense.value) {
      await update(editingExpense.value.id, payload);
      showToast("Expense updated");
    } else {
      await create(payload);
      showToast("Expense created");
    }
    closeForm();
  } catch (err) {
    error.value = getErrorMessage(err);
  }
}

async function handleDelete(expense: Expense): Promise<void> {
  const accepted = await confirm({
    title: "Delete expense",
    message: `Delete "${expense.description || expense.amount}"?`,
    confirmLabel: "Delete",
    danger: true,
  });
  if (!accepted) return;

  error.value = "";
  try {
    await remove(expense.id);
    showToast("Expense deleted");
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

async function handlePageChange(page: number): Promise<void> {
  error.value = "";
  try {
    await setPage(page);
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
          Expenses
        </h1>
        <p class="view-head__meta">
          {{ total }} records
        </p>
      </div>
      <BaseButton @click="openCreate">
        <PlusIcon class="icon-md" />
        Add expense
      </BaseButton>
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

    <div class="split-layout mb-4">
      <BaseCard class="filters-panel">
        <ExpenseFilters
          v-model="filters"
          :categories="categories"
          :tags="tags"
          @apply="handleApply"
          @reset="handleReset"
        />
      </BaseCard>

      <BaseCard>
        <Transition
          name="motion-body"
          mode="out-in"
        >
          <div
            v-if="loading"
            key="loading"
            class="flex justify-center py-12"
          >
            <LoadingSpinner />
          </div>

          <div
            v-else-if="items.length === 0"
            key="empty"
            class="empty"
          >
            <p class="empty__title">
              No expenses yet
            </p>
            <p class="empty__text">
              Add your first expense to start tracking.
            </p>
            <BaseButton
              class="mt-4"
              @click="openCreate"
            >
              <PlusIcon class="icon-md" />
              Add expense
            </BaseButton>
          </div>

          <div
            v-else
            key="list"
            class="list-scroll"
          >
            <ExpenseListItem
              v-for="expense in items"
              :key="expense.id"
              :expense="expense"
              @edit="openEdit"
              @delete="handleDelete"
            />

            <div
              v-if="pages > 1"
              class="pager"
            >
              <span>Page {{ filters.page }} of {{ pages }}</span>
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
          </div>
        </Transition>
      </BaseCard>
    </div>

    <BaseDrawer
      v-model="showForm"
      :title="editingExpense ? 'Edit expense' : 'New expense'"
      @close="closeForm"
    >
      <ExpenseForm
        :expense="editingExpense"
        :categories="categories"
        :tags="tags"
        @save="handleSave"
        @cancel="closeForm"
      />
    </BaseDrawer>
  </div>
</template>
