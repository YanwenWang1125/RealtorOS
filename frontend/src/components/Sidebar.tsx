/**
 * Sidebar component for RealtorOS.
 * 
 * This component provides the main navigation sidebar
 * with quick access to all major sections.
 */

'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function Sidebar() {
  const pathname = usePathname()

  const isActive = (path: string) => {
    return pathname.startsWith(path)
  }

  const navigation = [
    { name: 'Dashboard', href: '/', icon: '📊' },
    { name: 'Clients', href: '/clients', icon: '👥' },
    { name: 'Tasks', href: '/tasks', icon: '✅' },
    { name: 'Emails', href: '/emails', icon: '📧' },
  ]

  return (
    <aside className="w-64 bg-white shadow-sm border-r border-gray-200 min-h-screen">
      <div className="p-6">
        <nav className="space-y-2">
          {navigation.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive(item.href)
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              <span>{item.name}</span>
            </Link>
          ))}
        </nav>

        {/* Quick Stats */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Quick Stats
          </h3>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Active Clients</span>
              <span className="font-medium text-gray-900">12</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Pending Tasks</span>
              <span className="font-medium text-gray-900">8</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Emails Sent</span>
              <span className="font-medium text-gray-900">156</span>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Recent Activity
          </h3>
          <div className="space-y-2">
            <div className="text-sm text-gray-600">
              <p>New client added</p>
              <p className="text-xs text-gray-400">2 hours ago</p>
            </div>
            <div className="text-sm text-gray-600">
              <p>Follow-up email sent</p>
              <p className="text-xs text-gray-400">4 hours ago</p>
            </div>
            <div className="text-sm text-gray-600">
              <p>Task completed</p>
              <p className="text-xs text-gray-400">1 day ago</p>
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}
