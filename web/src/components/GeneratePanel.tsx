"use client";

import { useState, useRef } from "react";
import {
  ChevronDown, ChevronUp, FlaskConical,
  Repeat, Loader2, AlertCircle, Info, Sparkles, BookOpen, Zap,
} from "lucide-react";
import { generateBDD } from "@/lib/api";
import { addEntry } from "@/lib/history";
import { ScoreDisplay } from "./ScoreDisplay";
import { BDDViewer } from "./BDDViewer";
import { RunPanel } from "./RunPanel";
import { UnitTestPanel } from "./UnitTestPanel";
import { saveGeneration } from "@/lib/supabase/generations";
import { useUser } from "@/lib/supabase/useUser";
import type { GenerateResult, Model } from "@/types";

const EXAMPLE_STORIES = [
  "Como usuário, quero fazer login com email e senha para acessar minha conta.\n\nCritérios de aceitação:\n- Login com credenciais válidas\n- Mensagem de erro para credenciais inválidas\n- Bloqueio após 3 tentativas",
  "Como cliente, quero adicionar produtos ao carrinho para comprá-los depois.\n\nCritérios:\n- Adicionar produto disponível\n- Não permite adicionar produto sem estoque\n- Atualizar quantidade",
  "Como gestor, quero aprovar solicitações de férias para controlar ausências.\n\nCritérios:\n- Visualizar lista de solicitações pendentes\n- Aprovar ou rejeitar com justificativa\n- Notificar funcionário",
];

const FREE_MODEL = "llama";

export function GeneratePanel({ initialModels }: { initialModels: Model[] }) {
  const model = FREE_MODEL;

  const [story, setStory]               = useState("");
  const [threshold, setThreshold]       = useState(7.0);
  const [maxAttempts, setMaxAttempts]   = useState(5);
  const [research, setResearch]         = useState(false);
  const [untilConverged, setUntilConverged] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
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
    setLoadingPhase(research ? "Pesquisando story..." : "Gerando cenários...");

    try {
      const res = await generateBDD({
        story: story.trim(), model, threshold,
        max_attempts: maxAttempts, research, until_converged: untilConverged,
      });
      setResult(res); setSaved(false);
      addEntry({
        timestamp: Date.now(), story: story.trim(), model,
        bdd_text: res.bdd_text, score: res.score, attempts: res.attempts,
        total_tokens: res.total_tokens, research_tokens: res.research_tokens,
        converged: res.converged, duration_seconds: res.duration_seconds,
        options: { research, threshold },
      });
      setSaved(true);
      if (user) saveGeneration(user.id, story.trim(), model, res, { research, threshold });
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
        <div className="card">
          <button
            className="w-full flex items-center justify-between px-5 py-3.5 text-sm text-bist-muted hover:text-bist-primary transition-colors"
            onClick={() => setShowAdvanced(p => !p)}
          >
            <span className="font-medium">Opções avançadas</span>
            {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {showAdvanced && (
            <div className="px-5 pb-5 space-y-5 border-t border-bist-border pt-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm text-bist-mid flex items-center gap-1.5">
                    Score mínimo (threshold)
                    <Tooltip text="Score necessário para aprovar o BDD. Valores mais altos exigem mais tentativas de refinamento." />
                  </label>
                  <span className="text-sm font-code font-semibold text-bist-primary tabular-nums">{threshold.toFixed(1)}</span>
                </div>
                <input type="range" min="1" max="10" step="0.5" value={threshold}
                  onChange={e => setThreshold(parseFloat(e.target.value))}
                  className="w-full accent-[#a3fb73] cursor-pointer" />
                <div className="flex justify-between text-[10px] text-bist-dim font-code">
                  <span>1.0 — leniente</span><span>10.0 — rigoroso</span>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm text-bist-mid">Máx. tentativas</label>
                  <span className="text-sm font-code font-semibold text-bist-primary tabular-nums">{maxAttempts}</span>
                </div>
                <input type="range" min="1" max="20" step="1" value={maxAttempts}
                  onChange={e => setMaxAttempts(parseInt(e.target.value))}
                  className="w-full accent-[#a3fb73] cursor-pointer" />
                <div className="flex justify-between text-[10px] text-bist-dim font-code">
                  <span>1</span><span>20</span>
                </div>
              </div>

              <div className="space-y-2.5">
                <Toggle
                  id="research" checked={research} onChange={setResearch}
                  icon={<FlaskConical className="w-3.5 h-3.5" />}
                  label="Auto-research"
                  description="Analisa a story antes de gerar para extrair critérios de aceitação implícitos"
                />
                <Toggle
                  id="converged" checked={untilConverged} onChange={setUntilConverged}
                  icon={<Repeat className="w-3.5 h-3.5" />}
                  label="Refinar até convergir"
                  description="Refina até atingir o threshold (máx 50 tentativas)"
                />
              </div>
            </div>
          )}
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

        {loading && (
          <div className="card p-4 space-y-2">
            <div className="flex items-center gap-2 text-sm text-bist-muted">
              <Loader2 className="w-3.5 h-3.5 animate-spin text-[#a3fb73]" />
              <span>{loadingPhase || "Processando..."}</span>
            </div>
            <div className="h-1 bg-bist-border rounded-full overflow-hidden">
              <div className="h-full bg-[#a3fb73] animate-progress rounded-full" />
            </div>
            <div className="flex items-center gap-3 text-[10px] font-code text-bist-dim">
              <span className="flex items-center gap-1">
                <Zap className="w-3 h-3" />
                Llama 3.3 70B
              </span>
              <span className="text-[#2D6A3F] font-semibold">grátis</span>
              {research && (
                <span className="text-[#2D6A3F] font-medium">· auto-research ativo</span>
              )}
            </div>
          </div>
        )}

        {saved && !loading && (
          <p className="text-xs text-[#2D6A3F] text-center font-medium">
            ✓ Salvo no histórico
          </p>
        )}
      </div>

      {/* ── Results ─────────────────────────────────────────────────────── */}
      <div ref={resultRef} className="space-y-4 min-h-[300px]">
        {!result && !error && !loading && <EmptyState />}

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
              <BDDViewer bddText={result.bdd_text} />
            </div>

            <UnitTestPanel bddText={result.bdd_text} model={model} />

            <RunPanel initialStory={story} />
          </div>
        )}
      </div>
    </div>
  );
}

