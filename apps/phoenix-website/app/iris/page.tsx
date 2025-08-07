// 🤖 IRIS PAGE - Page dédiée à l'agent Iris Phoenix
import { IrisSection } from '@/components/iris';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Bot, Zap, Shield, Users, MessageCircle, Sparkles, CheckCircle } from 'lucide-react';

export default function IrisPage() {
  const authToken = null; // Auth token sera fourni par le système d'authentification

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <Badge
            variant="secondary"
            className="bg-purple-100 text-purple-700 px-6 py-3 text-lg mb-6"
          >
            <Bot className="w-5 h-5 mr-2" />
            Iris - Intelligence Artificielle Phoenix
          </Badge>

          <h1 className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-purple-600 via-blue-600 to-purple-600 bg-clip-text text-transparent mb-6">
            Votre Guide IA Personnel
          </h1>

          <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Iris vous accompagne 24h/24 dans votre transformation professionnelle avec des conseils
            personnalisés et une expertise IA de pointe
          </p>

          <div className="flex flex-wrap justify-center gap-4 mb-12">
            <Badge variant="outline" className="px-4 py-2 text-green-700 border-green-300">
              <CheckCircle className="w-4 h-4 mr-2" />
              100% Gratuit pour commencer
            </Badge>
            <Badge variant="outline" className="px-4 py-2 text-blue-700 border-blue-300">
              <Zap className="w-4 h-4 mr-2" />
              Réponses instantanées
            </Badge>
            <Badge variant="outline" className="px-4 py-2 text-purple-700 border-purple-300">
              <Shield className="w-4 h-4 mr-2" />
              Données sécurisées
            </Badge>
          </div>
        </div>
      </section>

      {/* Capacités d'Iris */}
      <section className="py-16 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">
            Les super-pouvoirs d&apos;Iris dans l&apos;écosystème Phoenix
          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="hover:shadow-lg transition-shadow border-purple-200">
              <CardHeader>
                <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white mb-4">
                  ✍️
                </div>
                <CardTitle className="text-purple-700">Iris Letters</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">
                  Expert en lettres de motivation personnalisées pour reconversions
                </p>
                <ul className="text-sm text-gray-500 space-y-1">
                  <li>• Adaptation aux offres d&apos;emploi</li>
                  <li>• Optimisation ATS</li>
                  <li>• Conseils sectoriels</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow border-blue-200">
              <CardHeader>
                <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center text-white mb-4">
                  📋
                </div>
                <CardTitle className="text-blue-700">Iris CV</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">
                  Optimisation CV et stratégie carrière intelligente
                </p>
                <ul className="text-sm text-gray-500 space-y-1">
                  <li>• Analyse de CV</li>
                  <li>• Conseils templates</li>
                  <li>• Trajectoire professionnelle</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow border-green-200">
              <CardHeader>
                <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full flex items-center justify-center text-white mb-4">
                  🌱
                </div>
                <CardTitle className="text-green-700">Iris Coach</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">
                  Accompagnement développement personnel et bien-être
                </p>
                <ul className="text-sm text-gray-500 space-y-1">
                  <li>• Coaching émotionnel</li>
                  <li>• Définition d&apos;objectifs</li>
                  <li>• Gestion du stress</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow border-orange-200">
              <CardHeader>
                <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center text-white mb-4">
                  🚀
                </div>
                <CardTitle className="text-orange-700">Iris Phoenix</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">
                  Guide général de l&apos;écosystème et orientation
                </p>
                <ul className="text-sm text-gray-500 space-y-1">
                  <li>• Navigation écosystème</li>
                  <li>• Recommandations d&apos;apps</li>
                  <li>• Support technique</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Interface Iris */}
      <IrisSection
        title="Essayez Iris maintenant"
        description="Posez vos questions et découvrez comment Iris peut transformer votre parcours professionnel"
        authToken={authToken}
        showFeatures={false}
        className="bg-gradient-to-br from-gray-50 to-white"
      />

      {/* Témoignages */}
      <section className="py-16 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">
            Ce que disent nos utilisateurs d&apos;Iris
          </h2>

          <div className="grid md:grid-cols-3 gap-6">
            <Card className="border-purple-200">
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                    👩‍💼
                  </div>
                  <div>
                    <p className="font-semibold text-gray-800">Marie L.</p>
                    <p className="text-sm text-gray-500">Reconversion Finance → UX Design</p>
                  </div>
                </div>
                <p className="text-gray-600 italic">
                  &quot;Iris m&apos;a aidée à structurer ma reconversion étape par étape. Ses
                  conseils personnalisés ont été un vrai game-changer !&quot;
                </p>
                <div className="flex text-yellow-400 mt-3">⭐⭐⭐⭐⭐</div>
              </CardContent>
            </Card>

            <Card className="border-blue-200">
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    👨‍💻
                  </div>
                  <div>
                    <p className="font-semibold text-gray-800">Thomas K.</p>
                    <p className="text-sm text-gray-500">Ingénieur → Chef de produit</p>
                  </div>
                </div>
                <p className="text-gray-600 italic">
                  &quot;L&apos;optimisation CV avec Iris est bluffante. Mon taux de réponse aux
                  candidatures a été multiplié par 3 !&quot;
                </p>
                <div className="flex text-yellow-400 mt-3">⭐⭐⭐⭐⭐</div>
              </CardContent>
            </Card>

            <Card className="border-green-200">
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                    👩‍🎓
                  </div>
                  <div>
                    <p className="font-semibold text-gray-800">Sophie M.</p>
                    <p className="text-sm text-gray-500">Enseignante → Data Analyst</p>
                  </div>
                </div>
                <p className="text-gray-600 italic">
                  &quot;Le soutien émotionnel d&apos;Iris pendant ma reconversion a été précieux. Je
                  recommande à 100% !&quot;
                </p>
                <div className="flex text-yellow-400 mt-3">⭐⭐⭐⭐⭐</div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Final */}
      <section className="py-20 px-4 bg-gradient-to-r from-purple-600 to-blue-600">
        <div className="max-w-4xl mx-auto text-center text-white">
          <Sparkles className="w-16 h-16 mx-auto mb-6" />
          <h2 className="text-4xl font-bold mb-6">Prêt à transformer votre carrière avec Iris ?</h2>
          <p className="text-xl mb-8 opacity-90">
            Rejoignez des milliers de professionnels qui ont déjà réussi leur reconversion avec
            Phoenix
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <button className="bg-white text-purple-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
              Commencer gratuitement
            </button>
            <button className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-purple-600 transition-colors">
              Découvrir l&apos;écosystème Phoenix
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
