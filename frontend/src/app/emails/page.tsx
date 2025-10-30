/**
 * Email history page for RealtorOS.
 * 
 * This component displays all sent emails with filtering,
 * search, and analytics capabilities.
 */

'use client'

import { useState } from 'react'
import { useEmails } from '@/hooks/useEmails'
import { useClients } from '@/hooks/useClients'
import EmailPreview from '@/components/EmailPreview'
import Modal from '@/components/Modal'

export default function EmailsPage() {
  const { emails, loading, error } = useEmails()
  const { clients } = useClients()
  
  const [selectedEmail, setSelectedEmail] = useState(null)
  const [filterStatus, setFilterStatus] = useState('all')
  const [filterClient, setFilterClient] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')

  const filteredEmails = emails?.filter(email => {
    const statusMatch = filterStatus === 'all' || email.status === filterStatus
    const clientMatch = filterClient === 'all' || email.client_id === filterClient
    const searchMatch = searchTerm === '' || 
      email.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
      email.to_email.toLowerCase().includes(searchTerm.toLowerCase())
    return statusMatch && clientMatch && searchMatch
  }) || []

  if (loading) return <div>Loading emails...</div>
  if (error) return <div>Error loading emails: {error.message}</div>

  const getClientName = (clientId: string) => {
    const client = clients?.find(c => c.id === clientId)
    return client?.name || 'Unknown Client'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Email History</h1>
        <p className="mt-2 text-gray-600">
          View and manage all sent emails and their performance
        </p>
      </div>

      {/* Filter Controls */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
              Search Emails
            </label>
            <input
              id="search"
              type="text"
              placeholder="Search by subject or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field"
            />
          </div>
          
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
              <option value="all">All Statuses</option>
              <option value="sent">Sent</option>
              <option value="delivered">Delivered</option>
              <option value="opened">Opened</option>
              <option value="clicked">Clicked</option>
              <option value="failed">Failed</option>
              <option value="bounced">Bounced</option>
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
        </div>
      </div>

      {/* Email Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500">Total Emails</h3>
          <p className="text-2xl font-bold text-gray-900">{emails?.length || 0}</p>
        </div>
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500">Sent Today</h3>
          <p className="text-2xl font-bold text-gray-900">
            {emails?.filter(e => {
              const today = new Date()
              const emailDate = new Date(e.created_at)
              return emailDate.toDateString() === today.toDateString()
            }).length || 0}
          </p>
        </div>
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500">Open Rate</h3>
          <p className="text-2xl font-bold text-gray-900">
            {emails?.length ? 
              Math.round((emails.filter(e => e.opened_at).length / emails.length) * 100) : 0}%
          </p>
        </div>
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500">Click Rate</h3>
          <p className="text-2xl font-bold text-gray-900">
            {emails?.length ? 
              Math.round((emails.filter(e => e.clicked_at).length / emails.length) * 100) : 0}%
          </p>
        </div>
      </div>

      {/* Emails List */}
      <div className="space-y-4">
        {filteredEmails.length > 0 ? (
          filteredEmails.map((email) => (
            <div key={email.id} className="card hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-medium text-gray-900">{email.subject}</h3>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
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
                  <p className="text-sm text-gray-600 mb-2">
                    To: {email.to_email} • Client: {getClientName(email.client_id)}
                  </p>
                  <p className="text-sm text-gray-500">
                    Sent: {email.sent_at ? new Date(email.sent_at).toLocaleString() : 'Not sent'}
                    {email.opened_at && (
                      <span> • Opened: {new Date(email.opened_at).toLocaleString()}</span>
                    )}
                    {email.clicked_at && (
                      <span> • Clicked: {new Date(email.clicked_at).toLocaleString()}</span>
                    )}
                  </p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setSelectedEmail(email)}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    View
                  </button>
                  {email.status === 'failed' && (
                    <button className="text-red-600 hover:text-red-800 text-sm font-medium">
                      Retry
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No emails found</p>
            <p className="text-gray-400 mt-2">
              {searchTerm || filterStatus !== 'all' || filterClient !== 'all'
                ? 'Try adjusting your search or filter criteria'
                : 'Emails will appear here once you start sending follow-ups'
              }
            </p>
          </div>
        )}
      </div>

      {/* Email Preview Modal */}
      {selectedEmail && (
        <Modal
          title="Email Preview"
          onClose={() => setSelectedEmail(null)}
        >
          <EmailPreview
            email={selectedEmail}
            onClose={() => setSelectedEmail(null)}
          />
        </Modal>
      )}
    </div>
  )
}
