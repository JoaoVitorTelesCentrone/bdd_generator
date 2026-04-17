"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Terminal, BarChart2, History, Play, TrendingUp, Lightbulb } from "lucide-react";
import { UserMenu } from "./UserMenu";

const appLinks = [
  { href: "/stories",  label: "story",    icon: Lightbulb },
  { href: "/generate", label: "generate", icon: Terminal  },
  { href: "/evaluate", label: "evaluate", icon: BarChart2 },
  { href: "/history",  label: "history",  icon: History   },
  { href: "/runs",     label: "runs",     icon: Play       },
  { href: "/stats",    label: "stats",    icon: TrendingUp },
];

export function Navbar() {
  const path = usePathname();
  const isApp = path.startsWith("/stories")  || path.startsWith("/generate")
             || path.startsWith("/evaluate") || path.startsWith("/history")
             || path.startsWith("/runs")     || path.startsWith("/stats");

  return (
    <header className="sticky top-0 z-50 border-b border-[#a3fb73]/12 bg-[#1a2c21]/96 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-6">

        {/* ── Logo ─────────────────────────────────────────────────────── */}
        <Link href="/" className="flex items-center gap-3 shrink-0 group">
          <div className="flex items-center gap-0.5">
            <span className="font-['Share_Tech_Mono',_'Consolas',_monospace] text-[#a3fb73] text-xl tracking-[0.25em] leading-none">
              BIST
            </span>
            <span className="text-[#a3fb73] text-xl leading-none animate-cursor-blink ml-0.5">
              ▮
            </span>
          </div>
          <div className="hidden sm:flex flex-col justify-center">
            <span className="text-[10px] text-[#5a7a65] font-mono leading-tight tracking-widest uppercase">
              bdd generator
            </span>
          </div>
        </Link>

        <div className="flex items-center gap-3">
          {/* ── App Nav Links (only shown on app pages) ─────────────────── */}
          {isApp && (
            <nav className="flex items-center gap-1">
              {appLinks.map(({ href, label, icon: Icon }) => {
                const active = path === href || path.startsWith(href + "/");
                return (
                  <Link
                    key={href}
                    href={href}
                    className={[
                      "flex items-center gap-1.5 px-3 py-1.5 rounded text-sm font-mono transition-all duration-150",
                      active
                        ? "bg-[#a3fb73]/12 text-[#a3fb73] border border-[#a3fb73]/25"
                        : "text-[#5a7a65] hover:text-[#a3fb73] hover:bg-[#a3fb73]/06 border border-transparent",
                    ].join(" ")}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    <span className="hidden sm:inline">
                      {active && <span className="text-[#a3fb73]/50 mr-0.5">./</span>}
                      {label}
                    </span>
                  </Link>
                );
              })}
            </nav>
          )}

          {/* ── CTA (landing) or separator+UserMenu (app) ───────────────── */}
          {!isApp ? (
            <Link
              href="/generate"
              className="btn-primary text-xs py-2 px-4 shadow-lg shadow-[#a3fb73]/15"
            >
              <Terminal className="w-3.5 h-3.5" />
              abrir app
            </Link>
          ) : (
            <>
              <div className="w-px h-5 bg-[#a3fb73]/15" />
              <UserMenu />
            </>
          )}
        </div>
      </div>
    </header>
  );
}
