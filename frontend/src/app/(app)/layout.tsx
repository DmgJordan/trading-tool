import type { ReactNode } from 'react';
import AuthProvider from '@/app-providers/auth-provider';
import QueryProvider from '@/app-providers/query-provider';
import ThemeProvider from '@/app-providers/theme-provider';
import Navbar from '@/shared/ui/Navbar';

interface AppLayoutProps {
  children: ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
  return (
    <QueryProvider>
      <ThemeProvider>
        <AuthProvider>
          <div className="flex min-h-screen flex-col">
            <Navbar />
            <main className="flex-1">{children}</main>
          </div>
        </AuthProvider>
      </ThemeProvider>
    </QueryProvider>
  );
}
