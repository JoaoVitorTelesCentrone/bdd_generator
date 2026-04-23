import Link from "next/link";
import { Check, Zap, Building2, ArrowRight } from "lucide-react";
import { PlanCheckoutButton } from "@/components/PlanCheckoutButton";

const plans = [
  {
    id: "free",
    name: "Free",
    price: "R$ 0",
    period: "para sempre",
    description: "Para explorar e prototipar",
    highlight: false,
    cta: "Começar grátis",
    ctaHref: "/generate",
    features: [
      "50.000 tokens/mês",
      "Modelo Gemini Flash",
      "Geração de BDD",
      "Avaliação de qualidade",
      "Histórico local (30 dias)",
    ],
    missing: [
      "Modelos Pro/Claude",
      "Execução E2E (BIST)",
      "Histórico ilimitado",
      "API CLI",
    ],
  },
  {
    id: "pro",
    name: "Pro",
    price: "R$ 97",
    period: "por mês",
    description: "Para times que levam qualidade a sério",
    highlight: true,
    cta: "Assinar Pro",
    ctaHref: "/api/stripe/checkout?plan=pro",
    features: [
      "Tokens ilimitados",
      "Todos os modelos (Flash, Pro, Claude)",
      "Execução E2E com BIST",
      "Auto-research",
      "Pipeline completo (batch + study)",
      "Histórico ilimitado no banco",
      "Acesso à API CLI",
      "Suporte prioritário",
    ],
    missing: [],
  },
  {
    id: "enterprise",
    name: "Enterprise",
    price: "Sob consulta",
    period: "",
    description: "Para empresas com demandas customizadas",
    highlight: false,
    cta: "Falar com vendas",
    ctaHref: "mailto:joaovtcentrone@gmail.com?subject=BIST Enterprise",
    features: [
      "Tudo do Pro",
      "SSO / SAML",
      "Multi-tenant",
      "SLA garantido",
      "Deploy on-premise",
      "Integrações customizadas",
      "Gerente de conta dedicado",
    ],
    missing: [],
  },
];

export default function PlanosPage() {
  return (
    <div className="flex-1 py-20 px-4 sm:px-8">
      <div className="max-w-5xl mx-auto space-y-14">

        <div className="text-center space-y-4 max-w-2xl mx-auto">
          <p className="text-xs font-code text-bist-muted uppercase tracking-widest">Planos</p>
          <h1 className="text-3xl sm:text-4xl font-bold text-bist-primary leading-tight">
            Escolha seu nível de inteligência
          </h1>
          <p className="text-sm text-bist-muted leading-relaxed">
            Do primeiro BDD gerado ao pipeline completo de qualidade com insights estratégicos.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={[
                "card p-6 flex flex-col gap-6 relative",
                plan.highlight
                  ? "border-[#a3fb73]/50 ring-1 ring-[#a3fb73]/30 shadow-lg"
                  : "",
              ].join(" ")}
            >
              {plan.highlight && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="bg-[#a3fb73] text-bist-primary text-[10px] font-bold px-3 py-1 rounded-full tracking-widest uppercase flex items-center gap-1">
                    <Zap className="w-3 h-3" /> Mais popular
                  </span>
                </div>
              )}

              <div className="space-y-1">
                <p className="text-xs font-code text-bist-muted uppercase tracking-widest">{plan.name}</p>
                <p className="text-3xl font-bold text-bist-primary">{plan.price}</p>
                {plan.period && <p className="text-xs text-bist-dim">{plan.period}</p>}
                <p className="text-xs text-bist-muted pt-1 leading-relaxed">{plan.description}</p>
              </div>

              <ul className="space-y-2 flex-1">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-sm text-bist-mid">
                    <Check className="w-3.5 h-3.5 text-[#2D6A3F] flex-shrink-0 mt-0.5" />
                    {f}
                  </li>
                ))}
                {plan.missing.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-sm text-bist-dim line-through">
                    <span className="w-3.5 h-3.5 flex-shrink-0 mt-0.5 text-center text-xs">—</span>
                    {f}
                  </li>
                ))}
              </ul>

              {plan.ctaHref.startsWith("mailto") ? (
                <a
                  href={plan.ctaHref}
                  className={plan.highlight ? "btn-primary text-sm py-2.5 text-center flex items-center justify-center gap-2" : "btn-secondary text-sm py-2.5 text-center flex items-center justify-center gap-2"}
                >
                  <Building2 className="w-3.5 h-3.5" /> {plan.cta}
                </a>
              ) : plan.id === "pro" ? (
                <PlanCheckoutButton
                  planId="pro"
                  label={plan.cta}
                  className={`w-full btn-primary text-sm py-2.5 text-center flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed`}
                />
              ) : (
                <Link
                  href={plan.ctaHref}
                  className={plan.highlight ? "btn-primary text-sm py-2.5 text-center flex items-center justify-center gap-2" : "btn-secondary text-sm py-2.5 text-center flex items-center justify-center gap-2"}
                >
                  {plan.cta} <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              )}
            </div>
          ))}
        </div>

        <div className="card p-8 text-center space-y-3 bg-bist-surface2">
          <p className="text-sm font-semibold text-bist-primary">Dúvidas antes de assinar?</p>
          <p className="text-xs text-bist-muted max-w-md mx-auto leading-relaxed">
            Todos os planos incluem geração de BDD com auto-refinamento e avaliação por 4 métricas.
            O Pro desbloqueia o ecossistema completo.
          </p>
          <a
            href="mailto:joaovtcentrone@gmail.com?subject=Duvida BIST"
            className="inline-flex items-center gap-1.5 text-xs text-bist-muted hover:text-bist-primary transition-colors"
          >
            Falar com o time →
          </a>
        </div>

      </div>
    </div>
  );
}
