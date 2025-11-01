import { Mail, Phone } from 'lucide-react';
import { Client } from '@/lib/types/client.types';
import { formatRelativeTime } from '@/lib/utils/format';

export function ClientHeader({ client }: { client: Client }) {
  return (
    <div>
      <h1 className="text-3xl font-bold">{client.name}</h1>
      <div className="flex flex-wrap gap-4 mt-2 text-muted-foreground">
        <div className="flex items-center gap-1">
          <Mail className="h-4 w-4" />
          {client.email}
        </div>
        {client.phone && (
          <div className="flex items-center gap-1">
            <Phone className="h-4 w-4" />
            {client.phone}
          </div>
        )}
      </div>
      {client.last_contacted && (
        <p className="text-sm text-muted-foreground mt-1">
          Last contacted {formatRelativeTime(client.last_contacted)}
        </p>
      )}
    </div>
  );
}

