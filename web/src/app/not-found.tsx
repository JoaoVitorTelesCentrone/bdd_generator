"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

export default function NotFound() {
  const router = useRouter();

  useEffect(() => {
    const timer = setTimeout(() => router.replace("/"), 2000);
    return () => clearTimeout(timer);
  }, [router]);

  return (
    <div className="min-h-screen bg-bist-bg flex flex-col items-center justify-center gap-4 text-center px-4">
      <div className="w-12 h-12 rounded-xl bg-bist-surface border border-bist-border flex items-center justify-center">
        <span className="font-code text-bist-dim text-lg font-bold">404</span>
      </div>
      <div className="space-y-1">
        <p className="text-sm font-medium text-bist-primary">Página não encontrada</p>
        <p className="text-xs text-bist-muted">Redirecionando para a home...</p>
      </div>
      <Loader2 className="w-4 h-4 animate-spin text-bist-dim" />
    </div>
  );
}
