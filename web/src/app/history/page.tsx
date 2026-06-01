"use client";

import { useEffect, useState } from "react";
import { getHistory, deleteEntry, type HistoryEntry } from "@/lib/history";
import { useUser } from "@/lib/supabase/useUser";
import { fetchHistory } from "@/lib/supabase/generations";
import { BDDViewer } from "@/components/BDDViewer";
import { ScoreDisplay } from "@/components/ScoreDisplay";
import { type Generation } from "@/lib/supabase/types";
import { Clock, Trash2, ChevronDown, ChevronUp, LogIn, Terminal } from "lucide-react";
import Link from "next/link";

type AnyEntry = HistoryEntry | Generation;

function isGeneration(e: AnyEntry): e is Generation {
  return "created_at" in e && typeof (e as Generation).created_at === "string";
}

function entryDate(e: AnyEntry): Date {
  if (isGeneration(e)) return new Date(e.created_at);
  return new Date((e as HistoryEntry).timestamp);
}

function entryScore(e: AnyEntry) {
  if (isGeneration(e)) {
    return {
      cobertura: e.cobertura,
      clareza: e.clareza,
      estrutura: e.estrutura,
      executabilidade: e.executabilidade,
      score_final: e.score_final,
      aprovado: e.aprovado,
      threshold: e.threshold ?? 7,
    };
  }
  return (e as HistoryEntry).score;
}

function entryId(e: AnyEntry): string {
  if (isGeneration(e)) return e.id;
  return (e as HistoryEntry).id;
}

function ScoreBadge({ score, approved }: { score: number; approved: boolean }) {
  const color = approved ? "text-[#a3fb73] border-[#a3fb73]/30 bg-[#a3fb73]/8"
                         : "text-[#f59e0b] border-[#f59e0b]/30 bg-[#f59e0b]/8";
  return (
    <span className={`font-mono text-xs px-2 py-0.5 rounded border ${color}`}>
      {score.toFixed(1)}
    </span>
  );
}

function ModelBadge({ model }: { model: string }) {
  const isGemini = model.includes("flash") || model.includes("pro");
  return (
    <span className={`font-mono text-[10px] px-1.5 py-0.5 rounded border
      ${isGemini
        ? "text-[#60a5fa] border-[#60a5fa]/20 bg-[#60a5fa]/5"
        : "text-[#c4b5fd] border-[#c4b5fd]/20 bg-[#c4b5fd]/5"}`}>
      {model}
    </span>
  );
}

export default function HistoryPage() {
  const { user, loading: userLoading } = useUser();
  const [entries, setEntries] = useState<AnyEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [source, setSource] = useState<"cloud" | "local">("local");

  useEffect(() => {
    if (userLoading) return;

    async function load() {
      setLoading(true);
      if (user) {
        const cloud = await fetchHistory(50);
        if (cloud.length > 0) {
          setEntries(cloud);
          setSource("cloud");
          setLoading(false);
          return;
        }
      }
      // fallback: local storage
      setEntries(getHistory());
      setSource("local");
      setLoading(false);
    }

    load();
  }, [user, userLoading]);

  function handleDelete(id: string) {
    if (source === "local") {
      deleteEntry(id);
      setEntries(prev => prev.filter(e => entryId(e) !== id));
    }
  }

  function toggleExpand(id: string) {
    setExpanded(prev => prev === id ? null : id);
  }

  return (
    <div className="flex-1 flex flex-col">
      <div className="border-b border-[#a3fb73]/10 bg-[#243d2c]/20">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-5">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-baseline gap-3">
                <span className="text-[#5a7a65] font-mono text-sm select-none">$</span>
                <h1 className="text-lg font-mono font-semibold text-[#a3fb73] tracking-tight">
                  bist history
                  <span className="text-[#5a7a65] font-normal"> --list</span>
                </h1>
              </div>
              <p className="text-sm text-[#5a7a65] font-mono mt-1.5 ml-5">
                {entries.length} gerações &middot; {source === "cloud" ? "sincronizado" : "armazenamento local"}
              </p>
            </div>

            {!user && !userLoading && (
              <Link href="/login?redirect=/history" className="btn-ghost text-xs flex items-center gap-1.5">
                <LogIn className="w-3.5 h-3.5" />
                entrar para sincronizar
              </Link>
            )}
          </div>
        </div>
      </div>

      <div className="flex-1 max-w-5xl mx-auto w-full px-4 sm:px-6 py-6">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="flex items-center gap-2 font-mono text-sm text-[#5a7a65]">
              <div className="w-4 h-4 border-2 border-[#a3fb73]/30 border-t-[#a3fb73] rounded-full animate-spin" />
              carregando histórico...
            </div>
          </div>
        ) : entries.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 gap-5 text-center">
            <Clock className="w-8 h-8 text-[#3d5a44]" />
            <div>
              <p className="font-mono text-[#7a9b87]">nenhuma geração ainda</p>
              <p className="font-mono text-xs text-[#3d5a44] mt-1">suas gerações aparecerão aqui</p>
            </div>
            <Link href="/generate" className="btn-primary text-sm py-2.5 px-6">
              <Terminal className="w-4 h-4" />
              gerar agora
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {entries.map(entry => {
              const id = entryId(entry);
              const date = entryDate(entry);
              const score = entryScore(entry);
              const isExp = expanded === id;

              return (
                <div key={id} className="card overflow-hidden">
                  {/* Summary row */}
                  <div className="flex items-start gap-4 p-4">
                    <div className="flex-1 min-w-0 space-y-2">
                      <div className="flex items-center gap-2 flex-wrap">
                        <ScoreBadge score={score.score_final} approved={score.aprovado} />
                        <ModelBadge model={entry.model} />
                        <span className="text-[10px] font-mono text-[#3d5a44]">
                          {date.toLocaleDateString("pt-BR", { day: "2-digit", month: "short" })}{" "}
                          {date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}
                        </span>
                        {"attempts" in entry && (
                          <span className="text-[10px] font-mono text-[#3d5a44]">
                            {(entry as HistoryEntry).attempts} tentativa{(entry as HistoryEntry).attempts !== 1 ? "s" : ""}
                          </span>
                        )}
                      </div>
                      <p className="text-sm font-mono text-[#7a9b87] leading-snug line-clamp-2">
                        {entry.story}
                      </p>
                    </div>

                    <div className="flex items-center gap-1 shrink-0">
                      {source === "local" && (
                        <button
                          onClick={() => handleDelete(id)}
                          className="p-1.5 rounded text-[#3d5a44] hover:text-red-400 hover:bg-red-400/8 transition-colors"
                          title="Remover do histórico"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                      <button
                        onClick={() => toggleExpand(id)}
                        className="p-1.5 rounded text-[#5a7a65] hover:text-[#a3fb73] hover:bg-[#a3fb73]/8 transition-colors"
                      >
                        {isExp ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  {/* Expanded detail */}
                  {isExp && (
                    <div className="border-t border-[#a3fb73]/10 p-4 space-y-4">
                      <ScoreDisplay
                        score={score}
                        attempts={"attempts" in entry ? (entry as HistoryEntry).attempts : (entry as Generation).attempts}
                        totalTokens={"total_tokens" in entry ? entry.total_tokens : 0}
                        researchTokens={"research_tokens" in entry ? entry.research_tokens : 0}
                        durationSeconds={"duration_seconds" in entry ? entry.duration_seconds : 0}
                        converged={"converged" in entry ? entry.converged : false}
                      />
                      <BDDViewer bddText={entry.bdd_text} />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
