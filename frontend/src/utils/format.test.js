import { describe, expect, it } from "vitest";

import { formatDate, formatMoney, monthLabel, todayIso } from "@/utils/format";

describe("formatMoney", () => {
  it("EC-P0 valid: numeric value is formatted as currency", () => {
    expect(formatMoney("42.5")).toMatch(/42[,.]50/);
  });

  it("EC-P0 invalid: non-numeric value is returned as-is", () => {
    expect(formatMoney("not-a-number")).toBe("not-a-number");
  });
});

describe("formatDate", () => {
  it("EC-P0 valid: ISO date is formatted", () => {
    expect(formatDate("2026-06-15")).toBe("Jun 15, 2026");
  });
});

describe("monthLabel", () => {
  it("EC-P0 valid: month and year produce label", () => {
    expect(monthLabel(6, 2026)).toBe("Jun 2026");
  });
});

describe("todayIso", () => {
  it("EC-P0 valid: returns YYYY-MM-DD shape", () => {
    expect(todayIso()).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });
});
