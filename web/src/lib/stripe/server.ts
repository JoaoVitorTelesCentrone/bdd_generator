import Stripe from "stripe";

// Instância singleton do Stripe para uso em Route Handlers e Server Actions
export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

// Verifica assinatura do webhook
export function constructWebhookEvent(
  payload: string | Buffer,
  signature: string,
): Stripe.Event {
  return stripe.webhooks.constructEvent(
    payload,
    signature,
    process.env.STRIPE_WEBHOOK_SECRET!,
  );
}
