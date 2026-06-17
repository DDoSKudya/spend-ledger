<script setup>
import {
  ArrowDownTrayIcon,
  ArrowRightOnRectangleIcon,
  ChartBarIcon,
  QueueListIcon,
  TagIcon,
  WalletIcon,
} from "@heroicons/vue/24/outline";
import { RouterLink, useRouter } from "vue-router";

import { useAuth } from "@/composables/useAuth";

const router = useRouter();
const { user, logout } = useAuth();

const links = [
  { to: "/expenses", label: "Expenses", icon: WalletIcon },
  { to: "/categories", label: "Categories", icon: QueueListIcon },
  { to: "/tags", label: "Tags", icon: TagIcon },
  { to: "/reports", label: "Reports", icon: ChartBarIcon },
  { to: "/export", label: "Export", icon: ArrowDownTrayIcon },
];

async function handleLogout() {
  await logout();
  await router.push({ name: "login" });
}
</script>

<template>
  <header class="border-b border-slate-200 bg-white">
    <div class="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-4 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex items-center gap-2 text-lg font-semibold text-slate-900">
        <WalletIcon class="size-6" />
        Spend Ledger
      </div>

      <nav class="flex flex-wrap gap-2">
        <RouterLink
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          class="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
          active-class="bg-slate-100 font-medium text-slate-900"
        >
          <component
            :is="link.icon"
            class="size-4"
          />
          {{ link.label }}
        </RouterLink>
      </nav>

      <div class="flex items-center gap-3 text-sm text-slate-600">
        <span class="truncate">{{ user?.email }}</span>
        <button
          type="button"
          class="inline-flex items-center gap-1 rounded-lg px-2 py-1 hover:bg-slate-100"
          @click="handleLogout"
        >
          <ArrowRightOnRectangleIcon class="size-4" />
          Logout
        </button>
      </div>
    </div>
  </header>
</template>
