import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY as string, {
  apiVersion: '2024-06-20', // Utilisez la version d'API Stripe que vous préférez
});

export async function POST(req: NextRequest) {
  try {
    const { priceId, quantity } = await req.json();

    if (!priceId || !quantity) {
      return NextResponse.json({ error: 'Missing priceId or quantity' }, { status: 400 });
    }

    const successUrl = `${req.nextUrl.origin}/success?session_id={CHECKOUT_SESSION_ID}`;
    const cancelUrl = `${req.nextUrl.origin}/cancel`;

    const session = await stripe.checkout.sessions.create({
      line_items: [
        {
          price: priceId,
          quantity: quantity,
        },
      ],
      mode: 'subscription', // Ou 'payment' si ce n'est pas un abonnement
      success_url: successUrl,
      cancel_url: cancelUrl,
      // Ajoutez d'autres options si nécessaire, comme customer_email, metadata, etc.
    });

    return NextResponse.json({ id: session.id, url: session.url });
  } catch (error: any) {
    console.error('Stripe checkout session creation failed:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
