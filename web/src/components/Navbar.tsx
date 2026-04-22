"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart2, FlaskConical, History, Play, TrendingUp, Lightbulb, Sparkles, TestTube2 } from "lucide-react";
import { UserMenu } from "./UserMenu";

const appLinks = [
  { href: "/stories",      label: "Stories",  icon: Lightbulb    },
  { href: "/generate",     label: "Gerar",    icon: Sparkles     },
  { href: "/evaluate",     label: "Avaliar",  icon: BarChart2    },
  { href: "/unit-tests",   label: "Testes",   icon: TestTube2    },
  { href: "/history",      label: "Histórico",icon: History      },
  { href: "/runs",         label: "Runs",     icon: Play         },
  { href: "/stats",        label: "Stats",    icon: TrendingUp   },
  { href: "/autoresearch", label: "Lab",      icon: FlaskConical },
];

export function Navbar() {
  const path = usePathname();
  const isApp = appLinks.some(l => path.startsWith(l.href));

  return (
    <header className="sticky top-0 z-50 bg-bist-surface border-b border-bist-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-6">

        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5 shrink-0 group">
          <div className="w-7 h-7 rounded-lg bg-bist-primary flex items-center justify-center">
            <span className="font-code text-[#a3fb73] text-xs font-semibold tracking-wider leading-none">B</span>
          </div>
          <div className="flex flex-col">
            <span className="font-semibold text-bist-primary text-sm leading-tight tracking-tight">BIST</span>
            <span className="text-[10px] text-bist-dim leading-tight hidden sm:block">BDD Generator</span>
          </div>
        </Link>

        <div className="flex items-center gap-2">
          {isApp && (
            <nav className="flex items-center gap-0.5">
              {appLinks.map(({ href, label, icon: Icon }) => {
                const active = path === href || path.startsWith(href + "/");
                return (
                  <Link
                    key={href}
                    href={href}
                    className={[
                      "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-all duration-150",
                      active
                        ? "bg-bist-primary text-white font-medium"
                        : "text-bist-muted hover:text-bist-primary hover:bg-bist-surface2",
                    ].join(" ")}
                  >
                    <Icon className="w-3.5 h-3.5 flex-shrink-0" />
                    <span className="hidden sm:inline">{label}</span>
                  </Link>
                );
              })}
            </nav>
          )}

          {!isApp ? (
            <Link href="/generate" className="btn-primary text-xs py-2 px-4">
              Abrir app
            </Link>
          ) : (
            <>
              <div className="w-px h-5 bg-bist-border mx-1" />
              <UserMenu />
            </>
          )}
        </div>
      </div>
    </header>
  );
}
