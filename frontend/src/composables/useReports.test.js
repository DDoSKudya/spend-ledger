import { beforeEach, describe, expect, it, vi } from "vitest";

import { useReports } from "@/composables/useReports";

const api = vi.fn();

vi.mock("@/api/client", () => ({
  api: (...args) => api(...args),
}));

describe("useReports", () => {
  beforeEach(() => {
    api.mockReset();
  });

  it("EC-P0 valid: load stores monthly report", async () => {
    const payload = {
      year: 2026,
      months: [{ month: 6, total: "42.50", by_category: [] }],
    };
    api.mockResolvedValueOnce(payload);

    const reports = useReports();
    await reports.load({ year: 2026 });

    expect(api).toHaveBeenCalledWith("/reports/monthly?year=2026");
    expect(reports.report.value).toEqual(payload);
    expect(reports.loading.value).toBe(false);
  });

  it("EC-P0 valid: load with category filter", async () => {
    api.mockResolvedValueOnce({ year: 2026, months: [] });

    const reports = useReports();
    await reports.load({ year: 2026, categoryId: "cat-1" });

    expect(api).toHaveBeenCalledWith("/reports/monthly?year=2026&category_id=cat-1");
    expect(reports.loading.value).toBe(false);
  });

  it("EC-P0 invalid: load clears loading after API error", async () => {
    api.mockRejectedValueOnce(new Error("network"));

    const reports = useReports();
    await expect(reports.load({ year: 2026 })).rejects.toThrow("network");
    expect(reports.loading.value).toBe(false);
    expect(reports.report.value).toBeNull();
  });
});
