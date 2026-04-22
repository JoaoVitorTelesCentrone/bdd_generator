"use client";

import { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Loader2, Wifi } from "lucide-react";
import { getAutoresearchRun, autoresearchWsUrl } from "@/lib/api";
import { ExperimentsTable } from "@/components/ExperimentsTable";
import { BestConfigCard } from "@/components/BestConfigCard";
import type { AutoresearchRunDetail, ExperimentRow } from "@/types";

function statusBadge(s: string) {
  const cls =
    s === "done"    ? "text-[#2D6A3F] bg-[#a3fb73]/15 border-[#a3fb73]/30" :
    s === "running" ? "text-amber-700 bg-amber-50 border-amber-200" :
                      "text-red-600 bg-red-50 border-red-200";
  return (
    <span className={`text-xs font-code px-2.5 py-0.5 rounded-full border font-medium ${cls}`}>
      {s}
    </span>
  );
}

function fmtDate(ts: number) {
  return new Date(ts * 1000).toLocaleString("pt-BR", { dateStyle: "long", timeStyle: "short" });
}

function ProgressBar({ current, total }: { current: number; total: number }) {
  const pct = total > 0 ? Math.round((current / total) * 100) : 0;
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-xs font-code text-bist-muted">
        <span>Progresso</span>
        <span className="tabular-nums">{current}/{total} ({pct}%)</span>
      </div>
      <div className="h-1.5 bg-bist-border rounded-full overflow-hidden">
        <div
          className="h-full bg-[#a3fb73] rounded-full transition-all duration-300"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

function LiveLog({ logs, done }: { logs: string[]; done: boolean }) {
  const bottomRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs.length]);

  return (
    <div className="card overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-bist-border bg-bist-surface2">
        <Wifi className="w-3.5 h-3.5 text-[#2D6A3F]" />
        <span className="text-xs font-semibold text-bist-primary">Live log</span>
        {!done && (
          <span className="ml-auto flex items-center gap-1.5 text-xs text-amber-600">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" /> ao vivo
          </span>
        )}
      </div>
      <div className="p-4 space-y-1 max-h-48 overflow-y-auto bg-[#1a2c21]">
        {logs.map((l, i) => (
          <p key={i} className="text-xs font-code text-[#7a9b87]">
            <span className="text-[#3d5a44] mr-2">›</span>{l}
          </p>
        ))}
        {!done && <p className="text-[#5a7a65] font-code text-xs animate-pulse">▮</p>}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}

