'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Menu, X, Zap } from 'lucide-react';
import GreenAIBadge from '@/components/green/GreenAIBadge';

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-slate-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-orange-500 rounded-lg flex items-center justify-center">
              <Zap className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold text-slate-900">Phoenix</span>
          </Link>

          {/* Navigation Desktop */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link href="/" className="text-slate-600 hover:text-slate-900 transition-colors">
              Accueil
            </Link>
            <Link href="/pricing" className="text-slate-600 hover:text-slate-900 transition-colors">
              Tarifs
            </Link>
            <Link
              href="/green-ai"
              className="text-slate-600 hover:text-slate-900 transition-colors"
            >
              Green AI
            </Link>
            <Link href="/about" className="text-slate-600 hover:text-slate-900 transition-colors">
              À propos
            </Link>
            <Link href="/contact" className="text-slate-600 hover:text-slate-900 transition-colors">
              Contact
            </Link>
          </nav>

          {/* Green AI Badge + CTA Desktop */}
          <div className="hidden md:flex items-center space-x-4">
            <GreenAIBadge variant="compact" />
            <Button asChild className="bg-orange-500 hover:bg-orange-600">
              <a
                href="https://phoenix-letters.streamlit.app/"
                target="_blank"
                rel="noopener noreferrer"
              >
                Commencer gratuitement
              </a>
            </Button>
          </div>

          {/* Menu Mobile */}
          <button className="md:hidden" onClick={() => setIsMenuOpen(!isMenuOpen)}>
            {isMenuOpen ? (
              <X className="h-6 w-6 text-slate-600" />
            ) : (
              <Menu className="h-6 w-6 text-slate-600" />
            )}
          </button>
        </div>

        {/* Menu Mobile */}
        {isMenuOpen && (
          <div className="md:hidden border-t border-slate-200 py-4">
            <nav className="flex flex-col space-y-4">
              <Link
                href="/"
                className="text-slate-600 hover:text-slate-900 transition-colors"
                onClick={() => setIsMenuOpen(false)}
              >
                Accueil
              </Link>
              <Link
                href="/pricing"
                className="text-slate-600 hover:text-slate-900 transition-colors"
                onClick={() => setIsMenuOpen(false)}
              >
                Tarifs
              </Link>
              <Link
                href="/green-ai"
                className="text-slate-600 hover:text-slate-900 transition-colors"
                onClick={() => setIsMenuOpen(false)}
              >
                Green AI
              </Link>
              <Link
                href="/about"
                className="text-slate-600 hover:text-slate-900 transition-colors"
                onClick={() => setIsMenuOpen(false)}
              >
                À propos
              </Link>
              <Link
                href="/contact"
                className="text-slate-600 hover:text-slate-900 transition-colors"
                onClick={() => setIsMenuOpen(false)}
              >
                Contact
              </Link>
              <div className="mt-4 space-y-3">
                <GreenAIBadge variant="compact" />
                <Button asChild className="bg-orange-500 hover:bg-orange-600 w-full">
                  <a
                    href="https://phoenix-letters.streamlit.app/"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Commencer gratuitement
                  </a>
                </Button>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
}
