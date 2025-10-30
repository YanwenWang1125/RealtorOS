/**
 * Create new client page for RealtorOS.
 * 
 * This component provides a form for creating new clients
 * with validation and error handling.
 */

'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import ClientForm from '@/components/ClientForm'

export default function NewClientPage() {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSave = async (clientData: any) => {
    setIsSubmitting(true)
    try {
      // TODO: Implement API call to create client
      console.log('Creating client:', clientData)
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Redirect to clients list
      router.push('/clients')
    } catch (error) {
      console.error('Error creating client:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCancel = () => {
    router.push('/clients')
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Add New Client</h1>
        <p className="mt-2 text-gray-600">
          Enter the client's information to get started with automated follow-ups
        </p>
      </div>

      <div className="card">
        <ClientForm
          onSave={handleSave}
          onCancel={handleCancel}
          isSubmitting={isSubmitting}
        />
      </div>
    </div>
  )
}
