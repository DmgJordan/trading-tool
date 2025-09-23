import Navbar from '../components/Navbar';
import ConfigurationTest from '../components/ConfigurationTest';
import CCXTTest from '../components/CCXTTest';

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      <Navbar />

      <main className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 py-12">
        {/* Header section avec plus d'espacement */}
        <div className="text-center mb-16">
          <h1 className="text-4xl sm:text-5xl font-bold text-black mb-6">
            Configuration du Trading Tool
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Vérifiez la connexion avec le backend et la base de données avant de commencer votre session de trading.
          </p>
        </div>

        {/* Configuration card centré avec plus d'espacement */}
        <div className="flex justify-center mb-16">
          <div className="w-full max-w-3xl">
            <ConfigurationTest />
          </div>
        </div>

        {/* Section CCXT Test */}
        <div className="flex justify-center">
          <div className="w-full max-w-4xl">
            <CCXTTest />
          </div>
        </div>

        {/* Espacement en bas */}
        <div className="mt-20"></div>
      </main>
    </div>
  );
}
