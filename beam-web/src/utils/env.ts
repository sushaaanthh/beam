const API_URL_FALLBACK = 'http://localhost:8000'

export const API_ROOT_URL = (import.meta.env.VITE_API_URL ?? API_URL_FALLBACK).replace(/\/$/, '')
export const API_V1_URL = `${API_ROOT_URL}/api/v1`