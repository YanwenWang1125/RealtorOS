/**
 * Task card component for RealtorOS.
 * 
 * This component displays task information in a card format
 * with status indicators and action buttons.
 */

'use client'

import Link from 'next/link'
import { Task } from '@/types/task'
import { Client } from '@/types/client'

interface TaskCardProps {
  task: Task
  client?: Client
}

export default function TaskCard({ task, client }: TaskCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'skipped':
        return 'bg-gray-100 text-gray-800'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'low':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const isOverdue = new Date(task.scheduled_for) < new Date() && task.status === 'pending'

  return (
    <div className={`card hover:shadow-md transition-shadow ${isOverdue ? 'border-l-4 border-red-500' : ''}`}>
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{task.followup_type}</h3>
          {client && (
            <p className="text-sm text-gray-600">{client.name}</p>
          )}
        </div>
        <div className="flex space-x-2">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
            {task.status.toUpperCase()}
          </span>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(task.priority)}`}>
            {task.priority.toUpperCase()}
          </span>
        </div>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex items-center text-sm text-gray-600">
          <span className="w-4 h-4 mr-2">📅</span>
          <span className={isOverdue ? 'text-red-600 font-medium' : ''}>
            {new Date(task.scheduled_for).toLocaleString()}
            {isOverdue && ' (Overdue)'}
          </span>
        </div>
        {task.notes && (
          <div className="flex items-start text-sm text-gray-600">
            <span className="w-4 h-4 mr-2 mt-0.5">📝</span>
            <span className="line-clamp-2">{task.notes}</span>
          </div>
        )}
      </div>

      <div className="flex justify-between items-center pt-4 border-t border-gray-200">
        <Link
          href={`/tasks/${task.id}`}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          View Details
        </Link>
        <div className="flex space-x-2">
          {task.status === 'pending' && (
            <>
              <button className="text-green-600 hover:text-green-800 text-sm">
                Complete
              </button>
              <button className="text-gray-600 hover:text-gray-800 text-sm">
                Skip
              </button>
            </>
          )}
          <button className="text-gray-600 hover:text-gray-800 text-sm">
            Reschedule
          </button>
        </div>
      </div>
    </div>
  )
}
