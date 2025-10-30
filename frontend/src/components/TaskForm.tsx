/**
 * Task form component for RealtorOS.
 * 
 * This component provides a form for creating and editing tasks
 * with validation and error handling.
 */

'use client'

import { useState, useEffect } from 'react'
import { Task } from '@/types/task'
import { useClients } from '@/hooks/useClients'

interface TaskFormProps {
  task?: Task
  clientId?: string
  onSave: () => void
  onCancel: () => void
  isSubmitting?: boolean
}

export default function TaskForm({ 
  task, 
  clientId, 
  onSave, 
  onCancel, 
  isSubmitting = false 
}: TaskFormProps) {
  const { clients } = useClients()
  
  const [formData, setFormData] = useState({
    client_id: clientId || task?.client_id || '',
    followup_type: task?.followup_type || 'Day 1',
    scheduled_for: task?.scheduled_for ? 
      new Date(task.scheduled_for).toISOString().slice(0, 16) : 
      new Date().toISOString().slice(0, 16),
    priority: task?.priority || 'medium',
    notes: task?.notes || ''
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  const followupTypes = [
    'Day 1',
    'Day 3', 
    'Week 1',
    'Week 2',
    'Month 1',
    'Custom'
  ]

  const priorities = [
    { value: 'high', label: 'High' },
    { value: 'medium', label: 'Medium' },
    { value: 'low', label: 'Low' }
  ]

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.client_id) {
      newErrors.client_id = 'Client is required'
    }
    if (!formData.followup_type) {
      newErrors.followup_type = 'Follow-up type is required'
    }
    if (!formData.scheduled_for) {
      newErrors.scheduled_for = 'Scheduled date is required'
    }
    if (!formData.priority) {
      newErrors.priority = 'Priority is required'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    try {
      // TODO: Implement API call to save task
      console.log('Saving task:', formData)
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      onSave()
    } catch (error) {
      console.error('Error saving task:', error)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="client_id" className="block text-sm font-medium text-gray-700 mb-2">
          Client *
        </label>
        <select
          id="client_id"
          name="client_id"
          value={formData.client_id}
          onChange={handleChange}
          disabled={!!clientId}
          className={`input-field ${errors.client_id ? 'border-red-500' : ''}`}
        >
          <option value="">Select a client</option>
          {clients?.map(client => (
            <option key={client.id} value={client.id}>
              {client.name} - {client.email}
            </option>
          ))}
        </select>
        {errors.client_id && (
          <p className="mt-1 text-sm text-red-600">{errors.client_id}</p>
        )}
      </div>

      <div>
        <label htmlFor="followup_type" className="block text-sm font-medium text-gray-700 mb-2">
          Follow-up Type *
        </label>
        <select
          id="followup_type"
          name="followup_type"
          value={formData.followup_type}
          onChange={handleChange}
          className={`input-field ${errors.followup_type ? 'border-red-500' : ''}`}
        >
          {followupTypes.map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
        {errors.followup_type && (
          <p className="mt-1 text-sm text-red-600">{errors.followup_type}</p>
        )}
      </div>

      <div>
        <label htmlFor="scheduled_for" className="block text-sm font-medium text-gray-700 mb-2">
          Scheduled For *
        </label>
        <input
          type="datetime-local"
          id="scheduled_for"
          name="scheduled_for"
          value={formData.scheduled_for}
          onChange={handleChange}
          className={`input-field ${errors.scheduled_for ? 'border-red-500' : ''}`}
        />
        {errors.scheduled_for && (
          <p className="mt-1 text-sm text-red-600">{errors.scheduled_for}</p>
        )}
      </div>

      <div>
        <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-2">
          Priority *
        </label>
        <select
          id="priority"
          name="priority"
          value={formData.priority}
          onChange={handleChange}
          className={`input-field ${errors.priority ? 'border-red-500' : ''}`}
        >
          {priorities.map(priority => (
            <option key={priority.value} value={priority.value}>
              {priority.label}
            </option>
          ))}
        </select>
        {errors.priority && (
          <p className="mt-1 text-sm text-red-600">{errors.priority}</p>
        )}
      </div>

      <div>
        <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
          Notes
        </label>
        <textarea
          id="notes"
          name="notes"
          rows={3}
          value={formData.notes}
          onChange={handleChange}
          placeholder="Optional notes about this task..."
          className="input-field"
        />
      </div>

      <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
        <button
          type="button"
          onClick={onCancel}
          className="btn-secondary"
          disabled={isSubmitting}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="btn-primary"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Saving...' : task ? 'Update Task' : 'Create Task'}
        </button>
      </div>
    </form>
  )
}
