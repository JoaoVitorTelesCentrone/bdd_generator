"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Play, FileCode, Loader2, AlertCircle, ToggleLeft, ToggleRight } from "lucide-react";
import { bistTriggerRun, bistExecuteRun } from "@/lib/api";

type Mode = "generate" | "execute";

export function RunPanel() {
  const router = useRouter();
  const [mode, setMode]           = useState<Mode>("generate");
  const [userStory, setUserStory] = useState("");
  const [featurePath, setFeaturePath] = useState("");
  const [envUrl, setEnvUrl]       = useState("");
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
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
    (mode === "generate" ? userStory.trim() : featurePath.trim()) &&
    !loading;

  return (
    <form onSubmit={handleSubmit} className="card-terminal p-5 space-y-4">
      <div className="flex items-center gap-2 text-xs font-mono text-[#5a7a65] border-b border-[#a3fb73]/10 pb-3">
        <span className="text-[#a3fb73]">$</span>
        <span>bist {mode === "generate" ? "full" : "execute"}</span>
      </div>

      {/* Mode toggle */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={() => setMode(mode === "generate" ? "execute" : "generate")}
          className="flex items-center gap-2 text-xs font-mono text-[#7a9b87] hover:text-[#a3fb73] transition-colors"
        >
          {mode === "generate"
            ? <ToggleLeft className="w-4 h-4" />
            : <ToggleRight className="w-4 h-4 text-[#a3fb73]" />}
          {mode === "generate" ? "gerar + executar" : "só executar (.feature)"}
        </button>
      </div>

      {/* Dynamic input */}
      {mode === "generate" ? (
        <div className="space-y-1.5">
          <label className="text-xs font-mono text-[#5a7a65]">user story</label>
          <textarea
            value={userStory}
            onChange={e => setUserStory(e.target.value)}
            rows={4}
            placeholder="Como usuário, quero fazer login..."
            className="w-full bg-[#0d1f14] border border-[#a3fb73]/15 rounded px-3 py-2 text-sm font-mono text-[#c8e8c8] placeholder:text-[#3d5a44] focus:outline-none focus:border-[#a3fb73]/40 resize-none"
          />
        </div>
      ) : (
        <div className="space-y-1.5">
          <label className="text-xs font-mono text-[#5a7a65] flex items-center gap-1.5">
            <FileCode className="w-3 h-3" /> caminho do .feature
          </label>
          <input
            type="text"
            value={featurePath}
            onChange={e => setFeaturePath(e.target.value)}
            placeholder="tests/login.feature"
            className="w-full bg-[#0d1f14] border border-[#a3fb73]/15 rounded px-3 py-2 text-sm font-mono text-[#c8e8c8] placeholder:text-[#3d5a44] focus:outline-none focus:border-[#a3fb73]/40"
          />
        </div>
      )}

      {/* Env URL */}
      <div className="space-y-1.5">
        <label className="text-xs font-mono text-[#5a7a65]">ambiente (url)</label>
        <input
          type="url"
          value={envUrl}
          onChange={e => setEnvUrl(e.target.value)}
          placeholder="https://staging.myapp.com"
          className="w-full bg-[#0d1f14] border border-[#a3fb73]/15 rounded px-3 py-2 text-sm font-mono text-[#c8e8c8] placeholder:text-[#3d5a44] focus:outline-none focus:border-[#a3fb73]/40"
        />
      </div>

      {error && (
        <div className="flex items-start gap-2 text-xs font-mono text-red-400 bg-red-400/8 border border-red-400/20 rounded px-3 py-2">
          <AlertCircle className="w-3.5 h-3.5 mt-0.5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <button
        type="submit"
        disabled={!canSubmit}
        className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {loading
          ? <><Loader2 className="w-4 h-4 animate-spin" /> iniciando...</>
          : <><Play className="w-4 h-4" /> executar</>}
      </button>
    </form>
  );
}
