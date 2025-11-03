'use client';

import { Email } from '@/lib/types/email.types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { formatDateTime } from '@/lib/utils/format';

interface EmailWebhookLogProps {
  email: Email;
}

export function EmailWebhookLog({ email }: EmailWebhookLogProps) {
  // Type guard for webhook_events
  const webhookEvents = Array.isArray(email.webhook_events) ? email.webhook_events : [];

  if (webhookEvents.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Webhook Events ({webhookEvents.length})</CardTitle>
      </CardHeader>
      <CardContent>
        <Accordion type="single" collapsible>
          {webhookEvents.map((event: any, index: number) => (
            <AccordionItem key={index} value={`event-${index}`}>
              <AccordionTrigger>
                <div className="flex justify-between w-full pr-4">
                  <span className="font-medium">{event.event || 'Unknown Event'}</span>
                  <span className="text-sm text-muted-foreground">
                    {event.timestamp ? formatDateTime(new Date(event.timestamp * 1000).toISOString()) : '-'}
                  </span>
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <pre className="bg-muted p-4 rounded-md text-xs overflow-x-auto">
                  {JSON.stringify(event, null, 2)}
                </pre>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </CardContent>
    </Card>
  );
}

