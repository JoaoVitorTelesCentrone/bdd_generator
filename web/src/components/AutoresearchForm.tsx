"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  FlaskConical, Upload, Loader2, AlertCircle, Info, ChevronDown, ChevronUp,
} from "lucide-react";
import { startAutoresearch } from "@/lib/api";

const MODELS = [
  { id: "flash",      label: "Gemini 2.5 Flash",     provider: "gemini" },
  { id: "pro",        label: "Gemini 2.5 Pro",        provider: "gemini" },
  { id: "flash-lite", label: "Gemini 2.0 Flash Lite", provider: "gemini" },
  { id: "sonnet",     label: "Claude Sonnet 4.6",     provider: "claude" },
  { id: "opus",       label: "Claude Opus 4.6",       provider: "claude" },
  { id: "haiku",      label: "Claude Haiku 4.5",      provider: "claude" },
];

const EXAMPLE_STORIES = [
  "Como usuário, quero fazer login com email e senha para acessar minha conta.",
  "Como cliente, quero adicionar produtos ao carrinho para comprá-los depois.",
  "Como gestor, quero aprovar solicitações de férias para controlar ausências.",
  "Como administrador, quero gerenciar usuários do sistema para manter o acesso controlado.",
  "Como cliente, quero rastrear meu pedido em tempo real para saber quando ele chega.",
  "Como usuário, quero redefinir minha senha por email para recuperar acesso à conta.",
  "Como vendedor, quero visualizar relatórios de vendas mensais para acompanhar metas.",
  "Como usuário, quero filtrar produtos por categoria para encontrar o que preciso mais rápido.",
  "Como gerente, quero exportar dados para CSV para analisar em outras ferramentas.",
  "Como cliente, quero avaliar produtos comprados para ajudar outros compradores.",
];

function Tooltip({ text }: { text: string }) {
  return (
    <span className="relative group cursor-help">
      <Info className="w-3 h-3 text-bist-dim" />
      <span className="absolute left-full ml-2 top-1/2 -translate-y-1/2 z-10 hidden group-hover:block
                       bg-bist-primary text-white text-xs rounded-lg p-2.5 w-52 shadow-lg leading-relaxed">
        {text}
      </span>
    </span>
  );
}

