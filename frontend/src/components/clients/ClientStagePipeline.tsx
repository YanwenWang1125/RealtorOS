import React from 'react';
import { ChevronRight } from 'lucide-react';
import { Client, ClientStage } from '@/lib/types/client.types';
import { CLIENT_STAGE_LABELS } from '@/lib/constants/client.constants';
import { cn } from '@/lib/utils/index';

export function ClientStagePipeline({ client }: { client: Client }) {
  const stages: ClientStage[] = ['lead', 'negotiating', 'closed'];
  // Handle deprecated 'under_contract' stage by mapping it to 'closed'
  const displayStage = client.stage === 'under_contract' ? 'closed' : client.stage;
  const currentIndex = stages.indexOf(displayStage);

  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-2">
      {stages.map((stage, index) => (
        <React.Fragment key={stage}>
          <div
            className={cn(
              "flex-1 min-w-[120px] rounded-lg p-4 text-center transition-colors whitespace-nowrap",
              index <= currentIndex
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground"
            )}
          >
            {CLIENT_STAGE_LABELS[stage]}
          </div>
          {index < stages.length - 1 && (
            <ChevronRight className="h-5 w-5 text-muted-foreground flex-shrink-0" />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}

