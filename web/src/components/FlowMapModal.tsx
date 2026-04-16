"use client";

import { useRef, useState, useCallback, useMemo, useEffect } from "react";
import {
  X, Download, ZoomIn, ZoomOut, Maximize2, RotateCcw, ImageDown,
} from "lucide-react";
import type { HistoryEntry } from "@/lib/history";
import {
  buildGraph, svgToPng, downloadSvg, downloadPng,
  NODE_W, NODE_H, ROOT_R,
  type MapNode, type MapEdge,
} from "@/lib/mindmap";

// ─── Score helpers ─────────────────────────────────────────────────────────────

function scoreFill(v: number) {
  if (v >= 8) return "#a3fb73";
  if (v >= 7) return "#7dd151";
  if (v >= 5) return "#f59e0b";
  return "#ef4444";
}

function borderCol(approved: boolean) {
  return approved ? "#a3fb73" : "#ef4444";
}

// ─── SVG element: Root node ────────────────────────────────────────────────────

function RootNode({ node }: { node: MapNode }) {
  return (
    <g>
      <circle cx={node.x} cy={node.y} r={ROOT_R + 18}
        fill="rgba(163,251,115,0.03)" stroke="rgba(163,251,115,0.08)" strokeWidth={1} />
      <circle cx={node.x} cy={node.y} r={ROOT_R + 8}
        fill="rgba(163,251,115,0.06)" stroke="rgba(163,251,115,0.14)" strokeWidth={1} />
      <circle cx={node.x} cy={node.y} r={ROOT_R}
        fill="rgba(20,38,26,0.95)" stroke="#a3fb73" strokeWidth={2} />
      <text x={node.x} y={node.y - 6} textAnchor="middle"
        fill="#a3fb73" fontSize={16} fontWeight="bold"
        fontFamily="'Share Tech Mono','Consolas',monospace" letterSpacing="4">
        BIST
      </text>
      <text x={node.x} y={node.y + 10} textAnchor="middle"
        fill="#5a7a65" fontSize={8.5}
        fontFamily="'Consolas','JetBrains Mono',monospace">
        {node.sublabel}
      </text>
    </g>
  );
}

// ─── SVG element: Feature node ─────────────────────────────────────────────────

function FeatureNode({
  node, hovered, selected, onClick, onEnter, onLeave,
}: {
  node: MapNode;
  hovered: boolean;
  selected: boolean;
  onClick: (n: MapNode) => void;
  onEnter: (n: MapNode) => void;
  onLeave: () => void;
}) {
  const x = node.x - NODE_W / 2;
  const y = node.y - NODE_H / 2;
  const approved = node.approved ?? false;
  const border = borderCol(approved);
  const sfill = scoreFill(node.score ?? 0);
  const scoreBarW = Math.round(((node.score ?? 0) / 10) * (NODE_W - 16));
  const active = hovered || selected;

  return (
    <g
      onClick={() => onClick(node)}
      onMouseEnter={() => onEnter(node)}
      onMouseLeave={onLeave}
      style={{ cursor: "pointer" }}
    >
      {/* Ambient glow when active */}
      {active && (
        <rect x={x - 6} y={y - 6} width={NODE_W + 12} height={NODE_H + 12}
          rx={13} fill="none"
          stroke={border} strokeWidth={1} strokeOpacity={0.25}
          filter="url(#nodeGlow)" />
      )}

      {/* Card background */}
      <rect x={x} y={y} width={NODE_W} height={NODE_H} rx={8}
        fill={active ? "rgba(36,61,44,0.95)" : "rgba(26,44,33,0.88)"}
        stroke={border}
        strokeWidth={selected ? 2 : active ? 1.8 : 1}
        strokeOpacity={selected ? 1 : active ? 0.7 : 0.4}
      />

      {/* Top accent line */}
      <rect x={x} y={y} width={NODE_W} height={3} rx={0}
        fill={border} fillOpacity={selected ? 0.6 : 0.3}
        style={{ borderTopLeftRadius: 8, borderTopRightRadius: 8 }}
      />

      {/* Score badge (top-right) */}
      <text x={x + NODE_W - 8} y={y + 16} textAnchor="end"
        fill={sfill} fontSize={11} fontWeight="700"
        fontFamily="'Consolas','JetBrains Mono',monospace">
        {(node.score ?? 0).toFixed(1)}
      </text>

      {/* Feature name */}
      <text x={x + 10} y={y + 18} textAnchor="start"
        fill={approved ? "#eef9e8" : "#c8c8c8"}
        fontSize={10.5} fontWeight="600"
        fontFamily="'Consolas','JetBrains Mono',monospace">
        {node.label}
      </text>

      {/* Sublabel: scenarios · model */}
      <text x={x + 10} y={y + 33} textAnchor="start"
        fill="#5a7a65" fontSize={8.5}
        fontFamily="'Consolas','JetBrains Mono',monospace">
        {node.sublabel}
      </text>

      {/* Tag pills */}
      {(node.tags ?? []).slice(0, 3).map((tag, i) => {
        const pw = Math.min(60, tag.length * 5.5 + 10);
        const px = x + 8 + i * (pw + 4);
        if (px + pw > x + NODE_W - 4) return null;
        return (
          <g key={tag}>
            <rect x={px} y={y + 42} width={pw} height={13} rx={3}
              fill="rgba(163,251,115,0.07)" stroke="rgba(163,251,115,0.18)" strokeWidth={0.5} />
            <text x={px + pw / 2} y={y + 52} textAnchor="middle"
              fill="#a3fb73" fontSize={7.5} fillOpacity={0.7}
              fontFamily="'Consolas','JetBrains Mono',monospace">
              {tag.length > 9 ? tag.slice(0, 8) + "…" : tag}
            </text>
          </g>
        );
      })}

      {/* Score bar */}
      <rect x={x + 8} y={y + NODE_H - 8} width={NODE_W - 16} height={3} rx={1.5}
        fill="rgba(163,251,115,0.07)" />
      <rect x={x + 8} y={y + NODE_H - 8} width={scoreBarW} height={3} rx={1.5}
        fill={sfill} fillOpacity={0.8} />
    </g>
  );
}

