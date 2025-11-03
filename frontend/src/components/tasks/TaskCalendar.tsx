'use client';

import { useMemo, useState } from 'react';
import { Calendar as BigCalendar, dateFnsLocalizer } from 'react-big-calendar';
import { format, parse, startOfWeek, getDay } from 'date-fns';
import { enUS } from 'date-fns/locale';
import { Task } from '@/lib/types/task.types';
import { TaskDetailModal } from '@/components/tasks/TaskDetailModal';
import { useClients } from '@/lib/hooks/queries/useClients';
import 'react-big-calendar/lib/css/react-big-calendar.css';

const locales = {
  'en-US': enUS,
};

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
});

interface TaskCalendarProps {
  tasks: Task[];
  isLoading: boolean;
}

export function TaskCalendar({ tasks, isLoading }: TaskCalendarProps) {
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  // Backend enforces limit <= 100
  const { data: clients } = useClients({ limit: 100 });

  const clientMap = useMemo(() => {
    if (!clients) return {};
    return Object.fromEntries(clients.map(c => [c.id, c]));
  }, [clients]);

  const events = useMemo(() => {
    return tasks.map(task => {
      const client = clientMap[task.client_id];
      return {
        id: task.id,
        title: `${client?.name || 'Unknown'} - ${task.followup_type}`,
        start: new Date(task.scheduled_for),
        end: new Date(task.scheduled_for),
        resource: task,
      };
    });
  }, [tasks, clientMap]);

  const eventStyleGetter = (event: any) => {
    const task = event.resource as Task;
    let backgroundColor = '#3B82F6'; // blue (low priority)

    if (task.priority === 'high') {
      backgroundColor = '#EF4444'; // red
    } else if (task.priority === 'medium') {
      backgroundColor = '#F97316'; // orange
    }

    // Grey out completed tasks
    if (task.status === 'completed' || task.status === 'skipped') {
      backgroundColor = '#9CA3AF'; // gray
    }

    return {
      style: {
        backgroundColor,
        borderRadius: '4px',
        opacity: 0.8,
        color: 'white',
        border: '0',
        display: 'block',
      },
    };
  };

  if (isLoading) {
    return <div className="h-[600px] flex items-center justify-center">
      <p className="text-muted-foreground">Loading calendar...</p>
    </div>;
  }

  return (
    <>
      <div className="h-[600px] bg-white p-4 rounded-lg border">
        <BigCalendar
          localizer={localizer}
          events={events}
          startAccessor="start"
          endAccessor="end"
          style={{ height: '100%' }}
          eventPropGetter={eventStyleGetter}
          onSelectEvent={(event) => setSelectedTask(event.resource)}
          views={['month', 'week', 'day']}
          defaultView="month"
        />
      </div>

      {/* Task Detail Modal */}
      {selectedTask && (
        <TaskDetailModal
          task={selectedTask}
          open={!!selectedTask}
          onOpenChange={(open) => !open && setSelectedTask(null)}
        />
      )}
    </>
  );
}

