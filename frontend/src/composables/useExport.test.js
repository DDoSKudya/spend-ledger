import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useExport } from "@/composables/useExport";

const api = vi.fn();
const apiBlob = vi.fn();

vi.mock("@/api/client", () => ({
  api: (...args) => api(...args),
  apiBlob: (...args) => apiBlob(...args),
}));

describe("useExport", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    api.mockReset();
    apiBlob.mockReset();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("EC-P0 valid: start polls until terminal status", async () => {
    api
      .mockResolvedValueOnce({ job_id: "job-1", status: "pending" })
      .mockResolvedValueOnce({ job_id: "job-1", status: "processing" })
      .mockResolvedValueOnce({ job_id: "job-1", status: "done" });

    const exports = useExport();
    const startPromise = exports.start({ format: "csv", filters: {} });
    await vi.advanceTimersByTimeAsync(1500);
    await startPromise;

    expect(exports.job.value.status).toBe("done");
    expect(exports.polling.value).toBe(false);
    expect(api).toHaveBeenCalledTimes(3);
  });

  it("EC-P0 invalid: poll error stops polling", async () => {
    api
      .mockResolvedValueOnce({ job_id: "job-1", status: "pending" })
      .mockRejectedValueOnce(new Error("network"));

    const exports = useExport();
    await expect(exports.start({ format: "csv", filters: {} })).rejects.toThrow("network");
    expect(exports.polling.value).toBe(false);
  });

  it("EC-P0 invalid: polling times out when job stays pending", async () => {
    api.mockResolvedValue({ job_id: "job-1", status: "pending" });

    const exports = useExport();
    const startPromise = exports.start({ format: "csv", filters: {} });
    const expectation = expect(startPromise).rejects.toThrow("Export timed out");

    for (let attempt = 0; attempt < 60; attempt += 1) {
      await vi.advanceTimersByTimeAsync(1500);
    }

    await expectation;
    expect(exports.polling.value).toBe(false);
  });

  it("EC-P0 valid: download saves blob with expected filename", async () => {
    const click = vi.fn();
    const createObjectURL = vi.fn(() => "blob:url");
    const revokeObjectURL = vi.fn();
    vi.stubGlobal("URL", { createObjectURL, revokeObjectURL });
    vi.stubGlobal(
      "document",
      {
        createElement: () => ({ click, download: "", href: "" }),
      },
    );

    apiBlob.mockResolvedValueOnce(new Blob(["data"]));

    const exports = useExport();
    await exports.download(undefined, "job-1", "csv");

    expect(apiBlob).toHaveBeenCalledWith("/exports/job-1/download");
    expect(click).toHaveBeenCalledOnce();
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:url");
  });
});
