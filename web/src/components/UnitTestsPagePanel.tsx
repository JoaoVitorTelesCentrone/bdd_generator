"use client";

import { useState, useEffect } from "react";
import {
  TestTube2, Loader2, AlertCircle, Copy, Check,
  Download, ChevronDown, Sparkles, FileCode, BookOpen, Info,
} from "lucide-react";
import { fetchUnitTestLanguages, generateUnitTests } from "@/lib/api";
import type { UnitTestLanguageCatalog, UnitTestResult } from "@/types";

const DEFAULT_MODEL = "flash";

const EXAMPLE_BDDS = [
  `Feature: Login de usuário
  Como usuário registrado
  Quero fazer login com email e senha
  Para acessar minha conta

  Background:
    Given o sistema de autenticação está disponível

  Scenario: Login com credenciais válidas
    Given o usuário acessa a página de login
    When preenche o email "user@example.com" e a senha "Senha@123"
    And clica no botão "Entrar"
    Then é redirecionado para o dashboard
    And vê a mensagem "Bem-vindo de volta"

  Scenario: Login com senha incorreta
    Given o usuário acessa a página de login
    When preenche o email "user@example.com" e a senha "senhaErrada"
    Then vê a mensagem de erro "Credenciais inválidas"
    And permanece na página de login

  Scenario: Bloqueio após 3 tentativas
    Given o usuário falhou nas últimas 2 tentativas de login
    When tenta fazer login com a senha "senhaErrada" novamente
    Then vê a mensagem "Conta bloqueada por 15 minutos"`,

  `Feature: Carrinho de compras
  Como cliente
  Quero adicionar produtos ao carrinho
  Para comprá-los em seguida

  Scenario: Adicionar produto disponível
    Given o cliente está na página do produto "Notebook Pro"
    When clica no botão "Adicionar ao carrinho"
    Then o produto aparece no carrinho com quantidade 1
    And o total do carrinho é atualizado

  Scenario: Não permite produto sem estoque
    Given o produto "Fone Bluetooth" está sem estoque
    When o cliente acessa a página do produto
    Then o botão "Adicionar ao carrinho" está desabilitado
    And vê a mensagem "Produto indisponível"`,
];

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
  python:     [{ id: "pytest",   label: "pytest",     hint: "pip install pytest" },
               { id: "unittest", label: "unittest",   hint: "stdlib — sem instalação" }],
  javascript: [{ id: "jest",     label: "Jest",       hint: "npm install --save-dev jest" },
               { id: "vitest",   label: "Vitest",     hint: "npm install --save-dev vitest" },
               { id: "mocha",    label: "Mocha+Chai", hint: "npm install --save-dev mocha chai" }],
  typescript: [{ id: "jest",     label: "Jest+ts-jest", hint: "npm install --save-dev jest ts-jest @types/jest" },
               { id: "vitest",   label: "Vitest",       hint: "npm install --save-dev vitest" }],
  java:       [{ id: "junit5",   label: "JUnit 5",    hint: "org.junit.jupiter:junit-jupiter:5.x" },
               { id: "testng",   label: "TestNG",     hint: "org.testng:testng:7.x" }],
  csharp:     [{ id: "nunit",    label: "NUnit",      hint: "dotnet add package NUnit" },
               { id: "xunit",    label: "xUnit",      hint: "dotnet add package xunit" },
               { id: "mstest",   label: "MSTest",     hint: "dotnet add package MSTest.TestFramework" }],
  go:         [{ id: "testing",  label: "testing",    hint: "stdlib — sem instalação" },
               { id: "testify",  label: "Testify",    hint: "go get github.com/stretchr/testify" }],
  ruby:       [{ id: "rspec",    label: "RSpec",      hint: "gem install rspec" },
               { id: "minitest", label: "Minitest",   hint: "stdlib — sem instalação" }],
  kotlin:     [{ id: "junit5",   label: "JUnit 5",    hint: "org.junit.jupiter:junit-jupiter:5.x" },
               { id: "kotest",   label: "Kotest",     hint: "io.kotest:kotest-runner-junit5:5.x" }],
};

