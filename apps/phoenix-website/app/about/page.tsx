import { Heart, Shield, Eye, Zap } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      <div className="container mx-auto px-4 py-16">
        {/* Mon Histoire */}
        <section className="mb-20">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6">
                Phoenix : Né de MA reconversion,
                <span className="text-purple-700"> construit AVEC vous</span>
              </h1>
              <div className="prose prose-lg text-slate-600 space-y-4">
                <p>
                  Phoenix est né de MA reconversion aide-soignant → tech. Je construis les outils
                  que j'aurais voulu avoir. Vous êtes mes premiers beta-testeurs, aidez-moi à les
                  perfectionner ensemble.
                </p>
              </div>
            </div>
            <div className="flex justify-center">
              <div className="relative">
                <div className="w-80 h-80 bg-gradient-to-br from-orange-500 to-orange-600 rounded-full flex items-center justify-center">
                  <div className="w-72 h-72 bg-white rounded-full flex items-center justify-center">
                    <div className="text-center">
                      <div className="w-32 h-32 bg-slate-200 rounded-full mx-auto mb-4 flex items-center justify-center">
                        <span className="text-4xl">👨‍💻</span>
                      </div>
                      <h3 className="text-xl font-bold text-slate-900">Matthieu</h3>
                      <p className="text-slate-600">Créateur de Phoenix</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Notre Mission & Vision (Authentique) */}
        <section className="mb-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
              Notre Mission & Vision
            </h2>
            <div className="max-w-4xl mx-auto">
              <p className="text-xl text-slate-600 leading-relaxed">
                Notre mission est simple : vous accompagner, vous, les reconvertis, avec des outils
                IA éthiques et accessibles.
                <br />
                Notre vision est de construire, ensemble, la référence de la reconversion
                professionnelle.
              </p>
            </div>
          </div>
          <div className="bg-purple-50 rounded-2xl p-8 border border-purple-100">
            <div className="text-center">
              <h3 className="text-2xl font-bold text-slate-900 mb-4">
                🎯 Objectif 2025 : 1000 Reconversions Ensemble !
              </h3>
              <p className="text-lg text-slate-700 max-w-3xl mx-auto">
                Chaque succès est le nôtre. Rejoignez l'aventure et aidons-nous mutuellement à
                atteindre nos objectifs.
              </p>
            </div>
          </div>
        </section>

        {/* Nos Valeurs */}
        <section>
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">Nos Valeurs</h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Ces quatre piliers guident chaque décision et façonnent l'expérience Phoenix.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <Card className="text-center p-6 hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Shield className="h-8 w-8 text-purple-500" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">Éthique</h3>
                <p className="text-slate-600">
                  IA transparente, données respectées, modèle économique équitable.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center p-6 hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Heart className="h-8 w-8 text-purple-500" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">Bienveillance</h3>
                <p className="text-slate-600">
                  Accompagnement humain, sans jugement, adapté à chaque parcours.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center p-6 hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Eye className="h-8 w-8 text-purple-500" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">Transparence</h3>
                <p className="text-slate-600">
                  Tarifs clairs, processus ouverts, communication directe.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center p-6 hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Zap className="h-8 w-8 text-purple-500" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">Efficacité</h3>
                <p className="text-slate-600">
                  Outils performants qui donnent des résultats concrets rapidement.
                </p>
              </CardContent>
            </Card>
          </div>
        </section>
      </div>
    </div>
  );
}
