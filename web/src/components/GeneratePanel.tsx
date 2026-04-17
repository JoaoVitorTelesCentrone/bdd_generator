"use client";

import { useState, useRef } from "react";
import {
  Terminal, ChevronDown, ChevronUp, FlaskConical,
  Repeat, Loader2, AlertCircle, Info,
} from "lucide-react";

const DEFAULT_MODEL = "flash";
import { generateBDD } from "@/lib/api";
import { addEntry } from "@/lib/history";
import { ScoreDisplay } from "./ScoreDisplay";
import { BDDViewer } from "./BDDViewer";
import { saveGeneration } from "@/lib/supabase/generations";
import { useUser } from "@/lib/supabase/useUser";
import type { GenerateResult, Model } from "@/types";

const EXAMPLE_STORIES = [
  "Como usuário, quero fazer login com email e senha para acessar minha conta.\n\nCritérios de aceitação:\n- Login com credenciais válidas\n- Mensagem de erro para credenciais inválidas\n- Bloqueio após 3 tentativas",
  "Como cliente, quero adicionar produtos ao carrinho para comprá-los depois.\n\nCritérios:\n- Adicionar produto disponível\n- Não permite adicionar produto sem estoque\n- Atualizar quantidade",
  "Como gestor, quero aprovar solicitações de férias para controlar ausências.\n\nCritérios:\n- Visualizar lista de solicitações pendentes\n- Aprovar ou rejeitar com justificativa\n- Notificar funcionário",
];

