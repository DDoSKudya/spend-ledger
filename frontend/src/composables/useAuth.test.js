import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useAuth } from "@/composables/useAuth";
import { useAuthStore } from "@/stores/auth";

vi.mock("@/api/client", () => ({
  configureApi: vi.fn(),
  apiPublic: vi.fn(),
  api: vi.fn(),
}));

describe("useAuth", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("EC-P0 valid: exposes store state and actions", () => {
    const store = useAuthStore();
    store.user = { email: "user@example.com" };
    store.accessToken = "token";

    const auth = useAuth();

    expect(auth.user.value).toEqual({ email: "user@example.com" });
    expect(auth.isAuthenticated.value).toBe(true);
    expect(auth.login).toBe(store.login);
    expect(auth.logout).toBe(store.logout);
  });
});
