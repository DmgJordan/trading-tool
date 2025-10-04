import CCXTTest from '@/features/dev-tools/ui/CCXTTest';
import ConfigurationTest from '@/features/dev-tools/ui/ConfigurationTest';

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      <main className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 py-12">
        <div className="text-center mb-16">
          <h1 className="text-4xl sm:text-5xl font-bold text-black mb-6">
            Configuration du Trading Tool
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Vérifiez la connexion avec le backend et la base de données avant de
            commencer votre session de trading.
          </p>
        </div>

        <div className="flex justify-center mb-16">
          <div className="w-full max-w-3xl">
            <ConfigurationTest />
          </div>
        </div>

        <div className="flex justify-center">
          <div className="w-full max-w-4xl">
            <CCXTTest />
          </div>
        </div>

        <div className="mt-20" />
      </main>
    </div>
  );
}
