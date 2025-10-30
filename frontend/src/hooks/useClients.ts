/**
 * Custom hook for managing clients data.
 * 
 * This hook provides client data fetching, caching, and state management
 * using SWR for the RealtorOS application.
 */

import useSWR from 'swr'
import { Client } from '@/types/client'

const fetcher = (url: string) => fetch(url).then(res => res.json())

export function useClients() {
  const { data, error, isLoading, mutate } = useSWR<Client[]>(
    '/api/clients',
    fetcher,
    {
      refreshInterval: 30000, // Refresh every 30 seconds
      revalidateOnFocus: true,
      revalidateOnReconnect: true
    }
  )

  return {
    clients: data,
    loading: isLoading,
    error,
    mutate
  }
}

export function useClient(id: string) {
  const { data, error, isLoading, mutate } = useSWR<Client>(
    id ? `/api/clients/${id}` : null,
    fetcher
  )

  return {
    client: data,
    loading: isLoading,
    error,
    mutate
  }
}
