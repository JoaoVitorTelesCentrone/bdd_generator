import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";

export const metadata: Metadata = {
  title: "BIST — BDD Generation Tool",
  description: "Gerador de cenários BDD com auto-refinamento — Gemini & Claude",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <body className="min-h-screen flex flex-col bg-bist-bg">
        <Navbar />
        <main className="flex-1 flex flex-col">{children}</main>
        <footer className="border-t border-bist-border py-5">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between">
            <span className="text-xs text-bist-dim">BIST v1.0 — behavior-driven development</span>
            <span className="text-xs text-bist-dim">Gemini & Claude — 4 quality metrics</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
