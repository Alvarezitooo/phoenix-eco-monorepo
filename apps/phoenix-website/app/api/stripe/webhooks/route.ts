// /apps/phoenix-website/app/api/stripe/webhooks/route.ts
import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';
import { Readable } from 'stream';
import { createClient } from '@supabase/supabase-js';

// Initialiser Stripe
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY as string, {
  apiVersion: '2025-07-30.basil',
});

// Initialiser le client Supabase admin pour l'écriture en BDD
const supabaseAdmin = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL || '',
  process.env.SUPABASE_SERVICE_ROLE_KEY || ''
);

// Fonction pour buffer la requête
async function buffer(readable: Readable): Promise<Buffer> {
  const chunks = [];
  for await (const chunk of readable) {
    chunks.push(typeof chunk === 'string' ? Buffer.from(chunk) : chunk);
  }
  return Buffer.concat(chunks);
}

// Le secret du webhook
const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET || '';

export async function POST(req: NextRequest) {
  try {
    const buf = await buffer(req.body as any);
    const sig = req.headers.get('stripe-signature') as string;

    let event: Stripe.Event;

    // 1. VÉRIFICATION DE LA SIGNATURE (ÉTAPE DE SÉCURITÉ CRITIQUE)
    try {
      event = stripe.webhooks.constructEvent(buf, sig, webhookSecret);
    } catch (err: any) {
      console.error(`❌ Erreur de vérification du webhook: ${err.message}`);
      return NextResponse.json({ error: `Webhook Error: ${err.message}` }, { status: 400 });
    }

    // 2. PUBLICATION DE L'ÉVÉNEMENT PHOENIX DANS LA BDD
    const eventType = event.type;
    const eventObject = event.data.object as any;
    let phoenixEvent = null;

    console.log(`✅ Webhook Stripe reçu et validé: ${eventType}`);

    switch (eventType) {
      case 'checkout.session.completed':
        const userId = eventObject.client_reference_id;
        if (!userId) {
          console.error('CRITICAL: checkout.session.completed sans client_reference_id!');
          break;
        }
        phoenixEvent = {
          stream_id: userId,
          event_type: 'billing.subscription_activated', // Type d'événement Phoenix
          app_source: 'billing',
          payload: {
            stripe_customer_id: eventObject.customer,
            stripe_subscription_id: eventObject.subscription,
            subscription_tier: eventObject.metadata?.plan_id || 'premium',
            activated_at: new Date().toISOString(),
          },
        };
        break;

      // Ajoutez d'autres cas ici si nécessaire
      // case 'customer.subscription.deleted':
      //   // ... logique pour l'événement d'annulation
      //   break;

      default:
        console.log(`-> Événement non traité: ${eventType}`);
        break;
    }

    // Si un événement Phoenix a été créé, on l'insère dans la table 'events'
    if (phoenixEvent) {
      const { error } = await supabaseAdmin.from('events').insert(phoenixEvent);
      if (error) {
        console.error('Erreur insertion événement Phoenix:', error);
        return NextResponse.json({ error: 'Failed to record Phoenix event' }, { status: 500 });
      }
      console.log(`✅ Événement Phoenix [${phoenixEvent.event_type}] publié pour l'utilisateur ${phoenixEvent.stream_id}`);
    }

    return NextResponse.json({ received: true });

  } catch (error: any) {
    console.error('Erreur inattendue dans le handler de webhook:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
