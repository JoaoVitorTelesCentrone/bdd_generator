import { NextResponse, type NextRequest } from "next/server";
import { resolveCliUser } from "@/lib/cli/auth";
import { getQuota, trackUsage } from "@/lib/cli/quota";

export async function POST(request: NextRequest) {
  const user = await resolveCliUser(request);
  if (!user) {
    return NextResponse.json({ error: "Token inválido ou expirado" }, { status: 401 });
  }

  // Verifica cota antes de chamar o backend Python
  const quota = await getQuota(user.id);
  if (quota.tokens_limit !== -1 && quota.tokens_remaining <= 0) {
    return NextResponse.json(
      {
        error: "quota_exceeded",
        detail: `Cota de tokens esgotada. Reset em ${quota.reset_at.slice(0, 10)}. Faça upgrade para Pro.`,
        quota,
      },
      { status: 402 },
    );
  }

  // Proxy para o FastAPI backend (que tem as LLM keys)
  const body = await request.json();
  const backendUrl = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

  let backendRes: Response;
  try {
    backendRes = await fetch(`${backendUrl}/api/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    return NextResponse.json({ error: "Backend indisponível" }, { status: 503 });
  }

  if (!backendRes.ok) {
    const err = await backendRes.json().catch(() => ({ detail: "Erro no backend" }));
    return NextResponse.json(err, { status: backendRes.status });
  }

  const result = await backendRes.json() as {
    total_tokens: number;
    research_tokens: number;
    [key: string]: unknown;
  };

  // Rastreia o uso de tokens no Supabase (fire-and-forget)
  const tokensUsed = (result.total_tokens ?? 0) + (result.research_tokens ?? 0);
  trackUsage(user.id, tokensUsed).catch(console.error);

  return NextResponse.json(result);
}
