/**
 * Task detail page for RealtorOS.
 * 
 * This component displays detailed information about a specific task
 * including email preview, completion status, and management options.
 */

'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useTasks } from '@/lib/hooks/queries/useTasks'
import { useClients } from '@/lib/hooks/queries/useClients'
import { useEmails } from '@/lib/hooks/queries/useEmails'
import TaskForm from '@/components/tasks/TaskForm'
import EmailPreview from '@/components/emails/EmailPreview'
import Modal from '@/components/ui/Modal'

export default function TaskDetailPage() {
  const params = useParams()
  const router = useRouter()
  const taskId = parseInt(params.id as string)
  
  const { data: tasks = [], isLoading: tasksLoading, isError: tasksError, error } = useTasks()
  const { data: clients = [] } = useClients()
  const { data: emails = [] } = useEmails()
  
  const [isEditing, setIsEditing] = useState(false)
  const [showEmailModal, setShowEmailModal] = useState(false)
  
  const task = tasks?.find(t => t.id === taskId)
  const client = clients?.find(c => c.id === task?.client_id)
  const taskEmails = emails?.filter(e => e.task_id === taskId) || []

  if (tasksLoading) return <div>Loading task...</div>
  if (tasksError) return <div>Error loading task: {error?.message || 'Unknown error'}</div>
  if (!task) return <div>Task not found</div>

  const handleComplete = async () => {
    // TODO: Implement task completion
    console.log('Complete task:', taskId)
  }

  const handleSkip = async () => {
    // TODO: Implement task skip
    console.log('Skip task:', taskId)
  }

  const handleReschedule = () => {
    setIsEditing(true)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            {task.followup_type} Follow-up
          </h1>
          <p className="mt-2 text-gray-600">
            {client?.name} - {client?.email}
          </p>
          <div className="mt-2 flex items-center space-x-4">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              task.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
              task.status === 'completed' ? 'bg-green-100 text-green-800' :
              task.status === 'skipped' ? 'bg-gray-100 text-gray-800' :
              'bg-red-100 text-red-800'
            }`}>
              {task.status.toUpperCase()}
            </span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              task.priority === 'high' ? 'bg-red-100 text-red-800' :
              task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
              'bg-green-100 text-green-800'
            }`}>
              {task.priority.toUpperCase()} PRIORITY
            </span>
          </div>
        </div>
        <div className="flex space-x-2">
          {task.status === 'pending' && (
            <>
              <button
                onClick={handleComplete}
                className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                Mark Complete
              </button>
              <button
                onClick={handleSkip}
                className="btn-secondary"
              >
                Skip
              </button>
            </>
          )}
          <button
            onClick={handleReschedule}
            className="btn-secondary"
          >
            Reschedule
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Task Details */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Task Details</h2>
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-gray-500">Scheduled For</label>
              <p className="text-gray-900">
                {new Date(task.scheduled_for).toLocaleString()}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Follow-up Type</label>
              <p className="text-gray-900">{task.followup_type}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Priority</label>
              <p className="text-gray-900 capitalize">{task.priority}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Created</label>
              <p className="text-gray-900">
                {new Date(task.created_at).toLocaleString()}
              </p>
            </div>
            {task.notes && (
              <div>
                <label className="text-sm font-medium text-gray-500">Notes</label>
                <p className="text-gray-900">{task.notes}</p>
              </div>
            )}
          </div>
        </div>

        {/* Client Information */}
        {client && (
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Client Information</h2>
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-gray-500">Name</label>
                <p className="text-gray-900">{client.name}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Email</label>
                <p className="text-gray-900">{client.email}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Property</label>
                <p className="text-gray-900">{client.property_address}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Stage</label>
                <p className="text-gray-900 capitalize">{client.stage.replace('_', ' ')}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Email History */}
      {taskEmails.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Email History</h2>
          <div className="space-y-4">
            {taskEmails.map((email) => (
              <div key={email.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-medium text-gray-900">{email.subject}</h3>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    email.status === 'sent' ? 'bg-green-100 text-green-800' :
                    email.status === 'failed' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {email.status.toUpperCase()}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-2">
                  Sent: {email.sent_at ? new Date(email.sent_at).toLocaleString() : 'Not sent'}
                </p>
                <button
                  onClick={() => setShowEmailModal(true)}
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  View Email Content
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {isEditing && (
        <Modal
          title="Edit Task"
          onClose={() => setIsEditing(false)}
        >
          <TaskForm
            task={task}
            onSave={() => setIsEditing(false)}
            onCancel={() => setIsEditing(false)}
          />
        </Modal>
      )}

      {/* Email Preview Modal */}
      {showEmailModal && (
        <Modal
          title="Email Preview"
          onClose={() => setShowEmailModal(false)}
        >
          <EmailPreview
            task={task}
            client={client}
            onClose={() => setShowEmailModal(false)}
          />
        </Modal>
      )}
    </div>
  )
}
