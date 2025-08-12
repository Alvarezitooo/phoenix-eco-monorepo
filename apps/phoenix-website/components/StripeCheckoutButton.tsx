'use client';

import { Button } from './ui/button';
import { useState } from 'react';
import { Loader2 } from 'lucide-react';

interface StripeCheckoutButtonProps {
  priceId: string;
  productName: string;
  price: string;
  className?: string;
  disabled?: boolean;
  variant?: 'default' | 'outline' | 'ghost';
}

export default function StripeCheckoutButton({
  priceId,
  productName,
  price,
  className = '',
  disabled = false,
  variant = 'default',
}: StripeCheckoutButtonProps) {
  const [loading, setLoading] = useState(false);

  const handleCheckout = async () => {
    setLoading(true);

    try {
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

      const { url } = payload as { url?: string };

      if (url) {
        // Redirection fiable
        window.location.assign(url);
        return;
      }

      throw new Error('URL Stripe manquante. Vérifiez STRIPE_SECRET_KEY et les price IDs.');
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
        `S'abonner - ${price}`
      )}
    </Button>
  );
}
