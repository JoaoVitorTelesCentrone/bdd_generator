/**
 * Gerenciamento de cota de tokens por usuário.
 *
 * Limites:
 *   free → 50.000 tokens/mês
 *   pro  → ilimitado (-1)
 */
import { createAdminClient } from "@/lib/supabase/server";

const FREE_LIMIT = 50_000;  // tokens por mês

export interface QuotaInfo {
  plan:              string;
  tokens_used:       number;
  tokens_limit:      number;   // -1 = ilimitado
  tokens_remaining:  number;   // -1 = ilimitado
  generations_used:  number;
  reset_at:          string;   // ISO — primeiro dia do próximo mês
}

function nextMonthReset(): string {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth() + 1, 1).toISOString();
}

function currentMonthStart(): string {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth(), 1).toISOString();
}

export async function getQuota(userId: string): Promise<QuotaInfo> {
  const supabase = createAdminClient();

  // Plano do usuário
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const { data: sub } = await (supabase as any)
    .from("subscriptions")
    .select("plan_id")
    .eq("user_id", userId)
    .single();

  const plan = (sub?.plan_id as string) ?? "free";

  // Uso do mês atual
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const { data: usage } = await (supabase as any)
    .from("cli_usage")
    .select("tokens_used")
    .eq("user_id", userId)
    .gte("created_at", currentMonthStart());

  const tokensUsed      = (usage as { tokens_used: number }[] | null)
    ?.reduce((sum, r) => sum + r.tokens_used, 0) ?? 0;
  const generationsUsed = (usage as unknown[] | null)?.length ?? 0;

  if (plan === "pro") {
    return {
      plan,
      tokens_used:      tokensUsed,
      tokens_limit:     -1,
      tokens_remaining: -1,
      generations_used: generationsUsed,
      reset_at:         nextMonthReset(),
    };
  }

  const limit     = FREE_LIMIT;
  const remaining = Math.max(0, limit - tokensUsed);

  return {
    plan,
    tokens_used:      tokensUsed,
    tokens_limit:     limit,
    tokens_remaining: remaining,
    generations_used: generationsUsed,
    reset_at:         nextMonthReset(),
  };
}

export async function trackUsage(userId: string, tokensUsed: number): Promise<void> {
  if (tokensUsed <= 0) return;
  const supabase = createAdminClient();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  await (supabase as any)
    .from("cli_usage")
    .insert({ user_id: userId, tokens_used: tokensUsed });
}
