"use client";

import { useState } from "react";
import { Copy, Check, Download } from "lucide-react";

interface Props {
  bddText: string;
  filename?: string;
}

function highlight(line: string): React.ReactNode {
  // Comments
  if (/^\s*#/.test(line)) {
    return <span className="bdd-comment">{line}</span>;
  }
  // Tags
  if (/^\s*@/.test(line)) {
    return <span className="bdd-tag">{line}</span>;
  }
  // Feature / Functionality
  if (/^\s*(Funcionalidade|Feature)\s*:/i.test(line)) {
    const idx = line.indexOf(":");
    const [kw, rest] = idx >= 0 ? [line.slice(0, idx), line.slice(idx + 1)] : [line, ""];
    return <>
      <span className="bdd-keyword-feature">{kw}:</span>
      <span className="text-zinc-200">{rest}</span>
    </>;
  }
  // Scenario / Background
  if (/^\s*(Cen[aá]rio|Scenario|Esquema do Cen[aá]rio|Background|Contexto|Exemplos)\s*[:|]/i.test(line)) {
    const m = line.match(/^(\s*)(Cen[aá]rio|Scenario|Esquema do Cen[aá]rio|Background|Contexto|Exemplos)(\s*[:|])(.*)/i);
    if (m) return <>
      <span>{m[1]}</span>
      <span className="bdd-keyword-scenario">{m[2]}{m[3]}</span>
      <span className="text-zinc-100 font-medium">{m[4]}</span>
    </>;
  }
  // Steps: Dado / Quando / Então
  if (/^\s*(Dado(?:\s+que)?|Quando|Então)\b/i.test(line)) {
    const m = line.match(/^(\s*)(Dado(?:\s+que)?|Quando|Então)(\s+)(.*)/i);
    if (m) return <>
      <span>{m[1]}</span>
      <span className="bdd-keyword-step">{m[2]}</span>
      <span>{m[3]}</span>
      <StepContent text={m[4]} />
    </>;
  }
  // And / But / E / Mas
  if (/^\s*(E\b|Mas\b|And\b|But\b)/i.test(line)) {
    const m = line.match(/^(\s*)(E\b|Mas\b|And\b|But\b)(\s+)(.*)/i);
    if (m) return <>
      <span>{m[1]}</span>
      <span className="bdd-keyword-and">{m[2]}</span>
      <span>{m[3]}</span>
      <StepContent text={m[4]} />
    </>;
  }
  // Table separator
  if (/^\s*\|/.test(line)) {
    return <span className="text-zinc-400">{line}</span>;
  }
  return <span className="text-zinc-300">{line}</span>;
}

function StepContent({ text }: { text: string }) {
  // Highlight quoted strings
  const parts = text.split(/(\"[^\"]*\")/g);
  return <>
    {parts.map((p, i) =>
      p.startsWith('"') && p.endsWith('"')
        ? <span key={i} className="bdd-string">{p}</span>
        : <span key={i} className="text-zinc-300">{p}</span>
    )}
  </>;
}

export function BDDViewer({ bddText, filename = "bdd.feature" }: Props) {
  const [copied, setCopied] = useState(false);

  const lines = bddText.split("\n");

  async function copy() {
    await navigator.clipboard.writeText(bddText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function download() {
    const blob = new Blob([bddText], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="flex flex-col">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-zinc-800/60 border-b border-zinc-700/50 rounded-t-lg">
        <span className="text-xs text-zinc-500 font-mono">{filename}</span>
        <div className="flex items-center gap-1">
          <button onClick={download} className="btn-ghost text-xs">
            <Download className="w-3.5 h-3.5" />
            .feature
          </button>
          <button onClick={copy} className="btn-ghost text-xs">
            {copied
              ? <><Check className="w-3.5 h-3.5 text-emerald-400" /> Copiado</>
              : <><Copy className="w-3.5 h-3.5" /> Copiar</>
            }
          </button>
        </div>
      </div>

      {/* Code block */}
      <div className="overflow-auto bg-zinc-900 rounded-b-lg border border-t-0 border-zinc-700/50 max-h-[500px]">
        <table className="w-full border-collapse text-sm font-mono leading-relaxed">
          <tbody>
            {lines.map((line, i) => (
              <tr key={i} className="hover:bg-zinc-800/30 transition-colors">
                <td className="select-none text-right text-zinc-700 px-3 py-0 w-10 text-xs align-top pt-0.5">
                  {i + 1}
                </td>
                <td className="px-3 py-0 whitespace-pre-wrap break-words text-xs sm:text-sm">
                  {highlight(line)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
