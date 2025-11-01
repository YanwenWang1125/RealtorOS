import { Mail, Eye, MousePointer } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/badge';
import { EmptyState } from '@/components/ui/EmptyState';
import { Email } from '@/lib/types/email.types';
import { EMAIL_STATUS_LABELS, EMAIL_STATUS_COLORS } from '@/lib/constants/email.constants';
import { formatRelativeTime } from '@/lib/utils/format';

export function ClientEmailHistory({ emails }: { emails: Email[] }) {
  if (emails.length === 0) {
    return (
      <EmptyState
        icon={Mail}
        title="No emails yet"
        description="Email history will appear here once follow-up emails are sent."
      />
    );
  }

  return (
    <div className="space-y-2">
      {emails.map(email => (
        <Card key={email.id} className="hover:bg-accent cursor-pointer transition-colors">
          <CardContent className="pt-6">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h3 className="font-semibold">{email.subject}</h3>
                <p className="text-sm text-muted-foreground">
                  {formatRelativeTime(email.sent_at || email.created_at)}
                </p>
              </div>
              <div className="flex gap-2 items-center">
                <Badge className={EMAIL_STATUS_COLORS[email.status]}>
                  {EMAIL_STATUS_LABELS[email.status]}
                </Badge>
                {email.opened_at && <Eye className="h-4 w-4 text-green-500" title="Opened" />}
                {email.clicked_at && <MousePointer className="h-4 w-4 text-purple-500" title="Clicked" />}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

