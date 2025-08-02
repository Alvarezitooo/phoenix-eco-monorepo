/** @type {import('next').NextConfig} */
const nextConfig = {
  // 🛡️ Headers de sécurité HTTP obligatoires
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Content-Security-Policy',
            value:
              "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self';",
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
    ];
  },

  // ✅ Réactivation ESLint en build (sécurité)
  eslint: {
    ignoreDuringBuilds: false,
  },

  // 🖼️ Configuration images optimisées
  images: {
    unoptimized: false,
    domains: ['phoenix-ecosystem.com'],
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 60,
  },

  // 🔒 Mode strict
  reactStrictMode: true,

  // 🛡️ SWC sécurisé
  swcMinify: true,

  // 🔍 Source maps désactivés en production
  productionBrowserSourceMaps: false,
};

module.exports = nextConfig;
