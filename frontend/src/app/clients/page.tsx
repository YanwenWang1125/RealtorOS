/**
 * Clients list page for RealtorOS.
 * 
 * This component displays a list of all clients with filtering,
 * search, and pagination capabilities.
 */

'use client'

import { useState, useEffect } from 'react'
import ClientCard from '@/components/ClientCard'
import { useClients } from '@/hooks/useClients'
import Link from 'next/link'

export default function ClientsPage() {
  const { clients, loading, error } = useClients()
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStage, setFilterStage] = useState('all')

  const filteredClients = clients?.filter(client => {
    const matchesSearch = client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         client.email.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStage = filterStage === 'all' || client.stage === filterStage
    return matchesSearch && matchesStage
  }) || []

  if (loading) return <div>Loading clients...</div>
  if (error) return <div>Error loading clients: {error.message}</div>

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Clients</h1>
          <p className="mt-2 text-gray-600">
            Manage your real estate clients and their follow-ups
          </p>
        </div>
        <Link
          href="/clients/new"
          className="btn-primary"
        >
          Add New Client
        </Link>
      </div>

      {/* Search and Filter Controls */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
              Search Clients
            </label>
            <input
              id="search"
              type="text"
              placeholder="Search by name or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field"
            />
          </div>
          <div>
            <label htmlFor="stage" className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Stage
            </label>
            <select
              id="stage"
              value={filterStage}
              onChange={(e) => setFilterStage(e.target.value)}
              className="input-field"
            >
              <option value="all">All Stages</option>
              <option value="lead">Lead</option>
              <option value="negotiating">Negotiating</option>
              <option value="under_contract">Under Contract</option>
              <option value="closed">Closed</option>
              <option value="lost">Lost</option>
            </select>
          </div>
        </div>
      </div>

      {/* Clients Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredClients.map((client) => (
          <ClientCard key={client.id} client={client} />
        ))}
      </div>

      {filteredClients.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No clients found</p>
          <p className="text-gray-400 mt-2">
            {searchTerm || filterStage !== 'all' 
              ? 'Try adjusting your search or filter criteria'
              : 'Get started by adding your first client'
            }
          </p>
        </div>
      )}
    </div>
  )
}
