import React from 'react';
import { Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import StripeCheckoutButton from '@/components/StripeCheckoutButton';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '../ui/badge';

const BundlePricing: React.FC = () => {
  return (
    <section className="py-16 px-4 bg-gray-100">
      <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 text-gray-800">
        📦 Bundles Attractifs : Économisez sur votre Reconversion
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
        {/* Starter Bundle */}
        <Card className="border-2 border-blue-200 shadow-lg">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-blue-700">Bundle Phoenix</CardTitle>
            <p className="text-gray-600 mt-2">Letters + CV</p>
            <div className="mt-4">
              <span className="text-4xl font-bold text-blue-800">15,99€</span>
              <span className="text-gray-600">/mois</span>
            </div>
            <Badge className="mt-2 bg-blue-500 text-white">vs 17,98€ séparément</Badge>
          </CardHeader>
          <CardContent className="space-y-4">
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Toutes les fonctionnalités Letters
              </li>
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Toutes les fonctionnalités CV
              </li>
            </ul>
            <StripeCheckoutButton
              priceId={process.env.NEXT_PUBLIC_STRIPE_PACK_PRICE_ID || 'price_pack_monthly'}
              productName="Bundle Phoenix (Letters + CV)"
              price="15,99€/mois"
              label="Choisir l'offre Premium"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
            />
          </CardContent>
        </Card>

        {/* Future Bundle - Phoenix Rise Coming Soon */}
        <Card className="relative border-2 border-gray-300 shadow-lg opacity-75">
          <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
            <Badge className="bg-gray-500 text-white px-4 py-1">Bientôt</Badge>
          </div>
          <CardHeader className="text-center pt-8">
            <CardTitle className="text-2xl text-gray-700">Bundle Complet</CardTitle>
            <p className="text-gray-600 mt-2">Letters + CV + Rise</p>
            <div className="mt-4">
              <span className="text-4xl font-bold text-gray-500">Bientôt</span>
              <span className="text-gray-600"> disponible</span>
            </div>
            <Badge className="mt-2 bg-gray-500 text-white">Avec Phoenix Rise</Badge>
          </CardHeader>
          <CardContent className="space-y-4">
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-center">
                <Check className="h-5 w-5 text-gray-400 mr-2" /> Toutes les fonctionnalités Letters
              </li>
              <li className="flex items-center">
                <Check className="h-5 w-5 text-gray-400 mr-2" /> Toutes les fonctionnalités CV
              </li>
              <li className="flex items-center">
                <Check className="h-5 w-5 text-gray-400 mr-2" /> Toutes les fonctionnalités Rise
              </li>
            </ul>
            <Button className="w-full bg-gray-400 text-white" disabled>
              Bientôt disponible
            </Button>
          </CardContent>
        </Card>

        {/* Information Card */}
        <Card className="border-2 border-blue-200 shadow-lg bg-blue-50">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-blue-700">💡 Pourquoi Bundle ?</CardTitle>
            <p className="text-gray-600 mt-2">L'écosystème complet</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <ul className="space-y-3 text-gray-700">
              <li className="flex items-start">
                <Check className="h-5 w-5 text-blue-500 mr-2 mt-0.5" />
                <div>
                  <strong>CV optimisé</strong>
                  <br />
                  <small>Phoenix CV crée votre profil professionnel</small>
                </div>
              </li>
              <li className="flex items-start">
                <Check className="h-5 w-5 text-blue-500 mr-2 mt-0.5" />
                <div>
                  <strong>Lettres personnalisées</strong>
                  <br />
                  <small>Phoenix Letters adapte selon chaque offre</small>
                </div>
              </li>
              <li className="flex items-start">
                <Check className="h-5 w-5 text-blue-500 mr-2 mt-0.5" />
                <div>
                  <strong>Données interconnectées</strong>
                  <br />
                  <small>Plus vous utilisez, plus c'est précis</small>
                </div>
              </li>
            </ul>
            <div className="text-center text-sm text-gray-600 mt-4 p-3 bg-white rounded">
              <strong>Économisez 1,99€/mois</strong>
              <br />
              vs achat séparé
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
};

export default BundlePricing;
