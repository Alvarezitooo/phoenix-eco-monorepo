import React from 'react';
import { Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import StripeCheckoutButton from '../StripeCheckoutButton';
import Link from 'next/link';

const IndividualAppPricing: React.FC = () => {
  return (
    <section className="py-16 px-4 bg-white">
      <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 text-gray-800">
        💰 Tarification Honnête : Applications Individuelles
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
        {/* Gratuit */}
        <Card className="border-2 border-gray-200 shadow-lg">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-gray-700">Gratuit</CardTitle>
            <p className="text-gray-600 mt-2">Découvrez Phoenix</p>
            <div className="mt-4">
              <span className="text-4xl font-bold text-gray-800">0€</span>
              <span className="text-gray-600">/mois</span>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> 3 lettres/mois (Phoenix Letters)
              </li>
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> 1 CV/mois (Phoenix CV)
              </li>
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Templates de base
              </li>
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Support communauté
              </li>
            </ul>
            <Link href="/demo">
              <Button
                variant="outline"
                className="w-full border-gray-600 text-gray-600 hover:bg-gray-50"
              >
                Commencer Gratuitement
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Phoenix Letters */}
        <Card className="border-2 border-purple-200 shadow-lg">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-purple-700">Phoenix Letters</CardTitle>
            <p className="text-gray-600 mt-2">Lettres de motivation IA</p>
            <div className="mt-4">
              <span className="text-4xl font-bold text-purple-800">9,99€</span>
              <span className="text-gray-600">/mois</span>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Illimité
              </li>
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Tous templates
              </li>
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Export PDF/DOCX
              </li>
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Suggestion compétences
                transférables
              </li>
              <li className="flex items-center text-purple-700 font-semibold">
                <Check className="h-5 w-5 text-purple-500 mr-2" /> Phoenix Caméléon (Premium)
                <br />
                <small className="text-gray-500 ml-7">
                  Analyse la culture d'entreprise et adapte le ton de votre lettre.
                </small>
              </li>
              <li className="flex items-center text-purple-700 font-semibold">
                <Check className="h-5 w-5 text-purple-500 mr-2" /> L'Amplificateur de Talents
                (Premium)
                <br />
                <small className="text-gray-500 ml-7">
                  Feedback IA en temps réel sur la qualité de votre lettre.
                </small>
              </li>
              <li className="flex items-center text-purple-700 font-semibold">
                <Check className="h-5 w-5 text-purple-500 mr-2" /> Phoenix Envol (Premium)
                <br />
                <small className="text-gray-500 ml-7">
                  Plans de reconversion personnalisés et roadmap stratégique.
                </small>
              </li>
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Le Détecteur de Talents (Gratuit)
                <br />
                <small className="text-gray-500 ml-7">
                  Optimisation des mots-clés pour les systèmes ATS et score de compatibilité.
                </small>
              </li>
            </ul>
            <div className="space-y-2">
              <Link href="/demo">
                <Button
                  variant="outline"
                  className="w-full border-purple-600 text-purple-600 hover:bg-purple-50"
                >
                  Tester Gratuitement
                </Button>
              </Link>
              <StripeCheckoutButton
                priceId={process.env.NEXT_PUBLIC_STRIPE_LETTERS_PRICE_ID || 'price_letters_monthly'}
                productName="Phoenix Letters"
                price="9,99€/mois"
                label="Tester Letters Premium"
                className="w-full bg-purple-600 hover:bg-purple-700 text-white"
              />
            </div>
            <p className="text-center text-sm text-gray-500">vs 23,70€ Zety</p>
          </CardContent>
        </Card>

        {/* Phoenix CV */}
        <Card className="border-2 border-purple-200 shadow-lg">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-purple-700">Phoenix CV</CardTitle>
            <p className="text-gray-600 mt-2">CV percutants</p>
            <div className="mt-4">
              <span className="text-4xl font-bold text-purple-800">7,99€</span>
              <span className="text-gray-600">/mois</span>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> CV illimités
              </li>
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Accroches personnalisées
              </li>
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Passe filtres ATS
              </li>
            </ul>
            <div className="space-y-2">
              <Link href="/demo">
                <Button
                  variant="outline"
                  className="w-full border-purple-600 text-purple-600 hover:bg-purple-50"
                >
                  Tester Gratuitement
                </Button>
              </Link>
              <StripeCheckoutButton
                priceId={process.env.NEXT_PUBLIC_STRIPE_CV_PRICE_ID || 'price_cv_monthly'}
                productName="Phoenix CV"
                price="7,99€/mois"
                label="Tester CV Premium"
                className="w-full bg-purple-600 hover:bg-purple-700 text-white"
              />
            </div>
            <p className="text-center text-sm text-gray-500">vs outils CV premium</p>
          </CardContent>
        </Card>

        {/* Phoenix Rise */}
        <Card className="border-2 border-purple-200 shadow-lg">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-purple-700">Phoenix Rise</CardTitle>
            <p className="text-gray-600 mt-2">Coach carrière IA</p>
            <div className="mt-4">
              <span className="text-4xl font-bold text-gray-500">Bientôt</span>
              <span className="text-gray-600"> disponible</span>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Coaching illimité
              </li>
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Journal de bord
              </li>
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Plan de carrière
              </li>
            </ul>
            <div className="space-y-2">
              <Link href="/demo">
                <Button
                  variant="outline"
                  className="w-full border-purple-600 text-purple-600 hover:bg-purple-50"
                >
                  Tester la Démo
                </Button>
              </Link>
              <Button className="w-full bg-gray-400 text-white" disabled>
                Bientôt disponible
              </Button>
            </div>
            <p className="text-center text-sm text-gray-500">vs coaching 50€/h</p>
          </CardContent>
        </Card>

        {/* Phoenix Aube */}
        <Card className="border-2 border-amber-200 shadow-lg">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-amber-700">Phoenix Aube</CardTitle>
            <p className="text-gray-600 mt-2">Trajectory Builder IA</p>
            <div className="mt-4">
              <span className="text-4xl font-bold text-gray-500">Bientôt</span>
              <span className="text-gray-600"> disponible</span>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Tests psychométriques avancés
              </li>
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Matching valeurs & compétences
              </li>
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Prédiction impact IA sur métiers
              </li>
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Plan de montée en compétences IA
              </li>
            </ul>
            <div className="space-y-2">
              <Button className="w-full bg-gray-400 text-white" disabled>
                Bientôt disponible
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
};

export default IndividualAppPricing;
