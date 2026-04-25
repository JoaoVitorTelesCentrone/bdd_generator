"use client";

import { useState } from "react";
import {
  Lightbulb, ArrowRight, Loader2, AlertCircle, CheckSquare,
  Check, Edit3, RotateCcw,
} from "lucide-react";
import { createStory } from "@/lib/api";
import type { StoryCreateResult } from "@/types";

const DEFAULT_MODEL = "flash";

export function StoryCreatorPanel() {
  const model = DEFAULT_MODEL;
  const [idea, setIdea]       = useState("");
  const [result, setResult]   = useState<StoryCreateResult | null>(null);
  const [editedStory, setEditedStory]         = useState("");
  const [editedCriteria, setEditedCriteria]   = useState<string[]>([]);
  const [editingStory, setEditingStory]       = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState<string | null>(null);

  async function handleCreate() {
    if (!idea.trim()) return;
    setLoading(true); setError(null);
    try {
      const res = await createStory({ idea: idea.trim(), model });
      setResult(res);
      setEditedStory(res.user_story);
      setEditedCriteria([...res.acceptance_criteria]);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  }

  function updateCriteria(idx: number, value: string) {
    setEditedCriteria(prev => prev.map((c, i) => i === idx ? value : c));
  }

  function restart() {
    setIdea(""); setResult(null); setError(null); setEditingStory(false);
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">

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

      {/* Input */}
      {!result && (
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
            onKeyDown={e => { if (e.key === "Enter" && e.ctrlKey) handleCreate(); }}
          />
          <p className="text-[10px] text-bist-dim font-code">{idea.length} chars · Ctrl+Enter para gerar</p>
          <button className="btn-primary w-full py-3 text-sm" disabled={loading || !idea.trim()} onClick={handleCreate}>
            {loading
              ? <><Loader2 className="w-4 h-4 animate-spin" /> Gerando regras de negócio...</>
              : <><ArrowRight className="w-4 h-4" /> Gerar stories</>
            }
          </button>
        </div>
      )}

      {/* Resultado */}
      {result && (
        <div className="space-y-4 animate-slide-up">

          {/* User Story */}
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

          {/* Critérios */}
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

          {/* Ações */}
          <div className="flex gap-3">
            <button onClick={restart} className="btn-secondary text-sm gap-1.5">
              <RotateCcw className="w-3.5 h-3.5" /> Nova ideia
            </button>
            <button onClick={handleCreate} disabled={loading} className="btn-ghost text-sm gap-1.5">
              {loading
                ? <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Regenerando...</>
                : <><Check className="w-3.5 h-3.5" /> Regenerar</>
              }
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
