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

function relativeTime(ts: number): string {
  const diff = Date.now() - ts;
  const m = Math.floor(diff / 60000);
  if (m < 1) return "agora";
  if (m < 60) return `há ${m} min`;
  const h = Math.floor(m / 60);
  if (h < 24) return `há ${h}h`;
  return `há ${Math.floor(h / 24)}d`;
}

function fmtDate(ts: number): string {
  return new Date(ts).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

function scoreColor(v: number) {
  if (v >= 8) return "text-[#2D6A3F]";
  if (v >= 7) return "text-[#3d7a4a]";
  if (v >= 5) return "text-amber-600";
  return "text-red-500";
}

function barWidth(v: number) { return `${Math.min(100, v / 10 * 100).toFixed(0)}%`; }
function barBg(v: number) {
  if (v >= 8) return "#a3fb73";
  if (v >= 6) return "#7dd151";
  if (v >= 5) return "#f59e0b";
  return "#ef4444";
}

// ── Stats bar ─────────────────────────────────────────────────────────────────

function StatsBar({ stats }: { stats: HistoryStats }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
      {[
        { label: "Features",    value: stats.total.toString() },
        { label: "Cenários",    value: stats.scenarios.toString() },
        { label: "Aprovados",   value: `${stats.approved}/${stats.total}` },
        { label: "Score médio", value: stats.total ? stats.avgScore.toFixed(1) : "—" },
      ].map(({ label, value }) => (
        <div key={label} className="card p-3 text-center">
          <p className="text-xl font-code font-bold text-bist-primary">{value}</p>
          <p className="text-[10px] font-code text-bist-dim uppercase tracking-widest mt-0.5">{label}</p>
        </div>
      ))}
    </div>
  );
}

// ── Entry card ────────────────────────────────────────────────────────────────

