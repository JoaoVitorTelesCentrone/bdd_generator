import { NextResponse, type NextRequest } from "next/server";
import { stripe } from "@/lib/stripe/server";
import { createClient } from "@/lib/supabase/server";

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();

    if (!user) {
      return NextResponse.json({ error: "Não autenticado" }, { status: 401 });
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const { data: subscription } = await (supabase as any)
      .from("subscriptions")
      .select("stripe_customer_id")
      .eq("user_id", user.id)
      .single();

    if (!subscription?.stripe_customer_id) {
      return NextResponse.json({ error: "Nenhuma assinatura encontrada" }, { status: 404 });
    }

    const origin = request.headers.get("origin") ?? "http://localhost:3001";

    const portalSession = await stripe.billingPortal.sessions.create({
      customer: subscription.stripe_customer_id,
      return_url: `${origin}/`,
    });

    return NextResponse.json({ url: portalSession.url });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Erro interno";
    console.error("[stripe/portal]", message);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
