/**
 * 🔗 Webhook Stripe Handler - Synchronisation des abonnements
 * Synchronise automatiquement les événements Stripe avec Supabase
 */

import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';
import { createClient } from '@supabase/supabase-js';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-11-20.acacia',
});

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET!;

export async function POST(request: NextRequest) {
  const body = await request.text();
  const signature = request.headers.get('stripe-signature')!;

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(body, signature, endpointSecret);
  } catch (err: any) {
    console.error('❌ Webhook signature verification failed:', err.message);
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 });
  }

  console.log('✅ Stripe webhook event:', event.type);

  try {
    switch (event.type) {
      case 'customer.subscription.created':
        await handleSubscriptionCreated(event.data.object as Stripe.Subscription);
        break;
      
      case 'customer.subscription.updated':
        await handleSubscriptionUpdated(event.data.object as Stripe.Subscription);
        break;
      
      case 'customer.subscription.deleted':
        await handleSubscriptionDeleted(event.data.object as Stripe.Subscription);
        break;
      
      case 'invoice.payment_succeeded':
        await handlePaymentSucceeded(event.data.object as Stripe.Invoice);
        break;
        
      case 'invoice.payment_failed':
        await handlePaymentFailed(event.data.object as Stripe.Invoice);
        break;

      default:
        console.log(`🔔 Unhandled event type: ${event.type}`);
    }

    return NextResponse.json({ received: true });
  } catch (error: any) {
    console.error('❌ Error processing webhook:', error);
    return NextResponse.json(
      { error: 'Webhook processing failed' }, 
      { status: 500 }
    );
  }
}

async function handleSubscriptionCreated(subscription: Stripe.Subscription) {
  const metadata = subscription.metadata;
  const phoenixUserId = metadata.phoenix_user_id;
  
  if (!phoenixUserId) {
    console.warn('⚠️ No phoenix_user_id in subscription metadata');
    return;
  }

  const subscriptionData = {
    user_id: phoenixUserId,
    stripe_customer_id: subscription.customer as string,
    stripe_subscription_id: subscription.id,
    subscription_tier: determineSubscriptionTier(subscription),
    status: 'active',
    current_period_start: new Date(subscription.current_period_start * 1000).toISOString(),
    current_period_end: new Date(subscription.current_period_end * 1000).toISOString(),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };

  // Mettre à jour ou créer l'abonnement
  const { error: subError } = await supabase
    .from('user_subscriptions')
    .upsert(subscriptionData, { onConflict: 'user_id' });

  if (subError) {
    console.error('❌ Error creating subscription:', subError);
    throw subError;
  }

  // Mettre à jour le profil utilisateur
  const { error: profileError } = await supabase
    .from('profiles')
    .update({
      subscription_tier: subscriptionData.subscription_tier,
      updated_at: new Date().toISOString()
    })
    .eq('id', phoenixUserId);

  if (profileError) {
    console.error('❌ Error updating profile:', profileError);
  }

  console.log(`✅ Subscription created for user ${phoenixUserId}: ${subscriptionData.subscription_tier}`);
}

async function handleSubscriptionUpdated(subscription: Stripe.Subscription) {
  const metadata = subscription.metadata;
  const phoenixUserId = metadata.phoenix_user_id;
  
  if (!phoenixUserId) return;

  const subscriptionData = {
    stripe_subscription_id: subscription.id,
    subscription_tier: determineSubscriptionTier(subscription),
    status: subscription.status === 'active' ? 'active' : 'inactive',
    current_period_start: new Date(subscription.current_period_start * 1000).toISOString(),
    current_period_end: new Date(subscription.current_period_end * 1000).toISOString(),
    updated_at: new Date().toISOString()
  };

  const { error } = await supabase
    .from('user_subscriptions')
    .update(subscriptionData)
    .eq('user_id', phoenixUserId);

  if (error) {
    console.error('❌ Error updating subscription:', error);
    throw error;
  }

  // Mettre à jour profil si nécessaire
  if (subscription.status === 'canceled' || subscription.status === 'unpaid') {
    await supabase
      .from('profiles')
      .update({ 
        subscription_tier: 'free',
        updated_at: new Date().toISOString()
      })
      .eq('id', phoenixUserId);
  }

  console.log(`✅ Subscription updated for user ${phoenixUserId}: ${subscription.status}`);
}

async function handleSubscriptionDeleted(subscription: Stripe.Subscription) {
  const metadata = subscription.metadata;
  const phoenixUserId = metadata.phoenix_user_id;
  
  if (!phoenixUserId) return;

  // Révoquer l'abonnement
  const { error: subError } = await supabase
    .from('user_subscriptions')
    .update({
      status: 'cancelled',
      updated_at: new Date().toISOString()
    })
    .eq('user_id', phoenixUserId);

  if (subError) {
    console.error('❌ Error cancelling subscription:', subError);
    throw subError;
  }

  // Remettre en gratuit
  const { error: profileError } = await supabase
    .from('profiles')
    .update({ 
      subscription_tier: 'free',
      updated_at: new Date().toISOString()
    })
    .eq('id', phoenixUserId);

  if (profileError) {
    console.error('❌ Error updating profile to free:', profileError);
  }

  console.log(`✅ Subscription cancelled for user ${phoenixUserId}`);
}

async function handlePaymentSucceeded(invoice: Stripe.Invoice) {
  const subscriptionId = invoice.subscription as string;
  
  if (subscriptionId) {
    // Récupérer l'abonnement pour obtenir les métadonnées
    const subscription = await stripe.subscriptions.retrieve(subscriptionId);
    const phoenixUserId = subscription.metadata.phoenix_user_id;
    
    if (phoenixUserId) {
      // Enregistrer le paiement réussi
      console.log(`💳 Payment succeeded for user ${phoenixUserId}: ${invoice.amount_paid / 100}€`);
      
      // S'assurer que l'abonnement est actif
      await supabase
        .from('user_subscriptions')
        .update({
          status: 'active',
          updated_at: new Date().toISOString()
        })
        .eq('user_id', phoenixUserId);
    }
  }
}

async function handlePaymentFailed(invoice: Stripe.Invoice) {
  const subscriptionId = invoice.subscription as string;
  
  if (subscriptionId) {
    const subscription = await stripe.subscriptions.retrieve(subscriptionId);
    const phoenixUserId = subscription.metadata.phoenix_user_id;
    
    if (phoenixUserId) {
      console.log(`❌ Payment failed for user ${phoenixUserId}`);
      
      // Marquer comme impayé
      await supabase
        .from('user_subscriptions')
        .update({
          status: 'past_due',
          updated_at: new Date().toISOString()
        })
        .eq('user_id', phoenixUserId);
    }
  }
}

function determineSubscriptionTier(subscription: Stripe.Subscription): string {
  const priceId = subscription.items.data[0]?.price?.id;
  
  // Mapping des Price IDs aux tiers
  const priceToTier: Record<string, string> = {
    'price_1RraUoDcM3VIYgvy0NXiKmKV': 'cv_premium',       // Phoenix CV Premium
    'price_1RraAcDcM3VIYgvyEBNFXfbR': 'letters_premium',  // Phoenix Letters Premium
    'price_1RraWhDcM3VIYgvyGykPghCc': 'pack_premium',     // Pack CV + Letters
  };

  return priceToTier[priceId!] || 'premium';
}