"use client";

import { useState, useRef } from "react";
import { Loader2, AlertCircle, Sparkles, BookOpen } from "lucide-react";
import { generateBDD } from "@/lib/api";
import { addEntry } from "@/lib/history";
import { ScoreDisplay } from "./ScoreDisplay";
import { BDDViewer } from "./BDDViewer";
import { saveGeneration } from "@/lib/supabase/generations";
import { useUser } from "@/lib/supabase/useUser";
import type { GenerateResult } from "@/types";

const EXAMPLE_STORIES = [
  "Como usuário, quero fazer login com email e senha para acessar minha conta.\n\nCritérios de aceitação:\n- Login com credenciais válidas\n- Mensagem de erro para credenciais inválidas\n- Bloqueio após 3 tentativas",
  "Como cliente, quero adicionar produtos ao carrinho para comprá-los depois.\n\nCritérios:\n- Adicionar produto disponível\n- Não permite adicionar produto sem estoque\n- Atualizar quantidade",
  "Como gestor, quero aprovar solicitações de férias para controlar ausências.\n\nCritérios:\n- Visualizar lista de solicitações pendentes\n- Aprovar ou rejeitar com justificativa\n- Notificar funcionário",
];

const DEFAULT_MODEL = "flash";

export function GeneratePanel() {
  const model = DEFAULT_MODEL;

  const [story, setStory]               = useState("");
  const [threshold, setThreshold]       = useState(7.0);
  const [loading, setLoading]           = useState(false);
  const [loadingPhase, setLoadingPhase] = useState("");
  const [result, setResult]             = useState<GenerateResult | null>(null);
  const [error, setError]               = useState<string | null>(null);
  const [saved, setSaved]               = useState(false);

  const { user } = useUser();
  const resultRef = useRef<HTMLDivElement>(null);

  async function handleGenerate() {
    if (!story.trim()) return;
    setLoading(true); setError(null); setResult(null);
    setLoadingPhase("Gerando cenários...");

    try {
      const res = await generateBDD({
        story: story.trim(), model, threshold,
        max_attempts: 5, research: false, until_converged: false,
      });
      setResult(res); setSaved(false);
      addEntry({
        timestamp: Date.now(), story: story.trim(), model,
        bdd_text: res.bdd_text, score: res.score, attempts: res.attempts,
        total_tokens: res.total_tokens, research_tokens: res.research_tokens,
        converged: res.converged, duration_seconds: res.duration_seconds,
        options: { research: false, threshold },
      });
      setSaved(true);
      if (user) saveGeneration(user.id, story.trim(), model, res, { research: false, threshold });
      setTimeout(() => resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 100);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erro desconhecido");
    } finally {
      setLoading(false);
      setLoadingPhase("");
    }
  }

  function loadExample() {
    setStory(EXAMPLE_STORIES[Math.floor(Math.random() * EXAMPLE_STORIES.length)]);
  }

  return (
    <div className="grid grid-cols-1 xl:grid-cols-[460px_1fr] gap-6 h-full">

      {/* ── Form ────────────────────────────────────────────────────────── */}
      <div className="space-y-4">

        {/* Story */}
        <div className="card p-5 space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-bist-primary">User Story</label>
            <button onClick={loadExample} className="btn-ghost text-xs gap-1">
              <BookOpen className="w-3.5 h-3.5" />
              Exemplo
            </button>
          </div>
          <textarea
            className="textarea h-44 leading-relaxed text-sm"
            placeholder={"Como [persona], quero [ação] para [benefício].\n\nCritérios de aceitação:\n- ..."}
            value={story}
            onChange={e => setStory(e.target.value)}
          />
          <p className="text-[10px] text-bist-dim font-code">{story.length} caracteres</p>
        </div>

        {/* Advanced */}
        <div className="card p-5 space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-sm text-bist-mid">Nota mínima (threshold)</label>
            <span className="text-sm font-code font-semibold text-bist-primary tabular-nums">{threshold.toFixed(1)}</span>
          </div>
          <input type="range" min="1" max="10" step="0.5" value={threshold}
            onChange={e => setThreshold(parseFloat(e.target.value))}
            className="w-full accent-[#a3fb73] cursor-pointer" />
          <div className="flex justify-between text-[10px] text-bist-dim font-code">
            <span>1.0 — leniente</span><span>10.0 — rigoroso</span>
          </div>
        </div>

        <button
          className="btn-primary w-full text-sm py-3"
          disabled={loading || !story.trim()}
          onClick={handleGenerate}
        >
          {loading
            ? <><Loader2 className="w-4 h-4 animate-spin" /> Gerando cenários BDD...</>
            : <><Sparkles className="w-4 h-4" /> Gerar BDD</>
          }
        </button>

        {saved && !loading && (
          <p className="text-xs text-[#2D6A3F] text-center font-medium">
            ✓ Salvo no histórico
          </p>
        )}
      </div>

      {/* ── Results ─────────────────────────────────────────────────────── */}
      <div ref={resultRef} className="space-y-4 min-h-[300px]">
        {!result && !error && !loading && <EmptyState />}
        {loading && <LoadingState phase={loadingPhase} />}

        {error && (
          <div className="card p-4 border-red-200 bg-red-50 flex items-start gap-3">
            <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-red-600">Erro na geração</p>
              <p className="text-xs text-red-500 mt-1">{error}</p>
              <p className="text-xs text-bist-dim mt-2">
                Verifique se o backend está rodando:{" "}
                <code className="font-code bg-bist-surface2 px-1 rounded">uvicorn backend.main:app --reload</code>
              </p>
            </div>
          </div>
        )}

        {result && (
          <div className="space-y-4 animate-slide-up">
            <div className="card p-5">
              <h2 className="text-xs font-code text-bist-dim uppercase tracking-widest mb-4">Avaliação de qualidade</h2>
              <ScoreDisplay
                score={result.score}
                attempts={result.attempts}
                totalTokens={result.total_tokens}
                researchTokens={result.research_tokens}
                durationSeconds={result.duration_seconds}
                converged={result.converged}
              />
            </div>

            <div className="space-y-0">
              <div className="px-1 pb-2">
                <h2 className="text-xs font-code text-bist-dim uppercase tracking-widest">Saída — output.feature</h2>
              </div>
              <BDDViewer bddText={result.bdd_text} approved={result.score.aprovado} />
            </div>

          </div>
        )}
      </div>
    </div>
  );
}


