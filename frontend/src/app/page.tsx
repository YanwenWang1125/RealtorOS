/**
 * Dashboard home page for RealtorOS.
 * 
 * This component displays the main dashboard with statistics,
 * recent activity, and quick actions for real estate agents.
 */

import DashboardStats from '@/components/DashboardStats'
import { Suspense } from 'react'

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome to your RealtorOS dashboard
        </p>
      </div>
      
      <Suspense fallback={<div>Loading dashboard stats...</div>}>
        <DashboardStats />
      </Suspense>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
          <p className="text-gray-500">Recent activity will be displayed here</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="space-y-2">
            <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded">
              Add New Client
            </button>
            <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded">
              View Pending Tasks
            </button>
            <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded">
              Check Email History
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
