import { CheckCircle, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function SuccessPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <CheckCircle className="w-8 h-8 text-green-600" />
        </div>
        
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          Paiement réussi ! 🎉
        </h1>
        
        <p className="text-gray-600 mb-6">
          Merci pour votre abonnement Phoenix. Vous allez recevoir un email de confirmation 
          avec vos accès premium dans quelques minutes.
        </p>
        
        <div className="space-y-4">
          <Link href="https://phoenix-letters.streamlit.app/" target="_blank">
            <Button className="w-full bg-green-600 hover:bg-green-700">
              Accéder à Phoenix Letters Premium
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
          
          <Link href="/">
            <Button variant="outline" className="w-full">
              Retour à l'accueil
            </Button>
          </Link>
        </div>
        
        <p className="text-sm text-gray-500 mt-6">
          Besoin d'aide ? Contactez-nous à support@phoenix-ecosystem.com
        </p>
      </div>
    </div>
  );
}
