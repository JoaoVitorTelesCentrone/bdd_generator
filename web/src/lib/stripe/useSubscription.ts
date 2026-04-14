"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { getPlan, type PlanId } from "./config";
import type { User } from "@supabase/supabase-js";

export interface SubscriptionState {
  planId: PlanId;
  status: string;
  currentPeriodEnd: string | null;
  loading: boolean;
}

export function useSubscription(user: User | null): SubscriptionState {
  const [state, setState] = useState<SubscriptionState>({
    planId: "free",
    status: "free",
    currentPeriodEnd: null,
    loading: true,
  });

  useEffect(() => {
    if (!user) {
      setState({ planId: "free", status: "free", currentPeriodEnd: null, loading: false });
      return;
    }

    const supabase = createClient();

    async function load() {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const { data } = await (supabase as any)
        .from("subscriptions")
        .select("plan_id, status, current_period_end")
        .eq("user_id", user!.id)
        .single();

      const planId = (data?.plan_id as PlanId) ?? "free";
      setState({
        planId,
        status:           data?.status ?? "free",
        currentPeriodEnd: data?.current_period_end ?? null,
        loading: false,
      });
    }

    load();
  }, [user]);

  return state;
}

// Helper para redirecionar para o checkout
export async function redirectToCheckout(priceId: string): Promise<void> {
  const res  = await fetch("/api/stripe/checkout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ priceId }),
  });
  const data = await res.json() as { url?: string; error?: string };
  if (data.url) window.location.href = data.url;
}

// Helper para abrir o portal de assinatura
export async function redirectToPortal(): Promise<void> {
  const res  = await fetch("/api/stripe/portal", { method: "POST" });
  const data = await res.json() as { url?: string; error?: string };
  if (data.url) window.location.href = data.url;
}
