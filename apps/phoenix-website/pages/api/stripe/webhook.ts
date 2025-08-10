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
        // TODO: Activer compte premium utilisateur
        return true;

      case 'customer.subscription.created':
        const subscriptionCreated = event.data.object as Stripe.Subscription;
        console.log('Subscription created', {
          subscriptionId: subscriptionCreated.id,
          customerId: subscriptionCreated.customer,
          status: subscriptionCreated.status,
        });
        // TODO: Traitement création abonnement
        return true;

      case 'customer.subscription.updated':
        const subscriptionUpdated = event.data.object as Stripe.Subscription;
        console.log('Subscription updated', {
          subscriptionId: subscriptionUpdated.id,
          customerId: subscriptionUpdated.customer,
          status: subscriptionUpdated.status,
        });
        // TODO: Traitement mise à jour abonnement
        return true;

      case 'customer.subscription.deleted':
        const subscriptionDeleted = event.data.object as Stripe.Subscription;
        console.log('Subscription deleted', {
          subscriptionId: subscriptionDeleted.id,
          customerId: subscriptionDeleted.customer,
        });
        // TODO: Désactiver compte premium utilisateur
        return true;

      case 'invoice.payment_succeeded':
        const paymentSucceeded = event.data.object as Stripe.Invoice;
        console.log('Payment succeeded', {
          invoiceId: paymentSucceeded.id,
          customerId: paymentSucceeded.customer,
          amount: paymentSucceeded.amount_paid,
        });
        // TODO: Confirmer paiement
        return true;

      case 'invoice.payment_failed':
        const paymentFailed = event.data.object as Stripe.Invoice;
        console.log('Payment failed', {
          invoiceId: paymentFailed.id,
          customerId: paymentFailed.customer,
          amount: paymentFailed.amount_due,
        });
        // TODO: Gérer échec paiement
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
