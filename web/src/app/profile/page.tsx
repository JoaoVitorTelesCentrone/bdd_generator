"use client";

import { useState } from "react";
import Link from "next/link";
import {
  User, Shield, Zap, Check, Eye, EyeOff,
  Loader2, CheckCircle2, AlertCircle, Chrome,
} from "lucide-react";
import { useUser } from "@/lib/supabase/useUser";
import { createClient } from "@/lib/supabase/client";
import Image from "next/image";

// ── Plano mockado ─────────────────────────────────────────────────────────────
const MOCK_PLAN = {
  id:    "free",
  label: "Free",
  features: [
    "50.000 tokens / mês",
    "Geração e avaliação de BDD",
    "Histórico local (30 dias)",
  ],
  missing: [
    "Execução E2E (BIST)",
    "Histórico ilimitado",
    "API CLI",
  ],
};

// ── Componente de senha ───────────────────────────────────────────────────────
function PasswordSection({ isOAuth }: { isOAuth: boolean }) {
  const [current,  setCurrent]  = useState("");
  const [next,     setNext]     = useState("");
  const [confirm,  setConfirm]  = useState("");
  const [showCurr, setShowCurr] = useState(false);
  const [showNext, setShowNext] = useState(false);
  const [loading,  setLoading]  = useState(false);
  const [status,   setStatus]   = useState<"idle" | "success" | "error">("idle");
  const [message,  setMessage]  = useState("");

  if (isOAuth) {
    return (
      <div className="flex items-start gap-3 p-4 rounded-lg bg-bist-surface2 border border-bist-border2">
        <Chrome className="w-4 h-4 text-bist-muted shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-medium text-bist-primary">Conta vinculada ao Google</p>
          <p className="text-xs text-bist-muted mt-0.5 leading-relaxed">
            Sua autenticação é gerenciada pelo Google. A senha é definida diretamente na sua conta Google.
          </p>
        </div>
      </div>
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("idle");

    if (next.length < 8) {
      setStatus("error");
      setMessage("A nova senha deve ter pelo menos 8 caracteres.");
      return;
    }
    if (next !== confirm) {
      setStatus("error");
      setMessage("As senhas não coincidem.");
      return;
    }

    setLoading(true);
    try {
      const supabase = createClient();
      const { error } = await supabase.auth.updateUser({ password: next });
      if (error) throw error;
      setStatus("success");
      setMessage("Senha atualizada com sucesso.");
      setCurrent(""); setNext(""); setConfirm("");
    } catch (err) {
      setStatus("error");
      setMessage(err instanceof Error ? err.message : "Erro ao atualizar a senha.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-3">
        <div className="space-y-1.5">
          <label className="text-xs text-bist-muted">Senha atual</label>
          <div className="relative">
            <input
              type={showCurr ? "text" : "password"}
              className="input w-full pr-10 text-sm"
              placeholder="••••••••"
              value={current}
              onChange={e => setCurrent(e.target.value)}
              required
            />
            <button
              type="button"
              onClick={() => setShowCurr(p => !p)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-bist-dim hover:text-bist-muted transition-colors"
            >
              {showCurr ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
            </button>
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="text-xs text-bist-muted">Nova senha</label>
          <div className="relative">
            <input
              type={showNext ? "text" : "password"}
              className="input w-full pr-10 text-sm"
              placeholder="Mínimo 8 caracteres"
              value={next}
              onChange={e => setNext(e.target.value)}
              required
            />
            <button
              type="button"
              onClick={() => setShowNext(p => !p)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-bist-dim hover:text-bist-muted transition-colors"
            >
              {showNext ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
            </button>
          </div>
          {next.length > 0 && (
            <div className="flex gap-1 mt-1">
              {[4, 8, 12].map(len => (
                <div
                  key={len}
                  className={`h-0.5 flex-1 rounded-full transition-colors ${
                    next.length >= len ? "bg-[#a3fb73]" : "bg-bist-border"
                  }`}
                />
              ))}
            </div>
          )}
        </div>

        <div className="space-y-1.5">
          <label className="text-xs text-bist-muted">Confirmar nova senha</label>
          <input
            type="password"
            className={`input w-full text-sm ${
              confirm.length > 0 && confirm !== next ? "border-red-300" : ""
            }`}
            placeholder="Repita a nova senha"
            value={confirm}
            onChange={e => setConfirm(e.target.value)}
            required
          />
        </div>
      </div>

      {status === "success" && (
        <div className="flex items-center gap-2 text-xs text-[#2D6A3F] bg-[#a3fb73]/10 border border-[#a3fb73]/30 rounded-lg px-3 py-2">
          <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
          {message}
        </div>
      )}
      {status === "error" && (
        <div className="flex items-center gap-2 text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
          <AlertCircle className="w-3.5 h-3.5 shrink-0" />
          {message}
        </div>
      )}

      <button
        type="submit"
        disabled={loading || !current || !next || !confirm}
        className="btn-primary text-sm py-2 px-5 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Salvando...</> : "Atualizar senha"}
      </button>
    </form>
  );
}

// ── Página principal ──────────────────────────────────────────────────────────
export default function ProfilePage() {
  const { user, loading } = useUser();

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center py-20">
        <Loader2 className="w-5 h-5 animate-spin text-bist-muted" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center py-20 gap-4 text-center">
        <p className="text-sm text-bist-muted">Você precisa estar logado para ver seu perfil.</p>
        <Link href="/login" className="btn-primary text-sm">Entrar</Link>
      </div>
    );
  }

  const avatarUrl    = user.user_metadata?.avatar_url as string | undefined;
  const fullName     = (user.user_metadata?.full_name ?? "") as string;
  const initials     = fullName.split(" ").map((w: string) => w[0]).slice(0, 2).join("").toUpperCase() || "?";
  const provider     = (user.app_metadata?.provider ?? "email") as string;
  const isOAuth      = provider !== "email";
  const createdAt    = user.created_at
    ? new Date(user.created_at).toLocaleDateString("pt-BR", { day: "2-digit", month: "long", year: "numeric" })
    : "—";

  return (
    <div className="flex-1 max-w-2xl mx-auto px-4 sm:px-6 py-10 space-y-8">

      {/* Cabeçalho */}
      <div className="card p-6 flex items-center gap-5">
        {avatarUrl ? (
          <Image
            src={avatarUrl}
            alt={fullName}
            width={64}
            height={64}
            className="rounded-full ring-2 ring-bist-border shrink-0"
          />
        ) : (
          <div className="w-16 h-16 rounded-full bg-bist-primary flex items-center justify-center shrink-0">
            <span className="font-bold text-white text-xl">{initials}</span>
          </div>
        )}

        <div className="min-w-0 space-y-1">
          <h1 className="text-lg font-semibold text-bist-primary truncate">
            {fullName || "Usuário"}
          </h1>
          <p className="text-sm text-bist-muted truncate">{user.email}</p>
          <div className="flex items-center gap-2 flex-wrap pt-0.5">
            <span className={`inline-flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded-full border ${
              isOAuth
                ? "bg-blue-50 text-blue-600 border-blue-200"
                : "bg-bist-surface2 text-bist-muted border-bist-border"
            }`}>
              {isOAuth ? <Chrome className="w-2.5 h-2.5" /> : <User className="w-2.5 h-2.5" />}
              {isOAuth ? "Google" : "Email"}
            </span>
            <span className="text-[10px] text-bist-dim font-code">
              Desde {createdAt}
            </span>
          </div>
        </div>
      </div>

      {/* Plano */}
      <div className="card p-5 space-y-4">
        <div className="flex items-center justify-between">
          <p className="text-xs font-code text-bist-dim uppercase tracking-widest">Plano atual</p>
          <span className="text-xs font-semibold px-2 py-0.5 rounded-full border bg-bist-surface2 text-bist-muted border-bist-border">
            {MOCK_PLAN.label.toUpperCase()}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1.5">
          {MOCK_PLAN.features.map(f => (
            <div key={f} className="flex items-center gap-2 text-sm text-bist-mid">
              <Check className="w-3.5 h-3.5 text-[#2D6A3F] shrink-0" />
              {f}
            </div>
          ))}
          {MOCK_PLAN.missing.map(f => (
            <div key={f} className="flex items-center gap-2 text-sm text-bist-dim line-through">
              <span className="w-3.5 h-3.5 shrink-0 text-center text-xs">—</span>
              {f}
            </div>
          ))}
        </div>

        <div className="pt-1 border-t border-bist-border">
          <div className="flex items-center justify-between">
            <p className="text-xs text-bist-muted leading-relaxed max-w-xs">
              Desbloqueie execução E2E e tokens ilimitados.
            </p>
            <Link href="/planos" className="btn-primary text-xs py-2 px-4 shrink-0 flex items-center gap-1.5">
              <Zap className="w-3 h-3" /> Fazer upgrade
            </Link>
          </div>
        </div>
      </div>

      {/* Segurança */}
      <div className="card p-5 space-y-4">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-bist-muted" />
          <p className="text-xs font-code text-bist-dim uppercase tracking-widest">Segurança</p>
        </div>
        <PasswordSection isOAuth={isOAuth} />
      </div>

    </div>
  );
}
