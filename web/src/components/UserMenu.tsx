"use client";

import { useState, useRef, useEffect } from "react";
import { LogOut, ChevronDown, Loader2 } from "lucide-react";
import { useUser } from "@/lib/supabase/useUser";
import Image from "next/image";

export function UserMenu() {
  const { user, loading } = useUser();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  if (loading) {
    return <Loader2 className="w-4 h-4 animate-spin text-[#3d5a44]" />;
  }

  if (!user) return null;

  const avatarUrl   = user.user_metadata?.avatar_url as string | undefined;
  const displayName = (user.user_metadata?.full_name ?? user.email ?? "Usuário") as string;
  const initials    = displayName.split(" ").map((w: string) => w[0]).slice(0, 2).join("").toUpperCase();

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(p => !p)}
        className="flex items-center gap-2 rounded px-2 py-1.5
                   hover:bg-[#a3fb73]/08 transition-colors duration-100
                   border border-transparent hover:border-[#a3fb73]/15
                   focus:outline-none focus:ring-1 focus:ring-[#a3fb73]/25"
      >
        {avatarUrl ? (
          <Image
            src={avatarUrl}
            alt={displayName}
            width={26} height={26}
            className="rounded-full ring-1 ring-[#a3fb73]/30"
          />
        ) : (
          <div className="w-6 h-6 rounded-full bg-[#a3fb73]/15 border border-[#a3fb73]/30
                          flex items-center justify-center text-[#a3fb73] text-xs font-mono font-bold">
            {initials}
          </div>
        )}
        <span className="hidden sm:block text-xs font-mono text-[#5a7a65] max-w-[100px] truncate">
          {displayName.split(" ")[0].toLowerCase()}
        </span>
        <ChevronDown className={`w-3 h-3 text-[#3d5a44] transition-transform duration-150 ${open ? "rotate-180" : ""}`} />
      </button>

      {/* Dropdown */}
      {open && (
        <div className="absolute right-0 top-full mt-1.5 w-52 card-terminal shadow-xl shadow-black/50 py-1 z-50 animate-fade-in">
          {/* User info */}
          <div className="px-3 py-2.5 border-b border-[#a3fb73]/10">
            <p className="text-sm font-mono font-medium text-[#eef9e8] truncate">{displayName}</p>
            <p className="text-xs font-mono text-[#3d5a44] truncate mt-0.5">{user.email}</p>
          </div>

          {/* Actions */}
          <div className="py-1">
            <form action="/auth/signout" method="POST">
              <button
                type="submit"
                className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-mono text-[#5a7a65]
                           hover:text-[#a3fb73] hover:bg-[#a3fb73]/06 transition-colors text-left"
              >
                <LogOut className="w-3.5 h-3.5" />
                sair
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
