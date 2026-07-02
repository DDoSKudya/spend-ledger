import { ref } from "vue";

import { api } from "@/api/client";
import type { MonthlyReport } from "@/types/models";

interface LoadReportParams {
  year: string | number;
  categoryId?: string;
}

export function useReports() {
  const report = ref<MonthlyReport | null>(null);
  const loading = ref(false);

  async function load({ year, categoryId = "" }: LoadReportParams): Promise<void> {
    loading.value = true;
    try {
      const params = new URLSearchParams({ year: String(year) });
      if (categoryId) {
        params.set("category_id", categoryId);
      }
      report.value = await api<MonthlyReport>(`/reports/monthly?${params.toString()}`);
    } finally {
      loading.value = false;
    }
  }

  return { report, loading, load };
}
