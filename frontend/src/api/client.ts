import { ofetch } from "ofetch";

import { getErrorMessage } from "@/api/errors";
import type {
  ApiRequestOptions,
  ConfigureApiOptions,
  FetchErrorLike,
} from "@/types/api";

let getAccessToken = (): string | null => null;
let refreshSession = async (): Promise<void> => {
  throw new Error("Auth is not configured");
};
let clearSession = (): void => {};

export function configureApi({ getToken, refresh, onFailure }: ConfigureApiOptions): void {
  getAccessToken = getToken;
  refreshSession = refresh;
  clearSession = onFailure ?? (() => {});
}

const rawApi = ofetch.create({
  baseURL: "/api/v1",
  credentials: "include",
  onRequest({ options }) {
    const token = getAccessToken();
    if (!token) {
      return;
    }

    const headers = new Headers(options.headers as HeadersInit);
    headers.set("Authorization", `Bearer ${token}`);
    options.headers = headers;
  },
});

export async function apiPublic<T>(url: string, options: ApiRequestOptions = {}): Promise<T> {
  return rawApi<T>(url, options);
}

export async function api<T>(url: string, options: ApiRequestOptions = {}): Promise<T> {
  try {
    return await rawApi<T>(url, options);
  } catch (error) {
    const fetchError = error as FetchErrorLike;
    const shouldRetry = fetchError.status === 401 && !options._retry && getAccessToken() !== null;

    if (shouldRetry) {
      try {
        await refreshSession();
        return api<T>(url, { ...options, _retry: true });
      } catch {
        clearSession();
      }
    }

    throw error;
  }
}

export async function apiBlob(url: string, options: ApiRequestOptions = {}): Promise<Blob> {
  const token = getAccessToken();
  const response = await fetch(`/api/v1${url}`, {
    credentials: "include",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  if (response.status === 401 && token && !options._retry) {
    try {
      await refreshSession();
      return apiBlob(url, { ...options, _retry: true });
    } catch {
      clearSession();
      throw new Error("Download failed (unauthorized)");
    }
  }

  if (!response.ok) {
    let message = `Download failed (${response.status})`;
    try {
      const body = await response.json();
      message = getErrorMessage({ data: body }, message);
    } catch {
      // Non-JSON error body — keep status-based message.
    }
    throw new Error(message);
  }

  return response.blob();
}
