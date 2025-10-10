import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,

  // Skip type checking during dev for faster compilation
  typescript: {
    ignoreBuildErrors: true,
    // Completely skip type checking in dev mode
    tsconfigPath: './tsconfig.json',
  },

  // Disable ESLint during builds
  eslint: {
    ignoreDuringBuilds: true,
  },

  // Optimize compilation speed
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },

  // Enable experimental features for faster builds
  experimental: {
    optimizePackageImports: ['lucide-react', 'recharts'],
  },

  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/:path*',
      },
    ];
  },
};

export default nextConfig;