export function UnitTestsPagePanel() {
  const [catalog, setCatalog]     = useState<UnitTestLanguageCatalog | null>(null);
  const [bddText, setBddText]     = useState("");
  const [language, setLanguage]   = useState("python");
  const [framework, setFramework] = useState("pytest");
  const [loading, setLoading]     = useState(false);
  const [result, setResult]       = useState<UnitTestResult | null>(null);
  const [error, setError]         = useState<string | null>(null);
  const [copied, setCopied]       = useState(false);

  useEffect(() => {
    fetchUnitTestLanguages()
      .then(data => {
        setCatalog(data);
        const defaultFw = data[language]?.default_framework;
        if (defaultFw) setFramework(defaultFw);
      })
      .catch(() => {});
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  function handleLanguageChange(lang: string) {
    setLanguage(lang);
    setResult(null);
    setError(null);
    const defaultFw = catalog?.[lang]?.default_framework
      ?? FALLBACK_FRAMEWORKS[lang]?.[0]?.id
      ?? "";
    setFramework(defaultFw);
  }

  function loadExample() {
    setBddText(EXAMPLE_BDDS[Math.floor(Math.random() * EXAMPLE_BDDS.length)]);
    setResult(null);
    setError(null);
  }

  async function handleGenerate() {
    if (!bddText.trim()) return;
    setLoading(true); setError(null); setResult(null);
    try {
      const res = await generateUnitTests({
        bdd_text: bddText.trim(),
        language,
        framework,
        model: DEFAULT_MODEL,
      });
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
  const langLabel = catalog?.[language]?.label ?? language;

  return (
    <div className="grid grid-cols-1 xl:grid-cols-[460px_1fr] gap-6 h-full">

      {/* ── Left: form ─────────────────────────────────────────────────────── */}
      <div className="space-y-4">

        {/* BDD Input */}
        <div className="card p-5 space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-bist-primary">Cenários BDD (Gherkin)</label>
            <button onClick={loadExample} className="btn-ghost text-xs gap-1">
              <BookOpen className="w-3.5 h-3.5" />
              Exemplo
            </button>
          </div>
          <textarea
            className="textarea h-52 leading-relaxed text-sm font-code"
            placeholder={"Feature: Nome da funcionalidade\n\n  Scenario: Cenário de exemplo\n    Given o contexto inicial\n    When o usuário executa uma ação\n    Then o resultado esperado aparece"}
            value={bddText}
            onChange={e => { setBddText(e.target.value); setResult(null); setError(null); }}
          />
          <p className="text-[10px] text-bist-dim font-code">{bddText.length} caracteres</p>
        </div>

        {/* Language + Framework */}
        <div className="card p-5 space-y-4">
          <h3 className="text-sm font-medium text-bist-primary">Linguagem & framework</h3>

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
                    ? Object.values(catalog).map(l => (
                        <option key={l.id} value={l.id}>{l.label}</option>
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
                  onChange={e => setFramework(e.target.value)}
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

          {currentHint && (
            <div className="flex items-center gap-2 text-[10px] font-code text-bist-dim bg-bist-surface2 rounded px-2.5 py-1.5 border border-bist-border2">
              <Info className="w-3 h-3 text-bist-dim shrink-0" />
              <span><span className="text-bist-muted">instalação:</span> {currentHint}</span>
            </div>
          )}
        </div>

        {/* Generate button */}
        <button
          className="btn-primary w-full text-sm py-3"
          disabled={loading || !bddText.trim()}
          onClick={handleGenerate}
        >
          {loading
            ? <><Loader2 className="w-4 h-4 animate-spin" /> Gerando testes em {langLabel}...</>
            : <><Sparkles className="w-4 h-4" /> Gerar testes em {langLabel}</>
          }
        </button>

        {loading && (
          <div className="card p-4 space-y-2">
            <div className="flex items-center gap-2 text-sm text-bist-muted">
              <Loader2 className="w-3.5 h-3.5 animate-spin text-[#a3fb73]" />
              <span>Convertendo cenários BDD em testes {langLabel}...</span>
            </div>
            <div className="h-1 bg-bist-border rounded-full overflow-hidden">
              <div className="h-full bg-[#a3fb73] animate-progress rounded-full" />
            </div>
            <p className="text-xs text-bist-dim font-code">
              framework: <span className="text-bist-muted">{framework}</span>
            </p>
          </div>
        )}
      </div>

      {/* ── Right: result ───────────────────────────────────────────────────── */}
      <div className="space-y-4 min-h-[300px]">
        {!result && !error && !loading && <EmptyState />}

        {error && (
          <div className="card p-4 border-red-200 bg-red-50 flex items-start gap-3">
            <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-red-600">Erro na geração</p>
              <p className="text-xs text-red-500 mt-1">{error}</p>
              <p className="text-xs text-bist-dim mt-2">
                Verifique se o backend está rodando:{" "}
                <code className="font-code bg-bist-surface2 px-1 rounded">uvicorn backend.main:app --reload</code>
              </p>
            </div>
          </div>
        )}

        {result && (
          <div className="space-y-4 animate-slide-up">

            {/* Metadata */}
            <div className="card p-4">
              <div className="flex items-center justify-between flex-wrap gap-3">
                <div className="flex items-center gap-3 flex-wrap">
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#a3fb73]/15 border border-[#a3fb73]/30 text-xs font-medium text-[#2D6A3F]">
                    <TestTube2 className="w-3 h-3" />
                    {result.num_tests} {result.num_tests === 1 ? "teste gerado" : "testes gerados"}
                  </span>
                  <span className="text-xs font-code text-bist-dim">
                    {result.language} · {result.framework}
                  </span>
                  <span className="text-xs font-code text-bist-dim">
                    {result.total_tokens.toLocaleString()} tokens · {result.duration_seconds}s
                  </span>
                </div>
                <span className="text-xs font-code text-bist-muted">{buildFilename(result)}</span>
              </div>
            </div>

            {/* Code block */}
            <div className="rounded-lg overflow-hidden border border-bist-border">
              {/* Toolbar */}
              <div className="flex items-center justify-between px-4 py-2.5 bg-bist-surface2 border-b border-bist-border">
                <div className="flex items-center gap-2">
                  <FileCode className="w-3.5 h-3.5 text-bist-muted" />
                  <span className="text-xs font-code text-bist-muted">{buildFilename(result)}</span>
                </div>
                <div className="flex items-center gap-1">
                  <button onClick={download} className="btn-ghost text-xs">
                    <Download className="w-3.5 h-3.5" />
                    <span className="hidden sm:inline">Download</span>
                  </button>
                  <button onClick={copy} className="btn-ghost text-xs">
                    {copied
                      ? <><Check className="w-3.5 h-3.5 text-[#2D6A3F]" /><span className="hidden sm:inline">Copiado</span></>
                      : <><Copy className="w-3.5 h-3.5" /><span className="hidden sm:inline">Copiar</span></>
                    }
                  </button>
                </div>
              </div>

              {/* Code */}
              <div className="overflow-auto bg-[#1a2c21] max-h-[600px]">
                <table className="w-full border-collapse leading-relaxed text-sm">
                  <tbody>
                    {result.code.split("\n").map((line, i) => (
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

          </div>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Code line colouring
// ---------------------------------------------------------------------------

function CodeLine({ text }: { text: string }) {
  if (/^\s*(#|\/\/|--|;)/.test(text))
    return <span style={{ color: "#4a7a5a", fontStyle: "italic" }}>{text}</span>;

  if (/^\s*(\/\*|\*(?!\/)|"""|''')/.test(text))
    return <span style={{ color: "#4a7a5a", fontStyle: "italic" }}>{text}</span>;

  if (/^\s*(@|\[|#\[)/.test(text))
    return <span style={{ color: "#a3fb73", opacity: 0.85 }}>{text}</span>;

  if (/["']/.test(text)) {
    const parts = text.split(/(\"[^\"]*\"|'[^']*')/g);
    return (
      <>
        {parts.map((part, i) =>
          part.startsWith('"') || part.startsWith("'")
            ? <span key={i} style={{ color: "#c3e9a8" }}>{part}</span>
            : <span key={i} style={{ color: "#c8e8c8" }}>{part}</span>
        )}
      </>
    );
  }

  return <span style={{ color: "#c8e8c8" }}>{text}</span>;
}

// ---------------------------------------------------------------------------
// Empty state
// ---------------------------------------------------------------------------

function EmptyState() {
  return (
    <div className="card p-10 flex flex-col items-center justify-center text-center gap-6 border-dashed min-h-[420px]">
      <div className="w-12 h-12 rounded-xl bg-bist-surface2 border border-bist-border flex items-center justify-center">
        <TestTube2 className="w-5 h-5 text-bist-muted" />
      </div>

      <div>
        <p className="text-sm font-medium text-bist-primary">Pronto para gerar</p>
        <p className="text-xs text-bist-dim mt-1 max-w-xs leading-relaxed">
          Cole seus cenários Gherkin à esquerda, escolha a linguagem e clique em{" "}
          <span className="text-bist-primary font-medium">Gerar testes</span>
        </p>
      </div>

      <div className="grid grid-cols-2 gap-2 w-full max-w-xs text-left">
        {[
          ["Scenario → test_*()",    "1 cenário por teste"],
          ["Background → setUp()",   "configuração automática"],
          ["Given/When/Then",        "comentários inline"],
          ["Outline → casos N",      "tabela expandida"],
        ].map(([k, v]) => (
          <div key={k} className="card-subtle px-3 py-2">
            <p className="text-xs font-medium text-bist-mid font-code">{k}</p>
            <p className="text-[10px] text-bist-dim mt-0.5">{v}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function buildFilename(result: UnitTestResult): string {
  const ext = result.file_extension;
  if (ext.startsWith("Test") || ext.startsWith("_test") || ext.startsWith("_spec")) {
    return `Login${ext}`;
  }
  return `tests${ext}`;
}
