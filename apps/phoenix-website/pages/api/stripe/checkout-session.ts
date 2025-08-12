import { NextApiRequest, NextApiResponse } from 'next';
import Stripe from 'stripe';

// Instanciate Stripe client (fail fast if not configured)
const secretKey = process.env.STRIPE_SECRET_KEY as string | undefined;
const stripe = secretKey ? new Stripe(secretKey) : null;

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    if (!stripe) {
      return res.status(500).json({ message: 'Stripe non configuré: STRIPE_SECRET_KEY manquant.' });
    }

    const { priceId, quantity = 1 } = req.body as { priceId?: string; quantity?: number };

    if (!priceId) {
      return res.status(400).json({ message: 'priceId manquant.' });
    }

    try {
      const origin =
        (req.headers.origin as string) ||
        process.env.NEXT_PUBLIC_SITE_URL ||
        'https://phoenix-eco-monorepo.vercel.app';
      const session = await stripe.checkout.sessions.create({
        line_items: [
          {
            price: priceId,
            quantity: quantity,
          },
        ],
        mode: 'subscription', // or 'payment' for one-time payments
        success_url: `${origin}/success?session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: `${origin}/cancel`,
      });
      // retourner l'id pour Stripe.js et url en fallback
      res.status(200).json({ id: session.id, url: session.url });
    } catch (err: any) {
      console.error('Stripe checkout session error', { error: err?.message || String(err) });
      res.status(err?.statusCode || 500).json({ message: err?.message || 'Erreur Stripe' });
    }
  } else {
    res.setHeader('Allow', 'POST');
    res.status(405).end('Method Not Allowed');
  }
}
