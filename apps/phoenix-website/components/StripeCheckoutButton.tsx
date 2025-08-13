'use client';

import { Button } from './ui/button';
import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { loadStripe } from '@stripe/stripe-js';

interface StripeCheckoutButtonProps {
  priceId: string;
  productName: string;
  price: string;
  className?: string;
  disabled?: boolean;
  variant?: 'default' | 'outline' | 'ghost';
  label?: string; // libellé personnalisé du bouton
}

export default function StripeCheckoutButton({
  priceId,
  productName,
  price,
  className = '',
  disabled = false,
  variant = 'default',
  label,
}: StripeCheckoutButtonProps) {
  const [loading, setLoading] = useState(false);

  const handleCheckout = async () => {
    setLoading(true);

    try {
      // Vérifier si l'utilisateur est connecté
      const { PhoenixWebsiteAuth } = await import('@/lib/auth');
      const auth = PhoenixWebsiteAuth.getInstance();
      const user = await auth.getCurrentUser();

      if (!user) {
        // Rediriger vers auth modal si non connecté
        alert('Veuillez vous connecter pour continuer vers le paiement');
        setLoading(false);
        return;
      }
      const publishableKey = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY as string | undefined;
      if (!publishableKey) {
        throw new Error('Stripe non configuré côté client (clé publique manquante).');
      }

      const response = await fetch('/api/stripe/checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          priceId: priceId,
          quantity: 1,
        }),
      });

      const payload = await response.json().catch(() => ({}));

      if (!response.ok) {
        const message =
          (payload && (payload.message || payload.error)) || `Erreur ${response.status}`;
        throw new Error(message);
      }

      const { id, url } = payload as { id?: string; url?: string };

      if (id) {
        const stripe = await loadStripe(publishableKey);
        if (!stripe) throw new Error('Impossible de charger Stripe.js');
        const result = await stripe.redirectToCheckout({ sessionId: id });
        if (result.error) {
          throw new Error(result.error.message || 'Redirection Stripe échouée');
        }
        return;
      }

      if (url) {
        window.location.assign(url);
        return;
      }

      throw new Error('Session Stripe manquante. Vérifiez la configuration serveur.');
    } catch (error) {
      console.error('Checkout error:', error);
      const message =
        error instanceof Error ? error.message : 'Erreur lors du paiement. Veuillez réessayer.';
      alert(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button
      className={className}
      variant={variant}
      disabled={disabled || loading}
      onClick={handleCheckout}
    >
      {loading ? (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          Redirection...
        </>
      ) : (
        label || `S'abonner - ${price}`
      )}
    </Button>
  );
}
