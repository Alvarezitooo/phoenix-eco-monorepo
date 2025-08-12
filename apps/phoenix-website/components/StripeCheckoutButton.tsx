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

      const { url } = await response.json();

      if (url) {
        window.location.href = url;
      } else {
        throw new Error('No checkout URL received');
      }
    } catch (error) {
      console.error('Checkout error:', error);
      alert('Erreur lors du paiement. Veuillez réessayer.');
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
