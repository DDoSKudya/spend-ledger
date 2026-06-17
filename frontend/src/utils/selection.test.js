import { describe, expect, it } from "vitest";

import { toggleItem } from "@/utils/selection";

describe("toggleItem", () => {
  it("EC-P0 valid: adds item to empty list", () => {
    expect(toggleItem([], "a")).toEqual(["a"]);
  });

  it("EC-P0 valid: removes existing item", () => {
    expect(toggleItem(["a", "b"], "a")).toEqual(["b"]);
  });

  it("EC-P0 valid: appends new item", () => {
    expect(toggleItem(["a"], "b")).toEqual(["a", "b"]);
  });
});
