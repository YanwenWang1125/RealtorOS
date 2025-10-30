/**
 * Email preview component for RealtorOS.
 * 
 * This component displays email content in a preview format
 * with options to send or edit the email.
 */

'use client'

import { useState } from 'react'
import { Task } from '@/types/task'
import { Client } from '@/types/client'
import { Email } from '@/types/email'

interface EmailPreviewProps {
  task?: Task
  client?: Client
  email?: Email
  onClose: () => void
}

export default function EmailPreview({ task, client, email, onClose }: EmailPreviewProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [isSending, setIsSending] = useState(false)
  const [emailContent, setEmailContent] = useState({
    subject: email?.subject || '',
    body: email?.body || ''
  })

  const handleGenerateEmail = async () => {
    if (!task || !client) return

    setIsGenerating(true)
    try {
      // TODO: Implement API call to generate email
      console.log('Generating email for task:', task.id, 'client:', client.id)
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Mock generated content
      setEmailContent({
        subject: `Follow-up: ${client.property_address}`,
        body: `Hi ${client.name},\n\nI hope you're doing well. I wanted to follow up regarding your interest in the property at ${client.property_address}.\n\nI have some updates that might interest you and would love to schedule a time to discuss them.\n\nPlease let me know when would be a good time to connect.\n\nBest regards,\nYour Realtor`
      })
    } catch (error) {
      console.error('Error generating email:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSendEmail = async () => {
    if (!emailContent.subject || !emailContent.body) return

    setIsSending(true)
    try {
      // TODO: Implement API call to send email
      console.log('Sending email:', emailContent)
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      onClose()
    } catch (error) {
      console.error('Error sending email:', error)
    } finally {
      setIsSending(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Email Preview</h2>
          {client && (
            <p className="text-sm text-gray-600">
              To: {client.name} ({client.email})
            </p>
          )}
        </div>
        <div className="flex space-x-2">
          {!email && (
            <button
              onClick={handleGenerateEmail}
              disabled={isGenerating}
              className="btn-secondary"
            >
              {isGenerating ? 'Generating...' : 'Generate Email'}
            </button>
          )}
          <button
            onClick={handleSendEmail}
            disabled={!emailContent.subject || !emailContent.body || isSending}
            className="btn-primary"
          >
            {isSending ? 'Sending...' : 'Send Email'}
          </button>
        </div>
      </div>

      {/* Email Content */}
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-700">Subject:</span>
            <span className="text-sm text-gray-900">{emailContent.subject || 'No subject'}</span>
          </div>
        </div>
        <div className="p-4">
          <div className="prose max-w-none">
            <pre className="whitespace-pre-wrap text-sm text-gray-900 font-sans">
              {emailContent.body || 'No content generated yet. Click "Generate Email" to create content.'}
            </pre>
          </div>
        </div>
      </div>

      {/* Email Metadata */}
      {email && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Email Details</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Status:</span>
              <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                email.status === 'sent' ? 'bg-green-100 text-green-800' :
                email.status === 'delivered' ? 'bg-blue-100 text-blue-800' :
                email.status === 'opened' ? 'bg-purple-100 text-purple-800' :
                email.status === 'clicked' ? 'bg-indigo-100 text-indigo-800' :
                email.status === 'failed' ? 'bg-red-100 text-red-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {email.status.toUpperCase()}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Sent:</span>
              <span className="ml-2 text-gray-900">
                {email.sent_at ? new Date(email.sent_at).toLocaleString() : 'Not sent'}
              </span>
            </div>
            {email.opened_at && (
              <div>
                <span className="text-gray-500">Opened:</span>
                <span className="ml-2 text-gray-900">
                  {new Date(email.opened_at).toLocaleString()}
                </span>
              </div>
            )}
            {email.clicked_at && (
              <div>
                <span className="text-gray-500">Clicked:</span>
                <span className="ml-2 text-gray-900">
                  {new Date(email.clicked_at).toLocaleString()}
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
        <button
          onClick={onClose}
          className="btn-secondary"
        >
          Close
        </button>
        {!email && emailContent.subject && emailContent.body && (
          <button
            onClick={handleSendEmail}
            disabled={isSending}
            className="btn-primary"
          >
            {isSending ? 'Sending...' : 'Send Email'}
          </button>
        )}
      </div>
    </div>
  )
}
