/**
 * Client form component for RealtorOS.
 * 
 * This component provides a form for creating and editing clients
 * with validation and error handling.
 */

'use client'

import { useState } from 'react'
import type { Client } from '@/lib/types'
import { CLIENT_STAGES, CLIENT_STAGE_LABELS } from '@/lib/constants/client.constants'

interface ClientFormProps {
  client?: Client
  onSave: (clientData: any) => void
  onCancel: () => void
  isSubmitting?: boolean
}

export default function ClientForm({ 
  client, 
  onSave, 
  onCancel, 
  isSubmitting = false 
}: ClientFormProps) {
  // Format current datetime for datetime-local input (YYYY-MM-DDTHH:mm)
  const getCurrentDateTimeLocal = () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  };

  const [formData, setFormData] = useState({
    name: client?.name || '',
    email: client?.email || '',
    phone: client?.phone || '',
    property_address: client?.property_address || '',
    property_type: client?.property_type || 'residential',
    stage: client?.stage || 'lead',
    notes: client?.notes || '',
    last_contacted: client?.last_contacted 
      ? new Date(client.last_contacted).toISOString().slice(0, 16)
      : getCurrentDateTimeLocal(),
    email_unsubscribed: client?.email_unsubscribed || false,
    create_tasks: false // Only for new clients
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  const propertyTypes = [
    { value: 'residential', label: 'Residential' },
    { value: 'commercial', label: 'Commercial' },
    { value: 'land', label: 'Land' },
    { value: 'other', label: 'Other' }
  ]

  const stages = CLIENT_STAGES.map(stage => ({
    value: stage,
    label: CLIENT_STAGE_LABELS[stage]
  }))

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required'
    }
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid'
    }
    if (!formData.property_address.trim()) {
      newErrors.property_address = 'Property address is required'
    }
    if (!formData.property_type) {
      newErrors.property_type = 'Property type is required'
    }
    if (!formData.stage) {
      newErrors.stage = 'Stage is required'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    // Prepare data to save - exclude create_tasks for edit mode
    const dataToSave = client 
      ? { ...formData, create_tasks: undefined }
      : formData
    
    // Remove undefined values
    const cleanedData = Object.fromEntries(
      Object.entries(dataToSave).filter(([_, value]) => value !== undefined)
    )

    onSave(cleanedData)
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
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-foreground mb-2">
            Full Name *
          </label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            className={`input-field ${errors.name ? 'border-red-500' : ''}`}
            placeholder="Enter client's full name"
          />
          {errors.name && (
            <p className="mt-1 text-sm text-red-600">{errors.name}</p>
          )}
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-medium text-foreground mb-2">
            Email Address *
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className={`input-field ${errors.email ? 'border-red-500' : ''}`}
            placeholder="client@example.com"
          />
          {errors.email && (
            <p className="mt-1 text-sm text-red-600">{errors.email}</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="phone" className="block text-sm font-medium text-foreground mb-2">
            Phone Number
          </label>
          <input
            type="tel"
            id="phone"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            className="input-field"
            placeholder="+1 (555) 123-4567"
          />
        </div>

        <div>
          <label htmlFor="property_type" className="block text-sm font-medium text-foreground mb-2">
            Property Type *
          </label>
          <select
            id="property_type"
            name="property_type"
            value={formData.property_type}
            onChange={handleChange}
            className={`input-field ${errors.property_type ? 'border-red-500' : ''}`}
          >
            {propertyTypes.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
          {errors.property_type && (
            <p className="mt-1 text-sm text-red-600">{errors.property_type}</p>
          )}
        </div>
      </div>

      <div>
        <label htmlFor="property_address" className="block text-sm font-medium text-foreground mb-2">
          Property Address *
        </label>
        <input
          type="text"
          id="property_address"
          name="property_address"
          value={formData.property_address}
          onChange={handleChange}
          className={`input-field ${errors.property_address ? 'border-red-500' : ''}`}
          placeholder="123 Main St, City, State 12345"
        />
        {errors.property_address && (
          <p className="mt-1 text-sm text-red-600">{errors.property_address}</p>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="stage" className="block text-sm font-medium text-foreground mb-2">
            Current Stage *
          </label>
          <select
            id="stage"
            name="stage"
            value={formData.stage}
            onChange={handleChange}
            className={`input-field ${errors.stage ? 'border-red-500' : ''}`}
          >
            {stages.map(stage => (
              <option key={stage.value} value={stage.value}>
                {stage.label}
              </option>
            ))}
          </select>
          {errors.stage && (
            <p className="mt-1 text-sm text-red-600">{errors.stage}</p>
          )}
        </div>

        <div>
          <label htmlFor="last_contacted" className="block text-sm font-medium text-foreground mb-2">
            Last Contacted
          </label>
          <input
            type="datetime-local"
            id="last_contacted"
            name="last_contacted"
            value={formData.last_contacted}
            onChange={handleChange}
            className="input-field"
          />
        </div>
      </div>

      <div>
        <label htmlFor="notes" className="block text-sm font-medium text-foreground mb-2">
          Notes
        </label>
        <textarea
          id="notes"
          name="notes"
          rows={4}
          value={formData.notes}
          onChange={handleChange}
          className="input-field"
          placeholder="Any additional notes about this client..."
        />
      </div>

      {client && (
        <div className="flex items-start space-x-3">
          <input
            type="checkbox"
            id="email_unsubscribed"
            name="email_unsubscribed"
            checked={formData.email_unsubscribed}
            onChange={(e) => setFormData(prev => ({ ...prev, email_unsubscribed: e.target.checked }))}
            className="mt-1 h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
          />
          <div className="flex-1">
            <label htmlFor="email_unsubscribed" className="text-sm font-medium text-foreground cursor-pointer">
              Email Unsubscribed
            </label>
            <p className="text-xs text-muted-foreground mt-1">
              Check this if the client has unsubscribed from email follow-ups. No emails will be sent to this client.
            </p>
          </div>
        </div>
      )}

      {!client && (
        <div className="flex items-start space-x-3">
          <input
            type="checkbox"
            id="create_tasks"
            name="create_tasks"
            checked={formData.create_tasks}
            onChange={(e) => setFormData(prev => ({ ...prev, create_tasks: e.target.checked }))}
            className="mt-1 h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
          />
          <div className="flex-1">
            <label htmlFor="create_tasks" className="text-sm font-medium text-foreground cursor-pointer">
              Create follow-up tasks
            </label>
            <p className="text-xs text-muted-foreground mt-1">
              Select this to create follow-up tasks for this client. You'll be able to choose which tasks to create after saving.
            </p>
          </div>
        </div>
      )}

      <div className="flex justify-end space-x-3 pt-6 border-t border-border">
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
          {isSubmitting ? 'Saving...' : client ? 'Update Client' : 'Create Client'}
        </button>
      </div>
    </form>
  )
}
