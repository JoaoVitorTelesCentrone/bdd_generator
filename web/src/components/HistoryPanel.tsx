"use client";

import { useState, useEffect, useMemo } from "react";
import {
  Search, ChevronDown, ArrowLeft, Eye, FileText,
  Trash2, Download, CheckCircle2, XCircle,
  FolderOpen, RefreshCw,
  FileCode, Globe, BookOpen, X, Check, GitBranch,
} from "lucide-react";
import {
  getHistory, deleteEntry, computeStats,
  type HistoryEntry, type HistoryStats,
} from "@/lib/history";
import { buildDoc, downloadFile, type DocFormat, type GenOptions } from "@/lib/docgen";
import { BDDViewer } from "./BDDViewer";
import { FlowMapModal } from "./FlowMapModal";
import { ScoreDisplay } from "./ScoreDisplay";

type View = "list" | "detail" | "modal" | "map";
type TimeFilter = "all" | "7d" | "30d" | "today";
type StatusFilter = "all" | "approved" | "rejected";

// ─── Helpers ───────────────────────────────────────────────────────────��──────

function relativeTime(ts: number): string {
  const diff = Date.now() - ts;
  const m = Math.floor(diff / 60000);
  if (m < 1) return "agora";
  if (m < 60) return `há ${m} min`;
  const h = Math.floor(m / 60);
  if (h < 24) return `há ${h}h`;
  const d = Math.floor(h / 24);
  return `há ${d}d`;
}

function fmtDate(ts: number): string {
  return new Date(ts).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

function scoreColor(v: number) {
  if (v >= 8) return "text-[#a3fb73]";
  if (v >= 7) return "text-[#7dd151]";
  if (v >= 5) return "text-[#f59e0b]";
  return "text-red-400";
}

function barWidth(v: number) { return `${Math.min(100, v / 10 * 100).toFixed(0)}%`; }
function barBg(v: number) {
  if (v >= 8) return "#a3fb73";
  if (v >= 6) return "#7dd151";
  if (v >= 5) return "#f59e0b";
  return "#ef4444";
}

// ─── Stats bar ────────────────────────────────────────────────────────────────

function StatsBar({ stats, entries }: { stats: HistoryStats; entries: HistoryEntry[] }) {
  const pct = stats.total ? Math.round(stats.approved / stats.total * 100) : 0;
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
      {[
        { label: "features", value: stats.total.toString() },
        { label: "cenários", value: stats.scenarios.toString() },
        { label: "aprovados", value: `${stats.approved}/${stats.total}` },
        { label: "score médio", value: stats.total ? stats.avgScore.toFixed(1) : "—" },
      ].map(({ label, value }) => (
        <div key={label} className="card p-3 text-center">
          <p className="text-xl font-mono font-bold text-[#a3fb73]">{value}</p>
          <p className="text-[10px] font-mono text-[#5a7a65] uppercase tracking-widest mt-0.5">{label}</p>
        </div>
      ))}
    </div>
  );
}

// ─── Entry card ──────────────────────────────────────────────────────────────

