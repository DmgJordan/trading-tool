'use client';

import { useState } from 'react';

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <nav className="bg-white shadow-sm border-b-2 border-black">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        <div className="flex justify-between items-center h-20">
          {/* Logo */}
          <div className="flex-shrink-0">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-black rounded-full flex items-center justify-center mr-4">
                <span className="text-white font-bold text-lg">T</span>
              </div>
              <span className="text-2xl font-bold text-black">
                Trading Tool
              </span>
            </div>
          </div>

          {/* Menu desktop */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-6">
              <span className="bg-black text-white px-4 py-3 rounded-lg text-sm font-semibold cursor-default">
                Configuration
              </span>
              <span className="text-gray-500 px-4 py-3 rounded-lg text-sm font-medium cursor-not-allowed">
                Dashboard
              </span>
              <span className="text-gray-500 px-4 py-3 rounded-lg text-sm font-medium cursor-not-allowed">
                Trading
              </span>
              <span className="text-gray-500 px-4 py-3 rounded-lg text-sm font-medium cursor-not-allowed">
                Historique
              </span>
            </div>
          </div>

          {/* Bouton menu mobile */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-black hover:text-gray-600 focus:outline-none p-2"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                {isMenuOpen ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Menu mobile */}
      {isMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 bg-white border-t-2 border-black">
            <span className="bg-black text-white block px-3 py-2 rounded-md text-base font-medium cursor-default">
              Configuration
            </span>
            <span className="text-gray-500 block px-3 py-2 rounded-md text-base font-medium cursor-not-allowed">
              Dashboard
            </span>
            <span className="text-gray-500 block px-3 py-2 rounded-md text-base font-medium cursor-not-allowed">
              Trading
            </span>
            <span className="text-gray-500 block px-3 py-2 rounded-md text-base font-medium cursor-not-allowed">
              Historique
            </span>
          </div>
        </div>
      )}
    </nav>
  );
}
