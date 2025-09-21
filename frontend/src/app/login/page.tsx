'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuthStore } from '../../store/authStore';
import { loginSchema, registerSchema, LoginFormData, RegisterFormData } from '../../lib/validation/auth';
import RouteGuard from '../../components/RouteGuard';

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const router = useRouter();
  const { login, register, isLoading, error, clearError } = useAuthStore();

  const loginForm = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const registerForm = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmitLogin = async (data: LoginFormData) => {
    try {
      clearError();
      await login(data);
      router.push('/');
    } catch {
      // L'erreur est déjà gérée dans le store
    }
  };

  const onSubmitRegister = async (data: RegisterFormData) => {
    try {
      clearError();
      const { email, username, password } = data;
      await register({ email, username, password });
      router.push('/');
    } catch {
      // L'erreur est déjà gérée dans le store
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    clearError();
    loginForm.reset();
    registerForm.reset();
  };

  return (
    <RouteGuard requireAuth={false}>
      <div className="min-h-screen bg-white flex items-center justify-center px-6">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-black rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-2xl">T</span>
            </div>
          </div>
          <h1 className="text-3xl font-bold text-black mb-2">
            {isLogin ? 'Connexion' : 'Créer un compte'}
          </h1>
          <p className="text-gray-600">
            {isLogin
              ? 'Connectez-vous à votre compte Trading Tool'
              : 'Créez votre compte Trading Tool'
            }
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {/* Login Form */}
        {isLogin ? (
          <form onSubmit={loginForm.handleSubmit(onSubmitLogin)} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                {...loginForm.register('email')}
                type="email"
                id="email"
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-black focus:outline-none transition-colors"
                placeholder="votre@email.com"
              />
              {loginForm.formState.errors.email && (
                <p className="text-red-600 text-sm mt-1">{loginForm.formState.errors.email.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Mot de passe
              </label>
              <input
                {...loginForm.register('password')}
                type="password"
                id="password"
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-black focus:outline-none transition-colors"
                placeholder="••••••••"
              />
              {loginForm.formState.errors.password && (
                <p className="text-red-600 text-sm mt-1">{loginForm.formState.errors.password.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-black text-white py-3 px-4 rounded-lg font-medium hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? 'Connexion...' : 'Se connecter'}
            </button>
          </form>
        ) : (
          /* Register Form */
          <form onSubmit={registerForm.handleSubmit(onSubmitRegister)} className="space-y-6">
            <div>
              <label htmlFor="register-email" className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                {...registerForm.register('email')}
                type="email"
                id="register-email"
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-black focus:outline-none transition-colors"
                placeholder="votre@email.com"
              />
              {registerForm.formState.errors.email && (
                <p className="text-red-600 text-sm mt-1">{registerForm.formState.errors.email.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                Nom d&apos;utilisateur
              </label>
              <input
                {...registerForm.register('username')}
                type="text"
                id="username"
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-black focus:outline-none transition-colors"
                placeholder="nom_utilisateur"
              />
              {registerForm.formState.errors.username && (
                <p className="text-red-600 text-sm mt-1">{registerForm.formState.errors.username.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="register-password" className="block text-sm font-medium text-gray-700 mb-2">
                Mot de passe
              </label>
              <input
                {...registerForm.register('password')}
                type="password"
                id="register-password"
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-black focus:outline-none transition-colors"
                placeholder="••••••••"
              />
              {registerForm.formState.errors.password && (
                <p className="text-red-600 text-sm mt-1">{registerForm.formState.errors.password.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="confirm-password" className="block text-sm font-medium text-gray-700 mb-2">
                Confirmer le mot de passe
              </label>
              <input
                {...registerForm.register('confirmPassword')}
                type="password"
                id="confirm-password"
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-black focus:outline-none transition-colors"
                placeholder="••••••••"
              />
              {registerForm.formState.errors.confirmPassword && (
                <p className="text-red-600 text-sm mt-1">{registerForm.formState.errors.confirmPassword.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-black text-white py-3 px-4 rounded-lg font-medium hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? 'Création...' : 'Créer le compte'}
            </button>
          </form>
        )}

        {/* Toggle Mode */}
        <div className="text-center">
          <button
            onClick={toggleMode}
            className="text-black hover:text-gray-600 font-medium transition-colors"
          >
{isLogin
              ? 'Pas encore de compte ? Créer un compte'
              : 'Déjà un compte ? Se connecter'
            }
          </button>
        </div>
      </div>
      </div>
    </RouteGuard>
  );
}