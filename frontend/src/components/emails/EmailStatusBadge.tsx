import { Badge } from '@/components/ui/badge';
import { EmailStatus } from '@/lib/types/email.types';
import { EMAIL_STATUS_LABELS, EMAIL_STATUS_COLORS } from '@/lib/constants/email.constants';
import { cn } from '@/lib/utils/cn';

interface EmailStatusBadgeProps {
  status: EmailStatus;
}

export function EmailStatusBadge({ status }: EmailStatusBadgeProps) {
  return (
    <Badge 
      className={cn(
        EMAIL_STATUS_COLORS[status],
        'border-transparent font-medium'
      )}
    >
      {EMAIL_STATUS_LABELS[status]}
    </Badge>
  );
}

