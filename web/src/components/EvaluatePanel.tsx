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
  const [story, setStory] = useState("");
  const [bddText, setBddText] = useState("");
  const [threshold, setThreshold] = useState(7.0);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScoreResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleEvaluate() {
    if (!story.trim() || !bddText.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await evaluateBDD({ story: story.trim(), bdd_text: bddText.trim(), threshold });
      setResult(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid grid-cols-1 xl:grid-cols-[1fr_380px] gap-6">
      {/* ── Left: Inputs ─────────────────────────────────────────────────── */}
      <div className="space-y-4">
        <div className="card p-4 space-y-3">
          <label className="text-sm font-medium text-zinc-300">User Story</label>
          <textarea
            className="textarea h-28"
            placeholder="Como usuário, quero fazer login para acessar minha conta..."
            value={story}
            onChange={e => setStory(e.target.value)}
          />
        </div>

        <div className="card p-4 space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-zinc-300">Cenários BDD (Gherkin)</label>
            <button className="btn-ghost text-xs" onClick={() => setBddText(SAMPLE_BDD)}>
              <ClipboardPaste className="w-3.5 h-3.5" />
              Exemplo
            </button>
          </div>
          <textarea
            className="textarea h-72 font-mono text-sm"
            placeholder={"Funcionalidade: ...\n\n  Cenário: ...\n    Dado que ...\n    Quando ...\n    Então ..."}
            value={bddText}
            onChange={e => setBddText(e.target.value)}
          />
        </div>

        {/* Threshold */}
        <div className="card p-4 space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-zinc-300">Threshold de aprovação</label>
            <span className="text-sm font-semibold text-indigo-400 tabular-nums">{threshold.toFixed(1)}</span>
          </div>
          <input type="range" min="1" max="10" step="0.5" value={threshold}
            onChange={e => setThreshold(parseFloat(e.target.value))}
            className="w-full accent-indigo-500" />
          <div className="flex justify-between text-[10px] text-zinc-600">
            <span>1.0</span><span>10.0</span>
          </div>
        </div>

        <button
          className="btn-primary w-full py-3"
          disabled={loading || !story.trim() || !bddText.trim()}
          onClick={handleEvaluate}
        >
          {loading
            ? <><Loader2 className="w-4 h-4 animate-spin" /> Avaliando...</>
            : <><BarChart2 className="w-4 h-4" /> Avaliar BDD</>
          }
        </button>
      </div>

      {/* ── Right: Score ─────────────────────────────────────────────────── */}
      <div>
        {!result && !error && !loading && (
          <div className="card p-8 flex flex-col items-center justify-center text-center gap-4 border-dashed border-zinc-700 min-h-[340px]">
            <div className="w-12 h-12 rounded-xl bg-indigo-600/10 border border-indigo-600/20 flex items-center justify-center">
              <BarChart2 className="w-5 h-5 text-indigo-400" />
            </div>
            <div>
              <p className="text-zinc-300 font-medium">Pronto para avaliar</p>
              <p className="text-sm text-zinc-600 mt-1">Preencha a story e o BDD para obter o score nas 4 métricas</p>
            </div>
          </div>
        )}

        {error && (
          <div className="card p-4 border-red-500/30 bg-red-500/5 flex items-start gap-3">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-red-400">Erro na avaliação</p>
              <p className="text-xs text-zinc-400 mt-1">{error}</p>
            </div>
          </div>
        )}

        {loading && (
          <div className="card p-6 flex items-center gap-3 text-sm text-zinc-400">
            <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
            Calculando métricas de qualidade...
          </div>
        )}

        {result && (
          <div className="card p-5 animate-slide-up space-y-1">
            <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide mb-4">
              Resultado da Avaliação
            </h2>
            <ScoreDisplay score={result} />
          </div>
        )}
      </div>
    </div>
  );
}
