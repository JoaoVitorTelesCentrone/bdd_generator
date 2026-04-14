import { NextResponse, type NextRequest } from "next/server";
import { constructWebhookEvent } from "@/lib/stripe/server";
import { createClient } from "@/lib/supabase/server";
import type Stripe from "stripe";

// Desabilita o body parser do Next.js — o Stripe precisa do raw body para validar a assinatura
export const runtime = "nodejs";

export async function POST(request: NextRequest) {
  const payload   = await request.text();
  const signature = request.headers.get("stripe-signature");

  if (!signature) {
    return NextResponse.json({ error: "Sem assinatura" }, { status: 400 });
  }

  let event: Stripe.Event;
  try {
    event = constructWebhookEvent(payload, signature);
  } catch (err) {
    const msg = err instanceof Error ? err.message : "Assinatura inválida";
    console.error("[webhook] Erro de validação:", msg);
    return NextResponse.json({ error: msg }, { status: 400 });
  }

  const supabase = await createClient();

  try {
    switch (event.type) {

      // ── Checkout concluído ───────────────────────────────────────────────
      case "checkout.session.completed": {
        const session = event.data.object as Stripe.Checkout.Session;
        const userId  = session.metadata?.supabase_user_id;
        if (!userId || !session.subscription) break;

        await upsertSubscription(supabase, {
          userId,
          stripeCustomerId:    session.customer as string,
          stripeSubscriptionId: session.subscription as string,
          status: "active",
          planId: "pro",
        });
        break;
      }

      // ── Renovação / mudança de plano ─────────────────────────────────────
      case "customer.subscription.updated": {
        const sub    = event.data.object as Stripe.Subscription;
        const userId = sub.metadata?.supabase_user_id;
        if (!userId) break;

        const status = sub.status === "active" ? "active" : "inactive";
        await upsertSubscription(supabase, {
          userId,
          stripeCustomerId:    sub.customer as string,
          stripeSubscriptionId: sub.id,
          status,
          planId: status === "active" ? "pro" : "free",
          currentPeriodEnd: new Date((sub as unknown as { current_period_end: number }).current_period_end * 1000).toISOString(),
        });
        break;
      }

      // ── Cancelamento / expiração ─────────────────────────────────────────
      case "customer.subscription.deleted": {
        const sub    = event.data.object as Stripe.Subscription;
        const userId = sub.metadata?.supabase_user_id;
        if (!userId) break;

        await upsertSubscription(supabase, {
          userId,
          stripeCustomerId:    sub.customer as string,
          stripeSubscriptionId: sub.id,
          status: "cancelled",
          planId: "free",
        });
        break;
      }

      // ── Falha no pagamento ───────────────────────────────────────────────
      case "invoice.payment_failed": {
        const invoice = event.data.object as Stripe.Invoice;
        const userId  = (invoice as unknown as { subscription_details?: { metadata?: Record<string, string> } })
          .subscription_details?.metadata?.supabase_user_id;
        if (!userId) break;

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        await (supabase as any)
          .from("subscriptions")
          .update({ status: "past_due" })
          .eq("user_id", userId);
        break;
      }

      default:
        // Evento não tratado — ignora silenciosamente
        break;
    }
  } catch (err) {
    console.error(`[webhook] Erro ao processar ${event.type}:`, err);
    return NextResponse.json({ error: "Erro interno" }, { status: 500 });
  }

  return NextResponse.json({ received: true });
}

// ─── Helper ──────────────────────────────────────────────────────────────────

async function upsertSubscription(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  supabase: any,
  data: {
    userId: string;
    stripeCustomerId: string;
    stripeSubscriptionId: string;
    status: string;
    planId: string;
    currentPeriodEnd?: string;
  },
) {
  const row = {
    user_id:                data.userId,
    stripe_customer_id:     data.stripeCustomerId,
    stripe_subscription_id: data.stripeSubscriptionId,
    status:                 data.status,
    plan_id:                data.planId,
    ...(data.currentPeriodEnd ? { current_period_end: data.currentPeriodEnd } : {}),
    updated_at:             new Date().toISOString(),
  };

  await supabase
    .from("subscriptions")
    .upsert(row, { onConflict: "user_id" });
}
