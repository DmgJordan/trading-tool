'use client';

import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import Navbar from '../../components/Navbar';
import RangeSlider from '../../components/preferences/RangeSlider';
import MultiSelect, {
  MultiSelectOption,
} from '../../components/preferences/MultiSelect';
import RadioCardGroup from '../../components/preferences/RadioCardGroup';
import { ToggleGroup } from '../../components/preferences/ToggleSwitch';
import {
  useInitializePreferences,
  usePreferencesActions,
  useAutoSavePreferences,
} from '../../store/preferencesStore';
import {
  validateAssetSymbol,
  validateTechnicalIndicator,
  defaultPreferencesValues,
} from '../../lib/validation/preferences';
import {
  RISK_TOLERANCE_OPTIONS,
  INVESTMENT_HORIZON_OPTIONS,
  TRADING_STYLE_OPTIONS,
  SLIDER_CONFIGS,
} from '../../lib/types/preferences';

// Options pour les cryptomonnaies populaires
const CRYPTO_OPTIONS: MultiSelectOption[] = [
  {
    value: 'BTC',
    label: 'Bitcoin',
    description: 'La première cryptomonnaie',
    category: 'Major',
    isPopular: true,
  },
  {
    value: 'ETH',
    label: 'Ethereum',
    description: 'Plateforme de contrats intelligents',
    category: 'Major',
    isPopular: true,
  },
  {
    value: 'SOL',
    label: 'Solana',
    description: 'Blockchain haute performance',
    category: 'Layer 1',
    isPopular: true,
  },
  {
    value: 'ADA',
    label: 'Cardano',
    description: 'Blockchain proof-of-stake',
    category: 'Layer 1',
  },
  {
    value: 'DOT',
    label: 'Polkadot',
    description: 'Interopérabilité blockchain',
    category: 'Layer 1',
  },
  {
    value: 'AVAX',
    label: 'Avalanche',
    description: 'Plateforme DeFi rapide',
    category: 'Layer 1',
  },
  {
    value: 'MATIC',
    label: 'Polygon',
    description: "Solution de mise à l'échelle Ethereum",
    category: 'Layer 2',
  },
  {
    value: 'LINK',
    label: 'Chainlink',
    description: 'Oracle décentralisé',
    category: 'Infrastructure',
  },
  {
    value: 'UNI',
    label: 'Uniswap',
    description: 'Exchange décentralisé',
    category: 'DeFi',
  },
  {
    value: 'AAVE',
    label: 'Aave',
    description: 'Protocole de prêt DeFi',
    category: 'DeFi',
  },
];

// Options pour les indicateurs techniques
const INDICATOR_OPTIONS: MultiSelectOption[] = [
  {
    value: 'RSI',
    label: 'RSI',
    description: 'Relative Strength Index',
    category: 'Momentum',
    isPopular: true,
  },
  {
    value: 'MACD',
    label: 'MACD',
    description: 'Moving Average Convergence Divergence',
    category: 'Momentum',
    isPopular: true,
  },
  {
    value: 'SMA',
    label: 'SMA',
    description: 'Simple Moving Average',
    category: 'Trend',
    isPopular: true,
  },
  {
    value: 'EMA',
    label: 'EMA',
    description: 'Exponential Moving Average',
    category: 'Trend',
  },
  {
    value: 'BB',
    label: 'Bollinger Bands',
    description: 'Bandes de Bollinger',
    category: 'Volatility',
  },
  {
    value: 'STOCH',
    label: 'Stochastic',
    description: 'Oscillateur stochastique',
    category: 'Momentum',
  },
  {
    value: 'ADX',
    label: 'ADX',
    description: 'Average Directional Index',
    category: 'Trend',
  },
  {
    value: 'CCI',
    label: 'CCI',
    description: 'Commodity Channel Index',
    category: 'Momentum',
  },
  {
    value: 'ATR',
    label: 'ATR',
    description: 'Average True Range',
    category: 'Volatility',
  },
  {
    value: 'VWAP',
    label: 'VWAP',
    description: 'Volume Weighted Average Price',
    category: 'Volume',
  },
  {
    value: 'OBV',
    label: 'OBV',
    description: 'On Balance Volume',
    category: 'Volume',
  },
];

// Helper pour convertir les erreurs en string
const getErrorMessage = (error: any): string | undefined => {
  if (typeof error === 'string') return error;
  if (error && typeof error.message === 'string') return error.message;
  return undefined;
};