export default function AutoresearchDetailPage() {
  const { id }  = useParams<{ id: string }>();
  const runId   = Number(id);

  const [run, setRun]             = useState<AutoresearchRunDetail | null>(null);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState("");

  // Live state accumulated from WebSocket
  const [liveExperiments, setLiveExperiments] = useState<ExperimentRow[]>([]);
  const [liveProgress, setLiveProgress]       = useState(0);
  const [liveTotal, setLiveTotal]             = useState(0);
  const [logs, setLogs]                       = useState<string[]>(["Conectando ao pipeline..."]);
  const [wsDone, setWsDone]                   = useState(false);
  const doneRef = useRef(false);

  async function load() {
    setLoading(true); setError("");
    try { setRun(await getAutoresearchRun(runId)); }
    catch (e: unknown) { setError(e instanceof Error ? e.message : String(e)); }
    finally { setLoading(false); }
  }

  useEffect(() => { load(); }, [runId]);

  // Open WebSocket only while run is in progress
  useEffect(() => {
    if (!run || run.status !== "running") return;

    let ws: WebSocket;
    let reconnectTimer: ReturnType<typeof setTimeout>;
    let attempt = 0;
    const MAX_RECONNECTS = 5;

    function connect() {
      ws = new WebSocket(autoresearchWsUrl(runId));

      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data) as Record<string, unknown>;

          if (msg.type === "log" && typeof msg.message === "string") {
            setLogs(prev => [...prev, msg.message as string]);
          }

          if (msg.type === "experiment") {
            const row: ExperimentRow = {
              experiment:      msg.i as number,
              mutation:        msg.mutation as string,
              avg_score:       msg.avg_score as number,
              n_approved:      msg.n_approved as number,
              total_tokens:    msg.total_tokens as number,
              accepted:        msg.accepted as boolean,
              is_best:         msg.is_best as boolean,
              ...(msg.config as object),
            } as ExperimentRow;
            setLiveExperiments(prev => [...prev, row]);
            setLiveProgress(msg.i as number);
            setLiveTotal(msg.total as number);
          }

          if (msg.type === "done") {
            doneRef.current = true;
            setWsDone(true);
            ws.close();
            setTimeout(load, 1000);
          }
        } catch { /* ignore malformed frames */ }
      };

      ws.onerror = () => setLogs(prev => [...prev, "Erro de conexão WebSocket"]);

      ws.onclose = () => {
        if (!doneRef.current && attempt < MAX_RECONNECTS) {
          attempt++;
          const delay = Math.min(1000 * 2 ** attempt, 30_000);
          setLogs(prev => [...prev, `Reconectando em ${delay / 1000}s… (${attempt}/${MAX_RECONNECTS})`]);
          reconnectTimer = setTimeout(connect, delay);
        }
      };
    }

    connect();
    return () => {
      clearTimeout(reconnectTimer);
      if (ws && ws.readyState !== WebSocket.CLOSED) ws.close();
    };
  }, [run?.status]);

  if (loading) return (
    <div className="flex items-center justify-center flex-1 py-20 gap-2">
      <Loader2 className="w-5 h-5 text-bist-muted animate-spin" />
      <span className="text-sm text-bist-muted">Carregando run...</span>
    </div>
  );

  if (error) return (
    <div className="flex-1 max-w-5xl mx-auto px-4 sm:px-6 py-10 space-y-4">
      <Link href="/autoresearch" className="btn-ghost text-xs gap-1.5 inline-flex">
        <ArrowLeft className="w-3.5 h-3.5" /> Voltar
      </Link>
      <div className="card p-6 text-center border-red-200 bg-red-50">
        <p className="text-sm text-red-600">{error}</p>
        <button onClick={load} className="btn-secondary text-xs mt-3">Tentar novamente</button>
      </div>
    </div>
  );

  if (!run) return null;

  const isLive       = run.status === "running";
  const isDone       = run.status === "done";
  const experiments  = isLive && !wsDone ? liveExperiments : run.experiments;
  const progress     = isLive ? liveProgress : (run.experiments.length - 1);
  const total        = isLive ? liveTotal : run.n_experiments;
  const baselineRow  = experiments.find(e => e.experiment === 0);
  const baselineScore = run.baseline_score ?? baselineRow?.avg_score ?? null;

  return (
    <div className="flex-1 flex flex-col">
      <div className="border-b border-bist-border bg-bist-surface">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-5">
          <div className="flex items-center gap-2 mb-1.5">
            <Link href="/autoresearch" className="text-xs text-bist-muted hover:text-bist-primary transition-colors flex items-center gap-1">
              <ArrowLeft className="w-3.5 h-3.5" /> Lab
            </Link>
            <span className="text-bist-dim">/</span>
            <span className="text-sm font-semibold text-bist-primary">Run #{run.id}</span>
            {statusBadge(run.status)}
          </div>
          <p className="text-xs text-bist-dim">
            {fmtDate(run.started_at)} · modelo: <span className="font-code">{run.model}</span>
            {" · "}{run.n_experiments} experimentos · sample: {run.sample_size} stories
          </p>
        </div>
      </div>

      <div className="flex-1 max-w-5xl mx-auto w-full px-4 sm:px-6 py-6 space-y-5">

        {isLive && (
          <>
            <ProgressBar current={progress} total={total || run.n_experiments} />
            <LiveLog logs={logs} done={wsDone} />
          </>
        )}

        {run.error && (
          <div className="card p-4 border-red-200 bg-red-50">
            <p className="text-sm font-semibold text-red-600 mb-1">Erro</p>
            <p className="text-xs text-red-500 font-code">{run.error}</p>
          </div>
        )}

        {isDone && run.best_config && (
          <BestConfigCard
            config={run.best_config}
            baselineScore={run.baseline_score}
            bestScore={run.best_score}
            nAccepted={run.n_accepted}
            nExperiments={run.n_experiments}
            totalTokens={run.total_tokens}
            durationSeconds={run.duration_seconds}
            runId={run.id}
          />
        )}

        {experiments.length > 0 && (
          <ExperimentsTable
            experiments={experiments}
            baselineScore={baselineScore}
          />
        )}

        {experiments.length === 0 && !isLive && (
          <div className="card p-8 text-center">
            <p className="text-sm text-bist-muted">Nenhum experimento registrado ainda.</p>
          </div>
        )}

      </div>
    </div>
  );
}
