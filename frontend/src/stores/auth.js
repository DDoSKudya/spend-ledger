import { defineStore } from "pinia";

import { api, apiPublic } from "@/api/client";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    accessToken: null,
  }),

  getters: {
    isAuthenticated: (state) => state.accessToken !== null,
  },

  actions: {
    async login(email, password) {
      const data = await apiPublic("/auth/login", {
        method: "POST",
        body: { email, password },
      });
      this.accessToken = data.access_token;
      await this.fetchMe();
    },

    async register(email, password) {
      return apiPublic("/auth/register", {
        method: "POST",
        body: { email, password },
      });
    },

    async refresh() {
      const data = await apiPublic("/auth/refresh", { method: "POST" });
      this.accessToken = data.access_token;
    },

    async fetchMe() {
      this.user = await api("/auth/me");
    },

    async logout() {
      try {
        await apiPublic("/auth/logout", { method: "POST" });
      } finally {
        this.clear();
      }
    },

    clear() {
      this.accessToken = null;
      this.user = null;
    },
  },
});
