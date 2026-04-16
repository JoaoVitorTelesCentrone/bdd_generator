import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";

export const metadata: Metadata = {
  title: "BIST — BDD Generation Tool",
  description: "Gerador de cenários BDD com auto-refinamento — Gemini & Claude",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen flex flex-col" suppressHydrationWarning>
        <Navbar />
        <main className="flex-1 flex flex-col">{children}</main>
        <footer className="relative z-10 border-t border-[#a3fb73]/10 py-4">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between">
            <span className="text-xs text-[#3d5a44] font-mono">
              BIST v1.0 &mdash; behavior-driven development
            </span>
            <span className="text-xs text-[#3d5a44] font-mono">
              Gemini &amp; Claude &mdash; 4 quality metrics
            </span>
          </div>
        </footer>
      </body>
    </html>
  );
}
