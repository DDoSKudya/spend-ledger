import { describe, expect, it } from "vitest";

import { getErrorMessage } from "@/api/errors";

describe("getErrorMessage", () => {
  it("EC-P0 valid: string detail is returned", () => {
    expect(getErrorMessage({ data: { detail: "Invalid email" } })).toBe("Invalid email");
  });

  it("EC-P0 valid: array detail is joined", () => {
    const error = {
      data: {
        detail: [{ msg: "too short" }, { msg: "required" }],
      },
    };
    expect(getErrorMessage(error)).toBe("too short, required");
  });

  it("EC-P0 invalid: missing detail uses fallback", () => {
    expect(getErrorMessage({}, "Fallback")).toBe("Fallback");
  });

  it("EC-P0 valid: known code is mapped when detail is absent", () => {
    expect(getErrorMessage({ data: { code: "invalid_credentials" } })).toBe(
      "Invalid email or password",
    );
  });

  it("EC-P0 valid: native Error message is returned", () => {
    expect(getErrorMessage(new Error("Export timed out"))).toBe("Export timed out");
  });
});
