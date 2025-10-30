/**
 * Custom hook for managing emails data.
 * 
 * This hook provides email data fetching, caching, and state management
 * using SWR for the RealtorOS application.
 */

import useSWR from 'swr'
import { Email } from '@/types/email'

const fetcher = (url: string) => fetch(url).then(res => res.json())

export function useEmails() {
  const { data, error, isLoading, mutate } = useSWR<Email[]>(
    '/api/emails',
    fetcher,
    {
      refreshInterval: 30000, // Refresh every 30 seconds
      revalidateOnFocus: true,
      revalidateOnReconnect: true
    }
  )

  return {
    emails: data,
    loading: isLoading,
    error,
    mutate
  }
}

export function useEmail(id: string) {
  const { data, error, isLoading, mutate } = useSWR<Email>(
    id ? `/api/emails/${id}` : null,
    fetcher
  )

  return {
    email: data,
    loading: isLoading,
    error,
    mutate
  }
}

export function useClientEmails(clientId: string) {
  const { data, error, isLoading, mutate } = useSWR<Email[]>(
    clientId ? `/api/emails?client_id=${clientId}` : null,
    fetcher
  )

  return {
    emails: data,
    loading: isLoading,
    error,
    mutate
  }
}
