"use client";

import { useState, useRef } from "react";
import {
  Loader2, CheckCircle2, AlertCircle, Circle,
  Copy, Check, Download, RotateCcw, Sparkles, ChevronDown, ChevronUp,
} from "lucide-react";
import { createStory, generateBDD, generateUnitTests } from "@/lib/api";
import { BDDViewer } from "@/components/BDDViewer";
import type { GenerateResult, StoryCreateResult, UnitTestResult } from "@/types";

// ── Tipos ─────────────────────────────────────────────────────────────────────

type StepStatus = "idle" | "running" | "done" | "error";

const LANGUAGES = [
  { id: "python",     label: "Python",     framework: "pytest"  },
  { id: "javascript", label: "JavaScript", framework: "jest"    },
  { id: "typescript", label: "TypeScript", framework: "jest"    },
  { id: "java",       label: "Java",       framework: "junit5"  },
];

// ── Sub-componentes ───────────────────────────────────────────────────────────

function StepIcon({ status }: { status: StepStatus }) {
  if (status === "running")
    return <Loader2 className="w-5 h-5 text-[#a3fb73] animate-spin" />;
  if (status === "done")
    return <CheckCircle2 className="w-5 h-5 text-[#a3fb73]" />;
  if (status === "error")
    return <AlertCircle className="w-5 h-5 text-red-400" />;
  return <Circle className="w-5 h-5 text-bist-border" />;
}

function StatusBadge({ status }: { status: StepStatus }) {
  const map: Record<StepStatus, { label: string; cls: string }> = {
    idle:    { label: "Aguardando",  cls: "bg-bist-surface2 text-bist-dim border-bist-border2" },
    running: { label: "Gerando…",   cls: "bg-[#a3fb73]/10 text-[#2D6A3F] border-[#a3fb73]/30 animate-pulse" },
    done:    { label: "Concluído",  cls: "bg-[#a3fb73]/15 text-[#2D6A3F] border-[#a3fb73]/40" },
    error:   { label: "Erro",       cls: "bg-red-50 text-red-500 border-red-200" },
  };
  const { label, cls } = map[status];
  return (
    <span className={`text-[10px] font-code font-semibold px-2 py-0.5 rounded-full border ${cls}`}>
      {label}
    </span>
  );
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  function copy() {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }
  return (
    <button onClick={copy} className="btn-ghost text-xs gap-1">
      {copied ? <><Check className="w-3 h-3 text-[#2D6A3F]" /> Copiado</> : <><Copy className="w-3 h-3" /> Copiar</>}
    </button>
  );
}

function ExpandCard({ children, show }: { children: React.ReactNode; show: boolean }) {
  if (!show) return null;
  return <div className="animate-slide-up">{children}</div>;
}

// ── Página principal ──────────────────────────────────────────────────────────

