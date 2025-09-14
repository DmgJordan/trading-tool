'use client';

import Navbar from '../../components/Navbar';
import ApiKeysConfiguration from '../../components/ApiKeysConfiguration';
import { useAuthStore } from '../../store/authStore';

export default function AccountPage() {
  const { user } = useAuthStore();

  return (
    <div className="min-h-screen bg-white">
      <Navbar />

      <main className="max-w-6xl mx-auto px-6 sm:px-8 lg:px-12 py-12">
        {/* Header section */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-black mb-4">
            Gestion du Compte
          </h1>
          <p className="text-lg text-gray-600">
            Gérez vos informations personnelles et configurez vos clés API.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Section informations personnelles */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg border-2 border-black p-6">
              <h2 className="text-2xl font-bold text-black mb-6">
                Informations Personnelles
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nom d&apos;utilisateur
                  </label>
                  <div className="px-4 py-3 bg-gray-50 rounded-lg border-2 border-gray-200">
                    <span className="text-black font-medium">{user?.username}</span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email
                  </label>
                  <div className="px-4 py-3 bg-gray-50 rounded-lg border-2 border-gray-200">
                    <span className="text-black font-medium">{user?.email}</span>
                  </div>
                </div>

                <div className="pt-4">
                  <p className="text-xs text-gray-500">
                    Pour modifier ces informations, contactez l&apos;administrateur.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Section configuration des API */}
          <div className="lg:col-span-2">
            <ApiKeysConfiguration />
          </div>
        </div>
      </main>
    </div>
  );
}