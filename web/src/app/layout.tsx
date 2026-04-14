import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";

export const metadata: Metadata = {
  title: "BDD Generator",
  description: "Gerador de cenários BDD com auto-refinamento — Gemini & Claude",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className="dark">
      <body className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 flex flex-col">{children}</main>
        <footer className="border-t border-zinc-800 py-4 text-center text-xs text-zinc-600">
          BDD Generator &mdash; Gemini &amp; Claude &mdash; Auto-refinamento com 4 métricas de qualidade
        </footer>
      </body>
    </html>
  );
}
