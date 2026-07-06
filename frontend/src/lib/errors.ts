import { AxiosError } from 'axios'

// Turn any thrown value (usually an AxiosError from our API client) into a
// human-readable message. FastAPI returns { detail: string } on errors.
export function getErrorMessage(error: unknown, fallback = 'Something went wrong. Please try again.'): string {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    // Pydantic validation errors come back as an array of { msg, loc }.
    if (Array.isArray(detail) && detail.length > 0 && detail[0]?.msg) {
      return detail[0].msg
    }
    if (error.response?.status === 403) return 'You do not have permission to do that.'
    if (error.response?.status === 401) return 'Your session has expired. Please log in again.'
    if (error.message) return error.message
  }
  if (error instanceof Error && error.message) return error.message
  return fallback
}
