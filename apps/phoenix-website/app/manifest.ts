import { MetadataRoute } from 'next';

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://phoenixcreator.netlify.app';

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Phoenix Ecosystem - Outils IA Reconversion',
    short_name: 'Phoenix',
    description:
      "Transformez votre parcours atypique en votre plus grande force avec Phoenix, l'écosystème d'applications IA conçu par un reconverti, pour les reconvertis.",
    start_url: '/',
    display: 'standalone',
    background_color: '#ffffff',
    theme_color: '#f97316',
    orientation: 'portrait-primary',
    categories: ['business', 'productivity', 'education'],
    lang: 'fr',
    icons: [
      {
        src: '/openart-image_594S3XHV_1753199070084_raw.jpg',
        sizes: '192x192',
        type: 'image/jpeg',
        purpose: 'maskable',
      },
      {
        src: '/openart-image_594S3XHV_1753199070084_raw.jpg',
        sizes: '512x512',
        type: 'image/jpeg',
        purpose: 'any',
      },
    ],
    screenshots: [
      {
        src: '/openart-image_594S3XHV_1753199070084_raw.jpg',
        sizes: '1280x720',
        type: 'image/jpeg',
      },
    ],
  };
}
