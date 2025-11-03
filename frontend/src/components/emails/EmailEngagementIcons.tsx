import { Email } from '@/lib/types/email.types';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Eye, MousePointer } from 'lucide-react';
import { formatRelativeTime } from '@/lib/utils/format';

interface EmailEngagementIconsProps {
  email: Email;
}

export function EmailEngagementIcons({ email }: EmailEngagementIconsProps) {
  return (
    <TooltipProvider>
      <div className="flex gap-2">
        {email.opened_at && (
          <Tooltip>
            <TooltipTrigger asChild>
              <div className="flex items-center">
                <Eye className="h-4 w-4 text-green-600" />
              </div>
            </TooltipTrigger>
            <TooltipContent>
              <p>Opened {formatRelativeTime(email.opened_at)}</p>
            </TooltipContent>
          </Tooltip>
        )}

        {email.clicked_at && (
          <Tooltip>
            <TooltipTrigger asChild>
              <div className="flex items-center">
                <MousePointer className="h-4 w-4 text-purple-600" />
              </div>
            </TooltipTrigger>
            <TooltipContent>
              <p>Clicked {formatRelativeTime(email.clicked_at)}</p>
            </TooltipContent>
          </Tooltip>
        )}

        {!email.opened_at && !email.clicked_at && email.status === 'sent' && (
          <span className="text-xs text-muted-foreground">No engagement yet</span>
        )}
      </div>
    </TooltipProvider>
  );
}

