import { Heart, Shield, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';

export default function EthicsSection() {
  return (
    <section className="py-20 bg-white">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            Un Modèle <span className="text-orange-500">Éthique</span>
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">La technologie avec une âme</p>
        </div>

        <div className="max-w-4xl mx-auto mb-12">
          <Card className="bg-orange-50 border-orange-200">
            <CardContent className="pt-8">
              <div className="text-center">
                <Shield className="h-12 w-12 text-orange-500 mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-slate-900 mb-4">Notre Engagement</h3>
                <p className="text-lg text-slate-700 leading-relaxed max-w-3xl mx-auto">
                  Phoenix propose des outils gratuits puissants. Les fonctionnalités premium
                  financent le développement et ma subsistance. À terme, 10% des revenus financeront
                  un fonds solidaire pour offrir des abonnements aux personnes les plus précaires.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <Card className="text-center">
            <CardHeader>
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Heart className="h-8 w-8 text-green-600" />
              </div>
              <CardTitle>Toujours Gratuit</CardTitle>
              <CardDescription>
                Les fonctionnalités essentielles restent accessibles à tous, pour toujours.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="text-center">
            <CardHeader>
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="h-8 w-8 text-blue-600" />
              </div>
              <CardTitle>Premium Juste</CardTitle>
              <CardDescription>
                Les fonctionnalités avancées à prix transparent pour financer le développement.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="text-center">
            <CardHeader>
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="h-8 w-8 text-purple-600" />
              </div>
              <CardTitle>Fonds Solidaire</CardTitle>
              <CardDescription>
                10% des revenus pour offrir l'accès premium aux personnes en difficulté.
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </div>
    </section>
  );
}
