"use client";

import { useState, useRef, useEffect } from "react";
import { LogOut, ChevronDown, Loader2, Settings, Zap } from "lucide-react";
import Link from "next/link";
import { useUser } from "@/lib/supabase/useUser";
import Image from "next/image";

export function UserMenu() {
  const { user, loading } = useUser();
  const [open, setOpen]   = useState(false);
  const ref               = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  if (loading) return <Loader2 className="w-4 h-4 animate-spin text-bist-muted" />;
  if (!user) return null;

  const avatarUrl   = user.user_metadata?.avatar_url as string | undefined;
  const displayName = (user.user_metadata?.full_name ?? user.email ?? "Usuário") as string;
  const initials    = displayName.split(" ").map((w: string) => w[0]).slice(0, 2).join("").toUpperCase();

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(p => !p)}
        className="flex items-center gap-2 rounded-lg px-2 py-1.5
                   hover:bg-bist-surface2 transition-colors
                   border border-transparent hover:border-bist-border
                   focus:outline-none"
      >
        {avatarUrl ? (
          <Image src={avatarUrl} alt={displayName} width={26} height={26} className="rounded-full ring-1 ring-bist-border" />
        ) : (
          <div className="w-6 h-6 rounded-full bg-bist-primary flex items-center justify-center text-white text-xs font-bold">
            {initials}
          </div>
        )}
        <span className="hidden sm:block text-xs text-bist-muted max-w-[100px] truncate">
          {displayName.split(" ")[0]}
        </span>
        <ChevronDown className={`w-3 h-3 text-bist-dim transition-transform duration-150 ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-1.5 w-52 card shadow-lg py-1 z-50 animate-fade-in">
          <div className="px-3 py-2.5 border-b border-bist-border">
            <p className="text-sm font-medium text-bist-primary truncate">{displayName}</p>
            <p className="text-xs text-bist-muted truncate mt-0.5">{user.email}</p>
          </div>
          <div className="py-1">
            <Link
              href="/settings"
              onClick={() => setOpen(false)}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-bist-muted
                         hover:text-bist-primary hover:bg-bist-surface2 transition-colors"
            >
              <Settings className="w-3.5 h-3.5" /> Configurações
            </Link>
            <Link
              href="/planos"
              onClick={() => setOpen(false)}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-[#2D6A3F]
                         hover:bg-[#a3fb73]/10 transition-colors"
            >
              <Zap className="w-3.5 h-3.5" /> Ver planos
            </Link>
          </div>
          <div className="border-t border-bist-border py-1">
            <form action="/auth/signout" method="POST">
              <button
                type="submit"
                className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-bist-muted
                           hover:text-red-600 hover:bg-red-50 transition-colors text-left"
              >
                <LogOut className="w-3.5 h-3.5" /> Sair
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
