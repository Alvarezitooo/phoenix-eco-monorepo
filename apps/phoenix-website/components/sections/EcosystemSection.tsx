import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '../ui/badge';
import { ArrowDown, ArrowRight, CheckCircle, Shield, Users, Zap } from 'lucide-react';
import Link from 'next/link';

export default function EcosystemSection() {
  // Force redeploy - Phoenix Aube + Trajectory Builder IA
  return (
    <section className="py-20 bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Votre Trajectory Builder IA</h2>
          <p className="text-xl text-gray-600 max-w-4xl mx-auto mb-8">
            Phoenix ne se contente pas de créer des documents. Il construit votre trajectoire
            complète de reconversion, de l'exploration de vos aspirations jusqu'à la concrétisation
            de votre nouveau métier.
          </p>
          <div className="bg-gradient-to-r from-orange-100 to-purple-100 rounded-xl p-6 max-w-3xl mx-auto">
            <p className="text-lg font-semibold text-gray-800">
              🎯{' '}
              <strong>
                Le seul écosystème qui connecte votre passé, votre présent et votre futur
              </strong>{' '}
              pour créer une trajectoire de reconversion cohérente et puissante.
            </p>
          </div>
        </div>

        {/* Applications Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-20">
          {/* Phoenix CV */}
          <Card className="relative overflow-hidden border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50">
            <CardHeader>
              <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center mb-4">
                <span className="text-white font-bold text-xl">🔍</span>
              </div>
              <CardTitle className="text-blue-800">Phoenix CV</CardTitle>
              <CardDescription className="text-blue-700">
                Créez des CV percutants et des accroches hyper-personnalisées qui passent les
                filtres ATS et captent l'attention des recruteurs.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 mb-6">
                <li className="flex items-center text-sm text-blue-700">
                  <CheckCircle className="w-4 h-4 mr-2 text-blue-500" />
                  Optimisation ATS automatique
                </li>
                <li className="flex items-center text-sm text-blue-700">
                  <CheckCircle className="w-4 h-4 mr-2 text-blue-500" />
                  Templates modernes et professionnels
                </li>
                <li className="flex items-center text-sm text-blue-700">
                  <CheckCircle className="w-4 h-4 mr-2 text-blue-500" />
                  Accroches personnalisées par poste
                </li>
                <li className="flex items-center text-sm text-blue-700">
                  <CheckCircle className="w-4 h-4 mr-2 text-blue-500" />
                  Analyse de compatibilité offre/profil
                </li>
              </ul>
              <Link href="https://phoenix-cv.streamlit.app/" target="_blank">
                <Button className="w-full bg-blue-500 hover:bg-blue-600">Tester Phoenix CV</Button>
              </Link>
            </CardContent>
          </Card>

          {/* Phoenix Letters */}
          <Card className="relative overflow-hidden border-2 border-orange-200 bg-gradient-to-br from-orange-50 to-red-50">
            <CardHeader>
              <div className="w-12 h-12 bg-orange-500 rounded-lg flex items-center justify-center mb-4">
                <span className="text-white font-bold text-xl">✍️</span>
              </div>
              <CardTitle className="text-orange-800">Phoenix Letters</CardTitle>
              <CardDescription className="text-orange-700">
                Générez des lettres de motivation uniques qui transforment votre expérience passée
                en un atout majeur pour votre futur métier.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 mb-6">
                <li className="flex items-center text-sm text-orange-700">
                  <CheckCircle className="w-4 h-4 mr-2 text-orange-500" />
                  Templates personnalisés par secteur
                </li>
                <li className="flex items-center text-sm text-orange-700">
                  <CheckCircle className="w-4 h-4 mr-2 text-orange-500" />
                  IA qui valorise votre parcours atypique
                </li>
                <li className="flex items-center text-sm text-orange-700">
                  <CheckCircle className="w-4 h-4 mr-2 text-orange-500" />
                  Export professionnel PDF/DOCX
                </li>
                <li className="flex items-center text-sm text-orange-700">
                  <CheckCircle className="w-4 h-4 mr-2 text-orange-500" />
                  Coaching intégré
                </li>
              </ul>
              <Link href="https://phoenix-letters.streamlit.app/" target="_blank">
                <Button className="w-full bg-orange-500 hover:bg-orange-600">
                  Tester Phoenix Letters
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Phoenix Aube */}
          <Card className="relative overflow-hidden border-2 border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50">
            <CardHeader>
              <div className="w-12 h-12 bg-gradient-to-r from-amber-500 to-orange-500 rounded-lg flex items-center justify-center mb-4">
                <span className="text-white font-bold text-xl">🌅</span>
              </div>
              <CardTitle className="text-amber-800">Phoenix Aube</CardTitle>
              <CardDescription className="text-amber-700">
                Explorez vos aspirations profondes et découvrez les métiers qui vous correspondent
                vraiment. L'outil qui révèle votre potentiel caché.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 mb-6">
                <li className="flex items-center text-sm text-amber-700">
                  <CheckCircle className="w-4 h-4 mr-2 text-amber-500" />
                  Tests psychométriques avancés
                </li>
                <li className="flex items-center text-sm text-amber-700">
                  <CheckCircle className="w-4 h-4 mr-2 text-amber-500" />
                  Matching valeurs/compétences
                </li>
                <li className="flex items-center text-sm text-amber-700">
                  <CheckCircle className="w-4 h-4 mr-2 text-amber-500" />
                  Score résistance IA des métiers
                </li>
                <li className="flex items-center text-sm text-amber-700">
                  <CheckCircle className="w-4 h-4 mr-2 text-amber-500" />
                  Plan de montée en compétences
                </li>
              </ul>
              <Button
                className="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600"
                disabled
              >
                Bientôt disponible
              </Button>
            </CardContent>
          </Card>

          {/* Phoenix Rise */}
          <Card className="relative overflow-hidden border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-pink-50">
            <CardHeader>
              <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center mb-4">
                <span className="text-white font-bold text-xl">🎯</span>
              </div>
              <CardTitle className="text-purple-800">Phoenix Rise</CardTitle>
              <CardDescription className="text-purple-700">
                Votre coach de carrière IA et journal de bord pour préparer vos entretiens, suivre
                votre motivation et piloter votre reconversion au quotidien.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 mb-6">
                <li className="flex items-center text-sm text-purple-700">
                  <CheckCircle className="w-4 h-4 mr-2 text-purple-500" />
                  Préparation d'entretiens personnalisée
                </li>
                <li className="flex items-center text-sm text-purple-700">
                  <CheckCircle className="w-4 h-4 mr-2 text-purple-500" />
                  Suivi de motivation et objectifs
                </li>
                <li className="flex items-center text-sm text-purple-700">
                  <CheckCircle className="w-4 h-4 mr-2 text-purple-500" />
                  Conseils de carrière adaptatifs
                </li>
                <li className="flex items-center text-sm text-purple-700">
                  <CheckCircle className="w-4 h-4 mr-2 text-purple-500" />
                  Tableau de bord de progression
                </li>
              </ul>
              <Link href="https://phoenix-rise.vercel.app/" target="_blank">
                <Button className="w-full bg-purple-500 hover:bg-purple-600">
                  Tester Phoenix Rise
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* Data Flywheel Section */}
        <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12 border-2 border-gray-100">
          <div className="text-center mb-12">
            <Badge className="mb-4 px-4 py-2 bg-gradient-to-r from-orange-500 to-purple-500 text-white">
              <Zap className="w-4 h-4 mr-2" />
              Innovation Phoenix
            </Badge>
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              Le Premier Trajectory Builder IA pour Reconversion
            </h3>
            <p className="text-xl text-gray-600 max-w-4xl mx-auto">
              Phoenix n'est pas juste une collection d'outils séparés. C'est le premier{' '}
              <strong>Trajectory Builder IA</strong> qui connecte intelligemment exploration métier,
              candidature et accompagnement pour construire votre parcours de reconversion idéal.
            </p>
          </div>

          {/* Trajectory Builder Visualization */}
          <div className="mb-12">
            <div className="flex flex-col lg:flex-row items-center justify-center space-y-8 lg:space-y-0 lg:space-x-4">
              {/* Phoenix Aube */}
              <div className="flex flex-col items-center text-center">
                <div className="w-24 h-24 bg-gradient-to-br from-amber-500 to-orange-500 rounded-full flex items-center justify-center mb-4 shadow-lg">
                  <span className="text-white font-bold text-2xl">🌅</span>
                </div>
                <h4 className="font-bold text-amber-800 mb-2">Phoenix Aube</h4>
                <p className="text-sm text-gray-600 max-w-xs">
                  explore vos <strong>aspirations profondes</strong>
                </p>
                <p className="text-xs text-gray-500 mt-1 italic">
                  Valeurs, compétences cachées, métiers compatibles
                </p>
              </div>

              {/* Arrow */}
              <div className="flex flex-col items-center lg:hidden">
                <ArrowDown className="w-8 h-8 text-gray-400" />
                <span className="text-sm font-semibold text-gray-600 mt-2">
                  Révèle votre potentiel
                </span>
              </div>
              <div className="hidden lg:flex flex-col items-center">
                <ArrowRight className="w-8 h-8 text-gray-400" />
                <span className="text-sm font-semibold text-gray-600 mt-2">
                  Révèle votre potentiel
                </span>
              </div>

              {/* Phoenix CV */}
              <div className="flex flex-col items-center text-center">
                <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center mb-4 shadow-lg">
                  <span className="text-white font-bold text-2xl">🔍</span>
                </div>
                <h4 className="font-bold text-blue-800 mb-2">Phoenix CV</h4>
                <p className="text-sm text-gray-600 max-w-xs">
                  structure votre <strong>parcours professionnel</strong>
                </p>
                <p className="text-xs text-gray-500 mt-1 italic">
                  Expériences, compétences, réalisations valorisées
                </p>
              </div>

              {/* Arrow down */}
              <div className="flex flex-col items-center lg:hidden">
                <ArrowDown className="w-8 h-8 text-gray-400" />
                <span className="text-sm font-semibold text-gray-600 mt-2">
                  Enrichit automatiquement
                </span>
              </div>
              <div className="hidden lg:flex flex-col items-center">
                <ArrowRight className="w-8 h-8 text-gray-400" />
                <span className="text-sm font-semibold text-gray-600 mt-2">
                  Enrichit automatiquement
                </span>
              </div>

              {/* Arrow */}
              <div className="flex flex-col items-center lg:hidden">
                <ArrowDown className="w-8 h-8 text-gray-400" />
                <span className="text-sm font-semibold text-gray-600 mt-2">
                  Construit votre story
                </span>
              </div>
              <div className="hidden lg:flex flex-col items-center">
                <ArrowRight className="w-8 h-8 text-gray-400" />
                <span className="text-sm font-semibold text-gray-600 mt-2">
                  Construit votre story
                </span>
              </div>

              {/* Phoenix Letters */}
              <div className="flex flex-col items-center text-center">
                <div className="w-24 h-24 bg-gradient-to-br from-orange-500 to-red-500 rounded-full flex items-center justify-center mb-4 shadow-lg">
                  <span className="text-white font-bold text-2xl">✍️</span>
                </div>
                <h4 className="font-bold text-orange-800 mb-2">Phoenix Letters</h4>
                <p className="text-sm text-gray-600 max-w-xs">
                  concrétise vos <strong>candidatures gagnantes</strong>
                </p>
                <p className="text-xs text-gray-500 mt-1 italic">
                  Lettres personnalisées, storytelling puissant
                </p>
              </div>

              {/* Arrow */}
              <div className="flex flex-col items-center lg:hidden">
                <ArrowDown className="w-8 h-8 text-gray-400" />
                <span className="text-sm font-semibold text-gray-600 mt-2">
                  Accompagne au quotidien
                </span>
              </div>
              <div className="hidden lg:flex flex-col items-center">
                <ArrowRight className="w-8 h-8 text-gray-400" />
                <span className="text-sm font-semibold text-gray-600 mt-2">
                  Accompagne au quotidien
                </span>
              </div>

              {/* Phoenix Rise */}
              <div className="flex flex-col items-center text-center">
                <div className="w-24 h-24 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center mb-4 shadow-lg">
                  <span className="text-white font-bold text-2xl">🎯</span>
                </div>
                <h4 className="font-bold text-purple-800 mb-2">Phoenix Rise</h4>
                <p className="text-sm text-gray-600 max-w-xs">
                  pilote votre <strong>transformation complète</strong>
                </p>
                <p className="text-xs text-gray-500 mt-1 italic">
                  Coach IA, préparation entretiens, suivi motivation
                </p>
              </div>
            </div>
          </div>

          {/* Results Comparison */}
          <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl p-8 mb-8">
            <h4 className="text-2xl font-bold text-center text-gray-900 mb-8">
              Le Résultat : Votre Trajectory Personnalisée
            </h4>

            <div className="grid md:grid-cols-2 gap-8">
              <div className="text-center">
                <div className="bg-gray-100 rounded-lg p-6 mb-4">
                  <h5 className="font-bold text-gray-800 mb-2">Approche classique</h5>
                  <p className="text-gray-700 text-sm mb-4">Outils séparés + démarche fragmentée</p>
                  <div className="text-2xl font-bold text-gray-600">🔧</div>
                  <p className="text-gray-600 text-sm">Vous naviguez seul(e)</p>
                </div>
              </div>

              <div className="text-center">
                <div className="bg-gradient-to-r from-amber-100 to-purple-100 rounded-lg p-6 mb-4">
                  <h5 className="font-bold text-amber-800 mb-2">Trajectory Builder Phoenix</h5>
                  <p className="text-amber-700 text-sm mb-4">
                    Parcours cohérent + IA qui apprend de vous
                  </p>
                  <div className="text-2xl font-bold text-amber-600">🚀</div>
                  <p className="text-amber-600 text-sm">Votre trajectoire sur-mesure</p>
                </div>
              </div>
            </div>

            <div className="text-center mt-8">
              <p className="text-lg text-gray-700 mb-2">
                <em>La différence ? Phoenix ne se contente pas de créer des documents.</em>
              </p>
              <p className="text-xl font-bold text-gray-900">
                Phoenix construit votre trajectoire de reconversion complète.
              </p>
            </div>
          </div>

          {/* Security & Transparency */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="flex items-center space-x-3">
              <Shield className="w-8 h-8 text-green-500" />
              <div>
                <h5 className="font-bold text-gray-900">RGPD Compliant</h5>
                <p className="text-sm text-gray-600">Vos données sont anonymisées et protégées</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Users className="w-8 h-8 text-blue-500" />
              <div>
                <h5 className="font-bold text-gray-900">Contrôle Total</h5>
                <p className="text-sm text-gray-600">
                  Exportez ou supprimez vos données en un clic
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-8 h-8 text-purple-500" />
              <div>
                <h5 className="font-bold text-gray-900">Éthique d'Abord</h5>
                <p className="text-sm text-gray-600">
                  Nous utilisons vos données pour VOUS servir, pas pour vous vendre
                </p>
              </div>
            </div>
          </div>

          {/* Call to Action */}
          <div className="text-center">
            <h4 className="text-2xl font-bold text-gray-900 mb-4">
              Construisez Votre Trajectory Dès Maintenant
            </h4>
            <p className="text-lg text-gray-600 mb-6">
              Commencez gratuitement avec Phoenix Letters. Chaque étape de votre parcours enrichit
              votre trajectory personnalisée.
            </p>
            <Link href="/demo">
              <Button
                size="lg"
                className="bg-gradient-to-r from-amber-500 to-purple-500 hover:from-amber-600 hover:to-purple-600 text-white px-8 py-3 text-lg"
              >
                Démarrer ma Trajectory →
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
