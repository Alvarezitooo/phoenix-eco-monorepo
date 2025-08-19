import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';

// Validation des variables d'environnement requises
if (!process.env.STRIPE_SECRET_KEY) {
  throw new Error('STRIPE_SECRET_KEY is required for checkout session creation');
}

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
  apiVersion: '2025-07-30.basil',
});

export async function POST(req: NextRequest) {
  try {
    const cookieStore = cookies();
    // Validation des variables d'environnement Supabase
    if (!process.env.SUPABASE_URL || !process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
      throw new Error('SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY are required');
    }

    const supabase = createServerClient(
      process.env.SUPABASE_URL,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
      {
        cookies: {
          get(name: string) {
            return cookieStore.get(name)?.value;
          },
        },
      },
    );
    const {
      data: { user },
    } = await supabase.auth.getUser();

    // 1. Vérifier si l'utilisateur est authentifié
    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { priceId, quantity } = await req.json();

    if (!priceId || !quantity) {
      return NextResponse.json({ error: 'Missing priceId or quantity' }, { status: 400 });
    }

    const successUrl = `${req.nextUrl.origin}/success?session_id={CHECKOUT_SESSION_ID}`;
    const cancelUrl = `${req.nextUrl.origin}/cancel`;

    // 2. Créer la session Stripe avec l'ID de l'utilisateur
    const session = await stripe.checkout.sessions.create({
      line_items: [
        {
          price: priceId,
          quantity: quantity,
        },
      ],
      mode: 'subscription',
      success_url: successUrl,
      cancel_url: cancelUrl,
      // 3. Lier la session à l'utilisateur Phoenix via client_reference_id
      client_reference_id: user.id,
      // Il est aussi recommandé de passer l'email ou un ID client Stripe existant
      // pour une meilleure gestion dans le dashboard Stripe.
      customer_email: user.email,
      // Si vous stockiez un stripe_customer_id sur votre objet utilisateur, il faudrait le passer ici:
      // customer: user.stripe_customer_id,
    });

    return NextResponse.json({ id: session.id, url: session.url });
  } catch (error) {
    // Error handling spécifique
    if (error instanceof Stripe.errors.StripeError) {
      console.error('Stripe API Error:', {
        type: error.type,
        code: error.code,
        message: error.message,
      });
      return NextResponse.json(
        { error: 'Payment processing error', details: error.message },
        { status: 400 }
      );
    }

    if (error instanceof Error && error.message.includes('required')) {
      console.error('Configuration Error:', error.message);
      return NextResponse.json(
        { error: 'Service configuration error' },
        { status: 500 }
      );
    }

    console.error('Unexpected error in checkout session:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
