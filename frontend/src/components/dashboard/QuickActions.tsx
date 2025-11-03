'use client';

import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { UserPlus, Mail, AlertCircle } from 'lucide-react';

export function QuickActions() {
  const router = useRouter();

  const actions = [
    {
      label: 'Create New Client',
      description: 'Add a new client to your CRM',
      icon: UserPlus,
      onClick: () => router.push('/clients/new'),
      color: 'bg-blue-100 text-blue-600 hover:bg-blue-200'
    },
    {
      label: 'Send Email',
      description: 'Compose and send an email',
      icon: Mail,
      onClick: () => router.push('/emails'),
      color: 'bg-purple-100 text-purple-600 hover:bg-purple-200'
    },
    {
      label: 'View Overdue Tasks',
      description: 'Check tasks that need attention',
      icon: AlertCircle,
      onClick: () => router.push('/tasks?filter=overdue'),
      color: 'bg-red-100 text-red-600 hover:bg-red-200'
    }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {actions.map((action, index) => {
          const Icon = action.icon;
          return (
            <Button
              key={index}
              variant="outline"
              className="w-full justify-start h-auto py-3"
              onClick={action.onClick}
            >
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center mr-3 ${action.color}`}>
                <Icon className="h-5 w-5" />
              </div>
              <div className="text-left">
                <p className="font-medium text-sm">{action.label}</p>
                <p className="text-xs text-muted-foreground">{action.description}</p>
              </div>
            </Button>
          );
        })}
      </CardContent>
    </Card>
  );
}

