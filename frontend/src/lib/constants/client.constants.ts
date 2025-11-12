import { PropertyType, ClientStage } from '@/lib/types/client.types';

export const PROPERTY_TYPES: PropertyType[] = [
  'residential',
  'commercial',
  'land',
  'other'
];

export const CLIENT_STAGES: ClientStage[] = [
  'lead',
  'negotiating',
  'closed',
  'lost'
];

export const PROPERTY_TYPE_LABELS: Record<PropertyType, string> = {
  residential: 'Residential',
  commercial: 'Commercial',
  land: 'Land',
  other: 'Other'
};

export const CLIENT_STAGE_LABELS: Record<ClientStage, string> = {
  lead: 'Lead',
  negotiating: 'Negotiating',
  under_contract: 'Under Contract', // Deprecated - kept for backward compatibility
  closed: 'Closed',
  lost: 'Lost'
};

export const CLIENT_STAGE_COLORS: Record<ClientStage, string> = {
  lead: 'bg-gray-100 text-gray-700',
  negotiating: 'bg-yellow-100 text-yellow-700',
  under_contract: 'bg-blue-100 text-blue-700', // Deprecated - kept for backward compatibility
  closed: 'bg-green-100 text-green-700',
  lost: 'bg-red-100 text-red-700'
};
