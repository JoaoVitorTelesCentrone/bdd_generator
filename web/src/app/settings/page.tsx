"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Settings, Zap, RotateCcw, ExternalLink, Loader2 } from "lucide-react";
import { useUser } from "@/lib/supabase/useUser";
import type { QuotaInfo } from "@/lib/cli/quota";

function QuotaBar({ used, limit }: { used: number; limit: number }) {
  const pct = limit <= 0 ? 0 : Math.min(100, (used / limit) * 100);
  const color =
    pct >= 90 ? "bg-red-500" :
    pct >= 70 ? "bg-amber-400" :
                "bg-[#a3fb73]";
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-xs text-bist-muted">
        <span>{used.toLocaleString("pt-BR")} tokens usados</span>
        <span>{limit.toLocaleString("pt-BR")} limite</span>
      </div>
      <div className="h-2 bg-bist-border rounded-full overflow-hidden">
        <div
          className={`h-full ${color} rounded-full transition-all duration-500`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className="text-[10px] text-bist-dim">{pct.toFixed(1)}% utilizado este mês</p>
    </div>
  );
}

export default function SettingsPage() {
  const { user, loading: userLoading } = useUser();
  const [quota, setQuota]   = useState<QuotaInfo | null>(null);
  const [quotaLoading, setQuotaLoading] = useState(false);
  const [quotaError, setQuotaError]     = useState("");

  useEffect(() => {
    if (!user) return;
    setQuotaLoading(true);
    fetch("/api/user/quota")
      .then(r => r.ok ? r.json() : Promise.reject(r.statusText))
      .then(setQuota)
      .catch(e => setQuotaError(String(e)))
      .finally(() => setQuotaLoading(false));
  }, [user]);

  if (userLoading) return (
    <div className="flex-1 flex items-center justify-center py-20">
      <Loader2 className="w-5 h-5 animate-spin text-bist-muted" />
    </div>
  );

  return (
    <div className="flex-1 max-w-2xl mx-auto px-4 sm:px-6 py-10 space-y-8">

      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <Settings className="w-4 h-4 text-bist-muted" />
          <h1 className="text-lg font-semibold text-bist-primary">Configurações</h1>
        </div>
        <p className="text-xs text-bist-muted">Conta, plano e uso de tokens</p>
      </div>

      {/* Conta */}
      <div className="card p-5 space-y-4">
        <p className="text-xs font-code text-bist-dim uppercase tracking-widest">Conta</p>
        {user ? (
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-bist-muted">Email</span>
              <span className="text-bist-primary font-medium">{user.email}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-bist-muted">Nome</span>
              <span className="text-bist-primary">{(user.user_metadata?.full_name as string) ?? "—"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-bist-muted">ID</span>
              <span className="font-code text-xs text-bist-dim">{user.id.slice(0, 16)}…</span>
            </div>
          </div>
        ) : (
          <div className="text-center py-4 space-y-3">
            <p className="text-sm text-bist-muted">Faça login para ver suas informações de conta.</p>
            <Link href="/login" className="btn-primary text-sm inline-flex items-center gap-2">
              Entrar
            </Link>
          </div>
        )}
      </div>

      {/* Plano & Quota */}
      {user && (
        <div className="card p-5 space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-xs font-code text-bist-dim uppercase tracking-widest">Plano & Uso</p>
            {quota && (
              <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${
                quota.plan === "pro"
                  ? "text-[#2D6A3F] bg-[#a3fb73]/15 border-[#a3fb73]/30"
                  : "text-bist-muted bg-bist-surface2 border-bist-border"
              }`}>
                {quota.plan.toUpperCase()}
              </span>
            )}
          </div>

          {quotaLoading && (
            <div className="flex items-center gap-2 text-sm text-bist-muted">
              <Loader2 className="w-3.5 h-3.5 animate-spin" /> Carregando...
            </div>
          )}

          {quotaError && (
            <p className="text-xs text-red-500">{quotaError}</p>
          )}

          {quota && !quotaLoading && (
            <div className="space-y-4">
              {quota.tokens_limit === -1 ? (
                <div className="flex items-center gap-2 text-sm text-[#2D6A3F]">
                  <Zap className="w-3.5 h-3.5" />
                  Tokens ilimitados (plano Pro)
                </div>
              ) : (
                <QuotaBar used={quota.tokens_used} limit={quota.tokens_limit} />
              )}

              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="card-subtle p-3 rounded-lg">
                  <p className="text-[10px] font-code text-bist-dim uppercase tracking-widest mb-1">Gerações</p>
                  <p className="text-lg font-bold text-bist-primary">{quota.generations_used}</p>
                  <p className="text-[10px] text-bist-muted">este mês</p>
                </div>
                <div className="card-subtle p-3 rounded-lg">
                  <p className="text-[10px] font-code text-bist-dim uppercase tracking-widest mb-1">Reset em</p>
                  <p className="text-sm font-medium text-bist-primary">
                    {new Date(quota.reset_at).toLocaleDateString("pt-BR", { day: "2-digit", month: "short" })}
                  </p>
                  <p className="text-[10px] text-bist-muted">próximo ciclo</p>
                </div>
              </div>

              {quota.plan === "free" && (
                <div className="border border-[#a3fb73]/30 bg-[#a3fb73]/5 rounded-lg p-4 space-y-2">
                  <p className="text-sm font-medium text-bist-primary">Desbloqueie o plano Pro</p>
                  <p className="text-xs text-bist-muted leading-relaxed">
                    Tokens ilimitados, execução E2E e pipeline completo.
                  </p>
                  <Link href="/planos" className="btn-primary text-xs inline-flex items-center gap-1.5 mt-1">
                    <Zap className="w-3 h-3" /> Ver planos
                  </Link>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Links úteis */}
      <div className="card p-5 space-y-3">
        <p className="text-xs font-code text-bist-dim uppercase tracking-widest">Recursos</p>
        <div className="space-y-1">
          {[
            { label: "Ver planos e preços", href: "/planos" },
            { label: "Histórico de gerações", href: "/history" },
            { label: "Estatísticas de execução", href: "/stats" },
          ].map(({ label, href }) => (
            <Link
              key={href}
              href={href}
              className="flex items-center justify-between px-3 py-2.5 rounded-lg hover:bg-bist-surface2 transition-colors text-sm text-bist-muted hover:text-bist-primary"
            >
              {label}
              <ExternalLink className="w-3 h-3" />
            </Link>
          ))}
        </div>
      </div>

      {/* Sair */}
      {user && (
        <div className="card p-5 space-y-3">
          <p className="text-xs font-code text-bist-dim uppercase tracking-widest">Sessão</p>
          <form action="/auth/signout" method="POST">
            <button
              type="submit"
              className="flex items-center gap-2 text-sm text-bist-muted hover:text-red-600 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" /> Encerrar sessão
            </button>
          </form>
        </div>
      )}

    </div>
  );
}
