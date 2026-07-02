export interface ApiErrorBody {
  detail?: string | Array<{ msg?: string }>;
  code?: string;
}

export interface FetchErrorLike {
  status?: number;
  data?: ApiErrorBody;
  message?: string;
}

export interface ApiRequestOptions {
  method?: string;
  body?: object | BodyInit | null;
  headers?: Record<string, string>;
  _retry?: boolean;
}

export interface AuthTokenResponse {
  access_token: string;
}

export interface ConfigureApiOptions {
  getToken: () => string | null;
  refresh: () => Promise<void>;
  onFailure?: () => void;
}
