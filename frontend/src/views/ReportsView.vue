<script setup>
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  LinearScale,
  Tooltip,
} from "chart.js";
import { computed, onMounted, ref } from "vue";
import { Bar } from "vue-chartjs";

import { getErrorMessage } from "@/api/errors";
import AppLayout from "@/components/layout/AppLayout.vue";
import BaseAlert from "@/components/ui/BaseAlert.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import { useCategories } from "@/composables/useCategories";
import { useReports } from "@/composables/useReports";
import { formatMoney, monthLabel } from "@/utils/format";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip);

const { items: categories, load: loadCategories } = useCategories();
const { report, loading, load: loadReportData } = useReports();

const error = ref("");
const year = ref(String(new Date().getFullYear()));
const categoryId = ref("");

const yearOptions = computed(() => {
  const current = new Date().getFullYear();
  return Array.from({ length: 5 }, (_, index) => {
    const value = current - index;
    return { value: String(value), label: String(value) };
  });
});

const chartData = computed(() => {
  if (!report.value) {
    return { labels: [], datasets: [] };
  }

  const reportYear = report.value.year ?? year.value;

  return {
    labels: report.value.months.map((item) => monthLabel(item.month, reportYear)),
    datasets: [
      {
        label: "Total",
        backgroundColor: "#334155",
        data: report.value.months.map((item) => Number(item.total)),
      },
    ],
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
};

const isEmptyReport = computed(() => {
  if (!report.value) {
    return false;
  }
  return Number(report.value.grand_total) === 0;
});

onMounted(async () => {
  try {
    await loadCategories();
    await loadReport();
  } catch (err) {
    error.value = getErrorMessage(err);
  }
});

async function loadReport() {
  error.value = "";
  try {
    await loadReportData({ year: year.value, categoryId: categoryId.value });
  } catch (err) {
    error.value = getErrorMessage(err);
  }
}
</script>

<template>
  <AppLayout>
    <h1 class="mb-6 text-2xl font-semibold">
      Monthly report
    </h1>

    <BaseAlert
      v-if="error"
      variant="error"
      class="mb-4"
    >
      {{ error }}
    </BaseAlert>

    <BaseCard class="mb-6">
      <div class="grid gap-4 sm:grid-cols-2">
        <BaseSelect
          v-model="year"
          label="Year"
          :options="yearOptions"
          @update:model-value="loadReport"
        />

        <BaseSelect
          v-model="categoryId"
          label="Category"
          @update:model-value="loadReport"
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
      </div>
    </BaseCard>

    <div
      v-if="loading"
      class="flex justify-center py-12"
    >
      <LoadingSpinner />
    </div>

    <template v-else-if="report">
      <p
        v-if="isEmptyReport"
        class="py-8 text-center text-slate-500"
      >
        No expenses in {{ year }}. Add expenses to see monthly totals here.
      </p>

      <template v-else>
        <BaseCard class="mb-6">
          <p class="mb-4 text-sm text-slate-600">
            Grand total: <span class="font-semibold text-slate-900">{{ formatMoney(report.grand_total) }}</span>
          </p>
          <div class="h-72">
            <Bar
              :data="chartData"
              :options="chartOptions"
            />
          </div>
        </BaseCard>

        <BaseCard>
          <table class="min-w-full text-left text-sm">
            <thead class="border-b border-slate-200 text-slate-600">
              <tr>
                <th class="px-2 py-3 font-medium">
                  Month
                </th>
                <th class="px-2 py-3 font-medium">
                  Total
                </th>
                <th class="px-2 py-3 font-medium">
                  Count
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in report.months"
                :key="row.month"
                class="border-b border-slate-100"
              >
                <td class="px-2 py-3">
                  {{ monthLabel(row.month, report.year ?? year) }}
                </td>
                <td class="px-2 py-3 font-medium">
                  {{ formatMoney(row.total) }}
                </td>
                <td class="px-2 py-3">
                  {{ row.count }}
                </td>
              </tr>
            </tbody>
          </table>
        </BaseCard>
      </template>
    </template>
  </AppLayout>
</template>
