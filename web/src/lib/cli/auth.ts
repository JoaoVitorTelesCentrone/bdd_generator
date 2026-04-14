/**
 * Resolve o usuário a partir do Bearer token enviado pelo CLI.
 * O token é o API token gerado no dashboard (tabela api_keys).
 */
import { type NextRequest } from "next/server";
import { createAdminClient } from "@/lib/supabase/server";
import type { User } from "@supabase/supabase-js";

export async function resolveCliUser(request: NextRequest): Promise<User | null> {
  const authHeader = request.headers.get("authorization");
  if (!authHeader?.startsWith("Bearer ")) return null;

  const token = authHeader.slice(7);
  if (!token) return null;

  // Admin client usa service_role — necessário para auth.admin.* e para
  // ler api_keys sem depender de auth.uid() (a requisição é Bearer, não cookie)
  const supabase = createAdminClient();

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const { data: apiKey } = await (supabase as any)
    .from("api_keys")
    .select("user_id, expires_at, revoked")
    .eq("token", token)
    .single();

  if (!apiKey || apiKey.revoked) return null;
  if (apiKey.expires_at && new Date(apiKey.expires_at) < new Date()) return null;

  // Busca o usuário pelo user_id do token
  const { data: { user }, error } = await supabase.auth.admin.getUserById(apiKey.user_id);
  if (error || !user) return null;

  return user;
}
