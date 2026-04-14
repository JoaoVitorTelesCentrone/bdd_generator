import { NextResponse, type NextRequest } from "next/server";
import { resolveCliUser } from "@/lib/cli/auth";
import { getQuota } from "@/lib/cli/quota";

export async function GET(request: NextRequest) {
  const user = await resolveCliUser(request);
  if (!user) {
    return NextResponse.json({ error: "Token inválido" }, { status: 401 });
  }

  const quota = await getQuota(user.id);
  return NextResponse.json(quota);
}
