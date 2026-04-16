import type { ScoreResult } from "@/types";

export interface HistoryEntry {
  id: string;
  timestamp: number;        // Unix ms
  story: string;
  model: string;
  bdd_text: string;
  score: ScoreResult;
  attempts: number;
  total_tokens: number;
  research_tokens: number;
  converged: boolean;
  duration_seconds: number;
  options: { research: boolean; threshold: number };
  // computed on save
  feature_name: string;
  tags: string[];
  scenario_count: number;
}

const KEY = "bist_history";
const MAX_ENTRIES = 200;

// ── Parsers ───────────────────────────────────────────────────────────────────

export function extractFeatureName(bdd: string): string {
  const m = bdd.match(/^\s*(?:Funcionalidade|Feature)\s*:\s*(.+)/mi);
  return m ? m[1].trim() : "Feature sem nome";
}

export function extractTags(bdd: string): string[] {
  const matches = bdd.match(/@\w+/g) ?? [];
  return Array.from(new Set(matches));
}

export function countScenarios(bdd: string): number {
  return (bdd.match(/^\s*(?:Cenário|Cen[aá]rio|Scenario)\s*:/gmi) ?? []).length;
}

// ── Storage ───────────────────────────────────────────────────────────────────

function load(): HistoryEntry[] {
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(localStorage.getItem(KEY) ?? "[]") as HistoryEntry[];
  } catch {
    return [];
  }
}

function save(entries: HistoryEntry[]) {
  localStorage.setItem(KEY, JSON.stringify(entries));
}

export function getHistory(): HistoryEntry[] {
  return load().sort((a, b) => b.timestamp - a.timestamp);
}

export function getEntry(id: string): HistoryEntry | undefined {
  return load().find(e => e.id === id);
}

export function addEntry(entry: Omit<HistoryEntry, "id" | "feature_name" | "tags" | "scenario_count">): HistoryEntry {
  const full: HistoryEntry = {
    ...entry,
    id: crypto.randomUUID(),
    feature_name: extractFeatureName(entry.bdd_text),
    tags: extractTags(entry.bdd_text),
    scenario_count: countScenarios(entry.bdd_text),
  };
  const entries = load();
  entries.unshift(full);
  save(entries.slice(0, MAX_ENTRIES));
  return full;
}

export function deleteEntry(id: string) {
  save(load().filter(e => e.id !== id));
}

export function clearHistory() {
  localStorage.removeItem(KEY);
}

// ── Stats ─────────────────────────────────────────────────────────────────────

export interface HistoryStats {
  total: number;
  scenarios: number;
  approved: number;
  avgScore: number;
  lastTimestamp: number | null;
  topTags: Array<{ tag: string; count: number }>;
  byModel: Array<{ model: string; count: number; avgScore: number }>;
}

export function computeStats(entries: HistoryEntry[]): HistoryStats {
  if (entries.length === 0) {
    return { total: 0, scenarios: 0, approved: 0, avgScore: 0, lastTimestamp: null, topTags: [], byModel: [] };
  }

  const tagMap = new Map<string, number>();
  const modelMap = new Map<string, { count: number; scoreSum: number }>();

  for (const e of entries) {
    for (const t of e.tags) tagMap.set(t, (tagMap.get(t) ?? 0) + 1);
    const m = modelMap.get(e.model) ?? { count: 0, scoreSum: 0 };
    m.count++;
    m.scoreSum += e.score.score_final;
    modelMap.set(e.model, m);
  }

  return {
    total: entries.length,
    scenarios: entries.reduce((s, e) => s + e.scenario_count, 0),
    approved: entries.filter(e => e.score.aprovado).length,
    avgScore: entries.reduce((s, e) => s + e.score.score_final, 0) / entries.length,
    lastTimestamp: entries[0]?.timestamp ?? null,
    topTags: Array.from(tagMap.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([tag, count]) => ({ tag, count })),
    byModel: Array.from(modelMap.entries())
      .map(([model, d]) => ({ model, count: d.count, avgScore: d.scoreSum / d.count }))
      .sort((a, b) => b.count - a.count),
  };
}
