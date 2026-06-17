import { beforeEach, describe, expect, it, vi } from "vitest";

import { useCategories } from "@/composables/useCategories";

const api = vi.fn();

vi.mock("@/api/client", () => ({
  api: (...args) => api(...args),
}));

describe("useCategories", () => {
  beforeEach(() => {
    api.mockReset();
  });

  it("EC-P0 valid: load stores category list", async () => {
    api.mockResolvedValueOnce([{ id: "1", name: "Food" }]);

    const categories = useCategories();
    await categories.load();

    expect(categories.items.value).toEqual([{ id: "1", name: "Food" }]);
    expect(categories.loading.value).toBe(false);
  });

  it("EC-P0 valid: create update remove reload list", async () => {
    api
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([]);

    const categories = useCategories();
    await categories.create("Food");
    await categories.update("1", "Groceries");
    await categories.remove("1");

    expect(api).toHaveBeenNthCalledWith(1, "/categories", {
      method: "POST",
      body: { name: "Food" },
    });
    expect(api).toHaveBeenNthCalledWith(3, "/categories/1", {
      method: "PUT",
      body: { name: "Groceries" },
    });
    expect(api).toHaveBeenNthCalledWith(5, "/categories/1", { method: "DELETE" });
    expect(api).toHaveBeenCalledTimes(6);
  });
});
