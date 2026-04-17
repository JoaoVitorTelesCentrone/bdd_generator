"use client";

import { useState } from "react";
import {
  Lightbulb, ArrowRight, Loader2, AlertCircle, CheckSquare,
  Terminal, Copy, Check, Edit3,
} from "lucide-react";
import { createStory, generateBDD } from "@/lib/api";
import { addEntry } from "@/lib/history";
import { ScoreDisplay } from "./ScoreDisplay";
import { BDDViewer } from "./BDDViewer";
import type { StoryCreateResult, GenerateResult } from "@/types";

const DEFAULT_MODEL = "flash";

type Step = "idea" | "story" | "bdd";

export function StoryCreatorPanel() {
  const [step, setStep] = useState<Step>("idea");
  const model = DEFAULT_MODEL;

  // Step 1
  const [idea, setIdea] = useState("");

  // Step 2
  const [storyResult, setStoryResult] = useState<StoryCreateResult | null>(null);
  const [editedStory, setEditedStory] = useState("");
  const [editedCriteria, setEditedCriteria] = useState<string[]>([]);
  const [editingStory, setEditingStory] = useState(false);

  // Step 3
  const [bddResult, setBddResult] = useState<GenerateResult | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  async function handleCreateStory() {
    if (!idea.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await createStory({ idea: idea.trim(), model });
      setStoryResult(res);
      setEditedStory(res.user_story);
      setEditedCriteria([...res.acceptance_criteria]);
      setStep("story");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerateBDD() {
    setLoading(true);
    setError(null);
    const fullStory = buildFullStory();
    try {
      const res = await generateBDD({
        story: fullStory,
        model,
        threshold: 7.0,
        max_attempts: 5,
        research: false,
        until_converged: false,
      });
      setBddResult(res);
      addEntry({
        timestamp: Date.now(),
        story: fullStory,
        model,
        bdd_text: res.bdd_text,
        score: res.score,
        attempts: res.attempts,
        total_tokens: res.total_tokens,
        research_tokens: res.research_tokens,
        converged: res.converged,
        duration_seconds: res.duration_seconds,
        options: { research: false, threshold: 7.0 },
      });
      setStep("bdd");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  }

  function buildFullStory(): string {
    const criteria = editedCriteria.filter(c => c.trim()).map(c => `- ${c}`).join("\n");
    return `${editedStory}\n\nCritérios de aceitação:\n${criteria}`;
  }

  function updateCriteria(idx: number, value: string) {
    setEditedCriteria(prev => prev.map((c, i) => i === idx ? value : c));
  }

  function addCriteria() {
    setEditedCriteria(prev => [...prev, ""]);
  }

  function removeCriteria(idx: number) {
    setEditedCriteria(prev => prev.filter((_, i) => i !== idx));
  }

  function copyBDD() {
    if (!bddResult) return;
    navigator.clipboard.writeText(bddResult.bdd_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function restart() {
    setStep("idea");
    setIdea("");
    setStoryResult(null);
    setBddResult(null);
    setError(null);
  }


  return (
    <div className="max-w-3xl mx-auto space-y-6">

      {/* ── Stepper ─────────────────────────────────────────────────────── */}
      <div className="flex items-center gap-0 font-mono text-xs">
        {(["idea", "story", "bdd"] as Step[]).map((s, i) => {
          const labels: Record<Step, string> = { idea: "01 ideia", story: "02 user story", bdd: "03 bdd" };
          const done = step === "story" && s === "idea"
            || step === "bdd" && (s === "idea" || s === "story");
          const active = step === s;
          return (
            <div key={s} className="flex items-center">
              {i > 0 && (
                <div className={`w-12 h-px mx-1 ${done || active ? "bg-[#a3fb73]/40" : "bg-[#243d2c]"}`} />
              )}
              <span className={[
                "px-2 py-1 rounded transition-colors",
                active ? "text-[#a3fb73] bg-[#a3fb73]/10 border border-[#a3fb73]/25" :
                done ? "text-[#5a7a65]" : "text-[#3d5a44]",
              ].join(" ")}>
                {done && <Check className="w-3 h-3 inline mr-1" />}
                {labels[s]}
              </span>
            </div>
          );
        })}
      </div>

      {/* ── Error ───────────────────────────────────────────────────────── */}
      {error && (
        <div className="card p-4 border border-red-500/20 bg-red-500/5 flex items-start gap-3">
          <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
          <div className="font-mono">
            <p className="text-sm font-semibold text-red-400">erro</p>
            <p className="text-xs text-[#7a9b87] mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* ── Step 1: Idea ────────────────────────────────────────────────── */}
      {step === "idea" && (
        <div className="card p-6 space-y-5">
          <div className="flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-[#a3fb73]" />
            <h2 className="text-sm font-mono text-[#7a9b87]">// descreva sua ideia</h2>
          </div>

          <textarea
            className="textarea h-32 text-sm leading-relaxed"
            placeholder={"Ex: quero um sistema de login com email e senha\nEx: o usuário precisa adicionar produtos ao carrinho\nEx: gestor precisa aprovar solicitações de férias"}
            value={idea}
            onChange={e => setIdea(e.target.value)}
            onKeyDown={e => { if (e.key === "Enter" && e.ctrlKey) handleCreateStory(); }}
          />
          <p className="text-[10px] text-[#3d5a44] font-mono">{idea.length} chars · ctrl+enter para gerar</p>

          <button
            className="btn-primary w-full py-3 text-sm"
            disabled={loading || !idea.trim()}
            onClick={handleCreateStory}
          >
            {loading
              ? <><Loader2 className="w-4 h-4 animate-spin" /> gerando user story...</>
              : <><ArrowRight className="w-4 h-4" /> gerar user story + critérios</>
            }
          </button>
        </div>
      )}

      {/* ── Step 2: Story + Criteria ─────────────────────────────────────── */}
      {step === "story" && storyResult && (
        <div className="space-y-4">

          {/* User Story */}
          <div className="card p-5 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckSquare className="w-4 h-4 text-[#a3fb73]" />
                <h2 className="text-sm font-mono text-[#7a9b87]">// user story</h2>
              </div>
              <button
                onClick={() => setEditingStory(p => !p)}
                className="btn-ghost text-xs gap-1"
              >
                <Edit3 className="w-3 h-3" />
                {editingStory ? "fechar" : "editar"}
              </button>
            </div>

            {editingStory ? (
              <textarea
                className="textarea h-20 text-sm leading-relaxed"
                value={editedStory}
                onChange={e => setEditedStory(e.target.value)}
              />
            ) : (
              <p className="text-sm font-mono text-[#eef9e8] leading-relaxed bg-[#243d2c]/60 rounded px-4 py-3 border border-[#a3fb73]/10">
                {editedStory}
              </p>
            )}
          </div>

          {/* Acceptance Criteria */}
          <div className="card p-5 space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-mono text-[#7a9b87]">
                <span className="text-[#5a7a65] mr-1">//</span>
                critérios de aceitação
                <span className="text-[#3d5a44] ml-2">({editedCriteria.length})</span>
              </h2>
              <button onClick={addCriteria} className="btn-ghost text-xs">+ adicionar</button>
            </div>

            <ul className="space-y-2">
              {editedCriteria.map((c, i) => (
                <li key={i} className="flex items-center gap-2">
                  <span className="text-[#a3fb73]/50 font-mono text-xs w-5 shrink-0">{i + 1}.</span>
                  <input
                    className="input flex-1 text-sm py-2"
                    value={c}
                    onChange={e => updateCriteria(i, e.target.value)}
                  />
                  <button
                    onClick={() => removeCriteria(i)}
                    className="text-[#3d5a44] hover:text-red-400 transition-colors font-mono text-sm px-1"
                    title="remover"
                  >
                    ×
                  </button>
                </li>
              ))}
            </ul>
          </div>

          {/* Preview */}
          <div className="card p-4 bg-[#243d2c]/30">
            <p className="text-[10px] font-mono text-[#3d5a44] mb-2">// preview que será enviado ao gerador</p>
            <pre className="text-xs font-mono text-[#7a9b87] whitespace-pre-wrap leading-relaxed">
              {buildFullStory()}
            </pre>
          </div>

          <div className="flex gap-3">
            <button onClick={restart} className="btn-secondary text-sm flex-shrink-0">
              ← recomeçar
            </button>
            <button
              className="btn-primary flex-1 py-3 text-sm"
              disabled={loading || !editedStory.trim()}
              onClick={handleGenerateBDD}
            >
              {loading
                ? <><Loader2 className="w-4 h-4 animate-spin" /> gerando bdd...</>
                : <><Terminal className="w-4 h-4" /> gerar bdd</>
              }
            </button>
          </div>
        </div>
      )}

      {/* ── Step 3: BDD Result ───────────────────────────────────────────── */}
      {step === "bdd" && bddResult && (
        <div className="space-y-4 animate-slide-up">

          {/* Score */}
          <div className="card p-5">
            <h2 className="text-xs font-mono text-[#5a7a65] uppercase tracking-widest mb-4">
              // quality assessment
            </h2>
            <ScoreDisplay
              score={bddResult.score}
              attempts={bddResult.attempts}
              totalTokens={bddResult.total_tokens}
              researchTokens={bddResult.research_tokens}
              durationSeconds={bddResult.duration_seconds}
              converged={bddResult.converged}
            />
          </div>

          {/* BDD */}
          <div className="card overflow-hidden">
            <div className="px-4 py-3 border-b border-[#a3fb73]/10 flex items-center justify-between">
              <h2 className="text-xs font-mono text-[#5a7a65] uppercase tracking-widest">
                // output.feature
              </h2>
              <button onClick={copyBDD} className="btn-ghost text-xs">
                {copied ? <><Check className="w-3 h-3" /> copiado!</> : <><Copy className="w-3 h-3" /> copiar</>}
              </button>
            </div>
            <div className="p-2">
              <BDDViewer bddText={bddResult.bdd_text} />
            </div>
          </div>

          <div className="flex gap-3">
            <button onClick={restart} className="btn-secondary text-sm flex-shrink-0">
              ← nova ideia
            </button>
            <button
              onClick={() => setStep("story")}
              className="btn-secondary text-sm flex-shrink-0"
            >
              ← editar story
            </button>
            <a
              href={`data:text/plain;charset=utf-8,${encodeURIComponent(bddResult.bdd_text)}`}
              download="feature.feature"
              className="btn-primary text-sm flex-1 text-center py-2.5 flex items-center justify-center gap-2"
            >
              <Terminal className="w-4 h-4" /> baixar .feature
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
