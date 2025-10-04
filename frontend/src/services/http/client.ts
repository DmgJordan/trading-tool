import { tryRefresh } from './auth';
import { toHttpError } from './errors';

const normalizeBaseUrl = (value: string | undefined) => {
  if (!value) return '';
  return value.replace(/\/$/, '');
};

export const BASE_URL = normalizeBaseUrl(process.env.NEXT_PUBLIC_API_URL);

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

export interface HttpRequestOptions
  extends Omit<RequestInit, 'method' | 'body' | 'credentials'> {
  auth?: boolean;
  raw?: boolean;
}

const resolveUrl = (path: string): string => {
  if (/^https?:\/\//i.test(path)) {
    return path;
  }

  const base = BASE_URL;

  if (!base) {
    return path;
  }

  if (path.startsWith('/')) {
    return `${base}${path}`;
  }

  return `${base}/${path}`;
};

const shouldSerializeBody = (body: unknown) =>
  body !== undefined && !(body instanceof FormData) && !(body instanceof Blob);

const applyAuthHeader = (headers: Headers) => {
  if (headers.has('Authorization')) return;
  if (typeof window === 'undefined') return;

  try {
    const raw = window.localStorage.getItem('auth_tokens');
    if (!raw) return;
    const tokens = JSON.parse(raw) as { access_token?: string } | null;
    if (tokens?.access_token) {
      headers.set('Authorization', `Bearer ${tokens.access_token}`);
    }
  } catch (error) {
    console.warn('Unable to read auth tokens from localStorage', error);
  }
};

const parseResponse = async <T>(res: Response, raw: boolean): Promise<T> => {
  if (!res.ok) {
    throw await toHttpError(res);
  }

  if (raw) {
    return res as unknown as T;
  }

  if (res.status === 204 || res.status === 205) {
    return undefined as T;
  }

  const contentLength = res.headers.get('content-length');
  if (contentLength === '0') {
    return undefined as T;
  }

  const contentType = res.headers.get('content-type') ?? '';

  if (contentType.includes('application/json')) {
    return (await res.json()) as T;
  }

  if (contentType.startsWith('text/')) {
    return (await res.text()) as unknown as T;
  }

  return undefined as T;
};

const request = async <T>(
  method: HttpMethod,
  path: string,
  body?: unknown,
  opts: HttpRequestOptions = {}
): Promise<T> => {
  const { auth = false, raw = false, headers, ...rest } = opts;
  const url = resolveUrl(path);

  const buildInit = (): RequestInit => {
    const requestHeaders = new Headers(headers ?? undefined);

    if (auth) {
      applyAuthHeader(requestHeaders);
    }

    if (shouldSerializeBody(body) && !requestHeaders.has('Content-Type')) {
      requestHeaders.set('Content-Type', 'application/json');
    }

    const init: RequestInit = {
      method,
      credentials: 'include',
      headers: requestHeaders,
      ...rest,
    };

    if (body !== undefined) {
      if (body instanceof FormData || body instanceof Blob) {
        init.body = body as BodyInit;
      } else {
        init.body = JSON.stringify(body);
      }
    }

    return init;
  };

  const execute = () => fetch(url, buildInit());

  let response = await execute();

  if (response.status === 401 && auth) {
    const refreshed = await tryRefresh();
    if (refreshed) {
      response = await execute();
    }
  }

  return parseResponse<T>(response, raw);
};

const get = <T>(path: string, opts?: HttpRequestOptions) =>
  request<T>('GET', path, undefined, opts);

const post = <T>(path: string, body?: unknown, opts?: HttpRequestOptions) =>
  request<T>('POST', path, body, opts);

const put = <T>(path: string, body?: unknown, opts?: HttpRequestOptions) =>
  request<T>('PUT', path, body, opts);

const del = <T>(path: string, body?: unknown, opts?: HttpRequestOptions) =>
  request<T>('DELETE', path, body, opts);

export const http = {
  get,
  post,
  put,
  del,
};

export default http;
