import Link from 'next/link';
import { Zap, Heart } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-white">
      <div className="container mx-auto px-4 py-12">
        <div className="grid md:grid-cols-4 gap-8">
          {/* Logo & Description */}
          <div className="md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-orange-500 rounded-lg flex items-center justify-center">
                <Zap className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold">Phoenix Ecosystem</span>
            </div>
            <p className="text-slate-400 mb-4 max-w-md">
              Outils IA éthiques pour transformer votre reconversion professionnelle en réussite.
              Créé par un reconverti, pour les reconvertis.
            </p>
            <div className="flex items-center text-sm text-slate-400">
              <span>Fait avec</span>
              <Heart className="h-4 w-4 mx-1 text-red-500" />
              <span>par Matthieu</span>
            </div>
          </div>

          {/* Navigation */}
          <div>
            <h3 className="font-semibold mb-4">Navigation</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/" className="text-slate-400 hover:text-white transition-colors">
                  Accueil
                </Link>
              </li>
              <li>
                <Link href="/pricing" className="text-slate-400 hover:text-white transition-colors">
                  Tarifs
                </Link>
              </li>
              <li>
                <Link href="/about" className="text-slate-400 hover:text-white transition-colors">
                  À propos
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-slate-400 hover:text-white transition-colors">
                  Contact
                </Link>
              </li>
            </ul>
          </div>

          {/* Applications */}
          <div>
            <h3 className="font-semibold mb-4">Applications</h3>
            <ul className="space-y-2">
              <li>
                <a
                  href="https://phoenix-letters.streamlit.app/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-slate-400 hover:text-white transition-colors"
                >
                  Phoenix Letters
                </a>
              </li>
              <li>
                <span className="text-slate-500">Phoenix CV (Q3 2025)</span>
              </li>
              <li>
                <span className="text-slate-500">Phoenix Rise (Q4 2025)</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-800 mt-12 pt-8 text-center text-slate-400">
          <p>&copy; 2025 Phoenix Ecosystem. Tous droits réservés.</p>
        </div>
      </div>
    </footer>
  );
}
