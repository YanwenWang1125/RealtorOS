export type PropertyType = 'residential' | 'commercial' | 'land' | 'other';

export type ClientStage = 'lead' | 'negotiating' | 'under_contract' | 'closed' | 'lost';

export interface Client {
  id: number;
  agent_id: number;
  name: string;
  email: string;
  phone?: string;
  property_address: string;
  property_type: PropertyType;
  stage: ClientStage;
  notes?: string;
  custom_fields?: Record<string, any>;
  created_at: string;
  updated_at: string;
  last_contacted?: string;
}

export interface ClientCreate {
  name: string;
  email: string;
  phone?: string;
  property_address: string;
  property_type: PropertyType;
  stage: ClientStage;
  notes?: string;
  custom_fields?: Record<string, any>;
}

export interface ClientUpdate {
  name?: string;
  email?: string;
  phone?: string;
  property_address?: string;
  property_type?: PropertyType;
  stage?: ClientStage;
  notes?: string;
  custom_fields?: Record<string, any>;
}
