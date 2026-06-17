import { beforeEach, describe, expect, it, vi } from "vitest";

import { useTags } from "@/composables/useTags";

const api = vi.fn();

vi.mock("@/api/client", () => ({
  api: (...args) => api(...args),
}));

describe("useTags", () => {
  beforeEach(() => {
    api.mockReset();
  });

  it("EC-P0 valid: load stores tag list", async () => {
    api.mockResolvedValueOnce([{ id: "1", name: "weekly" }]);

    const tags = useTags();
    await tags.load();

    expect(tags.items.value).toEqual([{ id: "1", name: "weekly" }]);
    expect(tags.loading.value).toBe(false);
  });

  it("EC-P0 valid: create update remove reload list", async () => {
    api
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([]);

    const tags = useTags();
    await tags.create("weekly");
    await tags.update("1", "monthly");
    await tags.remove("1");

    expect(api).toHaveBeenNthCalledWith(1, "/tags", {
      method: "POST",
      body: { name: "weekly" },
    });
    expect(api).toHaveBeenNthCalledWith(3, "/tags/1", {
      method: "PATCH",
      body: { name: "monthly" },
    });
    expect(api).toHaveBeenNthCalledWith(5, "/tags/1", { method: "DELETE" });
    expect(api).toHaveBeenCalledTimes(6);
  });
});
