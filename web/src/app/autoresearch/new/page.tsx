import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { AutoresearchForm } from "@/components/AutoresearchForm";

export default function NewAutoresearchPage() {
  return (
    <div className="flex-1 flex flex-col">
      <div className="border-b border-bist-border bg-bist-surface">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-5">
          <Link href="/autoresearch" className="inline-flex items-center gap-1.5 text-xs text-bist-muted hover:text-bist-primary transition-colors mb-3">
            <ArrowLeft className="w-3.5 h-3.5" /> Autoresearch
          </Link>
          <h1 className="text-lg font-semibold text-bist-primary">Novo run</h1>
          <p className="text-sm text-bist-muted mt-0.5">
            Configure o otimizador e escolha o conjunto de stories para o benchmark
          </p>
        </div>
      </div>
      <div className="flex-1 max-w-4xl mx-auto w-full px-4 sm:px-6 py-8">
        <AutoresearchForm />
      </div>
    </div>
  );
}
