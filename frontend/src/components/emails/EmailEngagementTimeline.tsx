import { Email } from '@/lib/types/email.types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { formatDateTime } from '@/lib/utils/format';
import { Check, Clock, Eye, MousePointer, Send } from 'lucide-react';
import { cn } from '@/lib/utils/cn';

interface EmailEngagementTimelineProps {
  email: Email;
}

export function EmailEngagementTimeline({ email }: EmailEngagementTimelineProps) {
  const steps = [
    {
      label: 'Sent',
      timestamp: email.sent_at,
      icon: Send,
      completed: !!email.sent_at
    },
    {
      label: 'Delivered',
      timestamp: email.status === 'delivered' || email.status === 'opened' || email.status === 'clicked' ? email.sent_at : null,
      icon: Check,
      completed: ['delivered', 'opened', 'clicked'].includes(email.status)
    },
    {
      label: 'Opened',
      timestamp: email.opened_at,
      icon: Eye,
      completed: !!email.opened_at
    },
    {
      label: 'Clicked',
      timestamp: email.clicked_at,
      icon: MousePointer,
      completed: !!email.clicked_at
    }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Engagement Timeline</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={step.label} className="flex-1">
                <div className="flex items-center">
                  {/* Step Circle */}
                  <div
                    className={cn(
                      'w-10 h-10 rounded-full flex items-center justify-center',
                      step.completed
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-200 text-gray-400'
                    )}
                  >
                    <Icon className="h-5 w-5" />
                  </div>

                  {/* Connecting Line */}
                  {index < steps.length - 1 && (
                    <div
                      className={cn(
                        'flex-1 h-1 mx-2',
                        step.completed && steps[index + 1].completed
                          ? 'bg-green-500'
                          : 'bg-gray-200'
                      )}
                    />
                  )}
                </div>

                {/* Label and Timestamp */}
                <div className="mt-2 text-center">
                  <p className="text-sm font-medium">{step.label}</p>
                  {step.timestamp ? (
                    <p className="text-xs text-muted-foreground">
                      {formatDateTime(step.timestamp)}
                    </p>
                  ) : (
                    <p className="text-xs text-muted-foreground">-</p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

