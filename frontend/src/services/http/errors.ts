export interface HttpError extends Error {
  status: number;
  statusText: string;
  url: string;
  data: unknown;
  response: {
    status: number;
    data: unknown;
  };
}

const extractMessage = (data: unknown, fallback: string) => {
  if (!data) return fallback;
  if (typeof data === 'string') return data;
  if (typeof data === 'object') {
    const detail = (data as { detail?: unknown }).detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      return detail.map(item => String(item)).join(', ');
    }
  }
  return fallback;
};

export async function toHttpError(res: Response): Promise<HttpError> {
  let data: unknown = null;
  const contentType = res.headers.get('content-type') ?? '';

  try {
    if (contentType.includes('application/json')) {
      data = await res.json();
    } else {
      const text = await res.text();
      data = text ? { message: text } : null;
    }
  } catch (error) {
    console.warn('Failed to parse error response', error);
  }

  const message = extractMessage(data, res.statusText || `HTTP ${res.status}`);
  const httpError = new Error(message) as HttpError;
  httpError.status = res.status;
  httpError.statusText = res.statusText;
  httpError.url = res.url;
  httpError.data = data;
  httpError.response = {
    status: res.status,
    data,
  };
  return httpError;
}
