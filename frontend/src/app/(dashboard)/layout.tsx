import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { MobileNav } from '@/components/layout/MobileNav';
import { AuthGuard } from '@/components/auth/AuthGuard';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard>
      <div className="flex h-screen overflow-hidden">
        {/* Sidebar for desktop */}
        <Sidebar />
        
        <div className="flex flex-1 flex-col overflow-hidden">
          {/* Header */}
          <Header />
          
          {/* Main content */}
          <main className="flex-1 overflow-y-auto bg-muted p-4 md:p-6 lg:p-8">
            {children}
          </main>
        </div>
        
        {/* Mobile navigation */}
        <MobileNav />
      </div>
    </AuthGuard>
  );
}
