"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { BookOpen, AlertCircle, Loader2 } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

function GoogleIcon() {
  return (
    <svg className="w-5 h-5" viewBox="0 0 24 24" aria-hidden="true">
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
        queryParams: {
          access_type: "offline",
          prompt: "consent",
        },
      },
    });
    // O redirect acontece automaticamente — loading fica ativo
  }

  return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-4">
      <div className="w-full max-w-sm space-y-6">
        {/* Logo */}
        <div className="flex flex-col items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <BookOpen className="w-6 h-6 text-white" />
          </div>
          <div className="text-center">
            <h1 className="text-xl font-semibold text-zinc-100">BDD Generator</h1>
            <p className="text-sm text-zinc-500 mt-1">
              Geração de cenários Gherkin com IA
            </p>
          </div>
        </div>

        {/* Card */}
        <div className="card p-6 space-y-4">
          <div className="text-center space-y-1">
            <h2 className="text-base font-medium text-zinc-200">Entrar na plataforma</h2>
            <p className="text-xs text-zinc-500">
              Use sua conta Google para acessar
            </p>
          </div>

          {/* Error message */}
          {errorParam && (
            <div className="flex items-start gap-2 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2.5">
              <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-xs text-red-400">
                {errorMessages[errorParam] ?? "Erro desconhecido. Tente novamente."}
              </p>
            </div>
          )}

          <button
            onClick={handleGoogleLogin}
            disabled={loading}
            className="w-full flex items-center justify-center gap-3 bg-white hover:bg-zinc-100
                       active:bg-zinc-200 text-zinc-900 font-medium rounded-lg px-4 py-2.5
                       transition-colors duration-150 disabled:opacity-60 disabled:cursor-not-allowed
                       focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
          >
            {loading
              ? <Loader2 className="w-4 h-4 animate-spin text-zinc-500" />
              : <GoogleIcon />
            }
            {loading ? "Redirecionando..." : "Continuar com Google"}
          </button>
        </div>

        <p className="text-center text-xs text-zinc-700">
          Ao entrar, você concorda com os termos de uso da plataforma.
        </p>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-zinc-500" />
      </div>
    }>
      <LoginContent />
    </Suspense>
  );
}
