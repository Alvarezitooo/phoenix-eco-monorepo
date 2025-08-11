import { NextApiRequest, NextApiResponse } from 'next';
import Stripe from 'stripe';
import { buffer } from 'micro';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY! as string, {
  apiVersion: '2025-07-30.basil',
});

// Anti-replay protection
const processedEvents = new Set<string>();
const EVENT_EXPIRY_TIME = 300000; // 5 minutes

// Rate limiting per IP
const rateLimitMap = new Map<string, { count: number; resetTime: number }>();
const RATE_LIMIT_MAX = 10; // 10 requests per minute
const RATE_LIMIT_WINDOW = 60000; // 1 minute

export const config = {
  api: {
    bodyParser: false,
  },
};

function getRateLimitKey(req: NextApiRequest): string {
  return (req.headers['x-forwarded-for'] as string) || req.socket.remoteAddress || 'unknown';
}

function checkRateLimit(clientKey: string): boolean {
  const now = Date.now();
  const clientData = rateLimitMap.get(clientKey);

  if (!clientData || now > clientData.resetTime) {
    rateLimitMap.set(clientKey, { count: 1, resetTime: now + RATE_LIMIT_WINDOW });
    return true;
  }

  if (clientData.count >= RATE_LIMIT_MAX) {
    return false;
  }

  clientData.count++;
  return true;
}

function cleanupOldEvents(): void {
  const now = Date.now();
  processedEvents.forEach((val) => {
    const [, timestamp] = val.split(':');
    if (now - parseInt(timestamp) > EVENT_EXPIRY_TIME) {
      processedEvents.delete(val);
    }
  });
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  // Rate limiting
  const clientKey = getRateLimitKey(req);
  if (!checkRateLimit(clientKey)) {
    return res.status(429).json({ error: 'Too Many Requests' });
  }

  try {
    const buf = await buffer(req);
    const sig = req.headers['stripe-signature'];
    const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

    // Validation des headers requis
    if (!sig) {
      return res.status(401).json({ error: 'Missing Stripe signature' });
    }

    if (!webhookSecret) {
      console.error('STRIPE_WEBHOOK_SECRET not configured');
      return res.status(500).json({ error: 'Server configuration error' });
    }

    let event: Stripe.Event;

    try {
      event = stripe.webhooks.constructEvent(buf, sig, webhookSecret);
    } catch (err: any) {
      console.error('Webhook signature verification failed', {
        error: err.message,
        clientIP: clientKey,
        timestamp: new Date().toISOString(),
      });
      return res.status(401).json({ error: 'Invalid signature' });
    }

    // Anti-replay protection
    const eventKey = `${event.id}:${event.created * 1000}`;
    if (processedEvents.has(eventKey)) {
      console.warn('Duplicate event detected', { eventId: event.id });
      return res.status(409).json({ error: 'Event already processed' });
    }

    // Vérification de l'âge de l'événement
    const eventAge = Date.now() - event.created * 1000;
    if (eventAge > EVENT_EXPIRY_TIME) {
      console.warn('Event too old', { eventId: event.id, age: eventAge });
      return res.status(400).json({ error: 'Event expired' });
    }

    processedEvents.add(eventKey);
    cleanupOldEvents();

    // Handle the event avec logging sécurisé
    const eventHandled = await handleStripeEvent(event);

    if (!eventHandled) {
      console.warn('Unhandled event type', { type: event.type, id: event.id });
    }

    return res.status(200).json({ received: true });
  } catch (error: any) {
    console.error('Webhook processing error', {
      error: error.message,
      clientIP: getRateLimitKey(req),
      timestamp: new Date().toISOString(),
    });
    return res.status(500).json({ error: 'Internal server error' });
  }
}

