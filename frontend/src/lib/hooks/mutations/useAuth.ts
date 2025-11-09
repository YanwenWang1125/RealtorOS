import { useMutation, useQueryClient } from '@tanstack/react-query';
import { agentsApi } from '@/lib/api/endpoints/agents';
import { useAuthStore } from '@/store/useAuthStore';
import { useRouter } from 'next/navigation';
import { useToast } from '@/lib/hooks/ui/useToast';
import { AgentCreate, AgentLogin, AgentUpdate } from '@/lib/types/agent.types';

// Helper function to clear all queries and reset cache after login
const clearCacheAndSetAuth = (queryClient: ReturnType<typeof useQueryClient>, setAuth: (data: any) => void, data: any) => {
  // Clear all React Query cache to prevent showing data from previous user
  queryClient.clear();
  // Set new auth data
  setAuth(data);
  // Invalidate all queries to force refetch with new token
  queryClient.invalidateQueries();
};

export const useRegister = () => {
  const queryClient = useQueryClient();
  const setAuth = useAuthStore((state) => state.setAuth);
  const router = useRouter();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (data: AgentCreate) => agentsApi.register(data),
    onSuccess: (data) => {
      clearCacheAndSetAuth(queryClient, setAuth, data);
      toast({
        title: 'Registration successful',
        description: 'Welcome to RealtorOS!',
      });
      router.push('/dashboard');
    },
    onError: (error: any) => {
      toast({
        title: 'Registration failed',
        description: error.response?.data?.detail || 'Something went wrong',
        variant: 'destructive',
      });
    },
  });
};

export const useLoginEmail = () => {
  const queryClient = useQueryClient();
  const setAuth = useAuthStore((state) => state.setAuth);
  const router = useRouter();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (credentials: AgentLogin) => agentsApi.loginEmail(credentials),
    onSuccess: (data) => {
      clearCacheAndSetAuth(queryClient, setAuth, data);
      toast({
        title: 'Login successful',
        description: `Welcome back, ${data.agent.name}!`,
      });
      router.push('/dashboard');
    },
    onError: (error: any) => {
      toast({
        title: 'Login failed',
        description: error.response?.data?.detail || 'Invalid credentials',
        variant: 'destructive',
      });
    },
  });
};

export const useLoginGoogle = () => {
  const queryClient = useQueryClient();
  const setAuth = useAuthStore((state) => state.setAuth);
  const router = useRouter();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (googleToken: string) => agentsApi.loginGoogle(googleToken),
    onSuccess: (data) => {
      clearCacheAndSetAuth(queryClient, setAuth, data);
      toast({
        title: 'Login successful',
        description: `Welcome, ${data.agent.name}!`,
      });
      router.push('/dashboard');
    },
    onError: (error: any) => {
      toast({
        title: 'Login failed',
        description: error.response?.data?.detail || 'Google authentication failed',
        variant: 'destructive',
      });
    },
  });
};

export const useUpdateProfile = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const { agent, token, setAuth } = useAuthStore();

  return useMutation({
    mutationFn: (data: AgentUpdate) => agentsApi.updateProfile(data),
    onSuccess: (updatedAgent) => {
      // Update auth store with new agent data
      if (agent && token) {
        setAuth({
          access_token: token,
          token_type: 'bearer',
          agent: updatedAgent,
        });
      }
      queryClient.invalidateQueries({ queryKey: ['agent', 'me'] });
      toast({
        title: 'Profile updated',
        description: 'Your profile has been updated successfully.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Update failed',
        description: error.response?.data?.detail || 'Something went wrong',
        variant: 'destructive',
      });
    },
  });
};

