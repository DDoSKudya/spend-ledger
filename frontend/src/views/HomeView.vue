<script setup>
import { WalletIcon } from "@heroicons/vue/24/outline";
import { onMounted, ref } from "vue";

import { api } from "@/api/client";

const status = ref("loading");

onMounted(async () => {
  try {
    const data = await api("/health");
    status.value = data.status === "ok" ? "ok" : "error";
  } catch {
    status.value = "error";
  }
});
</script>

<template>
  <main class="mx-auto flex max-w-3xl flex-col gap-4 p-8 font-sans text-slate-900">
    <div class="flex items-center gap-3">
      <WalletIcon class="size-8 text-slate-700" />
      <h1 class="text-2xl font-semibold">
        Spend Ledger
      </h1>
    </div>
    <p class="text-sm text-slate-600">
      API status: {{ status }}
    </p>
  </main>
</template>
