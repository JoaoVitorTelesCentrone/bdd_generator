"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Play, FileCode, Loader2, AlertCircle, ToggleLeft, ToggleRight } from "lucide-react";
import { bistTriggerRun, bistExecuteRun } from "@/lib/api";

type Mode = "generate" | "execute";

export function RunPanel({ initialStory }: { initialStory?: string } = {}) {
  const router = useRouter();
  const [mode, setMode]             = useState<Mode>("generate");
  const [userStory, setUserStory]   = useState(initialStory ?? "");
  const [featurePath, setFeaturePath] = useState("");
  const [envUrl, setEnvUrl]         = useState("");
  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault(); setError(""); setLoading(true);
    try {
      let result: { run_id: number };
      if (mode === "generate") {
        result = await bistTriggerRun({ user_story: userStory, env_url: envUrl });
      } else {
        result = await bistExecuteRun({ feature_path: featurePath, env_url: envUrl });
      }
      router.push(`/runs/${result.run_id}`);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const canSubmit = envUrl.trim() &&
    (mode === "generate" ? userStory.trim() : featurePath.trim()) && !loading;

  return (
    <form onSubmit={handleSubmit} className="card p-5 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-bist-border">
        <h3 className="text-sm font-semibold text-bist-primary">Executar testes E2E</h3>
        <button
          type="button"
          onClick={() => setMode(mode === "generate" ? "execute" : "generate")}
          className="flex items-center gap-2 text-xs text-bist-muted hover:text-bist-primary transition-colors"
        >
          {mode === "generate"
            ? <ToggleLeft className="w-4 h-4" />
            : <ToggleRight className="w-4 h-4 text-[#2D6A3F]" />}
          {mode === "generate" ? "Gerar + executar" : "Só executar (.feature)"}
        </button>
      </div>

      {mode === "generate" ? (
        <div className="space-y-1.5">
          <label className="text-sm font-medium text-bist-primary">User story</label>
          <textarea
            value={userStory}
            onChange={e => setUserStory(e.target.value)}
            rows={4}
            placeholder="Como usuário, quero fazer login..."
            className="textarea text-sm"
          />
        </div>
      ) : (
        <div className="space-y-1.5">
          <label className="text-sm font-medium text-bist-primary flex items-center gap-1.5">
            <FileCode className="w-3.5 h-3.5" /> Caminho do .feature
          </label>
          <input
            type="text"
            value={featurePath}
            onChange={e => setFeaturePath(e.target.value)}
            placeholder="tests/login.feature"
            className="input text-sm"
          />
        </div>
      )}

      <div className="space-y-1.5">
        <label className="text-sm font-medium text-bist-primary">URL do ambiente</label>
        <input
          type="url"
          value={envUrl}
          onChange={e => setEnvUrl(e.target.value)}
          placeholder="https://staging.myapp.com"
          className="input text-sm"
        />
      </div>

      {error && (
        <div className="flex items-start gap-2 text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
          <AlertCircle className="w-3.5 h-3.5 mt-0.5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <button type="submit" disabled={!canSubmit} className="btn-primary w-full">
        {loading
          ? <><Loader2 className="w-4 h-4 animate-spin" /> Iniciando...</>
          : <><Play className="w-4 h-4" /> Executar testes</>}
      </button>
    </form>
  );
}
