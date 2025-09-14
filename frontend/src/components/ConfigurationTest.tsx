'use client';

import { useState } from 'react';

interface TestResult {
  backend: 'success' | 'error' | 'testing' | null;
  database: 'success' | 'error' | 'testing' | null;
  message: string;
}

export default function ConfigurationTest() {
  const [testResult, setTestResult] = useState<TestResult>({
    backend: null,
    database: null,
    message: ''
  });

  const testBackendConnection = async () => {
    setTestResult(prev => ({ ...prev, backend: 'testing', message: 'Test de connexion au backend...' }));

    try {
      const response = await fetch('http://localhost:8000/health', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setTestResult(prev => ({
          ...prev,
          backend: 'success',
          message: 'Connexion backend réussie !'
        }));
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      setTestResult(prev => ({
        ...prev,
        backend: 'error',
        message: `Erreur backend: ${error instanceof Error ? error.message : 'Connexion échouée'}`
      }));
    }
  };

  const testDatabaseConnection = async () => {
    setTestResult(prev => ({ ...prev, database: 'testing', message: 'Test de connexion à la base de données...' }));

    try {
      const response = await fetch('http://localhost:8000/db-health', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setTestResult(prev => ({
          ...prev,
          database: 'success',
          message: 'Connexion base de données réussie !'
        }));
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      setTestResult(prev => ({
        ...prev,
        database: 'error',
        message: `Erreur base de données: ${error instanceof Error ? error.message : 'Connexion échouée'}`
      }));
    }
  };

  const getStatusIcon = (status: 'success' | 'error' | 'testing' | null) => {
    switch (status) {
      case 'success':
        return <span className="text-black text-xl font-bold">✓</span>;
      case 'error':
        return <span className="text-black text-xl font-bold">✗</span>;
      case 'testing':
        return <span className="text-black text-xl animate-spin">⟳</span>;
      default:
        return <span className="text-gray-400 text-xl">○</span>;
    }
  };

  const getStatusColor = (status: 'success' | 'error' | 'testing' | null) => {
    switch (status) {
      case 'success':
        return 'border-black bg-gray-100';
      case 'error':
        return 'border-black bg-gray-200';
      case 'testing':
        return 'border-black bg-gray-50';
      default:
        return 'border-gray-300 bg-white';
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border-2 border-black p-8 sm:p-10">
      <div className="mb-10 text-center">
        <h2 className="text-3xl font-bold text-black mb-3">
          Test de Configuration
        </h2>
        <p className="text-gray-600">
          Vérifiez que tous les services sont opérationnels
        </p>
      </div>

      <div className="space-y-6">
        {/* Test Backend */}
        <div className={`p-6 rounded-xl border-2 transition-all duration-300 ${getStatusColor(testResult.backend)}`}>
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center space-x-4">
              <div className="flex-shrink-0">
                {getStatusIcon(testResult.backend)}
              </div>
              <div>
                <h3 className="font-semibold text-black text-lg">Connexion Backend</h3>
                <p className="text-gray-700 mt-1">FastAPI sur port 8000</p>
              </div>
            </div>
            <button
              onClick={testBackendConnection}
              disabled={testResult.backend === 'testing'}
              className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium shadow-sm hover:shadow-md"
            >
              {testResult.backend === 'testing' ? 'Test...' : 'Tester'}
            </button>
          </div>
        </div>

        {/* Test Database */}
        <div className={`p-6 rounded-xl border-2 transition-all duration-300 ${getStatusColor(testResult.database)}`}>
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center space-x-4">
              <div className="flex-shrink-0">
                {getStatusIcon(testResult.database)}
              </div>
              <div>
                <h3 className="font-semibold text-black text-lg">Connexion Base de Données</h3>
                <p className="text-gray-700 mt-1">PostgreSQL</p>
              </div>
            </div>
            <button
              onClick={testDatabaseConnection}
              disabled={testResult.database === 'testing'}
              className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium shadow-sm hover:shadow-md"
            >
              {testResult.database === 'testing' ? 'Test...' : 'Tester'}
            </button>
          </div>
        </div>
      </div>

      {/* Message de statut */}
      {testResult.message && (
        <div className="mt-8 p-5 bg-gray-100 rounded-xl border-2 border-gray-300">
          <p className="text-black text-center font-medium">{testResult.message}</p>
        </div>
      )}

      {/* Test global */}
      <div className="mt-10 pt-8 border-t-2 border-gray-300">
        <button
          onClick={() => {
            testBackendConnection();
            setTimeout(() => testDatabaseConnection(), 1000);
          }}
          disabled={testResult.backend === 'testing' || testResult.database === 'testing'}
          className="w-full px-8 py-4 bg-black text-white rounded-xl hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-semibold text-lg shadow-md hover:shadow-lg"
        >
          Tester Toute la Configuration
        </button>
      </div>
    </div>
  );
}
