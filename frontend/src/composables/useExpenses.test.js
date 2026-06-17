import { beforeEach, describe, expect, it, vi } from "vitest";

import { useExpenses } from "@/composables/useExpenses";

const api = vi.fn();

vi.mock("@/api/client", () => ({
  api: (...args) => api(...args),
}));

describe("useExpenses", () => {
  beforeEach(() => {
    api.mockReset();
  });

  it("EC-P0 valid: load populates pagination state", async () => {
    api.mockResolvedValueOnce({
      items: [{ id: "1" }],
      total: 1,
      pages: 1,
      page: 1,
      size: 20,
    });

    const expenses = useExpenses();
    await expenses.load();

    expect(expenses.items.value).toEqual([{ id: "1" }]);
    expect(expenses.total.value).toBe(1);
    expect(expenses.loading.value).toBe(false);
    expect(api).toHaveBeenCalledWith(
      "/expenses?page=1&size=20&sort=expense_date%3Adesc",
    );
  });

  it("EC-P1 valid: filters are serialized into query string", async () => {
    api.mockResolvedValueOnce({
      items: [],
      total: 0,
      pages: 0,
      page: 1,
      size: 20,
    });

    const expenses = useExpenses();
    expenses.filters.value = {
      page: 2,
      size: 10,
      sort: "amount:asc",
      category_id: "cat-1",
      tag_ids: ["tag-1", "tag-2"],
      date_from: "2026-06-01",
      date_to: "2026-06-30",
      search: "coffee",
    };
    await expenses.load();

    const url = api.mock.calls[0][0];
    expect(url).toContain("page=2");
    expect(url).toContain("category_id=cat-1");
    expect(url).toContain("date_from=2026-06-01");
    expect(url).toContain("search=coffee");
    expect(url).toContain("tag_ids=tag-1");
    expect(url).toContain("tag_ids=tag-2");
  });

  it("EC-P0 valid: create reloads list", async () => {
    api
      .mockResolvedValueOnce({ items: [], total: 0, pages: 0, page: 1, size: 20 })
      .mockResolvedValueOnce({ items: [], total: 0, pages: 0, page: 1, size: 20 });

    const expenses = useExpenses();
    await expenses.create({ amount: "10.00" });

    expect(api).toHaveBeenNthCalledWith(1, "/expenses", {
      method: "POST",
      body: { amount: "10.00" },
    });
    expect(api).toHaveBeenCalledTimes(2);
  });

  it("EC-P0 valid: setPage and resetFilters trigger reload", async () => {
    api.mockResolvedValue({
      items: [],
      total: 0,
      pages: 0,
      page: 3,
      size: 20,
    });

    const expenses = useExpenses();
    await expenses.setPage(3);
    expect(api.mock.calls[0][0]).toContain("page=3");

    api.mockResolvedValue({
      items: [],
      total: 0,
      pages: 0,
      page: 1,
      size: 20,
    });
    await expenses.resetFilters();
    expect(expenses.filters.value.page).toBe(1);
    expect(expenses.filters.value.sort).toBe("expense_date:desc");
    expect(api).toHaveBeenCalledTimes(2);
  });
});
