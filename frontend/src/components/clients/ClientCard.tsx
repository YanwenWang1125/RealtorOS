'use client';

import { useRouter } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/badge';
import { Client } from '@/lib/types/client.types';
import { CLIENT_STAGE_COLORS, CLIENT_STAGE_LABELS } from '@/lib/constants/client.constants';

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
          <Badge className={CLIENT_STAGE_COLORS[client.stage]}>
            {CLIENT_STAGE_LABELS[client.stage]}
          </Badge>
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
