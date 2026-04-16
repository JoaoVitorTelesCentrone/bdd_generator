"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { AlertCircle, Loader2 } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

function GoogleIcon() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
      <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
      <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
      <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
    </svg>
  );
}

function LoginContent() {
  const [loading, setLoading] = useState(false);
  const searchParams = useSearchParams();
  const errorParam = searchParams.get("error");

  const errorMessages: Record<string, string> = {
    auth_callback_failed: "Falha ao completar autenticação. Tente novamente.",
    access_denied:        "Acesso negado pelo Google.",
  };

  async function handleGoogleLogin() {
    setLoading(true);
    const supabase = createClient();
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
        queryParams: { access_type: "offline", prompt: "consent" },
      },
    });
  }

  return (
    <div className="min-h-screen bg-[#1a2c21] flex items-center justify-center p-4">
      {/* Background grid is applied via body::before in globals.css */}
      <div className="w-full max-w-sm space-y-8 relative z-10">

        {/* ── Terminal header ───────────────────────────────────────────── */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center gap-1">
            <span className="font-['Share_Tech_Mono',_'Consolas',_monospace] text-[#a3fb73] text-5xl tracking-[0.3em] leading-none">
              BIST
            </span>
            <span className="text-[#a3fb73] text-5xl leading-none animate-cursor-blink">▮</span>
          </div>
          <div className="font-mono text-xs text-[#5a7a65] tracking-widest uppercase">
            bdd generation tool
          </div>
        </div>

        {/* ── Login card ───────────────────────────────────────────────── */}
        <div className="card-terminal p-6 space-y-5">

          {/* Terminal prompt */}
          <div className="space-y-1.5 font-mono text-sm border-b border-[#a3fb73]/10 pb-4">
            <div className="flex items-center gap-2">
              <span className="text-[#5a7a65]">$</span>
              <span className="text-[#a3fb73]">bist auth</span>
              <span className="text-[#5a7a65]">--provider=google</span>
            </div>
            <div className="flex items-center gap-2 text-[#5a7a65]">
              <span className="select-none">›</span>
              <span>autenticação necessária para salvar histórico</span>
            </div>
          </div>

          {/* Error */}
          {errorParam && (
            <div className="flex items-start gap-2 bg-red-500/8 border border-red-500/20 rounded p-3">
              <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-xs text-red-400 font-mono">
                {errorMessages[errorParam] ?? "erro desconhecido. tente novamente."}
              </p>
            </div>
          )}

          {/* Google button — temporariamente desabilitado */}
          {/* <button
            onClick={handleGoogleLogin}
            disabled={loading}
            className="w-full flex items-center justify-center gap-3
                       bg-[#eef9e8] hover:bg-[#ddf2dc] active:bg-[#c8e8c8]
                       text-[#1a2c21] font-mono font-semibold text-sm
                       rounded py-2.5 px-4 tracking-wide
                       transition-all duration-150
                       disabled:opacity-50 disabled:cursor-not-allowed
                       focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#a3fb73]/40"
          >
            {loading
              ? <Loader2 className="w-4 h-4 animate-spin text-[#1a2c21]" />
              : <GoogleIcon />
            }
            {loading ? "redirecionando..." : "authenticate --google"}
          </button> */}
          <div className="w-full flex items-center justify-center gap-3
                          border border-[#a3fb73]/15 bg-[#243d2c]/40
                          text-[#3d5a44] font-mono text-sm
                          rounded py-2.5 px-4 cursor-not-allowed select-none">
            <GoogleIcon />
            authenticate --google
            <span className="text-[10px] text-[#3d5a44] ml-auto">// em breve</span>
          </div>

          <p className="text-center text-[10px] text-[#3d5a44] font-mono">
            // autenticação opcional — gerar e avaliar funciona sem login
          </p>
        </div>

        <p className="text-center text-[10px] text-[#2f5237] font-mono">
          BIST v1.0 • Gemini & Claude • auto-refinamento
        </p>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#1a2c21] flex items-center justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-[#a3fb73]" />
      </div>
    }>
      <LoginContent />
    </Suspense>
  );
}
