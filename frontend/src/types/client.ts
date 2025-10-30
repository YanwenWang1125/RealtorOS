/**
 * Client type definitions for RealtorOS.
 * 
 * This module defines TypeScript types for client-related
 * data structures in the RealtorOS application.
 */

export interface Client {
  id: string
  name: string
  email: string
  phone?: string
  property_address: string
  property_type: 'residential' | 'commercial' | 'land' | 'other'
  stage: 'lead' | 'negotiating' | 'under_contract' | 'closed' | 'lost'
  notes?: string
  created_at: string
  updated_at: string
  last_contacted?: string
  custom_fields?: Record<string, any>
}

export interface ClientCreate {
  name: string
  email: string
  phone?: string
  property_address: string
  property_type: 'residential' | 'commercial' | 'land' | 'other'
  stage: 'lead' | 'negotiating' | 'under_contract' | 'closed' | 'lost'
  notes?: string
  custom_fields?: Record<string, any>
}

export interface ClientUpdate {
  name?: string
  email?: string
  phone?: string
  property_address?: string
  property_type?: 'residential' | 'commercial' | 'land' | 'other'
  stage?: 'lead' | 'negotiating' | 'under_contract' | 'closed' | 'lost'
  notes?: string
  last_contacted?: string
  custom_fields?: Record<string, any>
}
