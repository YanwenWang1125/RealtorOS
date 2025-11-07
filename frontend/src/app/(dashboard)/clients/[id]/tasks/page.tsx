/**
 * Client-specific tasks page for RealtorOS.
 * 
 * This component displays all tasks and follow-ups for a specific client
 * with the ability to manage and track task completion.
 */

'use client'

import { useState } from 'react'
import { useParams } from 'next/navigation'
import { useTasks } from '@/lib/hooks/queries/useTasks'
import TaskCard from '@/components/tasks/TaskCard'
import TaskForm from '@/components/tasks/TaskForm'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

export default function ClientTasksPage() {
  const params = useParams()
  const clientId = params.id as string
  
  const { data: tasks = [], isLoading: loading, isError, error } = useTasks({ client_id: parseInt(clientId) })
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [filterStatus, setFilterStatus] = useState('all')
  
  const clientTasks = tasks.filter(task => task.client_id === parseInt(clientId))
  
  const filteredTasks = clientTasks.filter(task => {
    if (filterStatus === 'all') return true
    return task.status === filterStatus
  })

  if (loading) return <div>Loading tasks...</div>
  if (isError) return <div>Error loading tasks: {error?.message || 'Unknown error'}</div>

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Client Tasks</h1>
          <p className="mt-2 text-gray-600">
            Manage follow-up tasks for this client
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary"
        >
          Create Task
        </button>
      </div>

      {/* Filter Controls */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-4">
          <label htmlFor="status" className="text-sm font-medium text-gray-700">
            Filter by Status:
          </label>
          <select
            id="status"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="input-field w-auto"
          >
            <option value="all">All Tasks</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
            <option value="skipped">Skipped</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      {/* Tasks List */}
      <div className="space-y-4">
        {filteredTasks.length > 0 ? (
          filteredTasks.map((task) => (
            <TaskCard key={task.id} task={task} />
          ))
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No tasks found</p>
            <p className="text-gray-400 mt-2">
              {filterStatus !== 'all' 
                ? `No tasks with status "${filterStatus}"`
                : 'Create your first task to get started'
              }
            </p>
          </div>
        )}
      </div>

      {/* Create Task Dialog */}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create New Task</DialogTitle>
          </DialogHeader>
          <TaskForm
            clientId={parseInt(clientId)}
            onSave={() => setShowCreateModal(false)}
            onCancel={() => setShowCreateModal(false)}
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}
