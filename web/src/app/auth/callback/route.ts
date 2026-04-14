import { createClient } from "@/lib/supabase/server";
import { NextResponse, type NextRequest } from "next/server";

export async function GET(request: NextRequest) {
  const { searchParams, origin } = new URL(request.url);
  const code  = searchParams.get("code");
  const next  = searchParams.get("next") ?? "/";
  const error = searchParams.get("error");

  // Erro retornado pelo provider OAuth
  if (error) {
    console.error("[auth/callback] OAuth error:", error, searchParams.get("error_description"));
    return NextResponse.redirect(`${origin}/login?error=${encodeURIComponent(error)}`);
  }

  if (code) {
    const supabase = await createClient();
    const { error: exchangeError } = await supabase.auth.exchangeCodeForSession(code);

    if (!exchangeError) {
      // Garante que o redirect é para o mesmo origin (evita open redirect)
      const redirectTo = next.startsWith("/") ? `${origin}${next}` : origin;
      return NextResponse.redirect(redirectTo);
    }

    console.error("[auth/callback] Exchange error:", exchangeError.message);
  }

  return NextResponse.redirect(`${origin}/login?error=auth_callback_failed`);
}
