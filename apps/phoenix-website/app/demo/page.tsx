import { Sparkles, ArrowRight, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import Link from 'next/link';

export default function DemoPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 py-16">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Démonstration Phoenix</h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Découvrez la puissance de Phoenix avant de vous abonner. Testez nos outils gratuitement
            et voyez la différence !
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {/* Phoenix Letters Demo */}
          <Card className="border-2 border-orange-200 bg-gradient-to-br from-orange-50 to-red-50">
            <CardHeader>
              <div className="w-12 h-12 bg-orange-500 rounded-lg flex items-center justify-center mb-4">
                <span className="text-white font-bold text-xl">✍️</span>
              </div>
              <CardTitle className="text-orange-800">Phoenix Letters</CardTitle>
              <p className="text-orange-700">
                Générez une lettre de motivation personnalisée en 2 minutes
              </p>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 mb-6">
                <p className="text-sm text-orange-700">✓ Analyse automatique du poste</p>
                <p className="text-sm text-orange-700">✓ Valorisation de votre parcours</p>
                <p className="text-sm text-orange-700">✓ Export PDF professionnel</p>
              </div>

              <div className="space-y-2">
                <a
                  href="https://phoenix-letters.streamlit.app/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block"
                >
                  <Button className="w-full bg-orange-500 hover:bg-orange-600">
                    Essayer Maintenant
                    <ExternalLink className="ml-2 h-4 w-4" />
                  </Button>
                </a>
                <p className="text-xs text-gray-500 text-center">
                  Version gratuite limitée • Premium illimité
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Phoenix CV Demo */}
          <Card className="border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50">
            <CardHeader>
              <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center mb-4">
                <span className="text-white font-bold text-xl">🔍</span>
              </div>
              <CardTitle className="text-blue-800">Phoenix CV</CardTitle>
              <p className="text-blue-700">Créez un CV optimisé ATS en quelques clics</p>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 mb-6">
                <p className="text-sm text-blue-700">✓ Templates professionnels</p>
                <p className="text-sm text-blue-700">✓ Optimisation mots-clés</p>
                <p className="text-sm text-blue-700">✓ Score de compatibilité</p>
              </div>

              <div className="space-y-2">
                <a
                  href="https://phoenix-cv.streamlit.app/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block"
                >
                  <Button className="w-full bg-blue-500 hover:bg-blue-600">
                    Essayer Maintenant
                    <ExternalLink className="ml-2 h-4 w-4" />
                  </Button>
                </a>
                <p className="text-xs text-gray-500 text-center">
                  Version gratuite limitée • Premium illimité
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Phoenix Rise Demo */}
          <Card className="border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-pink-50">
            <CardHeader>
              <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center mb-4">
                <span className="text-white font-bold text-xl">🎯</span>
              </div>
              <CardTitle className="text-purple-800">Phoenix Rise</CardTitle>
              <p className="text-purple-700">Votre coach carrière IA personnel</p>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 mb-6">
                <p className="text-sm text-purple-700">✓ Préparation d'entretiens</p>
                <p className="text-sm text-purple-700">✓ Journal de motivation</p>
                <p className="text-sm text-purple-700">✓ Suivi de progression</p>
              </div>

              <div className="space-y-2">
                <a
                  href="https://phoenix-rise.vercel.app/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block"
                >
                  <Button className="w-full bg-purple-500 hover:bg-purple-600">
                    Découvrir la Démo
                    <ExternalLink className="ml-2 h-4 w-4" />
                  </Button>
                </a>
                <p className="text-xs text-gray-500 text-center">Démo interactive disponible</p>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="text-center mt-12">
          <div className="bg-white rounded-2xl shadow-lg p-8 max-w-2xl mx-auto">
            <Sparkles className="w-12 h-12 text-orange-500 mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Prêt pour la version Premium ?
            </h3>
            <p className="text-gray-600 mb-6">
              Débloquez toutes les fonctionnalités et créez autant de contenus que vous voulez
            </p>
            <Link href="/pricing">
              <Button
                size="lg"
                className="bg-gradient-to-r from-orange-500 to-purple-500 hover:from-orange-600 hover:to-purple-600"
              >
                Voir les Tarifs Premium
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