// ─── SVG element: Branch edge (root → feature) ─────────────────────────────────

function BranchEdge({ edge, nodes }: { edge: MapEdge; nodes: MapNode[] }) {
  const src = nodes.find(n => n.id === edge.source)!;
  const tgt = nodes.find(n => n.id === edge.target)!;
  if (!src || !tgt) return null;

  const dx = tgt.x - src.x;
  const dy = tgt.y - src.y;
  const len = Math.hypot(dx, dy);
  const ux = dx / len; const uy = dy / len;

  // Start from root circle edge
  const sx = src.x + ux * (ROOT_R + 1);
  const sy = src.y + uy * (ROOT_R + 1);
  // End at feature node edge (closest point on rect)
  const hw = NODE_W / 2; const hh = NODE_H / 2;
  const ex = tgt.x - ux * (hw + 2);
  const ey = tgt.y - uy * (hh + 2);

  // Cubic bezier — control points at 40% along
  const cpLen = len * 0.45;
  const cp1x = sx + ux * cpLen; const cp1y = sy + uy * cpLen;
  const cp2x = ex - ux * cpLen; const cp2y = ey - uy * cpLen;

  const approved = nodes.find(n => n.id === edge.target)?.approved ?? true;
  const stroke = approved ? "rgba(163,251,115,0.22)" : "rgba(239,68,68,0.18)";

  return (
    <path
      d={`M ${sx} ${sy} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${ex} ${ey}`}
      fill="none" stroke={stroke} strokeWidth={1.5} strokeLinecap="round"
    />
  );
}

// ─── SVG element: Tag-link edge (feature → feature) ─────────────────��──────────

function TagEdge({ edge, nodes }: { edge: MapEdge; nodes: MapNode[] }) {
  const src = nodes.find(n => n.id === edge.source)!;
  const tgt = nodes.find(n => n.id === edge.target)!;
  if (!src || !tgt) return null;

  const mx = (src.x + tgt.x) / 2;
  const my = (src.y + tgt.y) / 2;
  const dx = tgt.x - src.x; const dy = tgt.y - src.y;
  const len = Math.hypot(dx, dy);
  const perp = 30;
  const cpx = mx + (-dy / len) * perp;
  const cpy = my + (dx / len) * perp;
  const color = edge.tagColor ?? "#a3fb73";

  return (
    <g>
      <path
        d={`M ${src.x} ${src.y} Q ${cpx} ${cpy} ${tgt.x} ${tgt.y}`}
        fill="none" stroke={color} strokeWidth={0.8}
        strokeOpacity={0.2} strokeDasharray="5 3"
      />
      {edge.tagLabel && (
        <text x={cpx} y={cpy - 5} textAnchor="middle"
          fill={color} fillOpacity={0.4} fontSize={7.5}
          fontFamily="'Consolas','JetBrains Mono',monospace">
          {edge.tagLabel}
        </text>
      )}
    </g>
  );
}

