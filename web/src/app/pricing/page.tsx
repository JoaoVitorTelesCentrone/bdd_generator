"use client";

import { useState } from "react";
import { useUser } from "@/lib/supabase/useUser";
import { useSubscription, redirectToCheckout, redirectToPortal } from "@/lib/stripe/useSubscription";
import { PLANS } from "@/lib/stripe/config";
import { CheckCircle, Zap, Terminal } from "lucide-react";
import Link from "next/link";

export default function PricingPage() {
  const { user } = useUser();
  const subscription = useSubscription(user);
  const [loadingCheckout, setLoadingCheckout] = useState(false);

  const isCurrentPro = subscription.planId === "pro" && !subscription.loading;

  async function handleUpgrade() {
    if (!user) { window.location.href = "/login?redirect=/pricing"; return; }
    setLoadingCheckout(true);
    try {
      if (isCurrentPro) await redirectToPortal();
      else await redirectToCheckout(PLANS.pro.priceId as string);
    } finally {
      setLoadingCheckout(false);
    }
  }

  return (
    <div className="flex-1 flex flex-col">
      <div className="border-b border-[#a3fb73]/10 bg-[#243d2c]/20">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-5">
          <div className="flex items-baseline gap-3">
            <span className="text-[#5a7a65] font-mono text-sm select-none">$</span>
            <h1 className="text-lg font-mono font-semibold text-[#a3fb73] tracking-tight">
              bist pricing
              <span className="text-[#5a7a65] font-normal"> --plans</span>
            </h1>
          </div>
          <p className="text-sm text-[#5a7a65] font-mono mt-1.5 ml-5">
            simples, sem surpresa — pague só o que usar
          </p>
        </div>
      </div>

      <div className="flex-1 max-w-5xl mx-auto w-full px-4 sm:px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto">

          {/* Free plan */}
          <div className="card p-6 space-y-6 flex flex-col">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-mono text-[#5a7a65] tracking-widest uppercase">free</span>
                {subscription.planId === "free" && !subscription.loading && (
                  <span className="text-[9px] font-mono bg-[#a3fb73]/15 text-[#a3fb73] px-2 py-0.5 rounded-full border border-[#a3fb73]/25">
                    plano atual
                  </span>
                )}
              </div>
              <p className="font-mono text-4xl font-bold text-[#eef9e8]">R$ 0</p>
              <p className="text-xs text-[#5a7a65] font-mono mt-1">para sempre</p>
            </div>

            <ul className="space-y-2.5 flex-1">
              {PLANS.free.features.map(f => (
                <li key={f} className="flex items-center gap-2.5 text-sm font-mono text-[#7a9b87]">
                  <CheckCircle className="w-3.5 h-3.5 text-[#5a7a65] flex-shrink-0" />
                  {f}
                </li>
              ))}
              <li className="flex items-center gap-2.5 text-sm font-mono text-[#3d5a44] line-through">
                <CheckCircle className="w-3.5 h-3.5 text-[#3d5a44] flex-shrink-0" />
                Claude (Sonnet, Opus, Haiku)
              </li>
              <li className="flex items-center gap-2.5 text-sm font-mono text-[#3d5a44] line-through">
                <CheckCircle className="w-3.5 h-3.5 text-[#3d5a44] flex-shrink-0" />
                Auto-Research
              </li>
            </ul>

            <Link
              href="/generate"
              className="btn-secondary text-sm py-2.5 text-center w-full"
            >
              <Terminal className="w-4 h-4" />
              começar grátis
            </Link>
          </div>

          {/* Pro plan */}
          <div className="card p-6 space-y-6 flex flex-col border-[#a3fb73]/30
                          shadow-[0_0_40px_rgba(163,251,115,0.06)] relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 rounded-full
                            bg-[#a3fb73]/4 blur-[60px] pointer-events-none" />

            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-mono text-[#a3fb73] tracking-widest uppercase">pro</span>
                {isCurrentPro && (
                  <span className="text-[9px] font-mono bg-[#a3fb73]/15 text-[#a3fb73] px-2 py-0.5 rounded-full border border-[#a3fb73]/25">
                    plano atual
                  </span>
                )}
              </div>
              <p className="font-mono text-4xl font-bold text-[#eef9e8]">
                R$ {PLANS.pro.price}
              </p>
              <p className="text-xs text-[#5a7a65] font-mono mt-1">por mês</p>
            </div>

            <ul className="space-y-2.5 flex-1">
              {PLANS.pro.features.map(f => (
                <li key={f} className="flex items-center gap-2.5 text-sm font-mono text-[#c8e8c8]">
                  <CheckCircle className="w-3.5 h-3.5 text-[#a3fb73] flex-shrink-0" />
                  {f}
                </li>
              ))}
            </ul>

            <button
              onClick={handleUpgrade}
              disabled={loadingCheckout || subscription.loading}
              className="btn-primary text-sm py-2.5 w-full
                         shadow-[0_0_30px_rgba(163,251,115,0.15)]
                         disabled:opacity-60 disabled:cursor-not-allowed"
            >
              <Zap className="w-4 h-4" />
              {loadingCheckout
                ? "redirecionando..."
                : isCurrentPro
                  ? "gerenciar assinatura"
                  : "assinar pro"
              }
            </button>

            {!user && (
              <p className="text-[10px] font-mono text-[#3d5a44] text-center -mt-3">
                login necessário para assinar
              </p>
            )}
          </div>
        </div>

        {/* FAQ */}
        <div className="mt-16 max-w-2xl mx-auto space-y-4">
          <p className="text-xs font-mono text-[#3d5a44] tracking-widest uppercase mb-6">// perguntas frequentes</p>
          {[
            ["O free é realmente grátis?", "Sim. 10 gerações por mês, sem cartão de crédito."],
            ["Posso cancelar o Pro a qualquer momento?", "Sim. O acesso fica ativo até o fim do período pago."],
            ["O que acontece quando esgoto as gerações free?", "Você vê um aviso e pode fazer upgrade ou aguardar o próximo mês."],
            ["Gemini ou Claude — qual é melhor?", "Para a maioria dos casos, Gemini 2.5 Flash entrega ótima qualidade. Claude Sonnet é superior em stories complexas."],
          ].map(([q, a]) => (
            <div key={q} className="card p-4 space-y-1.5">
              <p className="text-sm font-mono text-[#eef9e8]">{q}</p>
              <p className="text-xs font-mono text-[#5a7a65]">{a}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
