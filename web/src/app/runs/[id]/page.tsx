"use client";

import { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Globe, Clock, Loader2, RefreshCw, Wifi } from "lucide-react";
import { bistGetRun, bistWsUrl } from "@/lib/api";
import { ScenarioDetail } from "@/components/ScenarioDetail";
import type { BistRunDetail } from "@/types";

function statusBadge(s: string) {
  const cls =
    s === "passed"  ? "text-[#2D6A3F] bg-[#a3fb73]/15 border-[#a3fb73]/30" :
    s === "running" ? "text-amber-700 bg-amber-50 border-amber-200" :
                     "text-red-600 bg-red-50 border-red-200";
  return (
    <span className={`text-xs font-code px-2.5 py-0.5 rounded-full border font-medium ${cls}`}>{s}</span>
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

const MAX_WS_RECONNECTS = 5;

function LiveLog({ runId, onDone }: { runId: number; onDone: () => void }) {
  const [logs, setLogs] = useState<string[]>(["Conectando ao pipeline..."]);
  const [done, setDone] = useState(false);
  const doneRef         = useRef(false);

  useEffect(() => {
    let ws: WebSocket;
    let reconnectTimer: ReturnType<typeof setTimeout>;
    let attempt = 0;

    function connect() {
      ws = new WebSocket(bistWsUrl(runId));

      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data) as { type: string; message?: string; status?: string };
          if (msg.type === "log" && msg.message)
            setLogs(prev => [...prev, msg.message!]);
          if (msg.type === "done") {
            setLogs(prev => [...prev, `Pipeline finalizado: ${msg.status}`]);
            doneRef.current = true;
            setDone(true);
            ws.close();
            setTimeout(onDone, 1200);
          }
        } catch { /* ignore malformed frames */ }
      };

      ws.onerror = () =>
        setLogs(prev => [...prev, "Erro de conexão WebSocket"]);

      ws.onclose = () => {
        if (!doneRef.current && attempt < MAX_WS_RECONNECTS) {
          attempt++;
          const delay = Math.min(1000 * 2 ** attempt, 30_000);
          setLogs(prev => [
            ...prev,
            `Reconectando em ${delay / 1000}s… (tentativa ${attempt}/${MAX_WS_RECONNECTS})`,
          ]);
          reconnectTimer = setTimeout(connect, delay);
        } else if (!doneRef.current) {
          setLogs(prev => [...prev, "Conexão perdida. Recarregue a página."]);
        }
      };
    }

    connect();

    return () => {
      clearTimeout(reconnectTimer);
      if (ws && ws.readyState !== WebSocket.CLOSED) ws.close();
    };
  }, [runId]);

  return (
    <div className="card overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-bist-border bg-bist-surface2">
        <Wifi className="w-3.5 h-3.5 text-[#2D6A3F]" />
        <span className="text-xs font-semibold text-bist-primary">Live log — Run #{runId}</span>
        {!done && <span className="ml-auto flex items-center gap-1.5 text-xs text-amber-600">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" /> ao vivo
        </span>}
      </div>
      <div className="p-4 space-y-1 max-h-64 overflow-y-auto bg-[#1a2c21]">
        {logs.map((l, i) => (
          <p key={i} className="text-xs font-code text-[#7a9b87]">
            <span className="text-[#3d5a44] mr-2">→</span>{l}
          </p>
        ))}
        {!done && <p className="text-[#5a7a65] font-code text-xs animate-pulse">▮</p>}
      </div>
    </div>
  );
}

export default function RunDetailPage() {
  const { id } = useParams<{ id: string }>();
  const runId  = Number(id);

  const [run, setRun]         = useState<BistRunDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState("");

  async function load() {
    setLoading(true); setError("");
    try { setRun(await bistGetRun(runId)); }
    catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  }

  useEffect(() => { load(); }, [runId]);

  if (loading) return (
    <div className="flex items-center justify-center flex-1 py-20 gap-2">
      <Loader2 className="w-5 h-5 text-bist-muted animate-spin" />
      <span className="text-sm text-bist-muted">Carregando execução...</span>
    </div>
  );

  if (error) return (
    <div className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 py-10 space-y-4">
      <Link href="/runs" className="btn-ghost text-xs gap-1.5 inline-flex">
        <ArrowLeft className="w-3.5 h-3.5" /> Voltar
      </Link>
      <div className="card p-6 text-center border-red-200 bg-red-50">
        <p className="text-sm text-red-600">{error}</p>
        <button onClick={load} className="btn-secondary text-xs mt-3">Tentar novamente</button>
      </div>
    </div>
  );

  if (!run) return null;

  const passed = run.scenarios.filter(s => s.status === "passed").length;
  const isLive = run.status === "running";

  return (
    <div className="flex-1 flex flex-col">
      <div className="border-b border-bist-border bg-bist-surface">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-5">
          <div className="flex items-center gap-2 mb-1.5">
            <Link href="/runs" className="text-xs text-bist-muted hover:text-bist-primary transition-colors flex items-center gap-1">
              <ArrowLeft className="w-3.5 h-3.5" /> Runs
            </Link>
            <span className="text-bist-dim">/</span>
            <span className="text-sm font-semibold text-bist-primary">Run #{run.id}</span>
            {statusBadge(run.status)}
          </div>
          <p className="text-xs text-bist-dim">{fmtDate(run.started_at)}</p>
        </div>
      </div>

      <div className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-6 space-y-5">

        <div className="card p-5">
          <p className="text-xs font-code text-bist-dim uppercase tracking-widest mb-4">Detalhes da execução</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-3 text-sm">
            {[
              ["Status",    run.status],
              ["Ambiente",  run.env_url],
              ["Duração",   fmtDuration(run.duration_ms)],
              ["Cenários",  `${passed}/${run.scenarios.length} passou`],
              ["Feature",   run.feature_path.split(/[/\\]/).pop() || "—"],
            ].map(([k, v]) => (
              <div key={k} className="flex items-baseline gap-2">
                <span className="text-bist-muted w-24 shrink-0 text-xs">{k}</span>
                <span className="text-bist-primary font-medium truncate">{v}</span>
              </div>
            ))}
          </div>
        </div>

        {isLive && <LiveLog runId={run.id} onDone={load} />}

        {run.scenarios.length > 0 && (
          <div className="space-y-3">
            <p className="text-xs font-code text-bist-dim uppercase tracking-widest">Cenários</p>
            <ScenarioDetail scenarios={run.scenarios} />
          </div>
        )}

        {run.scenarios.length === 0 && !isLive && (
          <div className="card p-8 text-center">
            <p className="text-sm text-bist-muted">
              Nenhum cenário registrado — o run pode ter falhado antes da execução.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
