/**
 * Client detail page for RealtorOS.
 * 
 * This component displays detailed information about a specific client
 * including their property details, notes, and associated tasks.
 */

'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useClients } from '@/hooks/useClients'
import { useTasks } from '@/hooks/useTasks'
import ClientForm from '@/components/ClientForm'
import TaskCard from '@/components/TaskCard'
import Modal from '@/components/Modal'

export default function ClientDetailPage() {
  const params = useParams()
  const router = useRouter()
  const clientId = params.id as string
  
  const { clients, loading: clientsLoading, error: clientsError } = useClients()
  const { tasks, loading: tasksLoading } = useTasks()
  
  const [isEditing, setIsEditing] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  
  const client = clients?.find(c => c.id === clientId)
  const clientTasks = tasks?.filter(t => t.client_id === clientId) || []

  if (clientsLoading) return <div>Loading client...</div>
  if (clientsError) return <div>Error loading client: {clientsError.message}</div>
  if (!client) return <div>Client not found</div>

  const handleDelete = async () => {
    // TODO: Implement delete functionality
    console.log('Delete client:', clientId)
    setShowDeleteModal(false)
    router.push('/clients')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{client.name}</h1>
          <p className="mt-2 text-gray-600">{client.email}</p>
          <div className="mt-2 flex items-center space-x-4">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              client.stage === 'lead' ? 'bg-blue-100 text-blue-800' :
              client.stage === 'negotiating' ? 'bg-yellow-100 text-yellow-800' :
              client.stage === 'under_contract' ? 'bg-green-100 text-green-800' :
              client.stage === 'closed' ? 'bg-gray-100 text-gray-800' :
              'bg-red-100 text-red-800'
            }`}>
              {client.stage.replace('_', ' ').toUpperCase()}
            </span>
            {client.phone && (
              <span className="text-gray-600">{client.phone}</span>
            )}
          </div>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setIsEditing(true)}
            className="btn-secondary"
          >
            Edit Client
          </button>
          <button
            onClick={() => setShowDeleteModal(true)}
            className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            Delete
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Client Details */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Property Details</h2>
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-gray-500">Address</label>
              <p className="text-gray-900">{client.property_address}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Property Type</label>
              <p className="text-gray-900 capitalize">{client.property_type}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Last Contacted</label>
              <p className="text-gray-900">
                {client.last_contacted 
                  ? new Date(client.last_contacted).toLocaleDateString()
                  : 'Never'
                }
              </p>
            </div>
            {client.notes && (
              <div>
                <label className="text-sm font-medium text-gray-500">Notes</label>
                <p className="text-gray-900">{client.notes}</p>
              </div>
            )}
          </div>
        </div>

        {/* Client Tasks */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Follow-up Tasks</h2>
          <div className="space-y-3">
            {tasksLoading ? (
              <p>Loading tasks...</p>
            ) : clientTasks.length > 0 ? (
              clientTasks.map((task) => (
                <TaskCard key={task.id} task={task} />
              ))
            ) : (
              <p className="text-gray-500">No tasks found for this client</p>
            )}
          </div>
        </div>
      </div>

      {/* Edit Modal */}
      {isEditing && (
        <Modal
          title="Edit Client"
          onClose={() => setIsEditing(false)}
        >
          <ClientForm
            client={client}
            onSave={() => setIsEditing(false)}
            onCancel={() => setIsEditing(false)}
          />
        </Modal>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <Modal
          title="Delete Client"
          onClose={() => setShowDeleteModal(false)}
        >
          <div className="space-y-4">
            <p className="text-gray-600">
              Are you sure you want to delete this client? This action cannot be undone.
            </p>
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                Delete Client
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}
