"use client";

import { useState, useRef } from "react";
import {
  Loader2, CheckCircle2, AlertCircle, Circle,
  Copy, Check, Download, RotateCcw, Sparkles,
  ChevronDown, ChevronUp, ArrowRight, Building2,
  FlaskConical, TestTube2, Zap,
} from "lucide-react";
import { createStory, generateBDD, generateUnitTests } from "@/lib/api";
import { BDDViewer } from "@/components/BDDViewer";
import { MetricBar } from "@/components/MetricBar";
import type { GenerateResult, StoryCreateResult, UnitTestResult } from "@/types";

// ── Config ─────────────────────────────────────────────────────────────────────
const MODEL = "llama"; // Groq Llama 3.3 70B — free

const LANGUAGES = [
  { id: "python",     label: "Python",     framework: "pytest"  },
  { id: "javascript", label: "JavaScript", framework: "jest"    },
  { id: "typescript", label: "TypeScript", framework: "jest"    },
  { id: "java",       label: "Java",       framework: "junit5"  },
];

const EXAMPLES = [
  "Sistema de login com email e senha, bloqueio após 3 tentativas e recuperação de senha",
  "Carrinho de compras com cálculo de frete, cupom de desconto e validação de estoque",
  "Aprovação de solicitações de férias pelo gestor com notificação ao funcionário",
];

// ── Tipos ──────────────────────────────────────────────────────────────────────
type StepStatus = "idle" | "running" | "done" | "error";

// ── Sub-componentes ────────────────────────────────────────────────────────────

function StepIndicator({ n, status }: { n: number; status: StepStatus }) {
  if (status === "running")
    return <Loader2 className="w-5 h-5 text-[#a3fb73] animate-spin flex-shrink-0" />;
  if (status === "done")
    return <CheckCircle2 className="w-5 h-5 text-[#a3fb73] flex-shrink-0" />;
  if (status === "error")
    return <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />;
  return (
    <span className="w-5 h-5 rounded-full border border-bist-border flex items-center justify-center flex-shrink-0">
      <span className="text-[10px] font-code text-bist-dim">{n}</span>
    </span>
  );
}

function StatusChip({ status }: { status: StepStatus }) {
  const cfg: Record<StepStatus, { label: string; cls: string }> = {
    idle:    { label: "Aguardando", cls: "text-bist-dim bg-bist-surface2 border-bist-border2" },
    running: { label: "Gerando…",  cls: "text-[#2D6A3F] bg-[#a3fb73]/10 border-[#a3fb73]/30 animate-pulse" },
    done:    { label: "Concluído", cls: "text-[#2D6A3F] bg-[#a3fb73]/15 border-[#a3fb73]/40" },
    error:   { label: "Erro",      cls: "text-red-500 bg-red-50 border-red-200" },
  };
  const { label, cls } = cfg[status];
  return (
    <span className={`text-[10px] font-code font-semibold px-2 py-0.5 rounded-full border ${cls}`}>
      {label}
    </span>
  );
}

function CopyBtn({ text }: { text: string }) {
  const [ok, setOk] = useState(false);
  function copy() {
    navigator.clipboard.writeText(text);
    setOk(true);
    setTimeout(() => setOk(false), 2000);
  }
  return (
    <button onClick={copy} className="btn-ghost text-xs gap-1">
      {ok
        ? <><Check className="w-3 h-3 text-[#2D6A3F]" /> Copiado</>
        : <><Copy className="w-3 h-3" /> Copiar</>
      }
    </button>
  );
}

function Skeleton({ lines = 3 }: { lines?: number }) {
  return (
    <div className="card p-4 space-y-2.5">
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className={`h-3 bg-bist-surface2 rounded animate-pulse`}
             style={{ width: `${[75, 55, 65, 80, 50][i % 5]}%` }} />
      ))}
    </div>
  );
}

