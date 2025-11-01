/**
 * Client card component for RealtorOS.
 * 
 * This component displays client information in a card format
 * with quick actions and status indicators.
 */

'use client'

import Link from 'next/link'
import { Client } from '@/lib/types/client'

interface ClientCardProps {
  client: Client
}

export default function ClientCard({ client }: ClientCardProps) {
  const getStageColor = (stage: string) => {
    switch (stage) {
      case 'lead':
        return 'bg-blue-100 text-blue-800'
      case 'negotiating':
        return 'bg-yellow-100 text-yellow-800'
      case 'under_contract':
        return 'bg-green-100 text-green-800'
      case 'closed':
        return 'bg-gray-100 text-gray-800'
      case 'lost':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{client.name}</h3>
          <p className="text-sm text-gray-600">{client.email}</p>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStageColor(client.stage)}`}>
          {client.stage.replace('_', ' ').toUpperCase()}
        </span>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex items-center text-sm text-gray-600">
          <span className="w-4 h-4 mr-2">🏠</span>
          <span className="truncate">{client.property_address}</span>
        </div>
        <div className="flex items-center text-sm text-gray-600">
          <span className="w-4 h-4 mr-2">📞</span>
          <span>{client.phone || 'No phone'}</span>
        </div>
        <div className="flex items-center text-sm text-gray-600">
          <span className="w-4 h-4 mr-2">📅</span>
          <span>
            Last contact: {client.last_contacted 
              ? new Date(client.last_contacted).toLocaleDateString()
              : 'Never'
            }
          </span>
        </div>
      </div>

      {client.notes && (
        <div className="mb-4">
          <p className="text-sm text-gray-600 line-clamp-2">{client.notes}</p>
        </div>
      )}

      <div className="flex justify-between items-center pt-4 border-t border-gray-200">
        <Link
          href={`/clients/${client.id}`}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          View Details
        </Link>
        <div className="flex space-x-2">
          <Link
            href={`/clients/${client.id}/tasks`}
            className="text-gray-600 hover:text-gray-800 text-sm"
          >
            Tasks
          </Link>
          <Link
            href={`/clients/${client.id}`}
            className="text-gray-600 hover:text-gray-800 text-sm"
          >
            Edit
          </Link>
        </div>
      </div>
    </div>
  )
}
