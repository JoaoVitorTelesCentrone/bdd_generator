import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { getQuota } from "@/lib/quota";

export async function GET() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Não autenticado" }, { status: 401 });
  const quota = await getQuota(user.id);
  return NextResponse.json(quota);
}