export function GeneratePanel({ initialModels }: { initialModels: Model[] }) {
  const [story, setStory] = useState("");
  const model = DEFAULT_MODEL;
  const [threshold, setThreshold] = useState(7.0);
  const [maxAttempts, setMaxAttempts] = useState(5);
  const [research, setResearch] = useState(false);
  const [untilConverged, setUntilConverged] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GenerateResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const { user } = useUser();
  const resultRef = useRef<HTMLDivElement>(null);

  async function handleGenerate() {
    if (!story.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await generateBDD({ story: story.trim(), model, threshold, max_attempts: maxAttempts, research, until_converged: untilConverged });
      setResult(res);
      setSaved(false);
      // Save to local history
      addEntry({
        timestamp: Date.now(),
        story: story.trim(),
        model,
        bdd_text: res.bdd_text,
        score: res.score,
        attempts: res.attempts,
        total_tokens: res.total_tokens,
        research_tokens: res.research_tokens,
        converged: res.converged,
        duration_seconds: res.duration_seconds,
        options: { research, threshold },
      });
      setSaved(true);
      if (user) {
        saveGeneration(user.id, story.trim(), model, res, { research, threshold });
      }
      setTimeout(() => resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 100);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  }

  function loadExample() {
    const idx = Math.floor(Math.random() * EXAMPLE_STORIES.length);
    setStory(EXAMPLE_STORIES[idx]);
  }

  return (
    <div className="grid grid-cols-1 xl:grid-cols-[460px_1fr] gap-5 h-full">

      {/* ── Left: Form ──────────────────────────────────────────────────── */}
      <div className="space-y-3">

        {/* Story Input */}
        <div className="card p-4 space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-mono text-[#7a9b87]">
              <span className="text-[#5a7a65] mr-1">//</span> user story
            </label>
            <button onClick={loadExample} className="btn-ghost text-xs">
              <Terminal className="w-3 h-3" />
              exemplo
            </button>
          </div>
          <textarea
            className="textarea h-44 leading-relaxed text-sm"
            placeholder={"Como [persona], quero [ação] para [benefício].\n\nCritérios de aceitação:\n- ..."}
            value={story}
            onChange={e => setStory(e.target.value)}
          />
          <p className="text-[10px] text-[#3d5a44] font-mono">{story.length} chars</p>
        </div>

        {/* Advanced Options */}
        <div className="card">
          <button
            className="w-full flex items-center justify-between px-4 py-3 text-sm font-mono text-[#5a7a65] hover:text-[#7a9b87] transition-colors"
            onClick={() => setShowAdvanced(p => !p)}
          >
            <span>// opções avançadas</span>
            {showAdvanced
              ? <ChevronUp className="w-4 h-4" />
              : <ChevronDown className="w-4 h-4" />
            }
          </button>

          {showAdvanced && (
            <div className="px-4 pb-4 space-y-4 border-t border-[#a3fb73]/10 pt-4">
              {/* Threshold */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs text-[#5a7a65] font-mono flex items-center gap-1">
                    threshold (score mínimo)
                    <Tooltip text="Score necessário para aprovar o BDD. Valores mais altos exigem mais tentativas de refinamento." />
                  </label>
                  <span className="text-sm font-mono font-bold text-[#a3fb73] tabular-nums">{threshold.toFixed(1)}</span>
                </div>
                <input type="range" min="1" max="10" step="0.5" value={threshold}
                  onChange={e => setThreshold(parseFloat(e.target.value))}
                  className="w-full accent-[#a3fb73] cursor-pointer" />
                <div className="flex justify-between text-[10px] text-[#3d5a44] font-mono">
                  <span>1.0 (leniente)</span><span>10.0 (rigoroso)</span>
                </div>
              </div>

              {/* Max Attempts */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs text-[#5a7a65] font-mono">max tentativas</label>
                  <span className="text-sm font-mono font-bold text-[#eef9e8] tabular-nums">{maxAttempts}</span>
                </div>
                <input type="range" min="1" max="20" step="1" value={maxAttempts}
                  onChange={e => setMaxAttempts(parseInt(e.target.value))}
                  className="w-full accent-[#a3fb73] cursor-pointer" />
                <div className="flex justify-between text-[10px] text-[#3d5a44] font-mono">
                  <span>1</span><span>20</span>
                </div>
              </div>

              {/* Toggles */}
              <div className="space-y-2">
                <Toggle
                  id="research"
                  checked={research}
                  onChange={setResearch}
                  icon={<FlaskConical className="w-3.5 h-3.5" />}
                  label="--auto-research"
                  description="analisa a story antes de gerar para extrair critérios de aceitação implícitos"
                  color="lime"
                />
                <Toggle
                  id="converged"
                  checked={untilConverged}
                  onChange={setUntilConverged}
                  icon={<Repeat className="w-3.5 h-3.5" />}
                  label="--until-converged"
                  description="refina até atingir o threshold (máx 50 tentativas), ignorando o limite acima"
                  color="pale"
                />
              </div>
            </div>
          )}
        </div>

        {/* Generate Button */}
        <button
          className="btn-primary w-full text-sm py-3 shadow-lg shadow-[#a3fb73]/10"
          disabled={loading || !story.trim()}
          onClick={handleGenerate}
        >
          {loading
            ? <><Loader2 className="w-4 h-4 animate-spin" /> gerando cenários bdd...</>
            : <><Terminal className="w-4 h-4" /> bist generate --run</>
          }
        </button>

        {/* Loading progress */}
        {loading && (
          <div className="card p-3 space-y-2">
            <div className="flex items-center gap-2 text-xs font-mono text-[#5a7a65]">
              <Loader2 className="w-3 h-3 animate-spin text-[#a3fb73]" />
              <span>
                {research ? "// pesquisando story e gerando cenários..." : "// gerando e refinando cenários..."}
              </span>
            </div>
            <div className="h-0.5 bg-[#243d2c] rounded-full overflow-hidden">
              <div className="h-full bg-[#a3fb73] animate-progress rounded-full" />
            </div>
            <p className="text-[10px] font-mono text-[#3d5a44]">
              model: <span className="text-[#7a9b87]">{DEFAULT_MODEL}</span>
              {research && <> &middot; <span className="text-[#a3fb73]">auto-research on</span></>}
            </p>
          </div>
        )}

        {/* Saved indicator */}
        {saved && (
          <p className="text-[10px] font-mono text-[#a3fb73]/60 text-center">
            ✓ salvo no histórico
          </p>
        )}
      </div>

      {/* ── Right: Results ───────────────────────────────────────────────── */}
      <div ref={resultRef} className="space-y-4 min-h-[300px]">
        {!result && !error && !loading && <EmptyState />}

        {error && (
          <div className="card p-4 border border-red-500/20 bg-red-500/5 flex items-start gap-3">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
            <div className="font-mono">
              <p className="text-sm font-semibold text-red-400">erro na geração</p>
              <p className="text-xs text-[#7a9b87] mt-1">{error}</p>
              <p className="text-xs text-[#3d5a44] mt-2">
                verifique se o backend está rodando: <code className="text-[#7a9b87]">uvicorn backend.main:app --reload</code>
              </p>
            </div>
          </div>
        )}

        {result && (
          <div className="space-y-4 animate-slide-up">
            {/* Score card */}
            <div className="card p-5">
              <h2 className="text-xs font-mono text-[#5a7a65] uppercase tracking-widest mb-4">
                // quality assessment
              </h2>
              <ScoreDisplay
                score={result.score}
                attempts={result.attempts}
                totalTokens={result.total_tokens}
                researchTokens={result.research_tokens}
                durationSeconds={result.duration_seconds}
                converged={result.converged}
              />
            </div>

            {/* BDD Output */}
            <div className="card overflow-hidden">
              <div className="px-4 py-3 border-b border-[#a3fb73]/10">
                <h2 className="text-xs font-mono text-[#5a7a65] uppercase tracking-widest">
                  // output.feature
                </h2>
              </div>
              <div className="p-2">
                <BDDViewer bddText={result.bdd_text} />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Sub-components ──────────────────────────────────────────────────────────

function Toggle({
  id, checked, onChange, icon, label, description, color,
}: {
  id: string;
  checked: boolean;
  onChange: (v: boolean) => void;
  icon: React.ReactNode;
  label: string;
  description: string;
  color: "lime" | "pale";
}) {
  const trackActive  = color === "lime" ? "bg-[#a3fb73]" : "bg-[#7a9b87]";
  const labelActive  = color === "lime" ? "text-[#a3fb73]" : "text-[#c4e8a8]";

  return (
    <label htmlFor={id} className="flex items-start gap-3 cursor-pointer group">
      <div className="relative mt-0.5 flex-shrink-0">
        <input id={id} type="checkbox" className="sr-only" checked={checked} onChange={e => onChange(e.target.checked)} />
        <div className={`w-9 h-5 rounded-full transition-colors duration-200 ${checked ? trackActive : "bg-[#243d2c] border border-[#a3fb73]/20"}`}>
          <div className={`absolute top-0.5 left-0.5 w-4 h-4 bg-[#eef9e8] rounded-full shadow transition-transform duration-200 ${checked ? "translate-x-4" : "translate-x-0"}`} />
        </div>
      </div>
      <div>
        <p className={`text-sm font-mono flex items-center gap-1.5 ${checked ? labelActive : "text-[#5a7a65]"}`}>
          {icon}{label}
        </p>
        <p className="text-[10px] font-mono text-[#3d5a44] leading-snug mt-0.5">{description}</p>
      </div>
    </label>
  );
}

function Tooltip({ text }: { text: string }) {
  return (
    <span className="relative group cursor-help">
      <Info className="w-3 h-3 text-[#3d5a44]" />
      <span className="absolute left-full ml-1 top-1/2 -translate-y-1/2 z-10 hidden group-hover:block
                       bg-[#243d2c] border border-[#a3fb73]/20 text-[#7a9b87] text-xs font-mono
                       rounded p-2 w-52 shadow-xl">
        {text}
      </span>
    </span>
  );
}

function EmptyState() {
  return (
    <div className="card p-10 flex flex-col items-center justify-center text-center gap-5
                    border-dashed border-[#a3fb73]/12 min-h-[420px]">
      {/* Terminal window mockup */}
      <div className="w-full max-w-xs">
        <div className="card-terminal rounded-t-none border-b-0 p-0">
          <div className="flex items-center gap-1.5 px-3 py-2 border-b border-[#a3fb73]/15 bg-[#243d2c]/50">
            <div className="w-2.5 h-2.5 rounded-full bg-red-500/60" />
            <div className="w-2.5 h-2.5 rounded-full bg-[#f59e0b]/60" />
            <div className="w-2.5 h-2.5 rounded-full bg-[#a3fb73]/60" />
            <span className="text-[10px] font-mono text-[#3d5a44] ml-2">output.feature</span>
          </div>
          <div className="p-4 text-left space-y-1 text-xs font-mono">
            <p className="text-[#a3fb73]">Funcionalidade: <span className="text-[#7a9b87]">aguardando input...</span></p>
            <p className="text-[#5a7a65] pl-2">Cenário: <span className="opacity-40">___</span></p>
            <p className="text-[#5a7a65] pl-4">Dado que <span className="opacity-40">___</span></p>
            <p className="text-[#5a7a65] pl-4">Quando <span className="opacity-40">___</span></p>
            <p className="text-[#5a7a65] pl-4">Então <span className="opacity-40">___</span></p>
          </div>
        </div>
      </div>

      <div>
        <p className="text-[#7a9b87] font-mono text-sm">pronto para gerar</p>
        <p className="text-xs font-mono text-[#3d5a44] mt-1 max-w-xs">
          insira uma user story à esquerda e execute <span className="text-[#a3fb73]">bist generate --run</span>
        </p>
      </div>

      {/* Metrics legend */}
      <div className="grid grid-cols-2 gap-2 w-full max-w-xs text-left">
        {[
          ["cobertura",       "peso 30%"],
          ["estrutura gwt",   "peso 30%"],
          ["clareza",         "peso 20%"],
          ["executabilidade", "peso 20%"],
        ].map(([k, v]) => (
          <div key={k} className="bg-[#243d2c]/40 border border-[#a3fb73]/8 rounded px-3 py-2">
            <p className="text-[10px] font-mono font-semibold text-[#a3fb73]">{k}</p>
            <p className="text-[9px] font-mono text-[#3d5a44] mt-0.5">{v}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
