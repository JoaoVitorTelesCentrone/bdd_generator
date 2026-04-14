"use client";

import { useState, useRef, useEffect } from "react";
import {
  Sparkles, ChevronDown, ChevronUp, FlaskConical,
  Repeat, Loader2, AlertCircle, Info,
} from "lucide-react";
import { generateBDD, fetchModels } from "@/lib/api";
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
  const [models, setModels] = useState<Model[]>(initialModels);
  const [story, setStory] = useState("");
  const [model, setModel] = useState(initialModels.find(m => m.default)?.id ?? "flash");
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
      // Salva no Supabase se o usuário estiver autenticado
      if (user) {
        saveGeneration(user.id, story.trim(), model, res, { research, threshold })
          .then(saved => { if (saved) setSaved(true); });
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

  const selectedModel = models.find(m => m.id === model);

  return (
    <div className="grid grid-cols-1 xl:grid-cols-[480px_1fr] gap-6 h-full">
      {/* ── Left: Form ──────────────────────────────────────────────────── */}
      <div className="space-y-4">
        {/* Story Input */}
        <div className="card p-4 space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-zinc-300">User Story</label>
            <button onClick={loadExample} className="btn-ghost text-xs">
              <Sparkles className="w-3 h-3" />
              Exemplo
            </button>
          </div>
          <textarea
            className="textarea h-44 leading-relaxed"
            placeholder={"Como [persona], quero [ação] para [benefício].\n\nCritérios de aceitação:\n- ..."}
            value={story}
            onChange={e => setStory(e.target.value)}
          />
          <p className="text-xs text-zinc-600">{story.length} caracteres</p>
        </div>

        {/* Model Selector */}
        <div className="card p-4 space-y-3">
          <label className="text-sm font-medium text-zinc-300">Modelo</label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {models.map(m => (
              <button
                key={m.id}
                onClick={() => setModel(m.id)}
                className={[
                  "relative flex flex-col items-start px-3 py-2.5 rounded-lg border text-left transition-all duration-150",
                  model === m.id
                    ? "border-indigo-500 bg-indigo-600/10 text-indigo-300"
                    : "border-zinc-700 bg-zinc-800/50 text-zinc-400 hover:border-zinc-600 hover:text-zinc-300",
                ].join(" ")}
              >
                <span className="text-xs font-semibold leading-tight">{m.id}</span>
                <span className="text-[10px] text-zinc-500 leading-tight mt-0.5 truncate w-full">
                  {m.name.replace(/^(Gemini |Claude )/, "")}
                </span>
                <span className={`absolute top-1.5 right-1.5 text-[9px] font-medium ${m.provider === "gemini" ? "text-blue-500" : "text-violet-500"}`}>
                  {m.provider === "gemini" ? "G" : "C"}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Advanced Options */}
        <div className="card">
          <button
            className="w-full flex items-center justify-between px-4 py-3 text-sm font-medium text-zinc-300 hover:text-zinc-100 transition-colors"
            onClick={() => setShowAdvanced(p => !p)}
          >
            <span>Opções avançadas</span>
            {showAdvanced ? <ChevronUp className="w-4 h-4 text-zinc-500" /> : <ChevronDown className="w-4 h-4 text-zinc-500" />}
          </button>

          {showAdvanced && (
            <div className="px-4 pb-4 space-y-4 border-t border-zinc-800 pt-4">
              {/* Threshold */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs text-zinc-400 flex items-center gap-1">
                    Score mínimo (threshold)
                    <Tooltip text="Score necessário para aprovar o BDD. Valores mais altos exigem mais tentativas de refinamento." />
                  </label>
                  <span className="text-sm font-semibold text-indigo-400 tabular-nums">{threshold.toFixed(1)}</span>
                </div>
                <input type="range" min="1" max="10" step="0.5" value={threshold}
                  onChange={e => setThreshold(parseFloat(e.target.value))}
                  className="w-full accent-indigo-500 cursor-pointer" />
                <div className="flex justify-between text-[10px] text-zinc-600">
                  <span>1.0 (leniente)</span><span>10.0 (rigoroso)</span>
                </div>
              </div>

              {/* Max Attempts */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs text-zinc-400">Máximo de tentativas</label>
                  <span className="text-sm font-semibold text-zinc-300 tabular-nums">{maxAttempts}</span>
                </div>
                <input type="range" min="1" max="20" step="1" value={maxAttempts}
                  onChange={e => setMaxAttempts(parseInt(e.target.value))}
                  className="w-full accent-indigo-500 cursor-pointer" />
                <div className="flex justify-between text-[10px] text-zinc-600">
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
                  label="Auto-Research"
                  description="Analisa a story antes de gerar para extrair critérios de aceitação implícitos"
                  color="amber"
                />
                <Toggle
                  id="converged"
                  checked={untilConverged}
                  onChange={setUntilConverged}
                  icon={<Repeat className="w-3.5 h-3.5" />}
                  label="Until-Converged"
                  description="Refina até atingir o threshold (máx 50 tentativas), ignorando o limite acima"
                  color="violet"
                />
              </div>
            </div>
          )}
        </div>

        {/* Generate Button */}
        <button
          className="btn-primary w-full text-base py-3 shadow-lg shadow-indigo-500/20"
          disabled={loading || !story.trim()}
          onClick={handleGenerate}
        >
          {loading
            ? <><Loader2 className="w-4 h-4 animate-spin" /> Gerando cenários BDD...</>
            : <><Sparkles className="w-4 h-4" /> Gerar Cenários BDD</>
          }
        </button>

        {/* Loading progress */}
        {loading && (
          <div className="card p-3 space-y-2">
            <div className="flex items-center gap-2 text-xs text-zinc-400">
              <Loader2 className="w-3 h-3 animate-spin text-indigo-400" />
              <span>
                {research ? "Pesquisando story e gerando cenários..." : "Gerando e refinando cenários..."}
              </span>
            </div>
            <div className="h-1 bg-zinc-800 rounded-full overflow-hidden">
              <div className="h-full bg-indigo-500 animate-progress rounded-full" />
            </div>
            <p className="text-xs text-zinc-600">
              Modelo: <span className="text-zinc-400">{selectedModel?.name}</span>
              {research && <> &middot; <span className="text-amber-500">Auto-research ativo</span></>}
            </p>
          </div>
        )}
      </div>

      {/* ── Right: Results ───────────────────────────────────────────────── */}
      <div ref={resultRef} className="space-y-4 min-h-[300px]">
        {!result && !error && !loading && (
          <EmptyState />
        )}

        {error && (
          <div className="card p-4 border-red-500/30 bg-red-500/5 flex items-start gap-3">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-red-400">Erro na geração</p>
              <p className="text-xs text-zinc-400 mt-1">{error}</p>
              <p className="text-xs text-zinc-600 mt-2">Verifique se o backend está rodando: <code className="text-zinc-400">uvicorn backend.main:app --reload</code></p>
            </div>
          </div>
        )}

        {result && (
          <div className="space-y-4 animate-slide-up">
            {/* Score card */}
            <div className="card p-5">
              <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide mb-4">
                Avaliação de Qualidade
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
              <div className="px-4 py-3 border-b border-zinc-800">
                <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide">
                  Cenários BDD Gerados
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
  color: "amber" | "violet";
}) {
  const activeColor = color === "amber" ? "bg-amber-500" : "bg-violet-500";
  const textActive = color === "amber" ? "text-amber-400" : "text-violet-400";

  return (
    <label htmlFor={id} className="flex items-start gap-3 cursor-pointer group">
      <div className="relative mt-0.5">
        <input id={id} type="checkbox" className="sr-only" checked={checked} onChange={e => onChange(e.target.checked)} />
        <div className={`w-9 h-5 rounded-full transition-colors duration-200 ${checked ? activeColor : "bg-zinc-700"}`}>
          <div className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform duration-200 ${checked ? "translate-x-4" : "translate-x-0"}`} />
        </div>
      </div>
      <div>
        <p className={`text-sm font-medium flex items-center gap-1.5 ${checked ? textActive : "text-zinc-400"}`}>
          {icon}{label}
        </p>
        <p className="text-xs text-zinc-600 leading-snug mt-0.5">{description}</p>
      </div>
    </label>
  );
}

function Tooltip({ text }: { text: string }) {
  return (
    <span className="relative group cursor-help">
      <Info className="w-3 h-3 text-zinc-600" />
      <span className="absolute left-full ml-1 top-1/2 -translate-y-1/2 z-10 hidden group-hover:block
                       bg-zinc-800 border border-zinc-700 text-zinc-300 text-xs rounded-lg px-2 py-1 w-52 shadow-lg">
        {text}
      </span>
    </span>
  );
}

function EmptyState() {
  return (
    <div className="card p-10 flex flex-col items-center justify-center text-center gap-4 border-dashed border-zinc-700 min-h-[400px]">
      <div className="w-14 h-14 rounded-2xl bg-indigo-600/10 border border-indigo-600/20 flex items-center justify-center">
        <Sparkles className="w-6 h-6 text-indigo-400" />
      </div>
      <div>
        <p className="text-zinc-300 font-medium">Pronto para gerar</p>
        <p className="text-sm text-zinc-600 mt-1 max-w-xs">
          Insira uma user story à esquerda, escolha o modelo e clique em <strong className="text-zinc-400">Gerar Cenários BDD</strong>
        </p>
      </div>
      <div className="grid grid-cols-2 gap-2 w-full max-w-xs text-left mt-2">
        {[
          ["Cobertura", "30% do score"],
          ["Estrutura GWT", "30% do score"],
          ["Clareza", "20% do score"],
          ["Executabilidade", "20% do score"],
        ].map(([k, v]) => (
          <div key={k} className="bg-zinc-800/50 rounded-lg px-3 py-2">
            <p className="text-xs font-medium text-zinc-300">{k}</p>
            <p className="text-[10px] text-zinc-600">{v}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
