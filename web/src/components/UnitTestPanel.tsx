"use client";

import { useState, useEffect } from "react";
import {
  TestTube2, Loader2, AlertCircle, Copy, Check,
  Download, ChevronDown, Sparkles, FileCode,
} from "lucide-react";
import { fetchUnitTestLanguages, generateUnitTests } from "@/lib/api";
import type { UnitTestLanguageCatalog, UnitTestResult } from "@/types";

interface Props {
  bddText: string;
  model?: string;
}

export function UnitTestPanel({ bddText, model = "flash" }: Props) {
  const [catalog, setCatalog]           = useState<UnitTestLanguageCatalog | null>(null);
  const [language, setLanguage]         = useState("python");
  const [framework, setFramework]       = useState("pytest");
  const [loading, setLoading]           = useState(false);
  const [result, setResult]             = useState<UnitTestResult | null>(null);
  const [error, setError]               = useState<string | null>(null);
  const [copied, setCopied]             = useState(false);

  // Load catalog once on mount
  useEffect(() => {
    fetchUnitTestLanguages()
      .then(data => {
        setCatalog(data);
        // Apply defaults from catalog for the initial language
        const defaultFw = data[language]?.default_framework;
        if (defaultFw) setFramework(defaultFw);
      })
      .catch(() => {/* catalog unavailable — selects still work with hardcoded fallback */});
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  function handleLanguageChange(lang: string) {
    setLanguage(lang);
    setResult(null);
    setError(null);
    if (catalog?.[lang]) {
      setFramework(catalog[lang].default_framework);
    }
  }

  function handleFrameworkChange(fw: string) {
    setFramework(fw);
    setResult(null);
    setError(null);
  }

  async function handleGenerate() {
    setLoading(true); setError(null); setResult(null);
    try {
      const res = await generateUnitTests({ bdd_text: bddText, language, framework, model });
      setResult(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  }

  function copy() {
    if (!result) return;
    navigator.clipboard.writeText(result.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function download() {
    if (!result) return;
    const blob = new Blob([result.code], { type: "text/plain" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href = url;
    a.download = buildFilename(result);
    a.click();
    URL.revokeObjectURL(url);
  }

  const frameworks = catalog?.[language]?.frameworks ?? FALLBACK_FRAMEWORKS[language] ?? [];
  const currentHint = frameworks.find(f => f.id === framework)?.hint ?? "";
  const currentLangLabel = catalog?.[language]?.label ?? language;

  return (
    <div className="card p-5 space-y-4">

      {/* Header */}
      <div className="flex items-center gap-2 pb-3 border-b border-bist-border">
        <TestTube2 className="w-4 h-4 text-bist-muted" />
        <h3 className="text-sm font-semibold text-bist-primary">Gerar testes unitários</h3>
        <span className="text-xs text-bist-dim font-code ml-auto">a partir do BDD gerado</span>
      </div>

      {/* Selectors */}
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-bist-muted">Linguagem</label>
          <div className="relative">
            <select
              value={language}
              onChange={e => handleLanguageChange(e.target.value)}
              className="input text-sm w-full appearance-none pr-8 cursor-pointer"
            >
              {catalog
                ? Object.values(catalog).map(lang => (
                    <option key={lang.id} value={lang.id}>{lang.label}</option>
                  ))
                : FALLBACK_LANGUAGES.map(l => (
                    <option key={l.id} value={l.id}>{l.label}</option>
                  ))
              }
            </select>
            <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-bist-dim pointer-events-none" />
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="text-xs font-medium text-bist-muted">Framework</label>
          <div className="relative">
            <select
              value={framework}
              onChange={e => handleFrameworkChange(e.target.value)}
              className="input text-sm w-full appearance-none pr-8 cursor-pointer"
            >
              {frameworks.map(fw => (
                <option key={fw.id} value={fw.id}>{fw.label}</option>
              ))}
            </select>
            <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-bist-dim pointer-events-none" />
          </div>
        </div>
      </div>

      {/* Install hint */}
      {currentHint && (
        <p className="text-[10px] font-code text-bist-dim bg-bist-surface2 rounded px-2.5 py-1.5 border border-bist-border2">
          <span className="text-bist-muted font-medium">instalação: </span>
          {currentHint}
        </p>
      )}

      {/* Generate button */}
      <button
        className="btn-primary w-full text-sm py-2.5"
        disabled={loading || !bddText.trim()}
        onClick={handleGenerate}
      >
        {loading
          ? <><Loader2 className="w-4 h-4 animate-spin" /> Gerando testes para {currentLangLabel}...</>
          : <><Sparkles className="w-4 h-4" /> Gerar testes em {currentLangLabel}</>
        }
      </button>

      {/* Loading bar */}
      {loading && (
        <div className="h-1 bg-bist-border rounded-full overflow-hidden">
          <div className="h-full bg-[#a3fb73] animate-progress rounded-full" />
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-start gap-2 text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2.5">
          <AlertCircle className="w-3.5 h-3.5 mt-0.5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="space-y-3 animate-slide-up">

          {/* Metadata row */}
          <div className="flex items-center gap-2 flex-wrap">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#a3fb73]/15 border border-[#a3fb73]/30 text-xs font-medium text-[#2D6A3F]">
              <TestTube2 className="w-3 h-3" />
              {result.num_tests} {result.num_tests === 1 ? "teste" : "testes"} gerados
            </span>
            <span className="text-[10px] font-code text-bist-dim">
              {result.total_tokens.toLocaleString()} tokens · {result.duration_seconds}s
            </span>
            <span className="text-[10px] font-code text-bist-dim ml-auto">
              {buildFilename(result)}
            </span>
          </div>

          {/* Code viewer */}
          <CodeViewer
            code={result.code}
            filename={buildFilename(result)}
            onCopy={copy}
            onDownload={download}
            copied={copied}
          />
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Code viewer sub-component
// ---------------------------------------------------------------------------

function CodeViewer({
  code, filename, onCopy, onDownload, copied,
}: {
  code: string;
  filename: string;
  onCopy: () => void;
  onDownload: () => void;
  copied: boolean;
}) {
  const lines = code.split("\n");

  return (
    <div className="rounded-lg overflow-hidden border border-bist-border">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-bist-surface2 border-b border-bist-border">
        <div className="flex items-center gap-2">
          <FileCode className="w-3.5 h-3.5 text-bist-muted" />
          <span className="text-xs font-code text-bist-muted">{filename}</span>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={onDownload} className="btn-ghost text-xs">
            <Download className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Download</span>
          </button>
          <button onClick={onCopy} className="btn-ghost text-xs">
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
                <td
                  className="select-none text-right pr-4 pl-3 py-0 w-10 text-xs align-top pt-0.5 font-code"
                  style={{ color: "#2f5237" }}
                >
                  {i + 1}
                </td>
                <td className="pr-4 py-0 whitespace-pre-wrap break-words font-code text-xs sm:text-sm">
                  <CodeLine text={line} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Minimal syntax colouring that works for all supported languages
function CodeLine({ text }: { text: string }) {
  // Comment lines
  if (/^\s*(#|\/\/|--|;)/.test(text)) {
    return <span style={{ color: "#4a7a5a", fontStyle: "italic" }}>{text}</span>;
  }
  // Block comment / docstring markers
  if (/^\s*(\/\*|\*|\*\/|"""|''')/.test(text)) {
    return <span style={{ color: "#4a7a5a", fontStyle: "italic" }}>{text}</span>;
  }
  // Decorator / annotation lines  (@pytest.fixture, @Test, [Fact], #[test])
  if (/^\s*(@|\[|#\[)/.test(text)) {
    return <span style={{ color: "#a3fb73", opacity: 0.85 }}>{text}</span>;
  }
  // Keywords: def, func, fun, test, it, describe, class, import, etc.
  const keywordRe = /\b(def |func |fun |class |import |from |package |using |namespace |public |private |static |void |async |await |return |assert |expect|describe|it\(|test\(|beforeEach|setUp|setup|fail|raise)\b/;
  if (keywordRe.test(text)) {
    const parts = text.split(/(\"[^\"]*\"|'[^']*')/g);
    return (
      <>
        {parts.map((part, i) =>
          (part.startsWith('"') || part.startsWith("'"))
            ? <span key={i} style={{ color: "#c3e9a8" }}>{part}</span>
            : <span key={i} style={{ color: "#c8e8c8" }}>{part}</span>
        )}
      </>
    );
  }
  // String literals
  if (/["']/.test(text)) {
    const parts = text.split(/(\"[^\"]*\"|'[^']*')/g);
    return (
      <>
        {parts.map((part, i) =>
          (part.startsWith('"') || part.startsWith("'"))
            ? <span key={i} style={{ color: "#c3e9a8" }}>{part}</span>
            : <span key={i} style={{ color: "#c8e8c8" }}>{part}</span>
        )}
      </>
    );
  }
  return <span style={{ color: "#c8e8c8" }}>{text}</span>;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function buildFilename(result: UnitTestResult): string {
  const base = "tests";
  const ext  = result.file_extension;
  // Java/Kotlin already include "Test" in the extension value
  if (ext.startsWith("Test") || ext.startsWith("_test") || ext.startsWith("_spec")) {
    return `Login${ext}`;
  }
  return `${base}${ext}`;
}

// Fallback data used before the catalog API responds
const FALLBACK_LANGUAGES = [
  { id: "python",     label: "Python" },
  { id: "javascript", label: "JavaScript" },
  { id: "typescript", label: "TypeScript" },
  { id: "java",       label: "Java" },
  { id: "csharp",     label: "C#" },
  { id: "go",         label: "Go" },
  { id: "ruby",       label: "Ruby" },
  { id: "kotlin",     label: "Kotlin" },
];

const FALLBACK_FRAMEWORKS: Record<string, { id: string; label: string; hint: string }[]> = {
  python:     [{ id: "pytest",   label: "pytest",   hint: "pip install pytest" },
               { id: "unittest", label: "unittest", hint: "stdlib" }],
  javascript: [{ id: "jest",     label: "Jest",     hint: "npm i -D jest" },
               { id: "vitest",   label: "Vitest",   hint: "npm i -D vitest" },
               { id: "mocha",    label: "Mocha+Chai", hint: "npm i -D mocha chai" }],
  typescript: [{ id: "jest",     label: "Jest",     hint: "npm i -D jest ts-jest" },
               { id: "vitest",   label: "Vitest",   hint: "npm i -D vitest" }],
  java:       [{ id: "junit5",   label: "JUnit 5",  hint: "junit-jupiter:5.x" },
               { id: "testng",   label: "TestNG",   hint: "testng:7.x" }],
  csharp:     [{ id: "nunit",    label: "NUnit",    hint: "dotnet add package NUnit" },
               { id: "xunit",    label: "xUnit",    hint: "dotnet add package xunit" },
               { id: "mstest",   label: "MSTest",   hint: "dotnet add package MSTest.TestFramework" }],
  go:         [{ id: "testing",  label: "testing",  hint: "stdlib" },
               { id: "testify",  label: "Testify",  hint: "go get github.com/stretchr/testify" }],
  ruby:       [{ id: "rspec",    label: "RSpec",    hint: "gem install rspec" },
               { id: "minitest", label: "Minitest", hint: "stdlib" }],
  kotlin:     [{ id: "junit5",   label: "JUnit 5",  hint: "junit-jupiter:5.x" },
               { id: "kotest",   label: "Kotest",   hint: "io.kotest:kotest-runner-junit5:5.x" }],
};