function EntryCard({
  entry,
  onView,
  onGherkin,
  onDelete,
}: {
  entry: HistoryEntry;
  onView: () => void;
  onGherkin: () => void;
  onDelete: () => void;
}) {
  const [confirmDel, setConfirmDel] = useState(false);

  return (
    <div className="card p-4 space-y-3 hover:border-[#a3fb73]/25 transition-colors duration-200">
      {/* Header row */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-2.5 min-w-0">
          <div className={`flex-shrink-0 mt-0.5 ${entry.score.aprovado ? "text-[#a3fb73]" : "text-red-400"}`}>
            {entry.score.aprovado
              ? <CheckCircle2 className="w-4 h-4" />
              : <XCircle className="w-4 h-4" />
            }
          </div>
          <div className="min-w-0">
            <p className="font-mono text-sm font-semibold text-[#eef9e8] leading-snug truncate">
              {entry.feature_name}
            </p>
            <p className="text-[10px] font-mono text-[#5a7a65] mt-0.5">
              {fmtDate(entry.timestamp)} · {relativeTime(entry.timestamp)}
            </p>
          </div>
        </div>
        <div className={`flex-shrink-0 text-base font-mono font-bold tabular-nums ${scoreColor(entry.score.score_final)}`}>
          {entry.score.score_final.toFixed(1)}
        </div>
      </div>

      {/* Meta chips */}
      <div className="flex flex-wrap gap-1.5 text-[10px] font-mono">
        <span className="px-1.5 py-0.5 rounded bg-[#243d2c] text-[#7a9b87] border border-[#a3fb73]/8">
          {entry.scenario_count} cenários
        </span>
        <span className="px-1.5 py-0.5 rounded bg-[#243d2c] text-[#7a9b87] border border-[#a3fb73]/8">
          {entry.model}
        </span>
        {entry.tags.slice(0, 3).map(t => (
          <span key={t} className="px-1.5 py-0.5 rounded bg-[#a3fb73]/8 text-[#a3fb73]/70">
            {t}
          </span>
        ))}
        {entry.tags.length > 3 && (
          <span className="text-[#3d5a44]">+{entry.tags.length - 3}</span>
        )}
      </div>

      {/* Score mini-bars */}
      <div className="grid grid-cols-4 gap-1.5">
        {[
          ["cob", entry.score.cobertura],
          ["gwt", entry.score.estrutura],
          ["cla", entry.score.clareza],
          ["exe", entry.score.executabilidade],
        ].map(([l, v]) => (
          <div key={l as string}>
            <div className="text-[9px] font-mono text-[#3d5a44] mb-0.5">{l as string}</div>
            <div className="h-1 bg-[#243d2c] rounded-full">
              <div className="h-full rounded-full" style={{ width: barWidth(v as number), backgroundColor: barBg(v as number) }} />
            </div>
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-1 pt-1 border-t border-[#a3fb73]/8">
        <button onClick={onView} className="btn-ghost text-xs gap-1.5">
          <Eye className="w-3.5 h-3.5" /> Visualizar
        </button>
        <button onClick={onGherkin} className="btn-ghost text-xs gap-1.5">
          <FileText className="w-3.5 h-3.5" /> Gherkin
        </button>
        <div className="flex-1" />
        {confirmDel ? (
          <div className="flex items-center gap-1">
            <button onClick={() => { onDelete(); setConfirmDel(false); }}
              className="text-[10px] font-mono text-red-400 hover:text-red-300 px-2 py-1 rounded hover:bg-red-500/10 transition-colors">
              confirmar
            </button>
            <button onClick={() => setConfirmDel(false)}
              className="text-[10px] font-mono text-[#5a7a65] hover:text-[#7a9b87] px-1 py-1">
              cancelar
            </button>
          </div>
        ) : (
          <button onClick={() => setConfirmDel(true)} className="btn-ghost text-xs">
            <Trash2 className="w-3 h-3" />
          </button>
        )}
      </div>
    </div>
  );
}

// ─── Detail view ──────────────────────────────────────────────────────────────

function DetailView({ entry, onBack }: { entry: HistoryEntry; onBack: () => void }) {
  return (
    <div className="space-y-5 animate-slide-up">
      {/* Back + title */}
      <div className="flex items-center gap-3">
        <button onClick={onBack} className="btn-ghost text-xs gap-1.5">
          <ArrowLeft className="w-3.5 h-3.5" /> voltar
        </button>
        <div className="flex-1 h-px bg-[#a3fb73]/10" />
        <span className="text-xs font-mono text-[#5a7a65]">{fmtDate(entry.timestamp)}</span>
      </div>

      {/* Feature info */}
      <div className="card-terminal p-5 space-y-3">
        <div className="flex items-center gap-2 text-xs font-mono text-[#5a7a65] border-b border-[#a3fb73]/10 pb-3">
          <span className="text-[#a3fb73]">$</span>
          <span>bist inspect</span>
          <span className="text-[#3d5a44]">--id={entry.id.slice(0, 8)}</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-2 text-sm font-mono">
          {[
            ["feature", entry.feature_name],
            ["modelo",  entry.model],
            ["gerado",  fmtDate(entry.timestamp)],
            ["cenários",entry.scenario_count.toString()],
            ["tentativas", entry.attempts.toString()],
            ["tokens",  entry.total_tokens.toLocaleString()],
            ["duração", `${entry.duration_seconds.toFixed(1)}s`],
            ["tags",    entry.tags.join(", ") || "—"],
          ].map(([k, v]) => (
            <div key={k} className="flex items-baseline gap-2">
              <span className="text-[#3d5a44] w-20 flex-shrink-0">{k}:</span>
              <span className="text-[#c8e8c8] truncate">{v}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Score */}
      <div className="card p-5">
        <p className="text-xs font-mono text-[#5a7a65] uppercase tracking-widest mb-4">
          // quality assessment
        </p>
        <ScoreDisplay score={entry.score} attempts={entry.attempts}
          totalTokens={entry.total_tokens} researchTokens={entry.research_tokens}
          durationSeconds={entry.duration_seconds} converged={entry.converged} />
      </div>

      {/* BDD viewer */}
      <div className="card overflow-hidden">
        <div className="px-4 py-3 border-b border-[#a3fb73]/10">
          <p className="text-xs font-mono text-[#5a7a65] uppercase tracking-widest">
            // {entry.feature_name.toLowerCase().replace(/\s+/g, "_")}.feature
          </p>
        </div>
        <div className="p-2">
          <BDDViewer bddText={entry.bdd_text}
            filename={`${entry.feature_name.toLowerCase().replace(/\s+/g, "_")}.feature`} />
        </div>
      </div>

      {/* Story */}
      <div className="card p-5">
        <p className="text-xs font-mono text-[#5a7a65] uppercase tracking-widest mb-3">
          // user story original
        </p>
        <pre className="text-sm font-mono text-[#7a9b87] leading-relaxed whitespace-pre-wrap">{entry.story}</pre>
      </div>
    </div>
  );
}

// ─── Regression Modal ─────────────────────────────────────────────────────────

const FORMAT_OPTIONS: Array<{ id: DocFormat; label: string; ext: string; desc: string; icon: React.ReactNode; rec?: boolean }> = [
  { id: "html",     label: "HTML",     ext: ".html",    icon: <Globe    className="w-4 h-4" />, desc: "Estilizado, navegável, imprimível como PDF", rec: true },
  { id: "markdown", label: "Markdown", ext: ".md",      icon: <FileCode className="w-4 h-4" />, desc: "Compatível com Git, GitHub e GitLab" },
  { id: "feature",  label: "Gherkin",  ext: ".feature", icon: <FileText className="w-4 h-4" />, desc: "Arquivo Gherkin consolidado para execução" },
  { id: "txt",      label: "Texto",    ext: ".txt",     icon: <BookOpen className="w-4 h-4" />, desc: "Texto simples, universal, sem dependências" },
];

function RegressionModal({
  entries,
  onClose,
}: { entries: HistoryEntry[]; onClose: () => void }) {
  const today = new Date().toISOString().slice(0, 10);
  const [format, setFormat] = useState<DocFormat>("html");
  const [filename, setFilename] = useState(`Regressao_BIST_${today}`);
  const [done, setDone] = useState(false);
  const [opts, setOpts] = useState<Omit<GenOptions, "filename">>({
    includeIndex: true,
    includeStats: true,
    groupByModel: false,
    includeDate: true,
    onlyCritical: false,
    onlyApproved: false,
  });

  const filtered = useMemo(() => {
    let e = [...entries];
    if (opts.onlyCritical) e = e.filter(x => x.tags.includes("@critical"));
    if (opts.onlyApproved) e = e.filter(x => x.score.aprovado);
    return e;
  }, [entries, opts.onlyCritical, opts.onlyApproved]);

  const ext = FORMAT_OPTIONS.find(f => f.id === format)?.ext ?? ".html";
  const fullName = filename.replace(/\.[^.]+$/, "") + ext;

  function generate() {
    const fullOpts: GenOptions = { ...opts, filename: fullName };
    const { content, mime } = buildDoc(filtered, format, fullOpts);
    downloadFile(content, fullName, mime);
    setDone(true);
    setTimeout(() => setDone(false), 3000);
  }

  const toggle = (key: keyof typeof opts) =>
    setOpts(p => ({ ...p, [key]: !p[key] }));

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
         style={{ background: "rgba(10,20,13,0.85)", backdropFilter: "blur(8px)" }}>
      <div className="w-full max-w-2xl card-terminal overflow-hidden animate-slide-up max-h-[90vh] flex flex-col">

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-[#a3fb73]/15">
          <div>
            <p className="text-sm font-mono font-semibold text-[#a3fb73]">
              bist export --regression
            </p>
            <p className="text-xs font-mono text-[#5a7a65] mt-0.5">
              gerar documentação consolidada de regressão
            </p>
          </div>
          <button onClick={onClose} className="btn-ghost p-1.5">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="overflow-y-auto flex-1 px-5 py-4 space-y-5">

          {/* Summary */}
          <div className="card p-4">
            <p className="text-xs font-mono text-[#5a7a65] mb-3">// o que será incluído</p>
            <div className="grid grid-cols-3 gap-3 text-center">
              {[
                ["features", filtered.length],
                ["cenários", filtered.reduce((s,e)=>s+e.scenario_count,0)],
                ["modelos",  new Set(filtered.map(e=>e.model)).size],
              ].map(([l,v]) => (
                <div key={l as string}>
                  <p className="text-lg font-mono font-bold text-[#a3fb73]">{v}</p>
                  <p className="text-[10px] font-mono text-[#5a7a65] uppercase">{l as string}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Format selector */}
          <div>
            <p className="text-xs font-mono text-[#5a7a65] uppercase tracking-widest mb-3">
              // formato de saída
            </p>
            <div className="grid grid-cols-2 gap-2">
              {FORMAT_OPTIONS.map(f => (
                <button
                  key={f.id}
                  onClick={() => setFormat(f.id)}
                  className={[
                    "flex items-start gap-3 p-3 rounded border text-left transition-all",
                    format === f.id
                      ? "border-[#a3fb73]/50 bg-[#a3fb73]/8"
                      : "border-[#a3fb73]/10 hover:border-[#a3fb73]/25",
                  ].join(" ")}
                >
                  <span className={format === f.id ? "text-[#a3fb73]" : "text-[#5a7a65]"}>{f.icon}</span>
                  <div>
                    <div className="flex items-center gap-1.5">
                      <span className={`text-xs font-mono font-semibold ${format === f.id ? "text-[#a3fb73]" : "text-[#7a9b87]"}`}>
                        {f.label}
                      </span>
                      <span className={`text-[10px] font-mono ${format === f.id ? "text-[#5a7a65]" : "text-[#3d5a44]"}`}>
                        {f.ext}
                      </span>
                      {f.rec && <span className="text-[9px] font-mono text-[#a3fb73] bg-[#a3fb73]/10 px-1 rounded">rec.</span>}
                    </div>
                    <p className="text-[10px] font-mono text-[#3d5a44] mt-0.5 leading-snug">{f.desc}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Options */}
          <div>
            <p className="text-xs font-mono text-[#5a7a65] uppercase tracking-widest mb-3">
              // opções
            </p>
            <div className="space-y-2">
              {[
                { key: "includeIndex",  label: "Incluir índice navegável" },
                { key: "includeStats",  label: "Incluir estatísticas e métricas" },
                { key: "groupByModel",  label: "Agrupar por modelo" },
                { key: "includeDate",   label: "Incluir data de geração" },
                { key: "onlyCritical",  label: "Apenas cenários @critical" },
                { key: "onlyApproved",  label: "Apenas cenários aprovados" },
              ].map(({ key, label }) => {
                const checked = opts[key as keyof typeof opts];
                return (
                  <label key={key} className="flex items-center gap-3 cursor-pointer group">
                    <div className={[
                      "w-4 h-4 rounded flex items-center justify-center border transition-colors",
                      checked ? "bg-[#a3fb73] border-[#a3fb73]" : "bg-transparent border-[#a3fb73]/30 group-hover:border-[#a3fb73]/50",
                    ].join(" ")}>
                      {checked && <Check className="w-2.5 h-2.5 text-[#1a2c21]" />}
                    </div>
                    <span className="text-sm font-mono text-[#7a9b87] group-hover:text-[#c8e8c8] transition-colors">
                      {label}
                    </span>
                    <input type="checkbox" className="sr-only" checked={!!checked}
                      onChange={() => toggle(key as keyof typeof opts)} />
                  </label>
                );
              })}
            </div>
          </div>

          {/* Filename */}
          <div>
            <p className="text-xs font-mono text-[#5a7a65] uppercase tracking-widest mb-2">
              // nome do arquivo
            </p>
            <div className="flex items-center gap-0">
              <input
                type="text"
                value={filename}
                onChange={e => setFilename(e.target.value)}
                className="input rounded-r-none flex-1 text-sm"
              />
              <span className="bg-[#243d2c] border border-l-0 border-[#a3fb73]/25 px-3 py-2
                               text-sm font-mono text-[#5a7a65] rounded-r">
                {ext}
              </span>
            </div>
            <p className="text-[10px] font-mono text-[#3d5a44] mt-1">→ {fullName}</p>
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-[#a3fb73]/10 flex items-center justify-between gap-3">
          <button onClick={onClose} className="btn-secondary text-sm py-2 px-4">
            cancelar
          </button>
          <button
            onClick={generate}
            disabled={filtered.length === 0}
            className="btn-primary text-sm py-2.5 px-6 gap-2 disabled:opacity-40"
          >
            {done
              ? <><Check className="w-4 h-4" /> gerado!</>
              : <><Download className="w-4 h-4" /> gerar documentação</>
            }
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

export function HistoryPanel() {
  const [all, setAll] = useState<HistoryEntry[]>([]);
  const [view, setView] = useState<View>("list");
  const [selected, setSelected] = useState<HistoryEntry | null>(null);
  const [gherkinEntry, setGherkinEntry] = useState<HistoryEntry | null>(null);
  const [search, setSearch] = useState("");
  const [timeFilter, setTimeFilter] = useState<TimeFilter>("all");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [visible, setVisible] = useState(10);

  // Load history from localStorage
  useEffect(() => { setAll(getHistory()); }, []);

  const stats = useMemo(() => computeStats(all), [all]);

  // Filtering
  const filtered = useMemo(() => {
    const now = Date.now();
    const cutoffs: Record<TimeFilter, number> = {
      all: 0, today: now - 86400000, "7d": now - 604800000, "30d": now - 2592000000,
    };
    const q = search.toLowerCase();
    return all.filter(e => {
      if (e.timestamp < cutoffs[timeFilter]) return false;
      if (statusFilter === "approved" && !e.score.aprovado) return false;
      if (statusFilter === "rejected" && e.score.aprovado) return false;
      if (!q) return true;
      return (
        e.feature_name.toLowerCase().includes(q) ||
        e.story.toLowerCase().includes(q) ||
        e.tags.some(t => t.toLowerCase().includes(q)) ||
        e.model.toLowerCase().includes(q)
      );
    });
  }, [all, search, timeFilter, statusFilter]);

  function handleDelete(id: string) {
    deleteEntry(id);
    setAll(getHistory());
  }

  function openDetail(entry: HistoryEntry) {
    setSelected(entry);
    setView("detail");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function openGherkin(entry: HistoryEntry) {
    setGherkinEntry(entry);
  }

  // ── Detail view ───────────────���─────────────────────────────────────────────
  if (view === "detail" && selected) {
    return (
      <DetailView entry={selected} onBack={() => { setView("list"); setSelected(null); }} />
    );
  }

  // ── List view ───────────────────────────────────���──────────────────────────��─
  return (
    <div className="space-y-5">

      {/* Stats */}
      <StatsBar stats={stats} entries={all} />

      {/* Search + filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#3d5a44]" />
          <input
            type="text"
            placeholder="buscar por feature, tag, modelo..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="input pl-9 text-sm"
          />
        </div>
        <div className="flex gap-2">
          <select
            value={timeFilter}
            onChange={e => setTimeFilter(e.target.value as TimeFilter)}
            className="input text-xs py-2 pr-7 cursor-pointer"
          >
            <option value="all">todos os tempos</option>
            <option value="today">hoje</option>
            <option value="7d">últimos 7 dias</option>
            <option value="30d">últimos 30 dias</option>
          </select>
          <select
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value as StatusFilter)}
            className="input text-xs py-2 pr-7 cursor-pointer"
          >
            <option value="all">todos</option>
            <option value="approved">aprovados</option>
            <option value="rejected">reprovados</option>
          </select>
        </div>
      </div>

      {/* Results count */}
      <div className="flex items-center justify-between">
        <p className="text-xs font-mono text-[#5a7a65]">
          {filtered.length === all.length
            ? `${all.length} feature${all.length !== 1 ? "s" : ""}`
            : `${filtered.length} de ${all.length} features`
          }
          {search && <span className="text-[#a3fb73]"> · buscando por &ldquo;{search}&rdquo;</span>}
        </p>
        {filtered.length > 0 && (
          <div className="flex items-center gap-2">
            <button
              onClick={() => setView("map")}
              className="btn-secondary text-xs py-1.5 px-3 gap-1.5"
            >
              <GitBranch className="w-3.5 h-3.5" />
              mapa de fluxos
            </button>
            <button
              onClick={() => setView("modal")}
              className="btn-secondary text-xs py-1.5 px-3 gap-1.5"
            >
              <Download className="w-3.5 h-3.5" />
              exportar
            </button>
          </div>
        )}
      </div>

      {/* Empty state */}
      {all.length === 0 && (
        <div className="card p-12 flex flex-col items-center justify-center text-center gap-4
                        border-dashed border-[#a3fb73]/12 min-h-[300px]">
          <div className="w-14 h-14 rounded-full border border-[#a3fb73]/20 bg-[#a3fb73]/5
                          flex items-center justify-center">
            <FolderOpen className="w-6 h-6 text-[#a3fb73]" />
          </div>
          <div>
            <p className="text-[#7a9b87] font-mono text-sm">histórico vazio</p>
            <p className="text-xs font-mono text-[#3d5a44] mt-1">
              gere BDDs em{" "}
              <a href="/generate" className="text-[#a3fb73] hover:underline">/generate</a>
              {" "}para ver o histórico aqui
            </p>
          </div>
        </div>
      )}

      {/* No results */}
      {all.length > 0 && filtered.length === 0 && (
        <div className="card p-8 flex flex-col items-center text-center gap-3">
          <Search className="w-5 h-5 text-[#5a7a65]" />
          <p className="text-sm font-mono text-[#5a7a65]">
            nenhum resultado para &ldquo;{search}&rdquo;
          </p>
          <button onClick={() => { setSearch(""); setTimeFilter("all"); setStatusFilter("all"); }}
            className="btn-ghost text-xs gap-1.5">
            <RefreshCw className="w-3 h-3" /> limpar filtros
          </button>
        </div>
      )}

      {/* Entry list */}
      {filtered.length > 0 && (
        <div className="space-y-3">
          {filtered.slice(0, visible).map(entry => (
            <EntryCard
              key={entry.id}
              entry={entry}
              onView={() => openDetail(entry)}
              onGherkin={() => openGherkin(entry)}
              onDelete={() => handleDelete(entry.id)}
            />
          ))}

          {visible < filtered.length && (
            <button
              onClick={() => setVisible(v => v + 10)}
              className="w-full btn-secondary text-xs py-2.5 gap-1.5"
            >
              <ChevronDown className="w-3.5 h-3.5" />
              carregar mais ({filtered.length - visible} restantes)
            </button>
          )}
        </div>
      )}

      {/* Top CTA */}
      {all.length > 0 && (
        <div className="card p-5 flex flex-col sm:flex-row items-center justify-between gap-4
                        border-[#a3fb73]/20 bg-[#a3fb73]/3">
          <div>
            <p className="text-sm font-mono font-semibold text-[#a3fb73]">
              Gerar Documentação de Regressão Completa
            </p>
            <p className="text-xs font-mono text-[#5a7a65] mt-0.5">
              consolida todos os {stats.total} BDDs em um único documento exportável
            </p>
          </div>
          <div className="flex gap-2 flex-shrink-0">
            <button
              onClick={() => setView("map")}
              className="btn-secondary text-sm py-2.5 px-4 gap-2"
            >
              <GitBranch className="w-4 h-4" />
              mapa de fluxos
            </button>
            <button
              onClick={() => setView("modal")}
              className="btn-primary text-sm py-2.5 px-5 gap-2
                         shadow-[0_0_30px_rgba(163,251,115,0.15)]"
            >
              <Download className="w-4 h-4" />
              exportar
            </button>
          </div>
        </div>
      )}

      {/* Gherkin quick-view modal */}
      {gherkinEntry && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
             style={{ background: "rgba(10,20,13,0.85)", backdropFilter: "blur(8px)" }}>
          <div className="w-full max-w-2xl card-terminal overflow-hidden animate-slide-up max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between px-4 py-3 border-b border-[#a3fb73]/15">
              <p className="text-sm font-mono text-[#a3fb73]">{gherkinEntry.feature_name}</p>
              <button onClick={() => setGherkinEntry(null)} className="btn-ghost p-1">
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="overflow-auto p-2 flex-1">
              <BDDViewer bddText={gherkinEntry.bdd_text}
                filename={`${gherkinEntry.feature_name.toLowerCase().replace(/\s+/g,"_")}.feature`} />
            </div>
          </div>
        </div>
      )}

      {/* Regression modal */}
      {view === "modal" && (
        <RegressionModal
          entries={filtered.length > 0 ? filtered : all}
          onClose={() => setView("list")}
        />
      )}

      {/* Flow map */}
      {view === "map" && (
        <FlowMapModal
          entries={filtered.length > 0 ? filtered : all}
          onClose={() => setView("list")}
        />
      )}
    </div>
  );
}
