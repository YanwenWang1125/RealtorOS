/**
 * Dashboard stats component for RealtorOS.
 * 
 * This component displays key performance indicators
 * and statistics for the dashboard.
 */

'use client'

import { useClients } from '@/lib/hooks/queries/useClients'
import { useTasks } from '@/lib/hooks/queries/useTasks'
import { useEmails } from '@/lib/hooks/queries/useEmails'

export default function DashboardStats() {
  const { data: clients = [], isLoading: clientsLoading } = useClients({ limit: 1000 })
  const { data: tasks = [], isLoading: tasksLoading } = useTasks({ limit: 1000 })
  const { data: emails = [], isLoading: emailsLoading } = useEmails({ limit: 1000 })

  if (clientsLoading || tasksLoading || emailsLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="card animate-pulse">
            <div className="h-4 bg-muted rounded w-1/2 mb-2"></div>
            <div className="h-8 bg-muted rounded w-1/3"></div>
          </div>
        ))}
      </div>
    )
  }

  const totalClients = clients.length || 0
  const activeClients = clients.filter(c => c.stage !== 'closed' && c.stage !== 'lost').length || 0
  const pendingTasks = tasks.filter(t => t.status === 'pending').length || 0
  const completedTasks = tasks.filter(t => t.status === 'completed').length || 0
  const totalEmails = emails.length || 0
  const emailsToday = emails.filter(e => {
    const today = new Date()
    const emailDate = new Date(e.created_at)
    return emailDate.toDateString() === today.toDateString()
  }).length || 0

  const openRate = totalEmails > 0 ? 
    Math.round((emails.filter(e => e.opened_at).length || 0) / totalEmails * 100) : 0
  const clickRate = totalEmails > 0 ? 
    Math.round((emails.filter(e => e.clicked_at).length || 0) / totalEmails * 100) : 0

  const stats = [
    {
      name: 'Total Clients',
      value: totalClients,
      change: '+12%',
      changeType: 'positive' as const,
      icon: '👥'
    },
    {
      name: 'Active Clients',
      value: activeClients,
      change: '+8%',
      changeType: 'positive' as const,
      icon: '🎯'
    },
    {
      name: 'Pending Tasks',
      value: pendingTasks,
      change: '-5%',
      changeType: 'negative' as const,
      icon: '⏰'
    },
    {
      name: 'Completed Tasks',
      value: completedTasks,
      change: '+15%',
      changeType: 'positive' as const,
      icon: '✅'
    },
    {
      name: 'Emails Sent',
      value: totalEmails,
      change: '+23%',
      changeType: 'positive' as const,
      icon: '📧'
    },
    {
      name: 'Emails Today',
      value: emailsToday,
      change: '+3',
      changeType: 'positive' as const,
      icon: '📬'
    },
    {
      name: 'Open Rate',
      value: `${openRate}%`,
      change: '+2%',
      changeType: 'positive' as const,
      icon: '👁️'
    },
    {
      name: 'Click Rate',
      value: `${clickRate}%`,
      change: '+1%',
      changeType: 'positive' as const,
      icon: '🖱️'
    }
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-2xl">{stat.icon}</span>
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-muted-foreground">{stat.name}</p>
                <div className="flex items-baseline">
                  <p className="text-2xl font-semibold text-foreground">{stat.value}</p>
                  <p className={`ml-2 text-sm font-medium ${
                    stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {stat.change}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-foreground mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button className="w-full text-left px-4 py-3 text-sm text-foreground hover:bg-muted rounded-lg border border-border hover:border-primary transition-colors">
              <div className="flex items-center space-x-3">
                <span className="text-lg">👤</span>
                <div>
                  <p className="font-medium">Add New Client</p>
                  <p className="text-muted-foreground">Create a new client profile</p>
                </div>
              </div>
            </button>
            <button className="w-full text-left px-4 py-3 text-sm text-foreground hover:bg-muted rounded-lg border border-border hover:border-primary transition-colors">
              <div className="flex items-center space-x-3">
                <span className="text-lg">✅</span>
                <div>
                  <p className="font-medium">Create Task</p>
                  <p className="text-muted-foreground">Schedule a new follow-up</p>
                </div>
              </div>
            </button>
            <button className="w-full text-left px-4 py-3 text-sm text-foreground hover:bg-muted rounded-lg border border-border hover:border-primary transition-colors">
              <div className="flex items-center space-x-3">
                <span className="text-lg">📧</span>
                <div>
                  <p className="font-medium">Send Email</p>
                  <p className="text-muted-foreground">Send a manual email</p>
                </div>
              </div>
            </button>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-foreground mb-4">Recent Activity</h3>
          <div className="space-y-3">
            <div className="flex items-center space-x-3 text-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <div>
                <p className="text-foreground">New client added: John Smith</p>
                <p className="text-muted-foreground">2 hours ago</p>
              </div>
            </div>
            <div className="flex items-center space-x-3 text-sm">
              <div className="w-2 h-2 bg-primary rounded-full"></div>
              <div>
                <p className="text-foreground">Follow-up email sent</p>
                <p className="text-muted-foreground">4 hours ago</p>
              </div>
            </div>
            <div className="flex items-center space-x-3 text-sm">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <div>
                <p className="text-foreground">Task completed: Week 1 follow-up</p>
                <p className="text-muted-foreground">1 day ago</p>
              </div>
            </div>
            <div className="flex items-center space-x-3 text-sm">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <div>
                <p className="text-foreground">Email opened by client</p>
                <p className="text-muted-foreground">2 days ago</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
