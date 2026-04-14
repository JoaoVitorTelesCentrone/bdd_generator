"use client";

import { useState, useRef, useEffect } from "react";
import { LogOut, User, ChevronDown, Loader2 } from "lucide-react";
import { useUser } from "@/lib/supabase/useUser";
import Image from "next/image";

export function UserMenu() {
  const { user, loading } = useUser();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Fecha dropdown ao clicar fora
  useEffect(() => {
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  if (loading) {
    return <Loader2 className="w-4 h-4 animate-spin text-zinc-600" />;
  }

  if (!user) return null;

  const avatarUrl   = user.user_metadata?.avatar_url as string | undefined;
  const displayName = (user.user_metadata?.full_name ?? user.email ?? "Usuário") as string;
  const initials    = displayName.split(" ").map(w => w[0]).slice(0, 2).join("").toUpperCase();

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(p => !p)}
        className="flex items-center gap-2 rounded-lg px-2 py-1.5
                   hover:bg-zinc-800 transition-colors duration-100
                   focus:outline-none focus:ring-2 focus:ring-zinc-700"
      >
        {/* Avatar */}
        {avatarUrl ? (
          <Image
            src={avatarUrl}
            alt={displayName}
            width={28} height={28}
            className="rounded-full ring-1 ring-zinc-700"
          />
        ) : (
          <div className="w-7 h-7 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs font-semibold">
            {initials}
          </div>
        )}
        <span className="hidden sm:block text-sm text-zinc-300 max-w-[120px] truncate">
          {displayName.split(" ")[0]}
        </span>
        <ChevronDown className={`w-3.5 h-3.5 text-zinc-500 transition-transform duration-150 ${open ? "rotate-180" : ""}`} />
      </button>

      {/* Dropdown */}
      {open && (
        <div className="absolute right-0 top-full mt-1.5 w-56 card shadow-xl shadow-black/40 py-1 z-50 animate-fade-in">
          {/* User info */}
          <div className="px-3 py-2.5 border-b border-zinc-800">
            <p className="text-sm font-medium text-zinc-200 truncate">{displayName}</p>
            <p className="text-xs text-zinc-500 truncate mt-0.5">{user.email}</p>
          </div>

          {/* Actions */}
          <div className="py-1">
            <form action="/auth/signout" method="POST">
              <button
                type="submit"
                className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-zinc-400
                           hover:text-zinc-100 hover:bg-zinc-800 transition-colors text-left"
              >
                <LogOut className="w-3.5 h-3.5" />
                Sair
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
