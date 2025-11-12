import { useMutation, useQueryClient } from '@tanstack/react-query';
import { tasksApi } from '@/lib/api/endpoints/tasks';
import { TaskUpdate } from '@/lib/types/task.types';

export function useUpdateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: TaskUpdate }) => 
      tasksApi.update(id, data),
    onSuccess: (_, variables) => {
      // Invalidate all task queries (including those with agent_id in the key)
      queryClient.invalidateQueries({ queryKey: ['task'] });
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}
