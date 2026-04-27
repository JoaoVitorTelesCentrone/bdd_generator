import { createAdminClient } from "@/lib/supabase/server";

const FREE_LIMIT = 50_000;

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

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const { data: sub } = await (supabase as any)
    .from("subscriptions")
    .select("plan_id")
    .eq("user_id", userId)
    .single();

  const plan = (sub?.plan_id as string) ?? "free";

  // Uso do mês atual — lê da tabela generations (a web já salva lá)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const { data: rows } = await (supabase as any)
    .from("generations")
    .select("total_tokens")
    .eq("user_id", userId)
    .gte("created_at", currentMonthStart());

  const tokensUsed      = (rows as { total_tokens: number }[] | null)
    ?.reduce((sum, r) => sum + (r.total_tokens ?? 0), 0) ?? 0;
  const generationsUsed = (rows as unknown[] | null)?.length ?? 0;

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

  const remaining = Math.max(0, FREE_LIMIT - tokensUsed);

  return {
    plan,
    tokens_used:      tokensUsed,
    tokens_limit:     FREE_LIMIT,
    tokens_remaining: remaining,
    generations_used: generationsUsed,
    reset_at:         nextMonthReset(),
  };
}
