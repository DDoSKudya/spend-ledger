import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { api, apiPublic } from "@/api/client";
import type { AuthTokenResponse } from "@/types/api";
import type { User } from "@/types/models";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<User | null>(null);
  const accessToken = ref<string | null>(null);

  const isAuthenticated = computed(() => accessToken.value !== null);

  async function login(email: string, password: string): Promise<void> {
    const data = await apiPublic<AuthTokenResponse>("/auth/login", {
      method: "POST",
      body: { email, password },
    });
    accessToken.value = data.access_token;
    await fetchMe();
  }

  async function register(email: string, password: string): Promise<User> {
    return apiPublic<User>("/auth/register", {
      method: "POST",
      body: { email, password },
    });
  }

  async function refresh(): Promise<void> {
    const data = await apiPublic<AuthTokenResponse>("/auth/refresh", { method: "POST" });
    accessToken.value = data.access_token;
  }

  async function fetchMe(): Promise<void> {
    user.value = await api<User>("/auth/me");
  }

  async function logout(): Promise<void> {
    try {
      await apiPublic("/auth/logout", { method: "POST" });
    } finally {
      clear();
    }
  }

  function clear(): void {
    accessToken.value = null;
    user.value = null;
  }

  return {
    user,
    accessToken,
    isAuthenticated,
    login,
    register,
    refresh,
    fetchMe,
    logout,
    clear,
  };
});
