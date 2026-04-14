"use client";

import { createClient } from "./client";
import type { Generation } from "./types";
import type { GenerateResult } from "@/types";

export async function saveGeneration(
  userId: string,
  story: string,
  model: string,
  result: GenerateResult,
  options: { research: boolean; threshold: number },
): Promise<Generation | null> {
  const supabase = createClient();

  const row = {
    user_id:          userId,
    story:            story.slice(0, 2000),
    model,
    bdd_text:         result.bdd_text,
    score_final:      result.score.score_final,
    cobertura:        result.score.cobertura,
    clareza:          result.score.clareza,
    estrutura:        result.score.estrutura,
    executabilidade:  result.score.executabilidade,
    aprovado:         result.score.aprovado,
    attempts:         result.attempts,
    total_tokens:     result.total_tokens,
    research_tokens:  result.research_tokens,
    duration_seconds: result.duration_seconds,
    converged:        result.converged,
    research_enabled: options.research,
    threshold:        options.threshold,
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const { data, error } = await (supabase as any)
    .from("generations")
    .insert(row)
    .select()
    .single();

  if (error) {
    console.error("[saveGeneration]", error.message);
    return null;
  }
  return data;
}

export async function fetchHistory(limit = 20): Promise<Generation[]> {
  const supabase = createClient();

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const { data, error } = await (supabase as any)
    .from("generations")
    .select("*")
    .order("created_at", { ascending: false })
    .limit(limit);

  if (error) {
    console.error("[fetchHistory]", error.message);
    return [];
  }
  return data ?? [];
}
