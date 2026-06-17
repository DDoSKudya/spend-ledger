import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { configureApi } from "@/api/client";
import { useAuthStore } from "@/stores/auth";

const apiPublic = vi.fn();
const api = vi.fn();

vi.mock("@/api/client", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    apiPublic: (...args) => apiPublic(...args),
    api: (...args) => api(...args),
  };
});

describe("useAuthStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    apiPublic.mockReset();
    api.mockReset();
    configureApi({
      getToken: () => useAuthStore().accessToken,
      refresh: () => useAuthStore().refresh(),
      onFailure: () => useAuthStore().clear(),
    });
  });

  it("EC-P0 valid: login stores access token and loads profile", async () => {
    apiPublic.mockResolvedValueOnce({ access_token: "token-1" });
    api.mockResolvedValueOnce({ email: "user@example.com" });

    const store = useAuthStore();
    await store.login("user@example.com", "secret");

    expect(store.accessToken).toBe("token-1");
    expect(store.user).toEqual({ email: "user@example.com" });
    expect(store.isAuthenticated).toBe(true);
  });

  it("EC-P0 valid: clear resets session", () => {
    const store = useAuthStore();
    store.accessToken = "token-1";
    store.user = { email: "user@example.com" };

    store.clear();

    expect(store.accessToken).toBeNull();
    expect(store.user).toBeNull();
    expect(store.isAuthenticated).toBe(false);
  });

  it("EC-P0 valid: register calls public API", async () => {
    apiPublic.mockResolvedValueOnce({ id: "user-1", email: "new@example.com" });

    const store = useAuthStore();
    const user = await store.register("new@example.com", "secret");

    expect(user).toEqual({ id: "user-1", email: "new@example.com" });
    expect(apiPublic).toHaveBeenCalledWith("/auth/register", {
      method: "POST",
      body: { email: "new@example.com", password: "secret" },
    });
  });

  it("EC-P0 valid: refresh updates access token", async () => {
    apiPublic.mockResolvedValueOnce({ access_token: "token-2" });

    const store = useAuthStore();
    store.accessToken = "token-1";

    await store.refresh();

    expect(store.accessToken).toBe("token-2");
    expect(apiPublic).toHaveBeenCalledWith("/auth/refresh", { method: "POST" });
  });

  it("EC-P0 valid: logout clears session on success", async () => {
    apiPublic.mockResolvedValueOnce(undefined);
    const store = useAuthStore();
    store.accessToken = "token-1";
    store.user = { email: "user@example.com" };

    await store.logout();

    expect(store.accessToken).toBeNull();
    expect(store.user).toBeNull();
    expect(apiPublic).toHaveBeenCalledWith("/auth/logout", { method: "POST" });
  });

  it("EC-P0 valid: logout clears session even if api fails", async () => {
    apiPublic.mockRejectedValueOnce(new Error("network"));
    const store = useAuthStore();
    store.accessToken = "token-1";

    await expect(store.logout()).rejects.toThrow("network");
    expect(store.accessToken).toBeNull();
  });
});
