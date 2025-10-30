/**
 * Tasks overview page for RealtorOS.
 * 
 * This component displays all tasks across all clients
 * with filtering, sorting, and management capabilities.
 */

'use client'

import { useState } from 'react'
import { useTasks } from '@/hooks/useTasks'
import { useClients } from '@/hooks/useClients'
import TaskCard from '@/components/TaskCard'
import TaskForm from '@/components/TaskForm'
import Modal from '@/components/Modal'

export default function TasksPage() {
  const { tasks, loading: tasksLoading, error: tasksError } = useTasks()
  const { clients } = useClients()
  
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [filterStatus, setFilterStatus] = useState('pending')
  const [filterClient, setFilterClient] = useState('all')
  const [sortBy, setSortBy] = useState('scheduled_for')

  const filteredTasks = tasks?.filter(task => {
    const statusMatch = filterStatus === 'all' || task.status === filterStatus
    const clientMatch = filterClient === 'all' || task.client_id === filterClient
    return statusMatch && clientMatch
  }).sort((a, b) => {
    if (sortBy === 'scheduled_for') {
      return new Date(a.scheduled_for).getTime() - new Date(b.scheduled_for).getTime()
    }
    if (sortBy === 'priority') {
      const priorityOrder = { high: 1, medium: 2, low: 3 }
      return priorityOrder[a.priority] - priorityOrder[b.priority]
    }
    return 0
  }) || []

  if (tasksLoading) return <div>Loading tasks...</div>
  if (tasksError) return <div>Error loading tasks: {tasksError.message}</div>

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tasks & Follow-ups</h1>
          <p className="mt-2 text-gray-600">
            Manage all your follow-up tasks and automated emails
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary"
        >
          Create Task
        </button>
      </div>

      {/* Filter and Sort Controls */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Status
            </label>
            <select
              id="status"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="input-field"
            >
              <option value="all">All Tasks</option>
              <option value="pending">Pending</option>
              <option value="completed">Completed</option>
              <option value="skipped">Skipped</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          
          <div>
            <label htmlFor="client" className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Client
            </label>
            <select
              id="client"
              value={filterClient}
              onChange={(e) => setFilterClient(e.target.value)}
              className="input-field"
            >
              <option value="all">All Clients</option>
              {clients?.map(client => (
                <option key={client.id} value={client.id}>
                  {client.name}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label htmlFor="sort" className="block text-sm font-medium text-gray-700 mb-2">
              Sort by
            </label>
            <select
              id="sort"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="input-field"
            >
              <option value="scheduled_for">Scheduled Date</option>
              <option value="priority">Priority</option>
              <option value="created_at">Created Date</option>
            </select>
          </div>
        </div>
      </div>

      {/* Tasks List */}
      <div className="space-y-4">
        {filteredTasks.length > 0 ? (
          filteredTasks.map((task) => {
            const client = clients?.find(c => c.id === task.client_id)
            return (
              <TaskCard 
                key={task.id} 
                task={task} 
                client={client}
              />
            )
          })
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No tasks found</p>
            <p className="text-gray-400 mt-2">
              {filterStatus !== 'all' || filterClient !== 'all'
                ? 'Try adjusting your filters'
                : 'Create your first task to get started'
              }
            </p>
          </div>
        )}
      </div>

      {/* Create Task Modal */}
      {showCreateModal && (
        <Modal
          title="Create New Task"
          onClose={() => setShowCreateModal(false)}
        >
          <TaskForm
            onSave={() => setShowCreateModal(false)}
            onCancel={() => setShowCreateModal(false)}
          />
        </Modal>
      )}
    </div>
  )
}
