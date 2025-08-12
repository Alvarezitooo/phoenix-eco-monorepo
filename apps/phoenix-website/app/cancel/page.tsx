import { XCircle, ArrowLeft, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function CancelPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <XCircle className="w-8 h-8 text-red-600" />
        </div>

        <h1 className="text-2xl font-bold text-gray-900 mb-4">Paiement annulé</h1>

        <p className="text-gray-600 mb-6">
          Aucun problème ! Votre paiement n'a pas été traité. Vous pouvez toujours tester Phoenix
          gratuitement ou réessayer plus tard.
        </p>

        <div className="space-y-4">
          <Link href="https://phoenix-letters.streamlit.app/" target="_blank">
            <Button className="w-full bg-orange-600 hover:bg-orange-700">
              Tester Phoenix Letters Gratuit
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>

          <Link href="/pricing">
            <Button variant="outline" className="w-full">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Retour aux tarifs
            </Button>
          </Link>
        </div>

        <p className="text-sm text-gray-500 mt-6">
          Des questions ? Contactez-nous à support@phoenix-ecosystem.com
        </p>
      </div>
    </div>
  );
}
