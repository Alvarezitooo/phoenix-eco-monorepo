import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '../ui/badge';
import { ArrowDown, ArrowRight, CheckCircle, Shield, Users, Zap } from 'lucide-react';
import Link from 'next/link';

export default function EcosystemSection() {
  return (
    <section className="py-20 bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Notre Écosystème</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Trois applications complémentaires pour vous accompagner à chaque étape de votre
            reconversion professionnelle.
          </p>
        </div>

        {/* Applications Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-20">
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
              <Link href="https://phoenix-creator.netlify.app/" target="_blank">
                <Button className="w-full bg-blue-500 hover:bg-blue-600">Tester la béta</Button>
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
                  Commencer à écrire
                </Button>
              </Link>
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
              <Button className="w-full bg-purple-500 hover:bg-purple-600" disabled>
                Bientôt disponible
              </Button>
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
              Plus Vous Utilisez, Plus C'est Puissant
            </h3>
            <p className="text-xl text-gray-600 max-w-4xl mx-auto">
              Phoenix n'est pas juste une collection d'outils séparés. C'est un{' '}
              <strong>écosystème intelligent</strong> où chaque application nourrit les autres,
              créant un cercle vertueux qui devient plus performant à chaque utilisation.
            </p>
          </div>

          {/* Flywheel Visualization */}
          <div className="mb-12">
            <div className="flex flex-col lg:flex-row items-center justify-center space-y-8 lg:space-y-0 lg:space-x-8">
              {/* Phoenix CV */}
              <div className="flex flex-col items-center text-center">
                <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center mb-4 shadow-lg">
                  <span className="text-white font-bold text-2xl">🔍</span>
                </div>
                <h4 className="font-bold text-blue-800 mb-2">Phoenix CV</h4>
                <p className="text-sm text-gray-600 max-w-xs">
                  capture votre <strong>passé professionnel</strong>
                </p>
                <p className="text-xs text-gray-500 mt-1 italic">
                  Compétences, expériences, réalisations concrètes
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

              {/* Phoenix Letters */}
              <div className="flex flex-col items-center text-center">
                <div className="w-24 h-24 bg-gradient-to-br from-orange-500 to-red-500 rounded-full flex items-center justify-center mb-4 shadow-lg">
                  <span className="text-white font-bold text-2xl">✍️</span>
                </div>
                <h4 className="font-bold text-orange-800 mb-2">Phoenix Letters</h4>
                <p className="text-sm text-gray-600 max-w-xs">
                  révèle vos <strong>aspirations futures</strong>
                </p>
                <p className="text-xs text-gray-500 mt-1 italic">
                  Postes visés, motivations, entreprises cibles
                </p>
              </div>

              {/* Arrow down */}
              <div className="flex flex-col items-center lg:hidden">
                <ArrowDown className="w-8 h-8 text-gray-400" />
                <span className="text-sm font-semibold text-gray-600 mt-2">
                  Personnalise en continu
                </span>
              </div>
              <div className="hidden lg:flex flex-col items-center">
                <ArrowRight className="w-8 h-8 text-gray-400" />
                <span className="text-sm font-semibold text-gray-600 mt-2">
                  Personnalise en continu
                </span>
              </div>

              {/* Phoenix Rise */}
              <div className="flex flex-col items-center text-center">
                <div className="w-24 h-24 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center mb-4 shadow-lg">
                  <span className="text-white font-bold text-2xl">🎯</span>
                </div>
                <h4 className="font-bold text-purple-800 mb-2">Phoenix Rise</h4>
                <p className="text-sm text-gray-600 max-w-xs">
                  comprend votre <strong>contexte émotionnel</strong>
                </p>
                <p className="text-xs text-gray-500 mt-1 italic">
                  Valeurs, peurs, progression, objectifs personnels
                </p>
              </div>
            </div>
          </div>

          {/* Results Comparison */}
          <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl p-8 mb-8">
            <h4 className="text-2xl font-bold text-center text-gray-900 mb-8">
              Le Résultat : Une IA Qui Vous Connaît Vraiment
            </h4>

            <div className="grid md:grid-cols-2 gap-8">
              <div className="text-center">
                <div className="bg-red-100 rounded-lg p-6 mb-4">
                  <h5 className="font-bold text-red-800 mb-2">Candidature classique</h5>
                  <p className="text-red-700 text-sm mb-4">CV générique + lettre standard</p>
                  <div className="text-4xl font-bold text-red-600">2%</div>
                  <p className="text-red-600 text-sm">de réponses</p>
                </div>
              </div>

              <div className="text-center">
                <div className="bg-green-100 rounded-lg p-6 mb-4">
                  <h5 className="font-bold text-green-800 mb-2">Candidature Phoenix</h5>
                  <p className="text-green-700 text-sm mb-4">
                    Données interconnectées + IA personnalisée
                  </p>
                  <div className="text-4xl font-bold text-green-600">15%</div>
                  <p className="text-green-600 text-sm">de réponses</p>
                </div>
              </div>
            </div>

            <div className="text-center mt-8">
              <p className="text-lg text-gray-700 mb-2">
                <em>
                  Pourquoi cette différence ? Parce que Phoenix ne génère pas du contenu standard.
                </em>
              </p>
              <p className="text-xl font-bold text-gray-900">
                Phoenix raconte VOTRE histoire unique.
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
            <h4 className="text-2xl font-bold text-gray-900 mb-4">Découvrez l'Effet Phoenix</h4>
            <p className="text-lg text-gray-600 mb-6">
              Commencez gratuitement avec Phoenix CV. Plus vous utilisez l'écosystème, plus il
              devient puissant.
            </p>
            <Link href="https://phoenix-cv.streamlit.app/" target="_blank">
              <Button
                size="lg"
                className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white px-8 py-3 text-lg"
              >
                Commencer maintenant →
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
