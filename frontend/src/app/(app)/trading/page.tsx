'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import TradingAssistant from '@/features/trading/ui/TradingAssistant';
import { useAuthStore } from '@/features/auth/model/store';

export default function TradingPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated && user === null) {
      router.push('/login');
    }
  }, [isAuthenticated, user, router]);

  if (!isAuthenticated || !user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-7xl mx-auto px-6 py-10">
        <TradingAssistant />
      </main>
    </div>
  );
}
