'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import HyperliquidSection from '@/features/trading/ui/HyperliquidSection';
import { useAuthStore } from '@/features/auth/model/store';

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-black">Dashboard Trading</h1>
          <p className="text-gray-600 mt-2">
            Gérez vos positions et ordres Hyperliquid
          </p>
        </div>

        <HyperliquidSection />
      </main>
    </div>
  );
}
