"use client";

import { useState } from "react";
import { Copy, Check, Download } from "lucide-react";

interface Props {
  bddText: string;
  filename?: string;
}

function highlight(line: string): React.ReactNode {
  if (/^\s*#/.test(line)) {
    return <span className="bdd-comment">{line}</span>;
  }
  if (/^\s*@/.test(line)) {
    return <span className="bdd-tag">{line}</span>;
  }
  if (/^\s*(Funcionalidade|Feature)\s*:/i.test(line)) {
    const idx = line.indexOf(":");
    const [kw, rest] = idx >= 0 ? [line.slice(0, idx), line.slice(idx + 1)] : [line, ""];
    return <>
      <span className="bdd-keyword-feature">{kw}:</span>
      <span style={{ color: "#eef9e8" }}>{rest}</span>
    </>;
  }
  if (/^\s*(Cen[aá]rio|Scenario|Esquema do Cen[aá]rio|Background|Contexto|Exemplos)\s*[:|]/i.test(line)) {
    const m = line.match(/^(\s*)(Cen[aá]rio|Scenario|Esquema do Cen[aá]rio|Background|Contexto|Exemplos)(\s*[:|])(.*)/i);
    if (m) return <>
      <span>{m[1]}</span>
      <span className="bdd-keyword-scenario">{m[2]}{m[3]}</span>
      <span style={{ color: "#eef9e8", fontWeight: 500 }}>{m[4]}</span>
    </>;
  }
  if (/^\s*(Dado(?:\s+que)?|Quando|Então)\b/i.test(line)) {
    const m = line.match(/^(\s*)(Dado(?:\s+que)?|Quando|Então)(\s+)(.*)/i);
    if (m) return <>
      <span>{m[1]}</span>
      <span className="bdd-keyword-step">{m[2]}</span>
      <span>{m[3]}</span>
      <StepContent text={m[4]} />
    </>;
  }
  if (/^\s*(E\b|Mas\b|And\b|But\b)/i.test(line)) {
    const m = line.match(/^(\s*)(E\b|Mas\b|And\b|But\b)(\s+)(.*)/i);
    if (m) return <>
      <span>{m[1]}</span>
      <span className="bdd-keyword-and">{m[2]}</span>
      <span>{m[3]}</span>
      <StepContent text={m[4]} />
    </>;
  }
  if (/^\s*\|/.test(line)) {
    return <span style={{ color: "#7a9b87" }}>{line}</span>;
  }
  return <span style={{ color: "#c8e8c8" }}>{line}</span>;
}

function StepContent({ text }: { text: string }) {
  const parts = text.split(/(\"[^\"]*\")/g);
  return <>
    {parts.map((p, i) =>
      p.startsWith('"') && p.endsWith('"')
        ? <span key={i} className="bdd-string">{p}</span>
        : <span key={i} style={{ color: "#c8e8c8" }}>{p}</span>
    )}
  </>;
}

export function BDDViewer({ bddText, filename = "output.feature" }: Props) {
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
    <div className="flex flex-col rounded overflow-hidden">
      {/* Toolbar — terminal chrome */}
      <div className="flex items-center justify-between px-3 py-2
                      bg-[#243d2c] border border-[#a3fb73]/15 border-b-0 rounded-t">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-red-500/50" />
            <div className="w-2.5 h-2.5 rounded-full bg-[#f59e0b]/50" />
            <div className="w-2.5 h-2.5 rounded-full bg-[#a3fb73]/50" />
          </div>
          <span className="text-xs font-mono text-[#3d5a44]">{filename}</span>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={download} className="btn-ghost text-xs">
            <Download className="w-3.5 h-3.5" />
            .feature
          </button>
          <button onClick={copy} className="btn-ghost text-xs">
            {copied
              ? <><Check className="w-3.5 h-3.5 text-[#a3fb73]" /> copiado</>
              : <><Copy className="w-3.5 h-3.5" /> copiar</>
            }
          </button>
        </div>
      </div>

      {/* Code block */}
      <div className="overflow-auto bg-[#1a2c21] border border-[#a3fb73]/12 border-t-0 rounded-b max-h-[520px]">
        <table className="w-full border-collapse leading-relaxed text-sm">
          <tbody>
            {lines.map((line, i) => (
              <tr key={i} className="hover:bg-[#a3fb73]/03 transition-colors">
                <td className="select-none text-right pr-4 pl-3 py-0 w-10 text-xs align-top pt-0.5"
                    style={{ color: "#2f5237", fontFamily: "inherit" }}>
                  {i + 1}
                </td>
                <td className="pr-4 py-0 whitespace-pre-wrap break-words font-mono text-xs sm:text-sm">
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
