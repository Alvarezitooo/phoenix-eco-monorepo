import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY as string, {
  apiVersion: '2025-07-30.basil', // Version Stripe API la plus récente compatible
});

export async function POST(req: NextRequest) {
  try {
    const cookieStore = cookies();
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
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
  } catch (error: any) {
    console.error('Stripe checkout session creation failed:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
