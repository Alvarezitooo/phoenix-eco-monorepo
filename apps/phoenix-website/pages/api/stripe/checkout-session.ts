import { NextApiRequest, NextApiResponse } from 'next';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY! as string, {
  // Utiliser la valeur de type attendue par @types/stripe de ce repo
  apiVersion: '2025-07-30.basil',
});

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    const { priceId, quantity = 1 } = req.body;

    try {
      const session = await stripe.checkout.sessions.create({
        line_items: [
          {
            price: priceId,
            quantity: quantity,
          },
        ],
        mode: 'subscription', // or 'payment' for one-time payments
        success_url: `${req.headers.origin}/success?session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: `${req.headers.origin}/cancel`,
      });
      res.status(200).json({ url: session.url });
    } catch (err: any) {
      res.status(err.statusCode || 500).json({ message: err.message });
    }
  } else {
    res.setHeader('Allow', 'POST');
    res.status(405).end('Method Not Allowed');
  }
}
