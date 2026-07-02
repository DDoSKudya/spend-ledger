<script setup lang="ts">
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
import BaseAlert from "@/components/ui/BaseAlert.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import { useCategories } from "@/composables/useCategories";
import { useReports } from "@/composables/useReports";
import type { SelectOption } from "@/types/models";
import { formatMoney, monthLabel } from "@/utils/format";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip);

const { items: categories, load: loadCategories } = useCategories();
const { report, loading, load: loadReportData } = useReports();

const error = ref("");
const year = ref(String(new Date().getFullYear()));
const categoryId = ref("");

const yearOptions = computed<SelectOption[]>(() => {
  const current = new Date().getFullYear();
  return Array.from({ length: 5 }, (_, i) => {
    const value = current - i;
    return { value: String(value), label: String(value) };
  });
});

function chartColor(name: string, fallback: string): string {
  if (typeof document === "undefined") return fallback;
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback;
}

const chartData = computed(() => {
  if (!report.value) return { labels: [], datasets: [] };
  const reportYear = report.value.year ?? year.value;
  return {
    labels: report.value.months.map((item) => monthLabel(item.month, reportYear)),
    datasets: [{
      label: "Total",
      backgroundColor: chartColor("--chart-fill", "#5fb9a8"),
      hoverBackgroundColor: chartColor("--chart-fill-hover", "#4da896"),
      borderRadius: 4,
      data: report.value.months.map((item) => Number(item.total)),
    }],
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false } },
    y: { grid: { color: "rgba(148, 163, 184, 0.12)" } },
  },
};

const isEmpty = computed(() => report.value && Number(report.value.grand_total) === 0);

onMounted(async () => {
  try {
    await loadCategories();
    await loadReport();
  } catch (err) {
    error.value = getErrorMessage(err);
  }
});

async function loadReport(): Promise<void> {
  error.value = "";
  try {
    await loadReportData({ year: year.value, categoryId: categoryId.value });
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
          Monthly report
        </h1>
        <p class="view-head__meta">
          Spending by month
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
      <div class="form-grid form-grid--2">
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
        v-else-if="report && isEmpty"
        key="empty"
        class="empty"
      >
        <p class="empty__title">
          No data for {{ year }}
        </p>
        <p class="empty__text">
          Add expenses to see monthly totals.
        </p>
      </div>

      <div
        v-else-if="report"
        key="report"
      >
        <div class="stat-row">
          <div class="stat">
            <div class="stat__label">
              Total
            </div>
            <div class="stat__value">
              {{ formatMoney(report.grand_total) }}
            </div>
          </div>
          <div class="stat">
            <div class="stat__label">
              Year
            </div>
            <div class="stat__value">
              {{ report.year ?? year }}
            </div>
          </div>
          <div class="stat">
            <div class="stat__label">
              Active months
            </div>
            <div class="stat__value">
              {{ report.months.filter((r) => Number(r.count) > 0).length }}
            </div>
          </div>
        </div>

        <BaseCard class="mb-4">
          <div class="h-64">
            <Bar
              :data="chartData"
              :options="chartOptions"
            />
          </div>
        </BaseCard>

        <BaseCard>
          <div
            class="table-scroll"
            tabindex="-1"
          >
            <table class="table-lite">
              <thead>
                <tr>
                  <th>Month</th>
                  <th>Total</th>
                  <th>Count</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="row in report.months"
                  :key="row.month"
                  tabindex="0"
                >
                  <td>{{ monthLabel(row.month, report.year ?? year) }}</td>
                  <td class="mono">
                    {{ formatMoney(row.total) }}
                  </td>
                  <td>{{ row.count }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </BaseCard>
      </div>
    </Transition>
  </div>
</template>
