import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { Providers } from '@/components/providers';
import { Toaster } from 'sonner';
import { Navigation } from '@/components/navigation';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Phoenix Rise & Dojo Mental',
  description: 'Mental traction ecosystem - Journal Kaizen, Zazen rituals, mood tracking',
  keywords: ['phoenix', 'rise', 'dojo', 'mental', 'kaizen', 'zazen', 'journal', 'mood'],
  authors: [{ name: 'Phoenix Tech Team' }],
  openGraph: {
    title: 'Phoenix Rise & Dojo Mental',
    description: 'Mental traction ecosystem for personal growth',
    type: 'website',
  },
  robots: {
    index: false, // Private app
    follow: false,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          <Navigation />
          {children}
          <Toaster 
            position="top-right"
            richColors
            closeButton
            theme="system"
          />
        </Providers>
      </body>
    </html>
  );
}