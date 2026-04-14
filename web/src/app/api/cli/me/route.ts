import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { resolveCliUser } from "@/lib/cli/auth";

export async function GET(request: NextRequest) {
  const user = await resolveCliUser(request);
  if (!user) {
    return NextResponse.json({ error: "Token inválido ou expirado" }, { status: 401 });
  }

  const supabase = await createClient();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const { data: sub } = await (supabase as any)
    .from("subscriptions")
    .select("plan_id")
    .eq("user_id", user.id)
    .single();

  return NextResponse.json({
    id:    user.id,
    email: user.email,
    name:  user.user_metadata?.full_name ?? user.email,
    plan:  sub?.plan_id ?? "free",
  });
}