function Toggle({
  id, checked, onChange, icon, label, description,
}: {
  id: string; checked: boolean; onChange: (v: boolean) => void;
  icon: React.ReactNode; label: string; description: string;
}) {
  return (
    <label htmlFor={id} className="flex items-start gap-3 cursor-pointer group p-3 rounded-lg hover:bg-bist-surface2 transition-colors">
      <div className="relative mt-0.5 flex-shrink-0">
        <input id={id} type="checkbox" className="sr-only" checked={checked} onChange={e => onChange(e.target.checked)} />
        <div className={`w-9 h-5 rounded-full transition-colors duration-200 border ${checked ? "bg-[#a3fb73] border-[#a3fb73]" : "bg-bist-surface2 border-bist-border"}`}>
          <div className={`absolute top-0.5 left-0.5 w-4 h-4 bg-bist-surface rounded-full shadow-sm transition-transform duration-200 ${checked ? "translate-x-4" : "translate-x-0"}`} />
        </div>
      </div>
      <div>
        <p className={`text-sm font-medium flex items-center gap-1.5 ${checked ? "text-bist-primary" : "text-bist-muted"}`}>
          {icon} {label}
        </p>
        <p className="text-xs text-bist-dim leading-snug mt-0.5">{description}</p>
      </div>
    </label>
  );
}

function Tooltip({ text }: { text: string }) {
  return (
    <span className="relative group cursor-help">
      <Info className="w-3 h-3 text-bist-dim" />
      <span className="absolute left-full ml-2 top-1/2 -translate-y-1/2 z-10 hidden group-hover:block
                       bg-bist-primary text-white text-xs rounded-lg p-2.5 w-52 shadow-lg leading-relaxed">
        {text}
      </span>
    </span>
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
