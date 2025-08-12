/** @type {import('next').NextConfig} */
const nextConfig = {
  // 🔧 Résolution de chemin explicite pour build Netlify
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': require('path').resolve(__dirname),
    };
    return config;
  },
  // 🛡️ Headers de sécurité HTTP obligatoires
  async headers() {
    const apiOrigins = [];
    // Autoriser explicitement les API d'origines définies via env
    if (process.env.NEXT_PUBLIC_IRIS_API_URL) {
      try {
        const u = new URL(process.env.NEXT_PUBLIC_IRIS_API_URL);
        apiOrigins.push(`${u.protocol}//${u.host}`);
      } catch {}
    }
    if (process.env.NEXT_PUBLIC_DOJO_API_URL) {
      try {
        const u = new URL(process.env.NEXT_PUBLIC_DOJO_API_URL);
        apiOrigins.push(`${u.protocol}//${u.host}`);
      } catch {}
    }
    const staticApiOrigins = [
      'https://phoenix-eco-monorepo-production.up.railway.app',
      'https://phoenix-aube-production.up.railway.app',
    ];
    const connectSrcExtras = Array.from(new Set([...apiOrigins, ...staticApiOrigins])).join(' ');
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
            // SECURITY: lock down CSP. Consider using nonces/hashes if inline styles/scripts are needed.
            value: [
              "default-src 'self'",
              "script-src 'self' https://js.stripe.com",
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' data: https:",
              "font-src 'self' data:",
              `connect-src 'self' https://*.supabase.co http://localhost:8000 https://api.stripe.com https://js.stripe.com ${connectSrcExtras}`.trim(),
              "frame-ancestors 'none'",
            ].join('; '),
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