function LoadingState({ phase }: { phase: string }) {
  return (
    <div className="space-y-4 animate-pulse">
      {/* Score skeleton */}
      <div className="card p-5 space-y-4">
        <div className="h-3 w-32 bg-bist-border rounded" />
        <div className="grid grid-cols-2 gap-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card-subtle px-3 py-3 space-y-2">
              <div className="h-2.5 w-16 bg-bist-border rounded" />
              <div className="h-4 w-10 bg-bist-border rounded" />
            </div>
          ))}
        </div>
        <div className="h-2 w-full bg-bist-border rounded-full" />
      </div>

      {/* BDD output skeleton */}
      <div className="card p-5 space-y-3">
        <div className="h-3 w-40 bg-bist-border rounded" />
        <div className="space-y-2 pt-1">
          {[80, 60, 90, 55, 70, 65, 85, 50, 75, 60, 88, 52].map((w, i) => (
            <div
              key={i}
              className="h-3 bg-bist-border rounded"
              style={{ width: `${w}%`, marginLeft: i % 3 !== 0 ? "1.25rem" : 0 }}
            />
          ))}
        </div>
      </div>

      {/* Phase label */}
      <div className="flex items-center justify-center gap-2 text-xs text-bist-dim pt-1">
        <Loader2 className="w-3.5 h-3.5 animate-spin text-[#a3fb73]" />
        <span>{phase || "Processando..."}</span>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="card p-10 flex flex-col items-center justify-center text-center gap-6
                    border-dashed min-h-[420px]">
      <div className="w-12 h-12 rounded-xl bg-bist-surface2 border border-bist-border flex items-center justify-center">
        <Sparkles className="w-5 h-5 text-bist-muted" />
      </div>

      <div>
        <p className="text-sm font-medium text-bist-primary">Pronto para gerar</p>
        <p className="text-xs text-bist-dim mt-1 max-w-xs leading-relaxed">
          Insira uma user story à esquerda e clique em <span className="text-bist-primary font-medium">Gerar BDD</span>
        </p>
      </div>

      <div className="grid grid-cols-2 gap-2 w-full max-w-xs text-left">
        {[
          ["Cobertura",       "Peso 30%"],
          ["Estrutura GWT",   "Peso 30%"],
          ["Clareza",         "Peso 20%"],
          ["Executabilidade", "Peso 20%"],
        ].map(([k, v]) => (
          <div key={k} className="card-subtle px-3 py-2">
            <p className="text-xs font-medium text-bist-mid">{k}</p>
            <p className="text-[10px] font-code text-bist-dim mt-0.5">{v}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
