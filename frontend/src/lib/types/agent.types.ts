export interface Agent {
  id: number;
  email: string;
  name: string;
  phone?: string;
  title?: string;
  company?: string;
  bio?: string;
  avatar_url?: string;
  auth_provider: 'email' | 'google';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AgentCreate {
  email: string;
  password: string;
  name: string;
  phone?: string;
  title?: string;
  company?: string;
}

export interface AgentLogin {
  email: string;
  password: string;
}

export interface GoogleLoginRequest {
  credential: string;
}

export interface AgentUpdate {
  name?: string;
  phone?: string;
  title?: string;
  company?: string;
  bio?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  agent: Agent;
}