export default function FluxoPage() {
  const [idea,    setIdea]    = useState("");
  const [lang,    setLang]    = useState(LANGUAGES[0]);
  const [showLang, setShowLang] = useState(false);

  const [s1, setS1] = useState<StepStatus>("idle");
  const [s2, setS2] = useState<StepStatus>("idle");
  const [s3, setS3] = useState<StepStatus>("idle");

  const [rules,     setRules]     = useState<StoryCreateResult | null>(null);
  const [bddResult, setBddResult] = useState<GenerateResult | null>(null);
  const [testResult, setTestResult] = useState<UnitTestResult | null>(null);

  const [s1Expanded, setS1Expanded] = useState(true);
  const [s2Expanded, setS2Expanded] = useState(true);
  const [s3Expanded, setS3Expanded] = useState(true);

  const [globalError, setGlobalError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  const step2Ref = useRef<HTMLDivElement>(null);
  const step3Ref = useRef<HTMLDivElement>(null);

  function reset() {
    setIdea(""); setS1("idle"); setS2("idle"); setS3("idle");
    setRules(null); setBddResult(null); setTestResult(null);
    setGlobalError(null); setRunning(false);
    setS1Expanded(true); setS2Expanded(true); setS3Expanded(true);
  }

  async function runFlow() {
    if (!idea.trim() || running) return;
    setRunning(true);
    setGlobalError(null);
    setRules(null); setBddResult(null); setTestResult(null);
    setS1("idle"); setS2("idle"); setS3("idle");

    // ── Step 1: Regras de negócio ─────────────────────────────────────────────
    setS1("running");
    let storyResult: StoryCreateResult;
    try {
      storyResult = await createStory({ idea: idea.trim(), model: "flash" });
      setRules(storyResult);
      setS1("done");
    } catch (e) {
      setS1("error");
      setGlobalError(e instanceof Error ? e.message : "Erro ao gerar regras de negócio.");
      setRunning(false);
      return;
    }

    // ── Step 2: BDD ───────────────────────────────────────────────────────────
    setTimeout(() => step2Ref.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 150);
    setS2("running");
    const fullStory = [
      storyResult.user_story,
      "",
      "Critérios de aceitação:",
      ...storyResult.acceptance_criteria.map(c => `- ${c}`),
    ].join("\n");

    let genResult: GenerateResult;
    try {
      genResult = await generateBDD({
        story: fullStory, model: "flash",
        threshold: 7.0, max_attempts: 5,
        research: false, until_converged: false,
      });
      setBddResult(genResult);
      setS2("done");
    } catch (e) {
      setS2("error");
      setGlobalError(e instanceof Error ? e.message : "Erro ao gerar BDD.");
      setRunning(false);
      return;
    }

    // ── Step 3: Testes unitários ──────────────────────────────────────────────
    setTimeout(() => step3Ref.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 150);
    setS3("running");
    try {
      const testRes = await generateUnitTests({
        bdd_text: genResult.bdd_text,
        language: lang.id,
        framework: lang.framework,
        model: "flash",
      });
      setTestResult(testRes);
      setS3("done");
    } catch (e) {
      setS3("error");
      setGlobalError(e instanceof Error ? e.message : "Erro ao gerar testes unitários.");
    } finally {
      setRunning(false);
    }
  }

  const anyStarted = s1 !== "idle" || s2 !== "idle" || s3 !== "idle";

  return (
    <div className="flex-1 max-w-3xl mx-auto px-4 sm:px-6 py-10 space-y-6">

      {/* Header */}
      <div className="space-y-1">
        <h1 className="text-lg font-semibold text-bist-primary">Fluxo completo</h1>
        <p className="text-xs text-bist-muted">
          Descreva uma funcionalidade — o pipeline gera as regras de negócio, o BDD e os testes automaticamente.
        </p>
      </div>

      {/* Input */}
      <div className="card p-5 space-y-4">
        <div className="space-y-2">
          <label className="text-xs font-medium text-bist-muted">Funcionalidade</label>
          <textarea
            className="textarea h-28 text-sm leading-relaxed"
            placeholder={"Ex: sistema de login com email e senha\nEx: carrinho de compras com cálculo de frete\nEx: aprovação de férias pelo gestor"}
            value={idea}
            onChange={e => setIdea(e.target.value)}
            disabled={running}
          />
        </div>

        {/* Language selector */}
        <div className="space-y-2">
          <button
            type="button"
            onClick={() => setShowLang(p => !p)}
            className="flex items-center gap-1.5 text-xs text-bist-muted hover:text-bist-primary transition-colors"
          >
            {showLang ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            Linguagem dos testes:{" "}
            <span className="font-medium text-bist-primary">{lang.label} / {lang.framework}</span>
          </button>

          {showLang && (
            <div className="flex flex-wrap gap-2 animate-slide-up">
              {LANGUAGES.map(l => (
                <button
                  key={l.id}
                  onClick={() => { setLang(l); setShowLang(false); }}
                  disabled={running}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                    lang.id === l.id
                      ? "bg-bist-primary text-white border-bist-primary"
                      : "border-bist-border text-bist-muted hover:border-bist-muted hover:text-bist-primary"
                  }`}
                >
                  {l.label} <span className="opacity-60">/ {l.framework}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={runFlow}
            disabled={running || !idea.trim()}
            className="btn-primary text-sm py-2.5 px-6 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {running
              ? <><Loader2 className="w-4 h-4 animate-spin" /> Executando fluxo...</>
              : <><Sparkles className="w-4 h-4" /> Executar fluxo</>
            }
          </button>

          {anyStarted && !running && (
            <button onClick={reset} className="btn-ghost text-xs gap-1.5">
              <RotateCcw className="w-3.5 h-3.5" /> Recomeçar
            </button>
          )}
        </div>
      </div>

      {/* Pipeline */}
      {anyStarted && (
        <div className="space-y-0">

          {/* ── Step 1: Regras ───────────────────────────────────────────────── */}
          <div className="relative pl-8">
            <div className="absolute left-[11px] top-5 bottom-0 w-px bg-bist-border" />
            <div className="absolute left-0 top-4 w-5.5 h-5.5 flex items-center justify-center">
              <StepIcon status={s1} />
            </div>

            <div className="pb-6">
              <div
                className="flex items-center justify-between cursor-pointer select-none py-1 mb-1"
                onClick={() => s1 === "done" && setS1Expanded(p => !p)}
              >
                <div className="flex items-center gap-2.5">
                  <span className="text-xs font-code text-bist-dim">01</span>
                  <span className="text-sm font-semibold text-bist-primary">Regras de negócio</span>
                  <StatusBadge status={s1} />
                </div>
                {s1 === "done" && (
                  <button className="text-bist-dim hover:text-bist-muted transition-colors">
                    {s1Expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>
                )}
              </div>

              {s1 === "running" && (
                <div className="card p-4 space-y-2">
                  <div className="h-3 bg-bist-surface2 rounded animate-pulse w-3/4" />
                  <div className="h-3 bg-bist-surface2 rounded animate-pulse w-1/2" />
                  <div className="h-3 bg-bist-surface2 rounded animate-pulse w-2/3" />
                </div>
              )}

              <ExpandCard show={s1 === "done" && s1Expanded && !!rules}>
                <div className="card p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-code text-bist-dim uppercase tracking-widest">User Story</p>
                    <CopyButton text={rules!.user_story} />
                  </div>
                  <p className="text-sm text-bist-primary leading-relaxed bg-bist-surface2 rounded-lg px-4 py-3 border border-bist-border2">
                    {rules!.user_story}
                  </p>

                  <p className="text-xs font-code text-bist-dim uppercase tracking-widest pt-1">
                    Critérios de aceitação
                    <span className="text-bist-border ml-1 normal-case font-sans">({rules!.acceptance_criteria.length})</span>
                  </p>
                  <ul className="space-y-1.5">
                    {rules!.acceptance_criteria.map((c, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-bist-mid">
                        <span className="font-code text-[10px] text-bist-dim w-4 shrink-0 mt-0.5 text-right">{i + 1}.</span>
                        {c}
                      </li>
                    ))}
                  </ul>
                </div>
              </ExpandCard>

              {s1 === "error" && (
                <div className="card p-3 border-red-200 bg-red-50 flex items-start gap-2">
                  <AlertCircle className="w-3.5 h-3.5 text-red-500 shrink-0 mt-0.5" />
                  <p className="text-xs text-red-600">{globalError}</p>
                </div>
              )}
            </div>
          </div>

          {/* ── Step 2: BDD ──────────────────────────────────────────────────── */}
          <div className="relative pl-8" ref={step2Ref}>
            <div className="absolute left-[11px] top-0 bottom-0 w-px bg-bist-border" />
            <div className="absolute left-0 top-4 flex items-center justify-center">
              <StepIcon status={s2} />
            </div>

            <div className="pb-6">
              <div
                className="flex items-center justify-between cursor-pointer select-none py-1 mb-1"
                onClick={() => s2 === "done" && setS2Expanded(p => !p)}
              >
                <div className="flex items-center gap-2.5">
                  <span className="text-xs font-code text-bist-dim">02</span>
                  <span className="text-sm font-semibold text-bist-primary">Cenários BDD</span>
                  <StatusBadge status={s2} />
                  {s2 === "done" && bddResult && (
                    <span className="text-[10px] font-code text-bist-dim">
                      score {bddResult.score.score_final.toFixed(1)} · {bddResult.attempts} tentativa{bddResult.attempts !== 1 ? "s" : ""}
                    </span>
                  )}
                </div>
                {s2 === "done" && (
                  <button className="text-bist-dim hover:text-bist-muted transition-colors">
                    {s2Expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>
                )}
              </div>

              {s2 === "running" && (
                <div className="card p-4 space-y-2">
                  <div className="h-3 bg-bist-surface2 rounded animate-pulse w-full" />
                  <div className="h-3 bg-bist-surface2 rounded animate-pulse w-4/5" />
                  <div className="h-3 bg-bist-surface2 rounded animate-pulse w-3/5" />
                  <div className="h-3 bg-bist-surface2 rounded animate-pulse w-full" />
                </div>
              )}

              <ExpandCard show={s2 === "done" && s2Expanded && !!bddResult}>
                <div className="space-y-2">
                  <div className="flex items-center justify-between px-1">
                    <span className="text-[10px] font-code text-bist-dim">output.feature</span>
                    <div className="flex items-center gap-2">
                      <CopyButton text={bddResult!.bdd_text} />
                      <a
                        href={`data:text/plain;charset=utf-8,${encodeURIComponent(bddResult!.bdd_text)}`}
                        download="output.feature"
                        className="btn-ghost text-xs gap-1"
                      >
                        <Download className="w-3 h-3" /> .feature
                      </a>
                    </div>
                  </div>
                  <BDDViewer bddText={bddResult!.bdd_text} />

                  <div className="grid grid-cols-4 gap-2 pt-1">
                    {([
                      ["Cobertura",       bddResult!.score.cobertura],
                      ["Clareza",         bddResult!.score.clareza],
                      ["Estrutura",       bddResult!.score.estrutura],
                      ["Exec.",           bddResult!.score.executabilidade],
                    ] as [string, number][]).map(([label, val]) => (
                      <div key={label} className="card-subtle p-2 rounded-lg text-center">
                        <p className="text-[10px] font-code text-bist-dim">{label}</p>
                        <p className="text-sm font-bold text-bist-primary">{val.toFixed(1)}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </ExpandCard>

              {s2 === "error" && (
                <div className="card p-3 border-red-200 bg-red-50 flex items-start gap-2">
                  <AlertCircle className="w-3.5 h-3.5 text-red-500 shrink-0 mt-0.5" />
                  <p className="text-xs text-red-600">{globalError}</p>
                </div>
              )}
            </div>
          </div>

          {/* ── Step 3: Unit Tests ───────────────────────────────────────────── */}
          <div className="relative pl-8" ref={step3Ref}>
            <div className="absolute left-[11px] top-0 top-5 h-5 w-px bg-bist-border" />
            <div className="absolute left-0 top-4 flex items-center justify-center">
              <StepIcon status={s3} />
            </div>

            <div className="pb-2">
              <div
                className="flex items-center justify-between cursor-pointer select-none py-1 mb-1"
                onClick={() => s3 === "done" && setS3Expanded(p => !p)}
              >
                <div className="flex items-center gap-2.5">
                  <span className="text-xs font-code text-bist-dim">03</span>
                  <span className="text-sm font-semibold text-bist-primary">Testes unitários</span>
                  <StatusBadge status={s3} />
                  {s3 === "done" && testResult && (
                    <span className="text-[10px] font-code text-bist-dim">
                      {testResult.num_tests} teste{testResult.num_tests !== 1 ? "s" : ""} · {lang.label}/{lang.framework}
                    </span>
                  )}
                </div>
                {s3 === "done" && (
                  <button className="text-bist-dim hover:text-bist-muted transition-colors">
                    {s3Expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>
                )}
              </div>

              {s3 === "running" && (
                <div className="card p-4 space-y-2">
                  <div className="h-3 bg-bist-surface2 rounded animate-pulse w-2/3" />
                  <div className="h-3 bg-bist-surface2 rounded animate-pulse w-full" />
                  <div className="h-3 bg-bist-surface2 rounded animate-pulse w-3/4" />
                  <div className="h-3 bg-bist-surface2 rounded animate-pulse w-full" />
                  <div className="h-3 bg-bist-surface2 rounded animate-pulse w-1/2" />
                </div>
              )}

              <ExpandCard show={s3 === "done" && s3Expanded && !!testResult}>
                <div className="space-y-2">
                  <div className="flex items-center justify-between px-1">
                    <span className="text-[10px] font-code text-bist-dim">
                      test_output.{testResult?.file_extension}
                    </span>
                    <div className="flex items-center gap-2">
                      <CopyButton text={testResult!.code} />
                      <a
                        href={`data:text/plain;charset=utf-8,${encodeURIComponent(testResult!.code)}`}
                        download={`test_output.${testResult!.file_extension}`}
                        className="btn-ghost text-xs gap-1"
                      >
                        <Download className="w-3 h-3" /> .{testResult!.file_extension}
                      </a>
                    </div>
                  </div>
                  <div className="card overflow-hidden">
                    <pre className="p-4 text-xs font-code text-bist-mid leading-relaxed overflow-x-auto whitespace-pre max-h-96">
                      {testResult!.code}
                    </pre>
                  </div>
                </div>
              </ExpandCard>

              {s3 === "error" && (
                <div className="card p-3 border-red-200 bg-red-50 flex items-start gap-2">
                  <AlertCircle className="w-3.5 h-3.5 text-red-500 shrink-0 mt-0.5" />
                  <p className="text-xs text-red-600">{globalError}</p>
                </div>
              )}
            </div>
          </div>

        </div>
      )}

    </div>
  );
}
