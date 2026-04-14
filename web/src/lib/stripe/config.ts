// ─── Planos e preços ─────────────────────────────────────────────────────────
// Substitua os price IDs pelos seus do Stripe Dashboard → Products

export const PLANS = {
  free: {
    id: "free",
    name: "Free",
    description: "Para experimentar",
    price: 0,
    priceId: null,
    limits: {
      generationsPerMonth: 10,
      modelsAllowed: ["flash", "flash-lite"],
      researchEnabled: false,
      batchEnabled: false,
    },
    features: [
      "10 gerações por mês",
      "Modelos Flash",
      "Score de qualidade",
      "Download .feature",
    ],
  },
  pro: {
    id: "pro",
    name: "Pro",
    description: "Para uso profissional",
    price: 29,           // R$ 29/mês
    priceId: process.env.NEXT_PUBLIC_STRIPE_PRICE_PRO ?? "price_COLOQUE_AQUI",
    limits: {
      generationsPerMonth: Infinity,
      modelsAllowed: ["flash", "flash-lite", "pro", "sonnet", "opus", "haiku"],
      researchEnabled: true,
      batchEnabled: true,
    },
    features: [
      "Gerações ilimitadas",
      "Todos os modelos (Gemini + Claude)",
      "Auto-Research",
      "Until-Converged",
      "Histórico completo",
    ],
  },
} as const;

export type PlanId = keyof typeof PLANS;

export function getPlan(planId: string | null | undefined): typeof PLANS["free"] | typeof PLANS["pro"] {
  if (planId === "pro") return PLANS.pro;
  return PLANS.free;
}

export function canUseModel(planId: string | null | undefined, modelId: string): boolean {
  const plan = getPlan(planId);
  return (plan.limits.modelsAllowed as readonly string[]).includes(modelId);
}

export function canUseResearch(planId: string | null | undefined): boolean {
  return getPlan(planId).limits.researchEnabled;
}
