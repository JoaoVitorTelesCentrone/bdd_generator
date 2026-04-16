import type { HistoryEntry } from "./history";

export const NODE_W = 180;
export const NODE_H = 76;
export const ROOT_R = 46;

export interface MapNode {
  id: string;
  type: "root" | "feature";
  label: string;
  sublabel: string;
  x: number;
  y: number;
  score?: number;
  approved?: boolean;
  scenarioCount?: number;
  model?: string;
  tags?: string[];
  entryId?: string;
}

export interface MapEdge {
  id: string;
  source: string;
  target: string;
  type: "branch" | "tag-link";
  tagLabel?: string;
  tagColor?: string;
}

const TAG_PALETTE = [
  "#a3fb73","#7dd151","#60a5fa","#c4b5fd",
  "#f59e0b","#34d399","#fb7185","#38bdf8","#e879f9",
];

export function tagColor(tag: string): string {
  let h = 0;
  for (let i = 0; i < tag.length; i++) { h = ((h << 5) - h) + tag.charCodeAt(i); h |= 0; }
  return TAG_PALETTE[Math.abs(h) % TAG_PALETTE.length];
}

export function buildGraph(entries: HistoryEntry[]): {
  nodes: MapNode[];
  edges: MapEdge[];
  width: number;
  height: number;
} {
  if (entries.length === 0) {
    return { nodes: [], edges: [], width: 800, height: 600 };
  }

  const n = entries.length;
  // Ensure spacing: circumference > n * (NODE_W + 48)
  const minCirc = n * (NODE_W + 52);
  const radius = Math.max(300, minCirc / (2 * Math.PI));
  const width  = Math.ceil(2 * (radius + NODE_W + 80));
  const height = Math.ceil(2 * (radius + NODE_H + 80));
  const cx = width / 2;
  const cy = height / 2;

  const nodes: MapNode[] = [];
  const edges: MapEdge[] = [];

  // Root
  nodes.push({
    id: "root", type: "root",
    label: "BIST",
    sublabel: `${n} feature${n !== 1 ? "s" : ""} · ${entries.reduce((s, e) => s + e.scenario_count, 0)} cenários`,
    x: cx, y: cy,
  });

  // Feature nodes
  entries.forEach((entry, i) => {
    const angle = (i / n) * 2 * Math.PI - Math.PI / 2;
    const x = cx + Math.cos(angle) * radius;
    const y = cy + Math.sin(angle) * radius;
    const id = `f-${entry.id}`;

    const label = entry.feature_name.length > 24
      ? entry.feature_name.slice(0, 23) + "…"
      : entry.feature_name;

    nodes.push({
      id, type: "feature", label,
      sublabel: `${entry.scenario_count} cenários · ${entry.model}`,
      x, y,
      score: entry.score.score_final,
      approved: entry.score.aprovado,
      scenarioCount: entry.scenario_count,
      model: entry.model,
      tags: entry.tags,
      entryId: entry.id,
    });

    edges.push({
      id: `branch-${i}`,
      source: "root", target: id,
      type: "branch",
    });
  });

  // Tag-link edges (features sharing ≥1 tag)
  const added = new Set<string>();
  for (let i = 0; i < entries.length; i++) {
    for (let j = i + 1; j < entries.length; j++) {
      const si = new Set(entries[i].tags);
      const shared = entries[j].tags.filter(t => si.has(t));
      if (shared.length === 0) continue;
      const key = [entries[i].id, entries[j].id].sort().join("-");
      if (added.has(key)) continue;
      added.add(key);
      const tag = shared[0];
      edges.push({
        id: `tag-${key}`,
        source: `f-${entries[i].id}`,
        target: `f-${entries[j].id}`,
        type: "tag-link",
        tagLabel: tag,
        tagColor: tagColor(tag),
      });
    }
  }

  return { nodes, edges, width, height };
}

// ── SVG export helpers ────────────────────────��───────────────────────────────

export function svgToPng(svgEl: SVGSVGElement, scale = 2): Promise<string> {
  return new Promise((resolve, reject) => {
    const w = svgEl.viewBox.baseVal.width || svgEl.clientWidth;
    const h = svgEl.viewBox.baseVal.height || svgEl.clientHeight;
    const xml = new XMLSerializer().serializeToString(svgEl);
    const blob = new Blob([xml], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width  = w * scale;
      canvas.height = h * scale;
      const ctx = canvas.getContext("2d")!;
      ctx.scale(scale, scale);
      ctx.drawImage(img, 0, 0);
      URL.revokeObjectURL(url);
      resolve(canvas.toDataURL("image/png"));
    };
    img.onerror = reject;
    img.src = url;
  });
}

export function downloadSvg(svgEl: SVGSVGElement, filename: string) {
  const xml = new XMLSerializer().serializeToString(svgEl);
  const blob = new Blob([xml], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

export function downloadPng(dataUrl: string, filename: string) {
  const a = document.createElement("a");
  a.href = dataUrl; a.download = filename; a.click();
}