// ─── Tooltip ───────────────────────────────────────────────────────────────────

function Tooltip({ node, entries }: { node: MapNode; entries: HistoryEntry[] }) {
  const entry = entries.find(e => e.id === node.entryId);
  return (
    <div className="card-terminal p-4 space-y-2 min-w-[220px] shadow-xl shadow-black/50 pointer-events-none">
      <p className="text-xs font-mono font-semibold text-[#a3fb73]">{node.label}</p>
      {entry && (
        <>
          <div className="space-y-1 text-[10px] font-mono text-[#5a7a65]">
            <p>score: <span className="text-[#eef9e8]">{node.score?.toFixed(1)}/10</span></p>
            <p>cenários: <span className="text-[#eef9e8]">{node.scenarioCount}</span></p>
            <p>modelo: <span className="text-[#eef9e8]">{node.model}</span></p>
            <p>status: <span className={node.approved ? "text-[#a3fb73]" : "text-red-400"}>
              {node.approved ? "aprovado" : "reprovado"}
            </span></p>
          </div>
          {(node.tags ?? []).length > 0 && (
            <div className="flex flex-wrap gap-1 pt-1 border-t border-[#a3fb73]/10">
              {(node.tags ?? []).map(t => (
                <span key={t} className="text-[9px] font-mono text-[#a3fb73]/60 bg-[#a3fb73]/8 px-1.5 py-0.5 rounded">
                  {t}
                </span>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

// ─── Main Modal ────────────────────────────────────────────────────────────────

interface Props {
  entries: HistoryEntry[];
  onClose: () => void;
}

export function FlowMapModal({ entries, onClose }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const [scale, setScale] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [dragging, setDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [hoveredNode, setHoveredNode] = useState<MapNode | null>(null);
  const [selectedNode, setSelectedNode] = useState<MapNode | null>(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });
  const [exporting, setExporting] = useState(false);

  const { nodes, edges, width, height } = useMemo(() => buildGraph(entries), [entries]);

  // Fit to container on mount
  useEffect(() => {
    const el = containerRef.current;
    if (!el || width === 0) return;
    const cw = el.clientWidth;
    const ch = el.clientHeight;
    const fit = Math.min(cw / width, ch / height, 1) * 0.92;
    setScale(fit);
    setPan({ x: (cw - width * fit) / 2, y: (ch - height * fit) / 2 });
  }, [width, height]);

  // ── Wheel zoom ──
  const onWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY < 0 ? 1.1 : 0.9;
    setScale(s => Math.min(3, Math.max(0.2, s * delta)));
  }, []);

  // ── Drag pan ──
  const onMouseDown = useCallback((e: React.MouseEvent) => {
    if ((e.target as SVGElement).closest("[data-node]")) return;
    setDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  }, [pan]);

  const onMouseMove = useCallback((e: React.MouseEvent) => {
    if (!dragging) return;
    setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
    // update tooltip position
    if (hoveredNode) setTooltipPos({ x: e.clientX, y: e.clientY });
  }, [dragging, dragStart, hoveredNode]);

  const onMouseUp = useCallback(() => setDragging(false), []);

  const handleNodeEnter = (n: MapNode, e: React.MouseEvent) => {
    setHoveredNode(n);
    setTooltipPos({ x: e.clientX, y: e.clientY });
  };

  // ── Reset view ──
  const resetView = () => {
    const el = containerRef.current;
    if (!el || width === 0) return;
    const fit = Math.min(el.clientWidth / width, el.clientHeight / height, 1) * 0.92;
    setScale(fit);
    setPan({ x: (el.clientWidth - width * fit) / 2, y: (el.clientHeight - height * fit) / 2 });
  };

  // ── Export SVG ──
  const handleExportSvg = () => {
    if (!svgRef.current) return;
    downloadSvg(svgRef.current, `bist_fluxos_${Date.now()}.svg`);
  };

  // ── Export PNG ──
  const handleExportPng = async () => {
    if (!svgRef.current) return;
    setExporting(true);
    try {
      const dataUrl = await svgToPng(svgRef.current, 2);
      downloadPng(dataUrl, `bist_fluxos_${Date.now()}.png`);
    } finally {
      setExporting(false);
    }
  };

  const featureNodes = nodes.filter(n => n.type === "feature");
  const rootNode = nodes.find(n => n.type === "root");
  const branchEdges = edges.filter(e => e.type === "branch");
  const tagEdges = edges.filter(e => e.type === "tag-link");

  return (
    <div className="fixed inset-0 z-50 flex flex-col bg-[#1a2c21]" style={{ fontFamily: "Consolas,'JetBrains Mono',monospace" }}>

      {/* ── Toolbar ── */}
      <div className="flex items-center justify-between px-4 py-3
                      border-b border-[#a3fb73]/12 bg-[#1a2c21]/95 backdrop-blur
                      flex-shrink-0 z-10">
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono text-[#a3fb73]">bist map</span>
          <span className="text-[#3d5a44] text-xs font-mono">--flows --interactive</span>
          <div className="w-px h-4 bg-[#a3fb73]/15" />
          <span className="text-[10px] font-mono text-[#3d5a44]">
            {featureNodes.length} features · {tagEdges.length} conexões por tags
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Zoom controls */}
          <div className="flex items-center gap-1 border border-[#a3fb73]/15 rounded px-1">
            <button onClick={() => setScale(s => Math.max(0.2, s * 0.8))}
              className="btn-ghost p-1.5"><ZoomOut className="w-3.5 h-3.5" /></button>
            <span className="text-[10px] font-mono text-[#5a7a65] w-10 text-center tabular-nums">
              {Math.round(scale * 100)}%
            </span>
            <button onClick={() => setScale(s => Math.min(3, s * 1.25))}
              className="btn-ghost p-1.5"><ZoomIn className="w-3.5 h-3.5" /></button>
          </div>

          <button onClick={resetView} className="btn-ghost text-xs gap-1.5">
            <Maximize2 className="w-3.5 h-3.5" /> fit
          </button>

          <div className="w-px h-4 bg-[#a3fb73]/15" />

          {/* Export */}
          <button onClick={handleExportSvg}
            className="btn-secondary text-xs py-1.5 px-3 gap-1.5">
            <Download className="w-3.5 h-3.5" /> SVG
          </button>
          <button onClick={handleExportPng} disabled={exporting}
            className="btn-primary text-xs py-1.5 px-3 gap-1.5">
            <ImageDown className="w-3.5 h-3.5" />
            {exporting ? "gerando…" : "PNG"}
          </button>

          <div className="w-px h-4 bg-[#a3fb73]/15" />

          <button onClick={onClose} className="btn-ghost p-1.5">
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* ── Canvas ── */}
      <div
        ref={containerRef}
        className="flex-1 overflow-hidden relative"
        style={{ cursor: dragging ? "grabbing" : "grab", background: "#1a2c21" }}
        onWheel={onWheel}
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onMouseLeave={onMouseUp}
      >
        <svg
          ref={svgRef}
          viewBox={`0 0 ${width} ${height}`}
          width={width} height={height}
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${scale})`,
            transformOrigin: "0 0",
            transition: dragging ? "none" : "transform 0.05s ease",
            display: "block",
          }}
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            {/* Background */}
            <rect id="bg" width={width} height={height} fill="#1a2c21" />
            {/* Grid pattern */}
            <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
              <path d="M 32 0 L 0 0 0 32" fill="none"
                stroke="rgba(163,251,115,0.04)" strokeWidth="0.5" />
            </pattern>
            {/* Glow filter */}
            <filter id="nodeGlow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur in="SourceGraphic" stdDeviation="6" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
            <filter id="rootGlow" x="-80%" y="-80%" width="260%" height="260%">
              <feGaussianBlur in="SourceGraphic" stdDeviation="12" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Background fill */}
          <rect width={width} height={height} fill="#1a2c21" />
          <rect width={width} height={height} fill="url(#grid)" />

          {/* Subtle radial gradient around center */}
          <radialGradient id="centerGrad" cx="50%" cy="50%" r="40%">
            <stop offset="0%" stopColor="#a3fb73" stopOpacity="0.04" />
            <stop offset="100%" stopColor="#1a2c21" stopOpacity="0" />
          </radialGradient>
          <rect width={width} height={height} fill="url(#centerGrad)" />

          {/* ── Tag-link edges (behind everything) ── */}
          <g opacity={0.9}>
            {tagEdges.map(e => (
              <TagEdge key={e.id} edge={e} nodes={nodes} />
            ))}
          </g>

          {/* ── Branch edges ── */}
          <g>
            {branchEdges.map(e => (
              <BranchEdge key={e.id} edge={e} nodes={nodes} />
            ))}
          </g>

          {/* ── Feature nodes ── */}
          <g>
            {featureNodes.map(n => (
              <FeatureNode
                key={n.id} node={n}
                hovered={hoveredNode?.id === n.id}
                selected={selectedNode?.id === n.id}
                onClick={node => setSelectedNode(s => s?.id === node.id ? null : node)}
                onEnter={(node) => setHoveredNode(node)}
                onLeave={() => setHoveredNode(null)}
              />
            ))}
          </g>

          {/* ── Root node (on top) ── */}
          {rootNode && <RootNode node={rootNode} />}
        </svg>

        {/* ── Empty state ── */}
        {nodes.length === 0 && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 text-center">
            <p className="text-[#5a7a65] font-mono text-sm">histórico vazio</p>
            <p className="text-xs font-mono text-[#3d5a44]">
              gere BDDs em <a href="/generate" className="text-[#a3fb73]">/generate</a> para visualizar o mapa
            </p>
          </div>
        )}

        {/* ── Hint ── */}
        {nodes.length > 0 && (
          <div className="absolute bottom-4 left-4 text-[10px] font-mono text-[#2f5237] space-y-0.5 pointer-events-none">
            <p>scroll → zoom · drag → pan · click no nó → detalhe</p>
          </div>
        )}

        {/* ── Legend ── */}
        {nodes.length > 0 && (
          <div className="absolute bottom-4 right-4 card p-3 space-y-1.5 text-[9px] font-mono pointer-events-none">
            <p className="text-[#3d5a44] uppercase tracking-widest mb-2">legenda</p>
            <div className="flex items-center gap-2">
              <div className="w-8 h-0.5 bg-[#a3fb73] opacity-30 rounded" />
              <span className="text-[#3d5a44]">feature → BIST</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-0.5 border-t border-dashed border-[#a3fb73] opacity-30" />
              <span className="text-[#3d5a44]">tag compartilhada</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-sm border border-[#a3fb73] opacity-50" />
              <span className="text-[#3d5a44]">aprovado</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-sm border border-red-500 opacity-50" />
              <span className="text-[#3d5a44]">reprovado</span>
            </div>
          </div>
        )}
      </div>

      {/* ── Tooltip (absolute, follows mouse) ── */}
      {hoveredNode && hoveredNode.type === "feature" && (
        <div
          className="fixed z-50 pointer-events-none"
          style={{
            left: tooltipPos.x + 14,
            top: tooltipPos.y - 10,
            maxWidth: 240,
          }}
        >
          <Tooltip node={hoveredNode} entries={entries} />
        </div>
      )}

      {/* ── Selected node detail panel ── */}
      {selectedNode && selectedNode.type === "feature" && (
        <div className="absolute bottom-0 left-0 right-0 card-terminal border-t border-[#a3fb73]/15
                        p-4 flex items-center gap-6 animate-slide-up z-20 flex-shrink-0">
          <div className="flex-1 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
            <div>
              <p className="text-[#3d5a44]">feature</p>
              <p className="text-[#eef9e8] font-semibold mt-0.5">{selectedNode.label}</p>
            </div>
            <div>
              <p className="text-[#3d5a44]">score</p>
              <p className={`font-bold mt-0.5 ${selectedNode.approved ? "text-[#a3fb73]" : "text-red-400"}`}>
                {selectedNode.score?.toFixed(1)}/10 — {selectedNode.approved ? "aprovado" : "reprovado"}
              </p>
            </div>
            <div>
              <p className="text-[#3d5a44]">cenários · modelo</p>
              <p className="text-[#7a9b87] mt-0.5">{selectedNode.scenarioCount} · {selectedNode.model}</p>
            </div>
            <div>
              <p className="text-[#3d5a44]">tags</p>
              <p className="text-[#a3fb73]/70 mt-0.5">{(selectedNode.tags ?? []).join(", ") || "—"}</p>
            </div>
          </div>
          <button onClick={() => setSelectedNode(null)} className="btn-ghost p-1 flex-shrink-0">
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}
    </div>
  );
}
