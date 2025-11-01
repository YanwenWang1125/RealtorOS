'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils/cn';
import { ROUTES } from '@/lib/constants/routes';
import { 
  LayoutDashboard, 
  Users, 
  CheckSquare, 
  Mail, 
  BarChart3 
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: ROUTES.DASHBOARD, icon: LayoutDashboard },
  { name: 'Clients', href: ROUTES.CLIENTS, icon: Users },
  { name: 'Tasks', href: ROUTES.TASKS, icon: CheckSquare },
  { name: 'Emails', href: ROUTES.EMAILS, icon: Mail },
  { name: 'Analytics', href: ROUTES.ANALYTICS, icon: BarChart3 },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-64 border-r bg-white md:flex md:flex-col">
      <div className="flex h-16 items-center border-b px-6">
        <h1 className="text-xl font-bold">RealtorOS</h1>
      </div>
      
      <nav className="flex-1 space-y-1 p-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
          const Icon = item.icon;
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )}
            >
              <Icon className="h-5 w-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