async function handleStripeEvent(event: Stripe.Event): Promise<boolean> {
  try {
    switch (event.type) {
      case 'checkout.session.completed':
        const checkoutSession = event.data.object as Stripe.Checkout.Session;
        console.log('Checkout session completed', {
          sessionId: checkoutSession.id,
          customerId: checkoutSession.customer,
        });
        // Publish pending activation (await subscription events for final state)
        await publishSubscriptionEvent({
          type: 'SUBSCRIPTION_ACTIVATED',
          userId: extractUserIdFromSession(checkoutSession),
          planId: extractPlanIdFromSession(checkoutSession),
          status: 'pending',
          payload: {
            session_id: checkoutSession.id,
            customer_id: checkoutSession.customer,
          },
        });
        return true;

      case 'customer.subscription.created':
        const subscriptionCreated = event.data.object as Stripe.Subscription;
        console.log('Subscription created', {
          subscriptionId: subscriptionCreated.id,
          customerId: subscriptionCreated.customer,
          status: subscriptionCreated.status,
        });
        await publishSubscriptionEvent({
          type: 'SUBSCRIPTION_ACTIVATED',
          userId: extractUserIdFromSubscription(subscriptionCreated),
          planId: extractPlanIdFromSubscription(subscriptionCreated),
          status: subscriptionCreated.status,
          payload: {
            subscription_id: subscriptionCreated.id,
            customer_id: subscriptionCreated.customer,
          },
        });
        return true;

      case 'customer.subscription.updated':
        const subscriptionUpdated = event.data.object as Stripe.Subscription;
        console.log('Subscription updated', {
          subscriptionId: subscriptionUpdated.id,
          customerId: subscriptionUpdated.customer,
          status: subscriptionUpdated.status,
        });
        await publishSubscriptionEvent({
          type: 'SUBSCRIPTION_UPDATED',
          userId: extractUserIdFromSubscription(subscriptionUpdated),
          planId: extractPlanIdFromSubscription(subscriptionUpdated),
          status: subscriptionUpdated.status,
          payload: {
            subscription_id: subscriptionUpdated.id,
            customer_id: subscriptionUpdated.customer,
          },
        });
        return true;

      case 'customer.subscription.deleted':
        const subscriptionDeleted = event.data.object as Stripe.Subscription;
        console.log('Subscription deleted', {
          subscriptionId: subscriptionDeleted.id,
          customerId: subscriptionDeleted.customer,
        });
        await publishSubscriptionEvent({
          type: 'SUBSCRIPTION_CANCELLED',
          userId: extractUserIdFromSubscription(subscriptionDeleted),
          planId: extractPlanIdFromSubscription(subscriptionDeleted),
          status: 'canceled',
          payload: {
            subscription_id: subscriptionDeleted.id,
            customer_id: subscriptionDeleted.customer,
          },
        });
        return true;

      case 'invoice.payment_succeeded':
        const paymentSucceeded = event.data.object as Stripe.Invoice;
        console.log('Payment succeeded', {
          invoiceId: paymentSucceeded.id,
          customerId: paymentSucceeded.customer,
          amount: paymentSucceeded.amount_paid,
        });
        await publishSubscriptionEvent({
          type: 'SUBSCRIPTION_UPDATED',
          userId: extractUserIdFromInvoice(paymentSucceeded),
          planId: extractPlanIdFromInvoice(paymentSucceeded),
          status: 'payment_succeeded',
          payload: {
            invoice_id: paymentSucceeded.id,
            customer_id: paymentSucceeded.customer,
            amount: paymentSucceeded.amount_paid,
          },
        });
        return true;

      case 'invoice.payment_failed':
        const paymentFailed = event.data.object as Stripe.Invoice;
        console.log('Payment failed', {
          invoiceId: paymentFailed.id,
          customerId: paymentFailed.customer,
          amount: paymentFailed.amount_due,
        });
        await publishSubscriptionEvent({
          type: 'SUBSCRIPTION_UPDATED',
          userId: extractUserIdFromInvoice(paymentFailed),
          planId: extractPlanIdFromInvoice(paymentFailed),
          status: 'payment_failed',
          payload: {
            invoice_id: paymentFailed.id,
            customer_id: paymentFailed.customer,
            amount: paymentFailed.amount_due,
          },
        });
        return true;

      default:
        return false;
    }
  } catch (error: any) {
    console.error('Event handling error', {
      eventType: event.type,
      eventId: event.id,
      error: error.message,
    });
    return false;
  }
}