// ── Página ─────────────────────────────────────────────────────────────────────
export default function FluxoPage() {
  const [idea,    setIdea]    = useState("");
  const [lang,    setLang]    = useState(LANGUAGES[0]);

  const [s1, setS1] = useState<StepStatus>("idle");
  const [s2, setS2] = useState<StepStatus>("idle");
  const [s3, setS3] = useState<StepStatus>("idle");

  const [story,   setStory]   = useState<StoryCreateResult | null>(null);
  const [bdd,     setBdd]     = useState<GenerateResult | null>(null);
  const [tests,   setTests]   = useState<UnitTestResult | null>(null);

  const [exp1, setExp1] = useState(true);
  const [exp2, setExp2] = useState(true);
  const [exp3, setExp3] = useState(true);

  const [error,   setError]   = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  const refS2 = useRef<HTMLDivElement>(null);
  const refS3 = useRef<HTMLDivElement>(null);

  const anyStarted = s1 !== "idle";

  function reset() {
    setIdea(""); setError(null); setRunning(false);
    setS1("idle"); setS2("idle"); setS3("idle");
    setStory(null); setBdd(null); setTests(null);
    setExp1(true); setExp2(true); setExp3(true);
  }

  async function run() {
    if (!idea.trim() || running) return;
    setRunning(true); setError(null);
    setStory(null); setBdd(null); setTests(null);
    setS1("idle"); setS2("idle"); setS3("idle");

    // ── Passo 1: Negócio → User Story + Critérios ────────────────────────────
    setS1("running");
    let storyRes: StoryCreateResult;
    try {
      storyRes = await createStory({ idea: idea.trim(), model: MODEL });
      setStory(storyRes);
      setS1("done");
    } catch (e) {
      setS1("error");
      setError(e instanceof Error ? e.message : "Erro ao gerar user story.");
      setRunning(false);
      return;
    }

    // ── Passo 2: BDD ─────────────────────────────────────────────────────────
    setTimeout(() => refS2.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 200);
    setS2("running");
    const fullStory = [
      storyRes.user_story,
      "",
      "Critérios de aceitação:",
      ...storyRes.acceptance_criteria.map(c => `- ${c}`),
    ].join("\n");

    let bddRes: GenerateResult;
    try {
      bddRes = await generateBDD({
        story: fullStory, model: MODEL,
        threshold: 7.0, max_attempts: 5,
        research: false, until_converged: false,
      });
      setBdd(bddRes);
      setS2("done");
    } catch (e) {
      setS2("error");
      setError(e instanceof Error ? e.message : "Erro ao gerar BDD.");
      setRunning(false);
      return;
    }

    // ── Passo 3: TDD — Testes unitários ──────────────────────────────────────
    setTimeout(() => refS3.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 200);
    setS3("running");
    try {
      const testRes = await generateUnitTests({
        bdd_text: bddRes.bdd_text,
        language: lang.id,
        framework: lang.framework,
        model: MODEL,
      });
      setTests(testRes);
      setS3("done");
    } catch (e) {
      setS3("error");
      setError(e instanceof Error ? e.message : "Erro ao gerar testes.");
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="flex-1 flex flex-col">

      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <div className="border-b border-bist-border bg-bist-surface">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6 space-y-4">
          <div className="space-y-1">
            <h1 className="text-lg font-semibold text-bist-primary">Fluxo completo</h1>
            <p className="text-sm text-bist-muted">
              Descreva uma funcionalidade — o pipeline gera a user story, os cenários BDD e os testes automaticamente.
            </p>
          </div>

          {/* Flow visual */}
          <div className="flex items-center gap-2 pt-1">
            {[
              { icon: Building2,   label: "Negócio",  sub: "User story + critérios" },
              { icon: FlaskConical,label: "BDD",       sub: "Cenários Gherkin"       },
              { icon: TestTube2,   label: "TDD",       sub: "Testes unitários"       },
            ].map(({ icon: Icon, label, sub }, i) => (
              <div key={label} className="flex items-center gap-2">
                {i > 0 && <ArrowRight className="w-4 h-4 text-bist-border flex-shrink-0" />}
                <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-bist-surface2 border border-bist-border">
                  <Icon className="w-3.5 h-3.5 text-bist-muted flex-shrink-0" />
                  <div className="hidden sm:block">
                    <p className="text-xs font-semibold text-bist-primary leading-none">{label}</p>
                    <p className="text-[10px] text-bist-dim leading-none mt-0.5">{sub}</p>
                  </div>
                  <p className="text-xs font-semibold text-bist-primary sm:hidden">{label}</p>
                </div>
              </div>
            ))}
            <div className="ml-auto flex items-center gap-1 text-[10px] font-code text-[#2D6A3F]">
              <Zap className="w-3 h-3" />
              Llama 3.3 70B · grátis
            </div>
          </div>
        </div>
      </div>

      {/* ── Body ───────────────────────────────────────────────────────────── */}
      <div className="flex-1 max-w-3xl mx-auto w-full px-4 sm:px-6 py-6 space-y-6">

        {/* Input card */}
        <div className="card p-5 space-y-4">
          <div className="space-y-2">
            <label className="text-xs font-medium text-bist-muted uppercase tracking-widest font-code">
              Funcionalidade
            </label>
            <textarea
              className="textarea h-28 text-sm leading-relaxed"
              placeholder="Ex: sistema de login com email e senha&#10;Ex: carrinho de compras com cálculo de frete&#10;Ex: aprovação de férias pelo gestor"
              value={idea}
              onChange={e => setIdea(e.target.value)}
              disabled={running}
            />
            {!idea && (
              <div className="flex flex-wrap gap-1.5">
                {EXAMPLES.map(ex => (
                  <button key={ex} onClick={() => setIdea(ex)}
                    className="text-[10px] text-bist-dim border border-bist-border2 px-2 py-1 rounded hover:text-bist-primary hover:border-bist-border transition-colors">
                    {ex.slice(0, 40)}…
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Linguagem dos testes */}
          <div className="space-y-2">
            <p className="text-xs font-code text-bist-dim">Linguagem dos testes unitários</p>
            <div className="flex flex-wrap gap-1.5">
              {LANGUAGES.map(l => (
                <button key={l.id} onClick={() => setLang(l)} disabled={running}
                  className={`text-xs px-3 py-1.5 rounded-lg border transition-all font-medium ${
                    lang.id === l.id
                      ? "bg-bist-primary text-white border-bist-primary"
                      : "border-bist-border text-bist-muted hover:border-bist-muted hover:text-bist-primary"
                  }`}>
                  {l.label} <span className="opacity-60 font-normal">/ {l.framework}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-3 pt-1">
            <button onClick={run} disabled={running || !idea.trim()}
              className="btn-primary text-sm py-2.5 px-6 gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
              {running
                ? <><Loader2 className="w-4 h-4 animate-spin" /> Executando pipeline...</>
                : <><Sparkles className="w-4 h-4" /> Executar fluxo completo</>
              }
            </button>
            {anyStarted && !running && (
              <button onClick={reset} className="btn-ghost text-xs gap-1.5">
                <RotateCcw className="w-3.5 h-3.5" /> Recomeçar
              </button>
            )}
          </div>
        </div>

        {/* Error global */}
        {error && (
          <div className="card p-4 border-red-200 bg-red-50 flex items-start gap-3">
            <AlertCircle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-red-600">Erro no pipeline</p>
              <p className="text-xs text-red-500 mt-0.5">{error}</p>
            </div>
          </div>
        )}

        {/* ── Pipeline ─────────────────────────────────────────────────────── */}
        {anyStarted && (
          <div className="relative space-y-0">

            {/* Linha vertical do timeline */}
            <div className="absolute left-[9px] top-5 bottom-5 w-px bg-bist-border pointer-events-none" />

            {/* ── Step 1: Negócio ─────────────────────────────────── */}
            <div className="relative pl-9 pb-6">
              <div className="absolute left-0 top-[18px]">
                <StepIndicator n={1} status={s1} />
              </div>

              <StepHeader
                label="Negócio"
                sub="User story + critérios de aceitação"
                status={s1}
                expanded={exp1}
                onToggle={() => s1 === "done" && setExp1(p => !p)}
              />

              {s1 === "running" && <Skeleton lines={4} />}

              {s1 === "done" && story && exp1 && (
                <div className="card p-5 space-y-4 animate-slide-up">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-[10px] font-code text-bist-dim uppercase tracking-widest">User Story</p>
                      <CopyBtn text={story.user_story} />
                    </div>
                    <p className="text-sm text-bist-primary leading-relaxed bg-bist-surface2 rounded-lg px-4 py-3 border border-bist-border2">
                      {story.user_story}
                    </p>
                  </div>

                  <div>
                    <p className="text-[10px] font-code text-bist-dim uppercase tracking-widest mb-2">
                      Critérios de aceitação
                      <span className="ml-1 normal-case font-sans text-bist-border">({story.acceptance_criteria.length})</span>
                    </p>
                    <ul className="space-y-1.5">
                      {story.acceptance_criteria.map((c, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-bist-mid">
                          <span className="font-code text-[10px] text-bist-dim w-5 shrink-0 mt-0.5 text-right">{i + 1}.</span>
                          {c}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {s1 === "error" && <ErrorCard message={error} />}
            </div>

            {/* ── Step 2: BDD ─────────────────────────────────────── */}
            <div className="relative pl-9 pb-6" ref={refS2}>
              <div className="absolute left-0 top-[18px]">
                <StepIndicator n={2} status={s2} />
              </div>

              <StepHeader
                label="BDD"
                sub="Cenários Gherkin avaliados por 4 métricas"
                status={s2}
                expanded={exp2}
                onToggle={() => s2 === "done" && setExp2(p => !p)}
                extra={bdd && s2 === "done"
                  ? `score ${bdd.score.score_final.toFixed(1)} · ${bdd.attempts} tentativa${bdd.attempts !== 1 ? "s" : ""}`
                  : undefined
                }
              />

              {s2 === "running" && <Skeleton lines={5} />}

              {s2 === "done" && bdd && exp2 && (
                <div className="space-y-3 animate-slide-up">
                  {/* Métricas */}
                  <div className="card p-4 space-y-2">
                    <MetricBar label="Cobertura"       value={bdd.score.cobertura}       weight="30%" />
                    <MetricBar label="Estrutura GWT"   value={bdd.score.estrutura}        weight="30%" />
                    <MetricBar label="Clareza"         value={bdd.score.clareza}          weight="20%" />
                    <MetricBar label="Executabilidade" value={bdd.score.executabilidade}  weight="20%" />
                  </div>

                  {/* BDD Viewer */}
                  <div>
                    <div className="flex items-center justify-between px-1 pb-2">
                      <span className="text-[10px] font-code text-bist-dim">output.feature</span>
                      <div className="flex items-center gap-2">
                        <CopyBtn text={bdd.bdd_text} />
                        <a href={`data:text/plain;charset=utf-8,${encodeURIComponent(bdd.bdd_text)}`}
                           download="output.feature" className="btn-ghost text-xs gap-1">
                          <Download className="w-3 h-3" /> .feature
                        </a>
                      </div>
                    </div>
                    <BDDViewer bddText={bdd.bdd_text} />
                  </div>
                </div>
              )}

              {s2 === "error" && <ErrorCard message={error} />}
            </div>

            {/* ── Step 3: TDD ─────────────────────────────────────── */}
            <div className="relative pl-9 pb-2" ref={refS3}>
              <div className="absolute left-0 top-[18px]">
                <StepIndicator n={3} status={s3} />
              </div>

              <StepHeader
                label="TDD"
                sub={`Testes unitários — ${lang.label} / ${lang.framework}`}
                status={s3}
                expanded={exp3}
                onToggle={() => s3 === "done" && setExp3(p => !p)}
                extra={tests && s3 === "done"
                  ? `${tests.num_tests} teste${tests.num_tests !== 1 ? "s" : ""}`
                  : undefined
                }
              />

              {s3 === "running" && <Skeleton lines={6} />}

              {s3 === "done" && tests && exp3 && (
                <div className="space-y-2 animate-slide-up">
                  <div className="flex items-center justify-between px-1">
                    <span className="text-[10px] font-code text-bist-dim">
                      test_output.{tests.file_extension}
                    </span>
                    <div className="flex items-center gap-2">
                      <CopyBtn text={tests.code} />
                      <a href={`data:text/plain;charset=utf-8,${encodeURIComponent(tests.code)}`}
                         download={`test_output.${tests.file_extension}`}
                         className="btn-ghost text-xs gap-1">
                        <Download className="w-3 h-3" /> .{tests.file_extension}
                      </a>
                    </div>
                  </div>
                  <div className="card overflow-hidden">
                    <pre className="p-4 text-xs font-code text-bist-mid leading-relaxed overflow-x-auto whitespace-pre max-h-[420px]">
                      {tests.code}
                    </pre>
                  </div>
                </div>
              )}

              {s3 === "error" && <ErrorCard message={error} />}
            </div>

          </div>
        )}

        {/* Download all — só aparece quando tudo está pronto */}
        {s1 === "done" && s2 === "done" && s3 === "done" && bdd && tests && (
          <div className="card p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-[#a3fb73]/5 border-[#a3fb73]/30 animate-slide-up">
            <div>
              <p className="text-sm font-semibold text-bist-primary">Pipeline concluído</p>
              <p className="text-xs text-bist-muted mt-0.5">
                User story, cenários BDD e testes unitários gerados com sucesso.
              </p>
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              <a href={`data:text/plain;charset=utf-8,${encodeURIComponent(bdd.bdd_text)}`}
                 download="output.feature"
                 className="btn-secondary text-xs gap-1.5">
                <Download className="w-3.5 h-3.5" /> BDD
              </a>
              <a href={`data:text/plain;charset=utf-8,${encodeURIComponent(tests.code)}`}
                 download={`test_output.${tests.file_extension}`}
                 className="btn-primary text-xs gap-1.5">
                <Download className="w-3.5 h-3.5" /> Testes
              </a>
              <button onClick={reset} className="btn-ghost text-xs gap-1">
                <RotateCcw className="w-3.5 h-3.5" /> Nova
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

// ── Helper components ──────────────────────────────────────────────────────────

function StepHeader({
  label, sub, status, expanded, onToggle, extra,
}: {
  label: string; sub: string; status: StepStatus;
  expanded: boolean; onToggle: () => void; extra?: string;
}) {
  return (
    <div className="flex items-center justify-between cursor-pointer select-none py-1 mb-2" onClick={onToggle}>
      <div className="flex items-center gap-2.5 flex-wrap">
        <span className="text-sm font-semibold text-bist-primary">{label}</span>
        <span className="text-xs text-bist-dim hidden sm:inline">{sub}</span>
        <StatusChip status={status} />
        {extra && <span className="text-[10px] font-code text-bist-dim">{extra}</span>}
      </div>
      {status === "done" && (
        <button className="text-bist-dim hover:text-bist-muted transition-colors ml-2">
          {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      )}
    </div>
  );
}

function ErrorCard({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <div className="card p-3 border-red-200 bg-red-50 flex items-start gap-2">
      <AlertCircle className="w-3.5 h-3.5 text-red-500 shrink-0 mt-0.5" />
      <p className="text-xs text-red-600">{message}</p>
    </div>
  );
}
