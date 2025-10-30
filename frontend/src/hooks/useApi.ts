/**
 * Generic API hook for RealtorOS.
 * 
 * This hook provides generic API functionality for making
 * HTTP requests with error handling and loading states.
 */

import { useState, useCallback } from 'react'

interface ApiResponse<T> {
  data: T | null
  loading: boolean
  error: Error | null
}

interface ApiOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  headers?: Record<string, string>
  body?: any
}

export function useApi<T = any>() {
  const [state, setState] = useState<ApiResponse<T>>({
    data: null,
    loading: false,
    error: null
  })

  const request = useCallback(async (
    url: string, 
    options: ApiOptions = {}
  ): Promise<T> => {
    setState(prev => ({ ...prev, loading: true, error: null }))

    try {
      const response = await fetch(url, {
        method: options.method || 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        body: options.body ? JSON.stringify(options.body) : undefined
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setState({ data, loading: false, error: null })
      return data
    } catch (error) {
      const errorObj = error instanceof Error ? error : new Error('An unknown error occurred')
      setState({ data: null, loading: false, error: errorObj })
      throw errorObj
    }
  }, [])

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null })
  }, [])

  return {
    ...state,
    request,
    reset
  }
}
