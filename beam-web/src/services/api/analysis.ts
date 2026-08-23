import axios from 'axios'

import { apiClient } from './http'
import type {
  AnalysisCreateRequest,
  AnalysisCreatedResponse,
  AnalysisDetail,
  AnalysisListParams,
  AnalysisListResponse,
} from '../../types/analysis'

export const MAX_ANALYSIS_TEXT_CHARS = 20000
export const ANALYSIS_POLL_INTERVAL_MS = 800
export const ANALYSIS_POLL_TIMEOUT_MS = 30000

export async function createAnalysis(
  payload: AnalysisCreateRequest,
): Promise<AnalysisCreatedResponse> {
  const response = await apiClient.post<AnalysisCreatedResponse>('/analysis', payload)
  return response.data
}

export async function fetchAnalysis(sessionId: string): Promise<AnalysisDetail> {
  const response = await apiClient.get<AnalysisDetail>(`/analysis/${sessionId}`)
  return response.data
}

export async function fetchAnalysisHistory(
  params: AnalysisListParams,
): Promise<AnalysisListResponse> {
  const query: Record<string, string | number> = {}
  if (params.page) query.page = params.page
  if (params.page_size) query.page_size = params.page_size
  if (params.search) query.search = params.search
  if (params.status) query.status = params.status
  if (params.sort) query.sort = params.sort

  const response = await apiClient.get<AnalysisListResponse>('/analysis', { params: query })
  return response.data
}

export async function deleteAnalysis(sessionId: string): Promise<void> {
  await apiClient.delete(`/analysis/${sessionId}`)
}

/** Maps API/network failures to safe, user-facing messages. Never exposes stack traces. */
export function getApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status
    const detail: unknown = error.response?.data?.detail

    // Server faults get a curated message; raw detail may leak internals.
    if (status === 500 || status === undefined) {
      return status === 500
        ? 'B.E.A.M. could not complete the analysis. Please try again later.'
        : 'Unable to reach the analysis service. Check your connection and try again.'
    }
    if (typeof detail === 'string' && detail.length > 0 && status !== 500) {
      return detail
    }
    if (Array.isArray(detail)) {
      // FastAPI validation errors — surface the first message only.
      const first = detail[0] as { msg?: string } | undefined
      if (first?.msg) return `Invalid input: ${first.msg}`
    }

    switch (status) {
      case 400:
        return 'The request could not be processed. Please review your input.'
      case 401:
        return 'Your session has expired. Please sign in again.'
      case 403:
        return 'You do not have permission to perform this action.'
      case 404:
        return 'Analysis session not found.'
      case 413:
        return 'The text exceeds the maximum allowed input size.'
      case 422:
        return 'The submitted text is invalid. It must not be empty.'
      default:
        if (error.code === 'ECONNABORTED') {
          return 'The request timed out. Please try again.'
        }
        return 'Unable to reach the analysis service. Check your connection and try again.'
    }
  }

  return 'An unexpected error occurred. Please try again.'
}
