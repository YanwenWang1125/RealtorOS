'use client';

import { Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useUIStore } from '@/store/useUIStore';

export function Header() {
  const toggleSidebar = useUIStore((state) => state.toggleSidebar);

  return (
    <header className="flex h-16 items-center justify-between border-b bg-white px-4 md:px-6">
      <Button
        variant="ghost"
        size="icon"
        className="md:hidden"
        onClick={toggleSidebar}
      >
        <Menu className="h-6 w-6" />
      </Button>
      
      <div className="flex items-center gap-4 ml-auto">
        {/* Future: User profile, notifications, etc. */}
        <div className="text-sm text-muted-foreground">
          Welcome to RealtorOS
        </div>
      </div>
    </header>
  );
}
