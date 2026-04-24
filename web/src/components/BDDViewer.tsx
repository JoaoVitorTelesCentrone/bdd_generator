"use client";

import { useState } from "react";
import { Copy, Check, Download, FileCode } from "lucide-react";

interface Props {
  bddText: string;
  filename?: string;
}

// Strip markdown fences defensively (in case backend didn't)
function cleanBDD(raw: string): string {
  let text = raw.trim();
  if (text.startsWith("```")) {
    text = text.replace(/^```[a-zA-Z]*\n?/, "").replace(/\n?```$/, "").trim();
  }
  return text;
}

const KW_FEATURE   = /^\s*(Funcionalidade|Feature)\s*:/i;
const KW_SCENARIO  = /^\s*(Cen[aá]rio(?: Outline)?|Scenario(?: Outline)?|Esquema do Cen[aá]rio|Background|Contexto|Exemplos|Examples)\s*[:|]/i;
const KW_STEP      = /^\s*(Dado(?:\s+que)?|Quando|Então|Given|When|Then)\b/i;
const KW_AND       = /^\s*(E\b|Mas\b|And\b|But\b|\*\s)/i;
const KW_COMMENT   = /^\s*#/;
const KW_TAG       = /^\s*@/;
const KW_TABLE     = /^\s*\|/;
// Narrative lines inside Feature block (Como/Para/Eu quero)
const KW_NARRATIVE = /^\s*(Como|Para|Eu quero|As a|In order to|I want)\b/i;

function highlight(line: string): React.ReactNode {
  if (KW_COMMENT.test(line))
    return <span className="bdd-comment">{line}</span>;

  if (KW_TAG.test(line))
    return <span className="bdd-tag">{line}</span>;

  if (KW_FEATURE.test(line)) {
    const idx = line.indexOf(":");
    const kw  = line.slice(0, idx + 1);
    const rest = line.slice(idx + 1);
    return <><span className="bdd-keyword-feature">{kw}</span><span style={{ color: "#eef9e8" }}>{rest}</span></>;
  }

  if (KW_SCENARIO.test(line)) {
    const m = line.match(/^(\s*)(Cen[aá]rio(?: Outline)?|Scenario(?: Outline)?|Esquema do Cen[aá]rio|Background|Contexto|Exemplos|Examples)(\s*[:|])(.*)/i);
    if (m) return (
      <>
        <span>{m[1]}</span>
        <span className="bdd-keyword-scenario">{m[2]}{m[3]}</span>
        <span style={{ color: "#eef9e8", fontWeight: 500 }}>{m[4]}</span>
      </>
    );
  }

  if (KW_STEP.test(line)) {
    const m = line.match(/^(\s*)(Dado(?:\s+que)?|Quando|Então|Given|When|Then)(\s+|:?\s*)(.*)/i);
    if (m) return (
      <>
        <span>{m[1]}</span>
        <span className="bdd-keyword-step">{m[2]}</span>
        <span>{m[3]}</span>
        <StepContent text={m[4]} />
      </>
    );
  }

  if (KW_AND.test(line)) {
    const m = line.match(/^(\s*)(E\b|Mas\b|And\b|But\b|\*)(\s+)(.*)/i);
    if (m) return (
      <>
        <span>{m[1]}</span>
        <span className="bdd-keyword-and">{m[2]}</span>
        <span>{m[3]}</span>
        <StepContent text={m[4]} />
      </>
    );
  }

  if (KW_TABLE.test(line))
    return <span style={{ color: "#7a9b87" }}>{line}</span>;

  if (KW_NARRATIVE.test(line))
    return <span style={{ color: "#9ab89a" }}>{line}</span>;

  return <span style={{ color: "#c8e8c8" }}>{line}</span>;
}

function StepContent({ text }: { text: string }) {
  const parts = text.split(/(\"[^\"]*\")/g);
  return (
    <>
      {parts.map((p, i) =>
        p.startsWith('"') && p.endsWith('"')
          ? <span key={i} className="bdd-string">{p}</span>
          : <span key={i} style={{ color: "#c8e8c8" }}>{p}</span>
      )}
    </>
  );
}

export function BDDViewer({ bddText, filename = "output.feature" }: Props) {
  const [copied, setCopied] = useState(false);

  const cleaned = cleanBDD(bddText);
  const lines   = cleaned.split("\n");

  async function copy() {
    await navigator.clipboard.writeText(cleaned);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function download() {
    const blob = new Blob([cleaned], { type: "text/plain" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href = url; a.download = filename; a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="rounded-lg overflow-hidden border border-bist-border">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-bist-surface2 border-b border-bist-border">
        <div className="flex items-center gap-2">
          <FileCode className="w-3.5 h-3.5 text-bist-muted" />
          <span className="text-xs font-code text-bist-muted">{filename}</span>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={download} className="btn-ghost text-xs">
            <Download className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">.feature</span>
          </button>
          <button onClick={copy} className="btn-ghost text-xs">
            {copied
              ? <><Check className="w-3.5 h-3.5 text-[#2D6A3F]" /><span className="hidden sm:inline">Copiado</span></>
              : <><Copy className="w-3.5 h-3.5" /><span className="hidden sm:inline">Copiar</span></>
            }
          </button>
        </div>
      </div>

      {/* Code block */}
      <div className="overflow-auto bg-[#1a2c21] max-h-[520px]">
        <table className="w-full border-collapse leading-relaxed text-sm">
          <tbody>
            {lines.map((line, i) => (
              <tr key={i} className="hover:bg-[#a3fb73]/3 transition-colors">
                <td className="select-none text-right pr-4 pl-3 py-0 w-10 text-xs align-top pt-0.5 font-code"
                    style={{ color: "#2f5237" }}>
                  {i + 1}
                </td>
                <td className="pr-4 py-0 whitespace-pre-wrap break-words font-code text-xs sm:text-sm">
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
