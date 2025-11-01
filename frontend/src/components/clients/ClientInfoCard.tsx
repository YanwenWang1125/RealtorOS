import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Client } from '@/lib/types/client.types';
import { PROPERTY_TYPE_LABELS } from '@/lib/constants/client.constants';

export function ClientInfoCard({ client }: { client: Client }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Client Information</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="text-sm font-medium">Property Address</label>
          <p className="text-sm text-muted-foreground">{client.property_address}</p>
        </div>
        <div>
          <label className="text-sm font-medium">Property Type</label>
          <p className="text-sm text-muted-foreground">
            {PROPERTY_TYPE_LABELS[client.property_type]}
          </p>
        </div>
        {client.notes && (
          <div>
            <label className="text-sm font-medium">Notes</label>
            <p className="text-sm text-muted-foreground whitespace-pre-wrap">{client.notes}</p>
          </div>
        )}
        {client.custom_fields && Object.keys(client.custom_fields).length > 0 && (
          <div>
            <label className="text-sm font-medium">Custom Fields</label>
            <dl className="mt-2 space-y-2">
              {Object.entries(client.custom_fields).map(([key, value]) => (
                <div key={key} className="flex justify-between text-sm">
                  <dt className="text-muted-foreground">{key}:</dt>
                  <dd className="font-medium">{String(value)}</dd>
                </div>
              ))}
            </dl>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

