import { onUnmounted, ref } from "vue";

import { api, apiBlob } from "@/api/client";

const TERMINAL_STATUSES = new Set(["done", "failed"]);
const POLL_INTERVAL_MS = 1500;
const MAX_POLL_ATTEMPTS = 60;

export function useExport() {
  const job = ref(null);
  const loading = ref(false);
  const polling = ref(false);
  let pollTimer = null;
  let pollAttempts = 0;

  function stopPolling() {
    if (pollTimer !== null) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
    polling.value = false;
    pollAttempts = 0;
  }

  onUnmounted(stopPolling);

  async function start({ format, filters }) {
    loading.value = true;
    stopPolling();
    job.value = null;

    try {
      job.value = await api("/exports", {
        method: "POST",
        body: { format, filters },
      });
      await pollStatus(job.value.job_id);
    } finally {
      loading.value = false;
    }
  }

  async function pollStatus(jobId) {
    polling.value = true;
    pollAttempts = 0;

    const runPoll = async () => {
      pollAttempts += 1;
      if (pollAttempts > MAX_POLL_ATTEMPTS) {
        stopPolling();
        throw new Error("Export timed out");
      }

      try {
        job.value = await api(`/exports/${jobId}`);
      } catch (error) {
        stopPolling();
        throw error;
      }

      if (TERMINAL_STATUSES.has(job.value.status)) {
        stopPolling();
        return true;
      }
      return false;
    };

    if (await runPoll()) {
      return;
    }

    return new Promise((resolve, reject) => {
      pollTimer = setInterval(() => {
        runPoll()
          .then((done) => {
            if (done) {
              resolve();
            }
          })
          .catch(reject);
      }, POLL_INTERVAL_MS);
    });
  }

  async function download(downloadUrl, jobId, format) {
    const path = downloadUrl
      ? downloadUrl.replace(/^\/api\/v1/, "")
      : `/exports/${jobId}/download`;
    const blob = await apiBlob(path);
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `expenses-${jobId}.${format}`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return { job, loading, polling, start, download };
}
