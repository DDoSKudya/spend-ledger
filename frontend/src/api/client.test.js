import { beforeEach, describe, expect, it, vi } from "vitest";

const rawApi = vi.fn();

vi.mock("ofetch", () => ({
  ofetch: {
    create: () => rawApi,
  },
}));

describe("api client", () => {
  beforeEach(() => {
    vi.resetModules();
    rawApi.mockReset();
  });

  it("EC-P0 valid: apiPublic delegates to raw client", async () => {
    rawApi.mockResolvedValueOnce({ ok: true });
    const { configureApi, apiPublic } = await import("@/api/client");
    configureApi({
      getToken: () => null,
      refresh: async () => {},
      onFailure: () => {},
    });

    const result = await apiPublic("/health");

    expect(result).toEqual({ ok: true });
    expect(rawApi).toHaveBeenCalledWith("/health", {});
  });

  it("EC-P0 invalid: api retries once after refresh on 401", async () => {
    const refresh = vi.fn().mockResolvedValue(undefined);
    let token = "old-token";

    rawApi
      .mockRejectedValueOnce({ status: 401 })
      .mockResolvedValueOnce({ ok: true });

    const { configureApi, api } = await import("@/api/client");
    configureApi({
      getToken: () => token,
      refresh: async () => {
        await refresh();
        token = "new-token";
      },
      onFailure: () => {
        token = null;
      },
    });

    const result = await api("/categories", {});

    expect(refresh).toHaveBeenCalledOnce();
    expect(result).toEqual({ ok: true });
    expect(rawApi).toHaveBeenCalledTimes(2);
  });

  it("EC-P0 invalid: apiBlob retries once after refresh on 401", async () => {
    const refresh = vi.fn().mockResolvedValue(undefined);
    let token = "old-token";
    const blob = new Blob(["csv"]);

    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({ status: 401, ok: false })
        .mockResolvedValueOnce({ status: 200, ok: true, blob: () => Promise.resolve(blob) }),
    );

    const { configureApi, apiBlob } = await import("@/api/client");
    configureApi({
      getToken: () => token,
      refresh: async () => {
        await refresh();
        token = "new-token";
      },
      onFailure: () => {
        token = null;
      },
    });

    const result = await apiBlob("/exports/job-1/download");

    expect(refresh).toHaveBeenCalledOnce();
    expect(result).toEqual(blob);
    expect(fetch).toHaveBeenCalledTimes(2);
  });

  it("EC-P0 invalid: apiBlob reports non-ok response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        status: 404,
        ok: false,
        json: () => Promise.resolve({ detail: "Export job not found", code: "export_not_found" }),
      }),
    );

    const { configureApi, apiBlob } = await import("@/api/client");
    configureApi({
      getToken: () => null,
      refresh: async () => {},
      onFailure: () => {},
    });

    await expect(apiBlob("/exports/job-1/download")).rejects.toThrow("Export job not found");
  });
});
