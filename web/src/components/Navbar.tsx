"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Sparkles, BarChart2, BookOpen } from "lucide-react";
import { UserMenu } from "./UserMenu";

const links = [
  { href: "/",         label: "Gerar",   icon: Sparkles  },
  { href: "/evaluate", label: "Avaliar", icon: BarChart2  },
];

export function Navbar() {
  const path = usePathname();

  return (
    <header className="sticky top-0 z-50 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-6">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5 shrink-0">
          <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center">
            <BookOpen className="w-4 h-4 text-white" />
          </div>
          <span className="font-semibold text-zinc-100 tracking-tight">
            BDD <span className="text-indigo-400">Generator</span>
          </span>
        </Link>

        <div className="flex items-center gap-3">
          {/* Nav links */}
          <nav className="flex items-center gap-1">
            {links.map(({ href, label, icon: Icon }) => {
              const active = path === href;
              return (
                <Link
                  key={href}
                  href={href}
                  className={[
                    "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors",
                    active
                      ? "bg-indigo-600/20 text-indigo-400"
                      : "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800",
                  ].join(" ")}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {label}
                </Link>
              );
            })}
          </nav>

          <div className="w-px h-5 bg-zinc-800" />
          <UserMenu />
        </div>
      </div>
    </header>
  );
}
