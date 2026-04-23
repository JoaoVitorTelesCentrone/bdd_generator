"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Loader2 } from "lucide-react";
import { PLANS } from "@/lib/stripe/config";

interface Props {
  planId: keyof typeof PLANS;
  label: string;
  className: string;
}

export function PlanCheckoutButton({ planId, label, className }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState<string | null>(null);
  const router                = useRouter();

  async function handleCheckout() {
    const plan = PLANS[planId];
    if (!plan.priceId || plan.priceId === "price_COLOQUE_AQUI") {
      setError("Plano ainda não disponível. Volte em breve.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res  = await fetch("/api/stripe/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ priceId: plan.priceId }),
      });
      const data = await res.json() as { url?: string; error?: string };

      if (res.status === 401) {
        router.push("/login?next=/planos");
        return;
      }

      if (!res.ok || data.error) {
        setError(data.error ?? "Erro ao iniciar checkout.");
        return;
      }

      if (data.url) {
        window.location.href = data.url;
      }
    } catch {
      setError("Não foi possível conectar. Tente novamente.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-2">
      <button
        onClick={handleCheckout}
        disabled={loading}
        className={className}
      >
        {loading
          ? <Loader2 className="w-4 h-4 animate-spin" />
          : <>{label} <ArrowRight className="w-3.5 h-3.5" /></>
        }
      </button>
      {error && (
        <p className="text-xs text-red-500 text-center">{error}</p>
      )}
    </div>
  );
}
