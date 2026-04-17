"use client";

import { useState } from "react";
import { BarChart2, Loader2, AlertCircle, ClipboardPaste } from "lucide-react";
import { evaluateBDD } from "@/lib/api";
import { ScoreDisplay } from "./ScoreDisplay";
import type { ScoreResult } from "@/types";

const SAMPLE_BDD = `Funcionalidade: Login no sistema

  Cenário: Login com credenciais válidas
    Dado que estou na página de login em "/login"
    Quando preencho o campo de email com "usuario@email.com"
    E preencho o campo de senha com "Senha@123"
    E clico no botão "Entrar"
    Então devo ser redirecionado para "/dashboard"
    E devo ver a mensagem "Bem-vindo, usuario@email.com"

  Cenário: Login com senha incorreta
    Dado que estou na página de login em "/login"
    Quando preencho o campo de email com "usuario@email.com"
    E preencho o campo de senha com "senhaerrada"
    E clico no botão "Entrar"
    Então devo ver a mensagem "Credenciais inválidas"
    E devo permanecer na página "/login"`;

export function EvaluatePanel() {
  const [story, setStory]       = useState("");
  const [bddText, setBddText]   = useState("");
  const [threshold, setThreshold] = useState(7.0);
  const [loading, setLoading]   = useState(false);
  const [result, setResult]     = useState<ScoreResult | null>(null);
  const [error, setError]       = useState<string | null>(null);

  async function handleEvaluate() {
    if (!story.trim() || !bddText.trim()) return;
    setLoading(true); setError(null); setResult(null);
    try {
      setResult(await evaluateBDD({ story: story.trim(), bdd_text: bddText.trim(), threshold }));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid grid-cols-1 xl:grid-cols-[1fr_380px] gap-6">

      <div className="space-y-4">
        <div className="card p-5 space-y-3">
          <label className="text-sm font-medium text-bist-primary">User Story</label>
          <textarea
            className="textarea h-28 text-sm"
            placeholder="Como usuário, quero fazer login para acessar minha conta..."
            value={story}
            onChange={e => setStory(e.target.value)}
          />
        </div>

        <div className="card p-5 space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-bist-primary">Cenários BDD (Gherkin)</label>
            <button className="btn-ghost text-xs" onClick={() => setBddText(SAMPLE_BDD)}>
              <ClipboardPaste className="w-3.5 h-3.5" /> Exemplo
            </button>
          </div>
          <textarea
            className="textarea h-72 text-xs font-code leading-relaxed"
            placeholder={"Funcionalidade: ...\n\n  Cenário: ...\n    Dado que ...\n    Quando ...\n    Então ..."}
            value={bddText}
            onChange={e => setBddText(e.target.value)}
          />
        </div>

        <div className="card p-5 space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-bist-primary">Score mínimo (threshold)</label>
            <span className="text-sm font-code font-semibold text-bist-primary tabular-nums">{threshold.toFixed(1)}</span>
          </div>
          <input type="range" min="1" max="10" step="0.5" value={threshold}
            onChange={e => setThreshold(parseFloat(e.target.value))}
            className="w-full accent-[#a3fb73]" />
          <div className="flex justify-between text-[10px] font-code text-bist-dim">
            <span>1.0 — leniente</span><span>10.0 — rigoroso</span>
          </div>
        </div>

        <button
          className="btn-primary w-full py-3 text-sm"
          disabled={loading || !story.trim() || !bddText.trim()}
          onClick={handleEvaluate}
        >
          {loading
            ? <><Loader2 className="w-4 h-4 animate-spin" /> Avaliando...</>
            : <><BarChart2 className="w-4 h-4" /> Avaliar BDD</>
          }
        </button>
      </div>

      <div>
        {!result && !error && !loading && (
          <div className="card p-8 flex flex-col items-center justify-center text-center gap-4 border-dashed min-h-[340px]">
            <div className="w-12 h-12 rounded-xl bg-bist-surface2 border border-bist-border flex items-center justify-center">
              <BarChart2 className="w-5 h-5 text-bist-muted" />
            </div>
            <div>
              <p className="text-sm font-medium text-bist-primary">Pronto para avaliar</p>
              <p className="text-xs text-bist-muted mt-1 max-w-[200px] leading-relaxed">
                Preencha a story e o BDD para obter o score nas 4 métricas
              </p>
            </div>
          </div>
        )}

        {error && (
          <div className="card p-4 border-red-200 bg-red-50 flex items-start gap-3">
            <AlertCircle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-red-600">Erro na avaliação</p>
              <p className="text-xs text-red-500 mt-1">{error}</p>
            </div>
          </div>
        )}

        {loading && (
          <div className="card p-6 flex items-center gap-3 text-sm text-bist-muted">
            <Loader2 className="w-4 h-4 animate-spin text-[#a3fb73]" />
            Calculando métricas de qualidade...
          </div>
        )}

        {result && (
          <div className="card p-5 animate-slide-up">
            <p className="text-xs font-code text-bist-dim uppercase tracking-widest mb-4">Resultado da avaliação</p>
            <ScoreDisplay score={result} />
          </div>
        )}
      </div>
    </div>
  );
}
