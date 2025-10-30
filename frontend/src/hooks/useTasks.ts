/**
 * Custom hook for managing tasks data.
 * 
 * This hook provides task data fetching, caching, and state management
 * using SWR for the RealtorOS application.
 */

import useSWR from 'swr'
import { Task } from '@/types/task'

const fetcher = (url: string) => fetch(url).then(res => res.json())

export function useTasks() {
  const { data, error, isLoading, mutate } = useSWR<Task[]>(
    '/api/tasks',
    fetcher,
    {
      refreshInterval: 30000, // Refresh every 30 seconds
      revalidateOnFocus: true,
      revalidateOnReconnect: true
    }
  )

  return {
    tasks: data,
    loading: isLoading,
    error,
    mutate
  }
}

export function useTask(id: string) {
  const { data, error, isLoading, mutate } = useSWR<Task>(
    id ? `/api/tasks/${id}` : null,
    fetcher
  )

  return {
    task: data,
    loading: isLoading,
    error,
    mutate
  }
}

export function useClientTasks(clientId: string) {
  const { data, error, isLoading, mutate } = useSWR<Task[]>(
    clientId ? `/api/clients/${clientId}/tasks` : null,
    fetcher
  )

  return {
    tasks: data,
    loading: isLoading,
    error,
    mutate
  }
}
