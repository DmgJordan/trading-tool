'use client';

import RouteGuard from '@/features/auth/ui/RouteGuard';
import LoginForm from '@/features/auth/ui/LoginForm';

export default function LoginPage() {
  return (
    <RouteGuard>
      <div className="min-h-screen bg-white flex items-center justify-center px-6">
        <LoginForm />
      </div>
    </RouteGuard>
  );
}