type SubscriptionEventPayload = {
  type: 'SUBSCRIPTION_ACTIVATED' | 'SUBSCRIPTION_UPDATED' | 'SUBSCRIPTION_CANCELLED';
  userId: string | null;
  planId: string | null;
  status: string;
  payload: Record<string, any>;
};

async function publishSubscriptionEvent(data: SubscriptionEventPayload): Promise<void> {
  try {
    const SUPABASE_URL = process.env.SUPABASE_URL;
    const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

    if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
      console.warn('Supabase env not configured; skipping event publish');
      return;
    }

    if (!data.userId) {
      console.warn('Missing userId in subscription event; skipping publish');
      return;
    }

    const eventBody = {
      stream_id: data.userId,
      event_type: data.type,
      payload: {
        ...data.payload,
        plan_id: data.planId,
        status: data.status,
        source: 'stripe',
      },
      app_source: 'website',
      timestamp: new Date().toISOString(),
      metadata: {
        bridge_version: 'v1',
        published_at: new Date().toISOString(),
      },
    };

    const resp = await fetch(`${SUPABASE_URL}/rest/v1/events`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        apikey: SUPABASE_SERVICE_ROLE_KEY,
        Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
        Prefer: 'return=representation',
      },
      body: JSON.stringify(eventBody),
    });

    if (!resp.ok) {
      const text = await resp.text();
      console.error('Supabase publish failed', { status: resp.status, text });
    }
  } catch (e: any) {
    console.error('Supabase publish error', { error: e.message });
  }
}

function extractUserIdFromSession(session: Stripe.Checkout.Session): string | null {
  // Prefer metadata phoenix_user_id, fallback to client_reference_id
  const md = (session.metadata || {}) as Record<string, string>;
  if (md['phoenix_user_id']) return md['phoenix_user_id'];
  if (session.client_reference_id) return session.client_reference_id;
  return null;
}

function extractPlanIdFromSession(session: Stripe.Checkout.Session): string | null {
  const md = (session.metadata || {}) as Record<string, string>;
  if (md['plan_id']) return md['plan_id'];
  // When not expanded, plan/price may not be available
  return null;
}

function extractUserIdFromSubscription(sub: Stripe.Subscription): string | null {
  const md = (sub.metadata || {}) as Record<string, string>;
  if (md['phoenix_user_id']) return md['phoenix_user_id'];
  // Try default payment method billing details email mapping if needed (not recommended without mapping)
  return null;
}

function extractPlanIdFromSubscription(sub: Stripe.Subscription): string | null {
  try {
    const item = sub.items?.data?.[0];
    // price id is stable reference for plan
    // @ts-ignore
    return item?.price?.id || null;
  } catch {
    return null;
  }
}

function extractUserIdFromInvoice(inv: Stripe.Invoice): string | null {
  // Invoices do not carry metadata by default; rely on subscription
  // @ts-ignore
  const sub = inv.subscription as unknown as Stripe.Subscription | string | null;
  if (typeof sub === 'string' || !sub) return null;
  return extractUserIdFromSubscription(sub);
}

function extractPlanIdFromInvoice(inv: Stripe.Invoice): string | null {
  try {
    // @ts-ignore
    const sub = inv.subscription as unknown as Stripe.Subscription | string | null;
    if (typeof sub === 'string' || !sub) return null;
    return extractPlanIdFromSubscription(sub);
  } catch {
    return null;
  }
}
