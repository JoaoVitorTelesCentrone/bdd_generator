"use client";

import { useState } from "react";
import {
  Lightbulb, ArrowRight, Loader2, AlertCircle, CheckSquare,
  Download, Copy, Check, Edit3, Sparkles,
} from "lucide-react";
import { createStory, generateBDD } from "@/lib/api";
import { addEntry } from "@/lib/history";
import { ScoreDisplay } from "./ScoreDisplay";
import { BDDViewer } from "./BDDViewer";
import type { StoryCreateResult, GenerateResult } from "@/types";

const DEFAULT_MODEL = "flash";
type Step = "idea" | "story" | "bdd";

export function StoryCreatorPanel() {
  const [step, setStep]     = useState<Step>("idea");
  const model               = DEFAULT_MODEL;
  const [idea, setIdea]     = useState("");

  const [storyResult, setStoryResult]     = useState<StoryCreateResult | null>(null);
  const [editedStory, setEditedStory]     = useState("");
  const [editedCriteria, setEditedCriteria] = useState<string[]>([]);
  const [editingStory, setEditingStory]   = useState(false);

  const [bddResult, setBddResult] = useState<GenerateResult | null>(null);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState<string | null>(null);
  const [copied, setCopied]       = useState(false);

  async function handleCreateStory() {
    if (!idea.trim()) return;
    setLoading(true); setError(null);
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
    setLoading(true); setError(null);
    const fullStory = buildFullStory();
    try {
      const res = await generateBDD({ story: fullStory, model, threshold: 7.0, max_attempts: 5, research: false, until_converged: false });
      setBddResult(res);
      addEntry({
        timestamp: Date.now(), story: fullStory, model,
        bdd_text: res.bdd_text, score: res.score, attempts: res.attempts,
        total_tokens: res.total_tokens, research_tokens: res.research_tokens,
        converged: res.converged, duration_seconds: res.duration_seconds,
        options: { research: false, threshold: 7.0 },
      });
      setStep("bdd");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  }

  function buildFullStory() {
    const criteria = editedCriteria.filter(c => c.trim()).map(c => `- ${c}`).join("\n");
    return `${editedStory}\n\nCritérios de aceitação:\n${criteria}`;
  }

  function updateCriteria(idx: number, value: string) {
    setEditedCriteria(prev => prev.map((c, i) => i === idx ? value : c));
  }

  function restart() {
    setStep("idea"); setIdea(""); setStoryResult(null); setBddResult(null); setError(null);
  }

  function copyBDD() {
    if (!bddResult) return;
    navigator.clipboard.writeText(bddResult.bdd_text);
    setCopied(true); setTimeout(() => setCopied(false), 2000);
  }

  const stepLabels: Record<Step, string> = { idea: "Ideia", story: "User Story", bdd: "BDD" };
  const steps: Step[] = ["idea", "story", "bdd"];

  return (
    <div className="max-w-3xl mx-auto space-y-6">

      {/* Stepper */}
      <div className="flex items-center">
        {steps.map((s, i) => {
          const done   = (step === "story" && s === "idea") || (step === "bdd" && (s === "idea" || s === "story"));
          const active = step === s;
          return (
            <div key={s} className="flex items-center">
              {i > 0 && <div className={`w-12 h-px mx-2 ${done ? "bg-[#a3fb73]" : "bg-bist-border"}`} />}
              <div className={[
                "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-colors",
                active ? "bg-bist-primary text-white" :
                done   ? "bg-[#a3fb73]/15 text-[#2D6A3F] border border-[#a3fb73]/30" :
                         "text-bist-dim border border-bist-border2",
              ].join(" ")}>
                {done && <Check className="w-3 h-3" />}
                {!done && <span className="font-code text-[10px]">0{i+1}</span>}
                {stepLabels[s]}
              </div>
            </div>
          );
        })}
      </div>

      {/* Error */}
      {error && (
        <div className="card p-4 border-red-200 bg-red-50 flex items-start gap-3">
          <AlertCircle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-red-600">Erro</p>
            <p className="text-xs text-red-500 mt-0.5">{error}</p>
          </div>
        </div>
      )}

      {/* Step 1: Ideia */}
      {step === "idea" && (
        <div className="card p-6 space-y-5">
          <div className="flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-[#a3fb73]" />
            <h2 className="text-sm font-semibold text-bist-primary">Descreva sua ideia</h2>
          </div>
          <textarea
            className="textarea h-32 text-sm leading-relaxed"
            placeholder={"Ex: quero um sistema de login com email e senha\nEx: o usuário precisa adicionar produtos ao carrinho\nEx: gestor precisa aprovar solicitações de férias"}
            value={idea}
            onChange={e => setIdea(e.target.value)}
            onKeyDown={e => { if (e.key === "Enter" && e.ctrlKey) handleCreateStory(); }}
          />
          <div className="flex items-center justify-between">
            <p className="text-[10px] text-bist-dim font-code">{idea.length} chars · Ctrl+Enter para gerar</p>
          </div>
          <button className="btn-primary w-full py-3 text-sm" disabled={loading || !idea.trim()} onClick={handleCreateStory}>
            {loading
              ? <><Loader2 className="w-4 h-4 animate-spin" /> Gerando user story...</>
              : <><ArrowRight className="w-4 h-4" /> Gerar user story + critérios</>
            }
          </button>
        </div>
      )}

      {/* Step 2: Story + Criteria */}
      {step === "story" && storyResult && (
        <div className="space-y-4">
          <div className="card p-5 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckSquare className="w-4 h-4 text-[#2D6A3F]" />
                <h2 className="text-sm font-semibold text-bist-primary">User Story</h2>
              </div>
              <button onClick={() => setEditingStory(p => !p)} className="btn-ghost text-xs gap-1">
                <Edit3 className="w-3 h-3" />
                {editingStory ? "Fechar" : "Editar"}
              </button>
            </div>
            {editingStory ? (
              <textarea className="textarea h-20 text-sm leading-relaxed" value={editedStory} onChange={e => setEditedStory(e.target.value)} />
            ) : (
              <p className="text-sm text-bist-primary leading-relaxed bg-bist-surface2 rounded-lg px-4 py-3 border border-bist-border2">
                {editedStory}
              </p>
            )}
          </div>

          <div className="card p-5 space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-bist-primary">
                Critérios de aceitação
                <span className="text-bist-dim font-normal ml-2 text-xs">({editedCriteria.length})</span>
              </h2>
              <button onClick={() => setEditedCriteria(p => [...p, ""])} className="btn-ghost text-xs">+ Adicionar</button>
            </div>
            <ul className="space-y-2">
              {editedCriteria.map((c, i) => (
                <li key={i} className="flex items-center gap-2">
                  <span className="text-bist-dim font-code text-xs w-5 shrink-0 text-right">{i + 1}.</span>
                  <input
                    className="input flex-1 text-sm py-2"
                    value={c}
                    onChange={e => updateCriteria(i, e.target.value)}
                  />
                  <button
                    onClick={() => setEditedCriteria(p => p.filter((_, j) => j !== i))}
                    className="text-bist-dim hover:text-red-500 transition-colors text-lg leading-none px-1"
                  >×</button>
                </li>
              ))}
            </ul>
          </div>

          <div className="card-subtle p-4 rounded-lg">
            <p className="text-xs text-bist-dim mb-2 font-code">Preview que será enviado ao gerador</p>
            <pre className="text-xs font-code text-bist-muted whitespace-pre-wrap leading-relaxed">{buildFullStory()}</pre>
          </div>

          <div className="flex gap-3">
            <button onClick={restart} className="btn-secondary text-sm flex-shrink-0">← Recomeçar</button>
            <button className="btn-primary flex-1 py-3 text-sm" disabled={loading || !editedStory.trim()} onClick={handleGenerateBDD}>
              {loading
                ? <><Loader2 className="w-4 h-4 animate-spin" /> Gerando BDD...</>
                : <><Sparkles className="w-4 h-4" /> Gerar BDD</>
              }
            </button>
          </div>
        </div>
      )}

      {/* Step 3: BDD */}
      {step === "bdd" && bddResult && (
        <div className="space-y-4 animate-slide-up">
          <div className="card p-5">
            <p className="text-xs font-code text-bist-dim uppercase tracking-widest mb-4">Avaliação de qualidade</p>
            <ScoreDisplay
              score={bddResult.score}
              attempts={bddResult.attempts}
              totalTokens={bddResult.total_tokens}
              researchTokens={bddResult.research_tokens}
              durationSeconds={bddResult.duration_seconds}
              converged={bddResult.converged}
            />
          </div>

          <BDDViewer bddText={bddResult.bdd_text} />

          <div className="flex gap-3">
            <button onClick={restart} className="btn-secondary text-sm flex-shrink-0">← Nova ideia</button>
            <button onClick={() => setStep("story")} className="btn-secondary text-sm flex-shrink-0">← Editar story</button>
            <button onClick={copyBDD} className="btn-secondary text-sm flex-shrink-0 gap-1.5">
              {copied ? <><Check className="w-3.5 h-3.5 text-[#2D6A3F]" /> Copiado</> : <><Copy className="w-3.5 h-3.5" /> Copiar</>}
            </button>
            <a
              href={`data:text/plain;charset=utf-8,${encodeURIComponent(bddResult.bdd_text)}`}
              download="feature.feature"
              className="btn-primary text-sm flex-1 flex items-center justify-center gap-2 py-2.5"
            >
              <Download className="w-4 h-4" /> Baixar .feature
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
