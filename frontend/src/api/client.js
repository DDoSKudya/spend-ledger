import { ofetch } from "ofetch";

import { getErrorMessage } from "@/api/errors";

let getAccessToken = () => null;
let refreshSession = async () => {
  throw new Error("Auth is not configured");
};
let clearSession = () => {};

export function configureApi({ getToken, refresh, onFailure }) {
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

    options.headers = {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    };
  },
});

export async function apiPublic(url, options = {}) {
  return rawApi(url, options);
}

export async function api(url, options = {}) {
  try {
    return await rawApi(url, options);
  } catch (error) {
    const shouldRetry = error?.status === 401 && !options._retry && getAccessToken() !== null;

    if (shouldRetry) {
      try {
        await refreshSession();
        return api(url, { ...options, _retry: true });
      } catch {
        clearSession();
      }
    }

    throw error;
  }
}

export async function apiBlob(url, options = {}) {
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
