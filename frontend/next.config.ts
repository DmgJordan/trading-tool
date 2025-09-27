import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // Spécifier explicitement la racine du projet pour éviter les warnings de lockfiles multiples
  outputFileTracingRoot: '/Users/dmgjordan/Documents/dev/trading-tool/frontend',

  // Configuration pour optimiser les performances
  experimental: {
    optimizePackageImports: ['lucide-react', '@radix-ui/react-icons'],
  },
};

export default nextConfig;
