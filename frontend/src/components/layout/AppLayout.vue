<script setup lang="ts">
import type { Component as VueComponent } from "vue";
import {
  ArrowDownTrayIcon,
  ArrowRightOnRectangleIcon,
  ChartBarIcon,
  QueueListIcon,
  TagIcon,
  WalletIcon,
} from "@heroicons/vue/24/outline";
import { RouterLink, RouterView, useRoute, useRouter } from "vue-router";

import AppIcon from "@/components/AppIcon.vue";
import { useAuth } from "@/composables/useAuth";

const router = useRouter();
const route = useRoute();
const { user, logout } = useAuth();

const nav: Array<{ to: string; label: string; short: string; icon: VueComponent }> = [
  { to: "/expenses", label: "Expenses", short: "Spend", icon: WalletIcon },
  { to: "/categories", label: "Categories", short: "Cats", icon: QueueListIcon },
  { to: "/tags", label: "Tags", short: "Tags", icon: TagIcon },
  { to: "/reports", label: "Reports", short: "Stats", icon: ChartBarIcon },
  { to: "/export", label: "Export", short: "Export", icon: ArrowDownTrayIcon },
];

function isActive(path: string): boolean {
  return route.path === path;
}

async function handleLogout(): Promise<void> {
  await logout();
  await router.push({ name: "login" });
}
</script>

<template>
  <div class="app">
    <header class="app-header">
      <RouterLink
        to="/expenses"
        class="app-brand"
      >
        <AppIcon icon-class="h-7 w-7" />
        <span class="app-brand__name">Spend Ledger</span>
      </RouterLink>

      <nav
        class="app-nav"
        aria-label="Main"
      >
        <RouterLink
          v-for="item in nav"
          :key="item.to"
          :to="item.to"
          class="app-nav__link"
          :class="{ 'app-nav__link--active': isActive(item.to) }"
        >
          {{ item.label }}
        </RouterLink>
      </nav>

      <div class="app-header__actions">
        <span
          v-if="user"
          class="app-user"
        >{{ user.email }}</span>
        <button
          type="button"
          class="btn btn--ghost btn--icon"
          aria-label="Logout"
          title="Logout"
          @click="handleLogout"
        >
          <ArrowRightOnRectangleIcon class="icon-md" />
        </button>
      </div>
    </header>

    <main class="app-main">
      <RouterView v-slot="{ Component: PageComponent }">
        <Transition
          name="page-fade"
          mode="out-in"
        >
          <component
            :is="PageComponent"
            :key="route.path"
          />
        </Transition>
      </RouterView>
    </main>

    <nav
      class="app-tabbar"
      aria-label="Mobile"
    >
      <RouterLink
        v-for="item in nav"
        :key="item.to"
        :to="item.to"
        class="app-tabbar__link"
        :class="{ 'app-tabbar__link--active': isActive(item.to) }"
      >
        <component
          :is="item.icon"
          class="icon-md"
        />
        <span>{{ item.short }}</span>
      </RouterLink>
    </nav>
  </div>
</template>
