'use client';

import { DashboardStats } from '../../lib/types/ai_recommendations';
import GenerateButton from './GenerateButton';

interface DashboardHeaderProps {
  stats: DashboardStats | null;
  onGenerate: () => void;
  isGenerating: boolean;
  lastGenerated?: string | null;
}

export default function DashboardHeader({
  stats,
  onGenerate,
  isGenerating,
  lastGenerated
}: DashboardHeaderProps) {
  return (
    <div className="mb-8">
      {/* En-tête principal */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6">
        <div className="mb-4 lg:mb-0">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Dashboard IA Trading
          </h1>
          <p className="text-gray-600">
            Recommandations personnalisées basées sur vos préférences de trading
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          <button className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors">
            📊 Voir l&apos;historique
          </button>
          <GenerateButton
            onGenerate={onGenerate}
            isLoading={isGenerating}
            lastGenerated={lastGenerated}
            pendingCount={stats?.pending_recommendations || 0}
          />
        </div>
      </div>

      {/* Statistiques */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Recommandations actives */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Recommandations actives</p>
                <p className="text-2xl font-bold text-gray-900">{stats.pending_recommendations}</p>
              </div>
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 text-lg">📈</span>
              </div>
            </div>
          </div>

          {/* P&L estimé total */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">P&L estimé</p>
                <p className={`text-2xl font-bold ${stats.total_estimated_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {stats.total_estimated_pnl >= 0 ? '+' : ''}{stats.total_estimated_pnl.toFixed(0)}€
                </p>
                <p className={`text-xs ${stats.total_estimated_pnl_percentage >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {stats.total_estimated_pnl_percentage >= 0 ? '+' : ''}{stats.total_estimated_pnl_percentage.toFixed(1)}%
                </p>
              </div>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                stats.total_estimated_pnl >= 0 ? 'bg-green-100' : 'bg-red-100'
              }`}>
                <span className="text-lg">
                  {stats.total_estimated_pnl >= 0 ? '💰' : '📉'}
                </span>
              </div>
            </div>
          </div>

          {/* Recommandations acceptées */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Acceptées</p>
                <p className="text-2xl font-bold text-green-600">{stats.accepted_recommendations}</p>
                <p className="text-xs text-gray-500">
                  {stats.total_recommendations > 0
                    ? `${Math.round((stats.accepted_recommendations / stats.total_recommendations) * 100)}% du total`
                    : 'Aucune donnée'
                  }
                </p>
              </div>
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600 text-lg">✅</span>
              </div>
            </div>
          </div>

          {/* Recommandations rejetées */}
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Rejetées</p>
                <p className="text-2xl font-bold text-red-600">{stats.rejected_recommendations}</p>
                <p className="text-xs text-gray-500">
                  {stats.total_recommendations > 0
                    ? `${Math.round((stats.rejected_recommendations / stats.total_recommendations) * 100)}% du total`
                    : 'Aucune donnée'
                  }
                </p>
              </div>
              <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <span className="text-red-600 text-lg">❌</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Message si aucune donnée */}
      {!stats && (
        <div className="bg-white rounded-xl border-2 border-gray-200 p-8 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-gray-400 text-2xl">🤖</span>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Bienvenue dans votre Dashboard IA
          </h3>
          <p className="text-gray-600 mb-4">
            Générez vos premières recommandations de trading personnalisées basées sur vos préférences.
          </p>
          <GenerateButton
            onGenerate={onGenerate}
            isLoading={isGenerating}
            className="mx-auto"
          />
        </div>
      )}
    </div>
  );
}