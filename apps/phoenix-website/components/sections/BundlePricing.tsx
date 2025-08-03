import React from 'react';
import { Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
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
            <CardTitle className="text-2xl text-blue-700">Starter Bundle</CardTitle>
            <p className="text-gray-600 mt-2">Letters + CV</p>
            <div className="mt-4">
              <span className="text-4xl font-bold text-blue-800">12,99€</span>
              <span className="text-gray-600">/mois</span>
            </div>
            <Badge className="mt-2 bg-blue-500 text-white">Économisez 20%</Badge>
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
            <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white">
              Choisir Starter
            </Button>
          </CardContent>
        </Card>

        {/* Complete Bundle */}
        <Card className="relative border-2 border-purple-500 shadow-lg">
          <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
            <Badge className="bg-purple-500 text-white px-4 py-1">Recommandé</Badge>
          </div>
          <CardHeader className="text-center pt-8">
            <CardTitle className="text-2xl text-purple-700">Complete Bundle</CardTitle>
            <p className="text-gray-600 mt-2">Letters + CV + Rise</p>
            <div className="mt-4">
              <span className="text-4xl font-bold text-purple-800">17,99€</span>
              <span className="text-gray-600">/mois</span>
            </div>
            <Badge className="mt-2 bg-purple-500 text-white">Économisez 25%</Badge>
          </CardHeader>
          <CardContent className="space-y-4">
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Toutes les fonctionnalités Letters
              </li>
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Toutes les fonctionnalités CV
              </li>
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Toutes les fonctionnalités Rise
              </li>
            </ul>
            <Button className="w-full bg-purple-600 hover:bg-purple-700 text-white">
              Choisir Complet
            </Button>
          </CardContent>
        </Card>

        {/* Annuel Complete Bundle */}
        <Card className="border-2 border-green-200 shadow-lg">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-green-700">Annuel Complet</CardTitle>
            <p className="text-gray-600 mt-2">Paiement annuel</p>
            <div className="mt-4">
              <span className="text-4xl font-bold text-green-800">179€</span>
              <span className="text-gray-600">/an</span>
            </div>
            <Badge className="mt-2 bg-green-500 text-white">Économisez 35%</Badge>
          </CardHeader>
          <CardContent className="space-y-4">
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Accès illimité aux 3 apps pendant
                1 an
              </li>
              <li className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-2" /> Support prioritaire
              </li>
            </ul>
            <Button className="w-full bg-green-600 hover:bg-green-700 text-white">
              Choisir Annuel
            </Button>
          </CardContent>
        </Card>
      </div>
    </section>
  );
};

export default BundlePricing;
