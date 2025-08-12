import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

const inter = Inter({ subsets: ['latin'] });

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://phoenixcreator.netlify.app';

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: 'Phoenix - Outils IA gratuits pour réussir votre reconversion professionnelle',
  description:
    "Transformez votre parcours atypique en votre plus grande force avec Phoenix, l'écosystème d'applications IA conçu par un reconverti, pour les reconvertis.",
  keywords: [
    'reconversion professionnelle',
    'IA',
    'intelligence artificielle',
    'lettre de motivation',
    'CV',
    'coaching carrière',
    'Phoenix',
    'transition professionnelle',
  ],
  authors: [{ name: 'Phoenix Ecosystem' }],
  creator: 'Phoenix Ecosystem',
  publisher: 'Phoenix Ecosystem',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'fr_FR',
    url: siteUrl,
    title: 'Phoenix Ecosystem - Outils IA pour votre reconversion professionnelle',
    description:
      "Transformez votre parcours atypique en votre plus grande force avec Phoenix, l'écosystème d'applications IA conçu par un reconverti, pour les reconvertis.",
    siteName: 'Phoenix Ecosystem',
    images: [
      {
        url: '/openart-image_594S3XHV_1753199070084_raw.jpg',
        width: 1200,
        height: 630,
        alt: 'Phoenix Ecosystem - Outils IA reconversion',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Phoenix Ecosystem - Outils IA pour votre reconversion professionnelle',
    description: 'Transformez votre parcours atypique en votre plus grande force avec Phoenix.',
    images: ['/openart-image_594S3XHV_1753199070084_raw.jpg'],
    creator: '@phoenix_ecosystem',
  },
  alternates: {
    canonical: 'https://phoenix-ecosystem.com',
    languages: {
      'fr-FR': 'https://phoenix-ecosystem.com',
    },
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body className={`${inter.className} antialiased`}>
        <Header />
        <main className="min-h-screen">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
