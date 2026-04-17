"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft, CheckCircle2, XCircle, Loader2,
  Globe, Clock, FileCode, RefreshCw, Wifi,
} from "lucide-react";
import { bistGetRun, bistWsUrl } from "@/lib/api";
import { ScenarioDetail } from "@/components/ScenarioDetail";
import type { BistRunDetail } from "@/types";

function statusBadge(s: string) {
  const cls =
    s === "passed"  ? "text-[#a3fb73] border-[#a3fb73]/30 bg-[#a3fb73]/8" :
    s === "running" ? "text-[#f59e0b] border-[#f59e0b]/30 bg-[#f59e0b]/8" :
                     "text-red-400 border-red-400/30 bg-red-400/8";
  return (
    <span className={`text-xs font-mono px-2 py-0.5 rounded border ${cls}`}>{s}</span>
  );
}

function fmtDate(ts: number) {
  return new Date(ts * 1000).toLocaleString("pt-BR", { dateStyle: "long", timeStyle: "short" });
}

function fmtDuration(ms: number) {
  if (!ms) return "—";
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`;
}

// ── Live log stream ────────────────────────────────────────────────────────────

function LiveLog({ runId, onDone }: { runId: number; onDone: () => void }) {
  const [logs, setLogs]  = useState<string[]>(["conectando ao pipeline..."]);
  const [done, setDone]  = useState(false);

  useEffect(() => {
    const url = bistWsUrl(runId);
    const ws  = new WebSocket(url);

    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      if (msg.type === "log")  setLogs(prev => [...prev, msg.message]);
      if (msg.type === "done") {
        setLogs(prev => [...prev, `pipeline finalizado: ${msg.status}`]);
        setDone(true);
        ws.close();
        setTimeout(onDone, 1200);
      }
    };

    ws.onerror = () => setLogs(prev => [...prev, "erro de conexão WebSocket"]);

    return () => ws.readyState === WebSocket.OPEN && ws.close();
  }, [runId]);

  return (
    <div className="card-terminal p-4 space-y-1 max-h-64 overflow-y-auto font-mono text-xs">
      <div className="flex items-center gap-2 text-[#5a7a65] border-b border-[#a3fb73]/10 pb-2 mb-2">
        <Wifi className="w-3 h-3 text-[#a3fb73] animate-pulse" />
        <span>live log — run #{runId}</span>
      </div>
      {logs.map((l, i) => (
        <p key={i} className="text-[#7a9b87]">
          <span className="text-[#3d5a44] mr-2">→</span>{l}
        </p>
      ))}
      {!done && <p className="text-[#5a7a65] animate-pulse">▮</p>}
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function RunDetailPage() {
  const { id } = useParams<{ id: string }>();
  const runId  = Number(id);

  const [run, setRun]       = useState<BistRunDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      setRun(await bistGetRun(runId));
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [runId]);

  if (loading) return (
    <div className="flex items-center justify-center flex-1 py-20 gap-2">
      <RefreshCw className="w-5 h-5 text-[#5a7a65] animate-spin" />
      <span className="text-sm font-mono text-[#5a7a65]">carregando run...</span>
    </div>
  );

  if (error) return (
    <div className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 py-10 space-y-4">
      <Link href="/runs" className="btn-ghost text-xs gap-1.5 inline-flex">
        <ArrowLeft className="w-3.5 h-3.5" /> voltar
      </Link>
      <div className="card p-6 text-center">
        <p className="text-sm font-mono text-red-400">{error}</p>
        <button onClick={load} className="btn-ghost text-xs mt-3">tentar novamente</button>
      </div>
    </div>
  );

  if (!run) return null;

  const passed  = run.scenarios.filter(s => s.status === "passed").length;
  const isLive  = run.status === "running";

  return (
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <div className="border-b border-[#a3fb73]/10 bg-[#243d2c]/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-5">
          <div className="flex items-center gap-3 mb-1">
            <Link href="/runs" className="btn-ghost text-xs gap-1 py-1 px-2">
              <ArrowLeft className="w-3 h-3" /> runs
            </Link>
            <span className="text-[#3d5a44] font-mono text-xs">/</span>
            <span className="text-[#a3fb73] font-mono text-sm">#{run.id}</span>
            {statusBadge(run.status)}
          </div>
          <p className="text-xs text-[#5a7a65] font-mono ml-0.5">{fmtDate(run.started_at)}</p>
        </div>
      </div>

      <div className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-6 space-y-6">

        {/* Run meta */}
        <div className="card-terminal p-5">
          <div className="flex items-center gap-2 text-xs font-mono text-[#5a7a65] border-b border-[#a3fb73]/10 pb-3 mb-4">
            <span className="text-[#a3fb73]">$</span>
            <span>bist inspect</span>
            <span className="text-[#3d5a44]">--run-id={run.id}</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-2 text-sm font-mono">
            {[
              ["status",    run.status],
              ["ambiente",  run.env_url],
              ["duração",   fmtDuration(run.duration_ms)],
              ["cenários",  `${passed}/${run.scenarios.length} passou`],
              ["feature",   run.feature_path.split(/[/\\]/).pop() || "—"],
            ].map(([k, v]) => (
              <div key={k} className="flex items-baseline gap-2">
                <span className="text-[#3d5a44] w-24 shrink-0">{k}:</span>
                <span className="text-[#c8e8c8] truncate">{v}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Live log (only when running) */}
        {isLive && (
          <LiveLog runId={run.id} onDone={load} />
        )}

        {/* Scenarios */}
        {run.scenarios.length > 0 && (
          <div className="space-y-3">
            <p className="text-xs font-mono text-[#5a7a65] uppercase tracking-widest">
              // cenários
            </p>
            <ScenarioDetail scenarios={run.scenarios} />
          </div>
        )}

        {run.scenarios.length === 0 && !isLive && (
          <div className="card p-8 text-center">
            <p className="text-sm font-mono text-[#5a7a65]">
              nenhum cenário registrado — o run pode ter falhado antes da execução.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
