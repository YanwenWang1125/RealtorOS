'use client';

import { useRouter } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/badge';
import { Client } from '@/lib/types/client.types';
import { CLIENT_STAGE_COLORS, CLIENT_STAGE_LABELS } from '@/lib/constants/client.constants';
import { normalizeClientStage } from '@/lib/utils/formatters';

interface ClientCardProps {
  client: Client;
}

export function ClientCard({ client }: ClientCardProps) {
  const router = useRouter();

  return (
    <Card
      className="hover:bg-secondary/10 hover:text-secondary hover:shadow-md transition-all cursor-pointer"
      onClick={() => router.push(`/clients/${client.id}`)}
    >
      <CardContent className="pt-6">
        <div className="flex justify-between items-start mb-2">
          <div className="flex-1">
            <h3 className="font-semibold text-lg">{client.name}</h3>
            <p className="text-sm text-muted-foreground">{client.email}</p>
          </div>
          {(() => {
            const normalizedStage = normalizeClientStage(client.stage);
            const stageColor = CLIENT_STAGE_COLORS[normalizedStage] ?? 'bg-gray-100 text-gray-700';
            const stageLabel = CLIENT_STAGE_LABELS[normalizedStage] ?? client.stage;
            return (
              <span 
                className={`inline-flex items-center rounded-full px-2 py-1 text-sm font-medium ${stageColor}`}
              >
                {stageLabel}
              </span>
            );
          })()}
        </div>
        <div className="mt-3">
          <p className="text-sm text-muted-foreground">
            <span className="font-medium">Property:</span> {client.property_address}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
