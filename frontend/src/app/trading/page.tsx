'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '../../components/Navbar';
import TradingAssistant from '../../components/trading/TradingAssistant';
import { useAuthStore } from '../../store/authStore';

export default function TradingPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated && user === null) {
      router.push('/login');
    }
  }, [isAuthenticated, user, router]);

  // Ne rien afficher pendant la vérification d'authentification
  if (!isAuthenticated || !user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-7xl mx-auto px-6 py-10">
        <TradingAssistant />
      </main>
    </div>
  );
}
