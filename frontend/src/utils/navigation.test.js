import { describe, expect, it } from "vitest";

import { safeRedirectPath } from "@/utils/navigation";

describe("safeRedirectPath", () => {
  it("EC-P0 valid: returns internal path", () => {
    expect(safeRedirectPath("/reports")).toBe("/reports");
  });

  it("EC-P0 invalid: rejects external and protocol-relative URLs", () => {
    expect(safeRedirectPath("https://evil.com")).toBe("/expenses");
    expect(safeRedirectPath("//evil.com")).toBe("/expenses");
  });

  it("EC-P0 invalid: non-string uses fallback", () => {
    expect(safeRedirectPath(undefined)).toBe("/expenses");
    expect(safeRedirectPath(["/reports"])).toBe("/expenses");
  });
});