export function AutoresearchForm() {
  const router = useRouter();
  const fileRef = useRef<HTMLInputElement>(null);

  const [storiesText, setStoriesText]     = useState(EXAMPLE_STORIES.join("\n"));
  const [model, setModel]                 = useState("flash");
  const [nExperiments, setNExperiments]   = useState(30);
  const [sampleSize, setSampleSize]       = useState(10);
  const [seed, setSeed]                   = useState("");
  const [showAdvanced, setShowAdvanced]   = useState(false);
  const [loading, setLoading]             = useState(false);
  const [error, setError]                 = useState("");

  const stories = storiesText
    .split("\n")
    .map(s => s.trim())
    .filter(Boolean);

  const effectiveSample = Math.min(sampleSize, stories.length);
  const estimatedCalls  = (nExperiments + 1) * effectiveSample;

  function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const text = ev.target?.result as string;
      const lines = text.split("\n").slice(1); // skip CSV header
      const extracted = lines
        .map(line => {
          const cols = line.split(",");
          const title = cols[0]?.replace(/^"|"$/g, "").trim();
          const desc  = cols[1]?.replace(/^"|"$/g, "").trim();
          return desc ? `${title}. ${desc}` : title;
        })
        .filter(Boolean);
      setStoriesText(extracted.join("\n"));
    };
    reader.readAsText(file);
    e.target.value = "";
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (stories.length === 0) {
      setError("Insira ao menos uma user story.");
      return;
    }
    setError(""); setLoading(true);
    try {
      const { run_id } = await startAutoresearch({
        stories,
        model,
        n_experiments: nExperiments,
        sample_size: sampleSize,
        seed: seed ? parseInt(seed) : null,
      });
      router.push(`/autoresearch/${run_id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erro desconhecido");
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl mx-auto space-y-5">

      {/* Stories */}
      <div className="card p-5 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-bist-primary">User Stories</label>
            <Tooltip text="Uma story por linha. Quanto mais stories, mais representativo o benchmark." />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-code text-bist-dim">{stories.length} stories</span>
            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              className="btn-ghost text-xs gap-1"
            >
              <Upload className="w-3 h-3" /> CSV
            </button>
            <input
              ref={fileRef}
              type="file"
              accept=".csv"
              className="hidden"
              onChange={handleFileUpload}
            />
          </div>
        </div>
        <textarea
          className="textarea h-52 text-sm leading-relaxed font-code"
          placeholder={"Como usuário, quero...\nComo cliente, quero...\n..."}
          value={storiesText}
          onChange={e => setStoriesText(e.target.value)}
        />
        <p className="text-[10px] text-bist-dim">
          Uma story por linha · CSV deve ter colunas <code className="font-code">title, description</code>
        </p>
      </div>

      {/* Modelo */}
      <div className="card p-5 space-y-3">
        <label className="text-sm font-medium text-bist-primary">Modelo</label>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {MODELS.map(m => (
            <button
              key={m.id}
              type="button"
              onClick={() => setModel(m.id)}
              className={[
                "px-3 py-2.5 rounded-lg border text-xs text-left transition-colors",
                model === m.id
                  ? "border-[#a3fb73] bg-[#a3fb73]/10 text-bist-primary font-medium"
                  : "border-bist-border text-bist-muted hover:border-bist-muted",
              ].join(" ")}
            >
              <span className={`text-[10px] font-code block mb-0.5 ${m.provider === "claude" ? "text-violet-500" : "text-blue-500"}`}>
                {m.provider}
              </span>
              {m.label}
            </button>
          ))}
        </div>
      </div>

      {/* Experimentos */}
      <div className="card p-5 space-y-5">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-sm text-bist-mid flex items-center gap-1.5">
              Experimentos
              <Tooltip text="Número de mutações a testar. Mais experimentos = mais chances de encontrar uma config melhor, mas maior custo de API." />
            </label>
            <span className="text-sm font-code font-semibold text-bist-primary tabular-nums">{nExperiments}</span>
          </div>
          <input
            type="range" min={5} max={100} step={5} value={nExperiments}
            onChange={e => setNExperiments(parseInt(e.target.value))}
            className="w-full accent-[#a3fb73] cursor-pointer"
          />
          <div className="flex justify-between text-[10px] font-code text-bist-dim">
            <span>5 — rápido</span><span>100 — completo</span>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-sm text-bist-mid flex items-center gap-1.5">
              Stories por experimento
              <Tooltip text="Orçamento fixo: cada mutação é avaliada neste número de stories. Mais stories = avaliação mais confiável, mas maior custo." />
            </label>
            <span className="text-sm font-code font-semibold text-bist-primary tabular-nums">
              {effectiveSample}
              {stories.length < sampleSize && (
                <span className="text-[10px] text-amber-500 ml-1">(máx disponível)</span>
              )}
            </span>
          </div>
          <input
            type="range" min={3} max={30} step={1} value={sampleSize}
            onChange={e => setSampleSize(parseInt(e.target.value))}
            className="w-full accent-[#a3fb73] cursor-pointer"
          />
          <div className="flex justify-between text-[10px] font-code text-bist-dim">
            <span>3 — econômico</span><span>30 — preciso</span>
          </div>
        </div>

        <div className="flex items-center justify-between p-3 rounded-lg bg-bist-surface2 border border-bist-border text-xs text-bist-muted">
          <span>Chamadas LLM estimadas</span>
          <span className="font-code font-semibold text-bist-primary tabular-nums">
            ~{estimatedCalls.toLocaleString("pt-BR")}
          </span>
        </div>
      </div>

      {/* Avançado */}
      <div className="card">
        <button
          type="button"
          className="w-full flex items-center justify-between px-5 py-3.5 text-sm text-bist-muted hover:text-bist-primary transition-colors"
          onClick={() => setShowAdvanced(p => !p)}
        >
          <span className="font-medium">Avançado</span>
          {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        {showAdvanced && (
          <div className="px-5 pb-5 border-t border-bist-border pt-4 space-y-3">
            <div className="space-y-1.5">
              <label className="text-sm text-bist-mid flex items-center gap-1.5">
                Semente aleatória (seed)
                <Tooltip text="Garante reprodutibilidade: mesma seed = mesma sequência de mutações e mesmo sample de stories." />
              </label>
              <input
                type="number"
                value={seed}
                onChange={e => setSeed(e.target.value)}
                placeholder="deixe vazio para aleatório"
                className="input text-sm w-48"
              />
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="card p-3 border-red-200 bg-red-50 flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
          <p className="text-xs text-red-600">{error}</p>
        </div>
      )}

      <button
        type="submit"
        disabled={loading || stories.length === 0}
        className="btn-primary w-full py-3 text-sm"
      >
        {loading
          ? <><Loader2 className="w-4 h-4 animate-spin" /> Iniciando...</>
          : <><FlaskConical className="w-4 h-4" /> Iniciar Autoresearch</>
        }
      </button>
    </form>
  );
}
