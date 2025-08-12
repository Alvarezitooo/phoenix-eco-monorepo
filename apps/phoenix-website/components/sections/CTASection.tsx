import { Button } from '../ui/button';
import { ArrowRight, Star } from 'lucide-react';

export default function CTASection() {
  return (
    <section className="py-20 bg-gradient-to-r from-orange-500 to-orange-600">
      <div className="container mx-auto px-4 text-center">
        <div className="max-w-4xl mx-auto">
          <div className="flex justify-center mb-4">
            <div className="flex items-center space-x-1">
              {[...Array(5)].map((_, i) => (
                <Star key={i} className="h-5 w-5 text-orange-200 fill-current" />
              ))}
            </div>
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Prêt à transformer votre reconversion ?
          </h2>
          <p className="text-xl text-orange-100 mb-8 max-w-2xl mx-auto">
            Soyez parmi les premiers à tester Phoenix et à bénéficier d'un accompagnement
            personnalisé pour votre reconversion professionnelle.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              size="lg"
              className="bg-white text-orange-600 hover:bg-orange-50 text-lg px-8 py-4 h-auto"
              asChild
            >
              <a href="/demo">
                Commencer gratuitement
                <ArrowRight className="ml-2 h-5 w-5" />
              </a>
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-white text-white hover:bg-white hover:text-orange-600 text-lg px-8 py-4 h-auto"
              asChild
            >
              <a href="/pricing">Voir les tarifs</a>
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
}