export default function PreferencesPage() {
  const {
    initialize,
    isInitialized,
    isLoading,
    error: initError,
    preferences,
    defaults,
  } = useInitializePreferences();

  const {
    updateWithNotification,
    resetWithConfirmation,
    clearError,
    isSaving,
    error: saveError,
    lastSaved,
  } = usePreferencesActions();

  const { debouncedUpdate } = useAutoSavePreferences(3000); // Auto-save après 3 secondes

  const [showSuccess, setShowSuccess] = useState(false);
  const [notifications, setNotifications] = useState({
    email_alerts: true,
    push_notifications: false,
    telegram_alerts: false,
    discord_alerts: false,
  });

  // Configuration du formulaire
  const {
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isDirty },
  } = useForm({
    defaultValues: preferences || defaults || defaultPreferencesValues,
  });

  // Initialiser les préférences au chargement
  useEffect(() => {
    if (!isInitialized && !isLoading) {
      initialize();
    }
  }, [isInitialized, isLoading, initialize]);

  // Mettre à jour le formulaire quand les préférences sont chargées
  useEffect(() => {
    if (preferences) {
      Object.entries(preferences).forEach(([key, value]) => {
        if (
          key !== 'id' &&
          key !== 'user_id' &&
          key !== 'created_at' &&
          key !== 'updated_at'
        ) {
          setValue(key as keyof typeof defaultPreferencesValues, value);
        }
      });
    }
  }, [preferences, setValue]);

  // Surveiller les changements pour l'auto-save
  const watchedValues = watch();
  useEffect(() => {
    if (isDirty && isInitialized) {
      debouncedUpdate(watchedValues);
    }
  }, [watchedValues, isDirty, isInitialized, debouncedUpdate]);

  // Sauvegarde manuelle
  const onSubmit = async (data: typeof defaultPreferencesValues) => {
    updateWithNotification(
      data,
      () => {
        setShowSuccess(true);
        setTimeout(() => setShowSuccess(false), 3000);
      },
      error => console.error('Erreur de sauvegarde:', error)
    );
  };

  // Gestion du reset
  const handleReset = () => {
    resetWithConfirmation(
      () => {
        setShowSuccess(true);
        setTimeout(() => setShowSuccess(false), 3000);
      },
      error => console.error('Erreur de reset:', error)
    );
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-white">
        <Navbar />
        <main className="max-w-6xl mx-auto px-6 sm:px-8 lg:px-12 py-12">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
              <p className="text-gray-600">Chargement de vos préférences...</p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  // Error state
  if (initError) {
    return (
      <div className="min-h-screen bg-white">
        <Navbar />
        <main className="max-w-6xl mx-auto px-6 sm:px-8 lg:px-12 py-12">
          <div className="text-center">
            <div className="text-red-600 text-xl mb-4">
              Erreur de chargement
            </div>
            <p className="text-gray-600 mb-4">{initError}</p>
            <button
              onClick={initialize}
              className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800"
            >
              Réessayer
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <Navbar />

      <main className="max-w-6xl mx-auto px-6 sm:px-8 lg:px-12 py-12">
        {/* Header section */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-black mb-4">
            Préférences de Trading IA
          </h1>
          <p className="text-lg text-gray-600">
            Configurez vos préférences pour obtenir des recommandations
            personnalisées de notre IA de trading.
          </p>
        </div>

        {/* Messages de statut */}
        {showSuccess && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center">
              <svg
                className="w-5 h-5 text-green-500 mr-2"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
              <span className="text-green-700 font-medium">
                Préférences sauvegardées avec succès !
              </span>
            </div>
          </div>
        )}

        {saveError && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <svg
                  className="w-5 h-5 text-red-500 mr-2"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="text-red-700 font-medium">{saveError}</span>
              </div>
              <button
                onClick={clearError}
                className="text-red-500 hover:text-red-700"
              >
                ×
              </button>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
          {/* Section 1: Profil de Trading */}
          <div className="bg-white rounded-xl shadow-lg border-2 border-black p-6">
            <h2 className="text-2xl font-bold text-black mb-6">
              🎯 Profil de Trading
            </h2>

            <div className="space-y-8">
              {/* Tolérance au risque */}
              <RadioCardGroup
                options={RISK_TOLERANCE_OPTIONS}
                value={watch('risk_tolerance')}
                onChange={value =>
                  setValue('risk_tolerance', value as 'LOW' | 'MEDIUM' | 'HIGH')
                }
                label="Tolérance au risque"
                description="Quel niveau de risque êtes-vous prêt à accepter ?"
                error={errors.risk_tolerance?.message}
              />

              {/* Horizon d'investissement */}
              <RadioCardGroup
                options={INVESTMENT_HORIZON_OPTIONS}
                value={watch('investment_horizon')}
                onChange={value =>
                  setValue(
                    'investment_horizon',
                    value as 'SHORT_TERM' | 'MEDIUM_TERM' | 'LONG_TERM'
                  )
                }
                label="Horizon d'investissement"
                description="Sur quelle période envisagez-vous vos investissements ?"
                error={errors.investment_horizon?.message}
              />

              {/* Style de trading */}
              <RadioCardGroup
                options={TRADING_STYLE_OPTIONS}
                value={watch('trading_style')}
                onChange={value =>
                  setValue(
                    'trading_style',
                    value as 'CONSERVATIVE' | 'BALANCED' | 'AGGRESSIVE'
                  )
                }
                label="Style de trading"
                description="Quelle approche correspond le mieux à votre stratégie ?"
                error={errors.trading_style?.message}
              />
            </div>
          </div>

          {/* Section 2: Gestion des Risques */}
          <div className="bg-white rounded-xl shadow-lg border-2 border-black p-6">
            <h2 className="text-2xl font-bold text-black mb-6">
              ⚠️ Gestion des Risques
            </h2>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <RangeSlider
                value={watch('max_position_size')}
                onChange={value => setValue('max_position_size', value)}
                config={SLIDER_CONFIGS.max_position_size}
                label="Taille maximale de position"
                description="Pourcentage maximum de votre portefeuille pour une seule position"
                error={errors.max_position_size?.message}
              />

              <RangeSlider
                value={watch('stop_loss_percentage')}
                onChange={value => setValue('stop_loss_percentage', value)}
                config={SLIDER_CONFIGS.stop_loss_percentage}
                label="Stop-loss par défaut"
                description="Pourcentage de perte acceptable avant de couper une position"
                error={errors.stop_loss_percentage?.message}
              />

              <div className="lg:col-span-2">
                <RangeSlider
                  value={watch('take_profit_ratio')}
                  onChange={value => setValue('take_profit_ratio', value)}
                  config={SLIDER_CONFIGS.take_profit_ratio}
                  label="Ratio risk/reward"
                  description="Ratio entre le gain espéré et la perte potentielle"
                  error={errors.take_profit_ratio?.message}
                />
              </div>
            </div>
          </div>

          {/* Section 3: Actifs Préférés */}
          <div className="bg-white rounded-xl shadow-lg border-2 border-black p-6">
            <h2 className="text-2xl font-bold text-black mb-6">
              💰 Actifs Préférés
            </h2>

            <MultiSelect
              options={CRYPTO_OPTIONS}
              selected={watch('preferred_assets') || []}
              onChange={selected => setValue('preferred_assets', selected)}
              label="Cryptomonnaies préférées"
              description="Sélectionnez jusqu'à 20 cryptomonnaies que vous souhaitez trader"
              placeholder="Rechercher des cryptomonnaies..."
              maxItems={20}
              allowCustom={true}
              customValidator={validateAssetSymbol}
              error={getErrorMessage(errors.preferred_assets)}
            />
          </div>

          {/* Section 4: Indicateurs Techniques */}
          <div className="bg-white rounded-xl shadow-lg border-2 border-black p-6">
            <h2 className="text-2xl font-bold text-black mb-6">
              📊 Indicateurs Techniques
            </h2>

            <MultiSelect
              options={INDICATOR_OPTIONS}
              selected={watch('technical_indicators') || []}
              onChange={selected => setValue('technical_indicators', selected)}
              label="Indicateurs préférés"
              description="Sélectionnez jusqu'à 15 indicateurs techniques pour l'analyse"
              placeholder="Rechercher des indicateurs..."
              maxItems={15}
              allowCustom={true}
              customValidator={validateTechnicalIndicator}
              error={getErrorMessage(errors.technical_indicators)}
            />
          </div>

          {/* Section 5: Notifications */}
          <div className="bg-white rounded-xl shadow-lg border-2 border-black p-6">
            <h2 className="text-2xl font-bold text-black mb-6">
              🔔 Notifications
            </h2>

            <ToggleGroup
              title="Alertes de trading"
              description="Choisissez comment vous souhaitez être notifié des nouvelles recommandations"
              toggles={[
                {
                  key: 'email_alerts',
                  label: 'Alertes par email',
                  description: 'Recevoir les recommandations par email',
                  checked: notifications.email_alerts,
                },
                {
                  key: 'push_notifications',
                  label: 'Notifications push',
                  description: 'Notifications directes dans votre navigateur',
                  checked: notifications.push_notifications,
                },
                {
                  key: 'telegram_alerts',
                  label: 'Alertes Telegram',
                  description:
                    'Recevoir les signaux via Telegram (bientôt disponible)',
                  checked: notifications.telegram_alerts,
                  disabled: true,
                },
                {
                  key: 'discord_alerts',
                  label: 'Alertes Discord',
                  description:
                    'Recevoir les signaux via Discord (bientôt disponible)',
                  checked: notifications.discord_alerts,
                  disabled: true,
                },
              ]}
              onChange={(key, checked) =>
                setNotifications(prev => ({ ...prev, [key]: checked }))
              }
            />
          </div>

          {/* Actions */}
          <div className="flex justify-between items-center pt-6">
            <div className="flex items-center space-x-4">
              <button
                type="button"
                onClick={handleReset}
                className="px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:border-gray-400 hover:bg-gray-50 transition-colors"
                disabled={isSaving}
              >
                Réinitialiser
              </button>

              {lastSaved && (
                <span className="text-sm text-gray-500">
                  Dernière sauvegarde :{' '}
                  {new Date(lastSaved).toLocaleTimeString()}
                </span>
              )}
            </div>

            <button
              type="submit"
              disabled={isSaving}
              className="px-8 py-3 bg-black text-white rounded-lg hover:bg-gray-800 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center"
            >
              {isSaving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Sauvegarde...
                </>
              ) : (
                'Sauvegarder'
              )}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}