function EntryCard({ entry, onView, onGherkin, onDelete }: {
  entry: HistoryEntry; onView: () => void; onGherkin: () => void; onDelete: () => void;
}) {
  const [confirmDel, setConfirmDel] = useState(false);

  return (
    <div className="card p-4 space-y-3 hover:border-bist-muted transition-colors">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-2.5 min-w-0">
          <div className={`flex-shrink-0 mt-0.5 ${entry.score.aprovado ? "text-[#2D6A3F]" : "text-red-500"}`}>
            {entry.score.aprovado ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-bist-primary leading-snug truncate">{entry.feature_name}</p>
            <p className="text-xs text-bist-muted mt-0.5">{fmtDate(entry.timestamp)} · {relativeTime(entry.timestamp)}</p>
          </div>
        </div>
        <div className={`flex-shrink-0 text-base font-code font-bold tabular-nums ${scoreColor(entry.score.score_final)}`}>
          {entry.score.score_final.toFixed(1)}
        </div>
      </div>

      <div className="flex flex-wrap gap-1.5 text-[10px]">
        <span className="px-2 py-0.5 rounded-full bg-bist-surface2 text-bist-muted border border-bist-border2">{entry.scenario_count} cenários</span>
        <span className="px-2 py-0.5 rounded-full bg-bist-surface2 text-bist-muted border border-bist-border2">{entry.model}</span>
        {entry.tags.slice(0, 3).map(t => (
          <span key={t} className="px-2 py-0.5 rounded-full bg-[#a3fb73]/12 text-[#2D6A3F] border border-[#a3fb73]/25">{t}</span>
        ))}
        {entry.tags.length > 3 && <span className="text-bist-dim">+{entry.tags.length - 3}</span>}
      </div>

      <div className="grid grid-cols-4 gap-1.5">
        {[
          ["Cob", entry.score.cobertura],
          ["GWT", entry.score.estrutura],
          ["Cla", entry.score.clareza],
          ["Exe", entry.score.executabilidade],
        ].map(([l, v]) => (
          <div key={l as string}>
            <div className="text-[9px] font-code text-bist-dim mb-0.5">{l as string}</div>
            <div className="h-1 bg-bist-border rounded-full">
              <div className="h-full rounded-full" style={{ width: barWidth(v as number), backgroundColor: barBg(v as number) }} />
            </div>
          </div>
        ))}
      </div>

      <div className="flex items-center gap-1 pt-1 border-t border-bist-border2">
        <button onClick={onView} className="btn-ghost text-xs gap-1.5"><Eye className="w-3.5 h-3.5" /> Visualizar</button>
        <button onClick={onGherkin} className="btn-ghost text-xs gap-1.5"><FileText className="w-3.5 h-3.5" /> Gherkin</button>
        <div className="flex-1" />
        {confirmDel ? (
          <div className="flex items-center gap-1">
            <button onClick={() => { onDelete(); setConfirmDel(false); }}
              className="text-[10px] text-red-600 hover:text-red-700 px-2 py-1 rounded hover:bg-red-50 transition-colors">
              Confirmar
            </button>
            <button onClick={() => setConfirmDel(false)} className="text-[10px] text-bist-muted px-1 py-1">Cancelar</button>
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

// ── Detail view ───────────────────────────────────────────────────────────────

function DetailView({ entry, onBack }: { entry: HistoryEntry; onBack: () => void }) {
  return (
    <div className="space-y-5 animate-slide-up">
      <div className="flex items-center gap-3">
        <button onClick={onBack} className="btn-ghost text-xs gap-1.5"><ArrowLeft className="w-3.5 h-3.5" /> Voltar</button>
        <div className="flex-1 h-px bg-bist-border" />
        <span className="text-xs text-bist-dim">{fmtDate(entry.timestamp)}</span>
      </div>

      <div className="card p-5 space-y-3">
        <p className="text-xs font-code text-bist-dim uppercase tracking-widest mb-3">Informações da feature</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-3 text-sm">
          {[
            ["Feature",    entry.feature_name],
            ["Modelo",     entry.model],
            ["Gerado",     fmtDate(entry.timestamp)],
            ["Cenários",   entry.scenario_count.toString()],
            ["Tentativas", entry.attempts.toString()],
            ["Tokens",     entry.total_tokens.toLocaleString()],
            ["Duração",    `${entry.duration_seconds.toFixed(1)}s`],
            ["Tags",       entry.tags.join(", ") || "—"],
          ].map(([k, v]) => (
            <div key={k} className="flex items-baseline gap-2">
              <span className="text-bist-muted w-24 flex-shrink-0 text-xs">{k}</span>
              <span className="text-bist-primary font-medium truncate">{v}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="card p-5">
        <p className="text-xs font-code text-bist-dim uppercase tracking-widest mb-4">Avaliação de qualidade</p>
        <ScoreDisplay score={entry.score} attempts={entry.attempts}
          totalTokens={entry.total_tokens} researchTokens={entry.research_tokens}
          durationSeconds={entry.duration_seconds} converged={entry.converged} />
      </div>

      <div>
        <p className="text-xs font-code text-bist-dim uppercase tracking-widest mb-2">
          {entry.feature_name.toLowerCase().replace(/\s+/g, "_")}.feature
        </p>
        <BDDViewer bddText={entry.bdd_text}
          filename={`${entry.feature_name.toLowerCase().replace(/\s+/g, "_")}.feature`}
          approved={entry.score?.aprovado} />
      </div>

      <div className="card p-5">
        <p className="text-xs font-code text-bist-dim uppercase tracking-widest mb-3">User story original</p>
        <pre className="text-sm font-code text-bist-mid leading-relaxed whitespace-pre-wrap">{entry.story}</pre>
      </div>
    </div>
  );
}

// ── Regression Modal ──────────────────────────────────────────────────────────

const FORMAT_OPTIONS: Array<{ id: DocFormat; label: string; ext: string; desc: string; icon: React.ReactNode; rec?: boolean }> = [
  { id: "html",     label: "HTML",     ext: ".html",    icon: <Globe    className="w-4 h-4" />, desc: "Estilizado, navegável, imprimível como PDF", rec: true },
  { id: "markdown", label: "Markdown", ext: ".md",      icon: <FileCode className="w-4 h-4" />, desc: "Compatível com Git, GitHub e GitLab" },
  { id: "feature",  label: "Gherkin",  ext: ".feature", icon: <FileText className="w-4 h-4" />, desc: "Arquivo Gherkin consolidado para execução" },
  { id: "txt",      label: "Texto",    ext: ".txt",     icon: <BookOpen className="w-4 h-4" />, desc: "Texto simples, universal, sem dependências" },
];

function RegressionModal({ entries, onClose }: { entries: HistoryEntry[]; onClose: () => void }) {
  const today    = new Date().toISOString().slice(0, 10);
  const [format, setFormat]     = useState<DocFormat>("html");
  const [filename, setFilename] = useState(`Regressao_BIST_${today}`);
  const [done, setDone]         = useState(false);
  const [opts, setOpts]         = useState<Omit<GenOptions, "filename">>({
    includeIndex: true, includeStats: true, groupByModel: false,
    includeDate: true,  onlyCritical: false, onlyApproved: false,
  });

  const filtered = useMemo(() => {
    let e = [...entries];
    if (opts.onlyCritical) e = e.filter(x => x.tags.includes("@critical"));
    if (opts.onlyApproved) e = e.filter(x => x.score.aprovado);
    return e;
  }, [entries, opts.onlyCritical, opts.onlyApproved]);

  const ext      = FORMAT_OPTIONS.find(f => f.id === format)?.ext ?? ".html";
  const fullName = filename.replace(/\.[^.]+$/, "") + ext;

  function generate() {
    const { content, mime } = buildDoc(filtered, format, { ...opts, filename: fullName });
    downloadFile(content, fullName, mime);
    setDone(true);
    setTimeout(() => setDone(false), 3000);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
      <div className="w-full max-w-2xl card overflow-hidden animate-slide-up max-h-[90vh] flex flex-col">
        <div className="flex items-center justify-between px-5 py-4 border-b border-bist-border">
          <div>
            <p className="text-sm font-semibold text-bist-primary">Exportar documentação de regressão</p>
            <p className="text-xs text-bist-muted mt-0.5">Gera um arquivo consolidado com todos os BDDs</p>
          </div>
          <button onClick={onClose} className="btn-ghost p-1.5"><X className="w-4 h-4" /></button>
        </div>

        <div className="overflow-y-auto flex-1 px-5 py-4 space-y-5">
          <div className="card-subtle p-4 rounded-lg">
            <p className="text-xs font-code text-bist-dim mb-3 uppercase tracking-widest">O que será incluído</p>
            <div className="grid grid-cols-3 gap-3 text-center">
              {[
                ["Features", filtered.length],
                ["Cenários", filtered.reduce((s, e) => s + e.scenario_count, 0)],
                ["Modelos",  new Set(filtered.map(e => e.model)).size],
              ].map(([l, v]) => (
                <div key={l as string}>
                  <p className="text-xl font-code font-bold text-bist-primary">{v}</p>
                  <p className="text-[10px] font-code text-bist-dim uppercase">{l as string}</p>
                </div>
              ))}
            </div>
          </div>

          <div>
            <p className="text-xs font-code text-bist-dim uppercase tracking-widest mb-3">Formato de saída</p>
            <div className="grid grid-cols-2 gap-2">
              {FORMAT_OPTIONS.map(f => (
                <button
                  key={f.id}
                  onClick={() => setFormat(f.id)}
                  className={[
                    "flex items-start gap-3 p-3 rounded-lg border text-left transition-all",
                    format === f.id
                      ? "border-[#a3fb73] bg-[#a3fb73]/8 shadow-sm"
                      : "border-bist-border hover:border-bist-muted",
                  ].join(" ")}
                >
                  <span className={format === f.id ? "text-[#2D6A3F]" : "text-bist-muted"}>{f.icon}</span>
                  <div>
                    <div className="flex items-center gap-1.5">
                      <span className={`text-xs font-semibold ${format === f.id ? "text-bist-primary" : "text-bist-mid"}`}>{f.label}</span>
                      <span className="text-[10px] font-code text-bist-dim">{f.ext}</span>
                      {f.rec && <span className="text-[9px] font-code text-[#2D6A3F] bg-[#a3fb73]/15 px-1 rounded">rec.</span>}
                    </div>
                    <p className="text-[10px] text-bist-dim mt-0.5 leading-snug">{f.desc}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div>
            <p className="text-xs font-code text-bist-dim uppercase tracking-widest mb-3">Opções</p>
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
                      checked ? "bg-[#a3fb73] border-[#a3fb73]" : "bg-bist-surface border-bist-border group-hover:border-bist-muted",
                    ].join(" ")}>
                      {checked && <Check className="w-2.5 h-2.5 text-bist-primary" />}
                    </div>
                    <span className="text-sm text-bist-mid group-hover:text-bist-primary transition-colors">{label}</span>
                    <input type="checkbox" className="sr-only" checked={!!checked}
                      onChange={() => setOpts(p => ({ ...p, [key]: !p[key as keyof typeof opts] }))} />
                  </label>
                );
              })}
            </div>
          </div>

          <div>
            <p className="text-xs font-code text-bist-dim uppercase tracking-widest mb-2">Nome do arquivo</p>
            <div className="flex items-center">
              <input type="text" value={filename} onChange={e => setFilename(e.target.value)}
                className="input rounded-r-none flex-1 text-sm" />
              <span className="bg-bist-surface2 border border-l-0 border-bist-border px-3 py-[9px] text-sm font-code text-bist-muted rounded-r-lg">
                {ext}
              </span>
            </div>
            <p className="text-[10px] font-code text-bist-dim mt-1">→ {fullName}</p>
          </div>
        </div>

        <div className="px-5 py-4 border-t border-bist-border flex items-center justify-between gap-3">
          <button onClick={onClose} className="btn-secondary text-sm py-2 px-4">Cancelar</button>
          <button onClick={generate} disabled={filtered.length === 0} className="btn-primary text-sm py-2.5 px-6 gap-2 disabled:opacity-40">
            {done ? <><Check className="w-4 h-4" /> Gerado!</> : <><Download className="w-4 h-4" /> Gerar documentação</>}
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────

export function HistoryPanel() {
  const [all, setAll]               = useState<HistoryEntry[]>([]);
  const [view, setView]             = useState<View>("list");
  const [selected, setSelected]     = useState<HistoryEntry | null>(null);
  const [gherkinEntry, setGherkinEntry] = useState<HistoryEntry | null>(null);
  const [search, setSearch]         = useState("");
  const [timeFilter, setTimeFilter] = useState<TimeFilter>("all");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [visible, setVisible]       = useState(10);

  useEffect(() => { setAll(getHistory()); }, []);

  const stats    = useMemo(() => computeStats(all), [all]);
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
      return e.feature_name.toLowerCase().includes(q) || e.story.toLowerCase().includes(q) ||
             e.tags.some(t => t.toLowerCase().includes(q)) || e.model.toLowerCase().includes(q);
    });
  }, [all, search, timeFilter, statusFilter]);

  function handleDelete(id: string) { deleteEntry(id); setAll(getHistory()); }

  if (view === "detail" && selected) {
    return <DetailView entry={selected} onBack={() => { setView("list"); setSelected(null); }} />;
  }

  return (
    <div className="space-y-5">
      <StatsBar stats={stats} />

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-bist-muted" />
          <input type="text" placeholder="Buscar por feature, tag, modelo..."
            value={search} onChange={e => setSearch(e.target.value)} className="input pl-9 text-sm" />
        </div>
        <div className="flex gap-2">
          <select value={timeFilter} onChange={e => setTimeFilter(e.target.value as TimeFilter)} className="input text-xs py-2 pr-7 cursor-pointer">
            <option value="all">Todos os tempos</option>
            <option value="today">Hoje</option>
            <option value="7d">Últimos 7 dias</option>
            <option value="30d">Últimos 30 dias</option>
          </select>
          <select value={statusFilter} onChange={e => setStatusFilter(e.target.value as StatusFilter)} className="input text-xs py-2 pr-7 cursor-pointer">
            <option value="all">Todos</option>
            <option value="approved">Aprovados</option>
            <option value="rejected">Reprovados</option>
          </select>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-xs text-bist-muted">
          {filtered.length === all.length
            ? `${all.length} feature${all.length !== 1 ? "s" : ""}`
            : `${filtered.length} de ${all.length} features`
          }
          {search && <span className="text-bist-primary font-medium"> · "{search}"</span>}
        </p>
        {filtered.length > 0 && (
          <div className="flex items-center gap-2">
            <button onClick={() => setView("map")} className="btn-secondary text-xs py-1.5 px-3 gap-1.5">
              <GitBranch className="w-3.5 h-3.5" /> Mapa de fluxos
            </button>
            <button onClick={() => setView("modal")} className="btn-secondary text-xs py-1.5 px-3 gap-1.5">
              <Download className="w-3.5 h-3.5" /> Exportar
            </button>
          </div>
        )}
      </div>

      {all.length === 0 && (
        <div className="card p-12 flex flex-col items-center justify-center text-center gap-4 border-dashed min-h-[300px]">
          <div className="w-12 h-12 rounded-xl bg-bist-surface2 border border-bist-border flex items-center justify-center">
            <FolderOpen className="w-5 h-5 text-bist-muted" />
          </div>
          <div>
            <p className="text-sm font-medium text-bist-primary">Histórico vazio</p>
            <p className="text-xs text-bist-muted mt-1">
              Gere BDDs em <a href="/generate" className="text-bist-primary font-medium underline">/generate</a> para ver o histórico aqui
            </p>
          </div>
        </div>
      )}

      {all.length > 0 && filtered.length === 0 && (
        <div className="card p-8 flex flex-col items-center text-center gap-3">
          <Search className="w-5 h-5 text-bist-muted" />
          <p className="text-sm text-bist-muted">Nenhum resultado para &ldquo;{search}&rdquo;</p>
          <button onClick={() => { setSearch(""); setTimeFilter("all"); setStatusFilter("all"); }}
            className="btn-ghost text-xs gap-1.5">
            <RefreshCw className="w-3 h-3" /> Limpar filtros
          </button>
        </div>
      )}

      {filtered.length > 0 && (
        <div className="space-y-3">
          {filtered.slice(0, visible).map(entry => (
            <EntryCard key={entry.id} entry={entry}
              onView={() => { setSelected(entry); setView("detail"); window.scrollTo({ top: 0, behavior: "smooth" }); }}
              onGherkin={() => setGherkinEntry(entry)}
              onDelete={() => handleDelete(entry.id)}
            />
          ))}
          {visible < filtered.length && (
            <button onClick={() => setVisible(v => v + 10)} className="w-full btn-secondary text-xs py-2.5 gap-1.5">
              <ChevronDown className="w-3.5 h-3.5" />
              Carregar mais ({filtered.length - visible} restantes)
            </button>
          )}
        </div>
      )}

      {all.length > 0 && (
        <div className="card p-5 flex flex-col sm:flex-row items-center justify-between gap-4 border-[#a3fb73]/30 bg-[#a3fb73]/5">
          <div>
            <p className="text-sm font-semibold text-bist-primary">Exportar documentação de regressão</p>
            <p className="text-xs text-bist-muted mt-0.5">
              Consolida todos os {stats.total} BDDs em um único documento
            </p>
          </div>
          <div className="flex gap-2 flex-shrink-0">
            <button onClick={() => setView("map")} className="btn-secondary text-sm py-2.5 px-4 gap-2">
              <GitBranch className="w-4 h-4" /> Mapa de fluxos
            </button>
            <button onClick={() => setView("modal")} className="btn-primary text-sm py-2.5 px-5 gap-2">
              <Download className="w-4 h-4" /> Exportar
            </button>
          </div>
        </div>
      )}

      {gherkinEntry && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
          <div className="w-full max-w-2xl card overflow-hidden animate-slide-up max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between px-4 py-3 border-b border-bist-border">
              <p className="text-sm font-semibold text-bist-primary">{gherkinEntry.feature_name}</p>
              <button onClick={() => setGherkinEntry(null)} className="btn-ghost p-1"><X className="w-4 h-4" /></button>
            </div>
            <div className="overflow-auto flex-1">
              <BDDViewer bddText={gherkinEntry.bdd_text}
                filename={`${gherkinEntry.feature_name.toLowerCase().replace(/\s+/g, "_")}.feature`}
                approved={gherkinEntry.score?.aprovado} />
            </div>
          </div>
        </div>
      )}

      {view === "modal" && (
        <RegressionModal entries={filtered.length > 0 ? filtered : all} onClose={() => setView("list")} />
      )}

      {view === "map" && (
        <FlowMapModal entries={filtered.length > 0 ? filtered : all} onClose={() => setView("list")} />
      )}
    </div>
  );
}
