import axios from 'axios'

/**
 * Maps any API/network failure to a specific, useful message.
 *
 * Distinguishes: no connection ("Network Error"), timeouts, and individual
 * HTTP statuses (401/403/404/422/500) so the UI never shows a generic
 * "Network Error" when the server actually responded.
 */
export function describeApiError(error: unknown, fallback = 'An unexpected error occurred.'): string {
  if (axios.isAxiosError(error)) {
    if (!error.response) {
      if (error.code === 'ECONNABORTED') {
        return 'The request timed out. Is the API server running?'
      }
      return `Cannot reach the API server at ${error.config?.baseURL ?? 'the configured address'}. Is FastAPI running?`
    }

    const status = error.response.status
    const detail: unknown = (error.response.data as { detail?: unknown } | undefined)?.detail

    switch (status) {
      case 400:
        return typeof detail === 'string' ? detail : 'The request could not be processed.'
      case 401:
        return 'Incorrect username or password.'
      case 403:
        return 'This account does not have access.'
      case 404:
        return 'API endpoint not found. Is the backend up to date?'
      case 422:
        return 'The submitted data is invalid.'
      case 500:
        return 'Internal server error. Check the FastAPI logs.'
      case 502:
      case 503:
        return 'The API server is unavailable. Try again shortly.'
      default:
        return fallback
    }
  }

  if (error instanceof Error && error.message) {
    return error.message
  }
  return fallback
}
