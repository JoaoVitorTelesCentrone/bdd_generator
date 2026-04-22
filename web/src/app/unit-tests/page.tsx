import { UnitTestsPagePanel } from "@/components/UnitTestsPagePanel";

export const metadata = {
  title: "Testes Unitários — BIST",
  description: "Gere stubs de testes unitários em qualquer linguagem a partir de cenários BDD Gherkin",
};

export default function UnitTestsPage() {
  return (
    <div className="flex-1 flex flex-col">

      {/* Page header */}
      <div className="border-b border-bist-border bg-bist-surface">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-5">
          <h1 className="text-lg font-semibold text-bist-primary">Testes Unitários</h1>
          <p className="text-sm text-bist-muted mt-0.5">
            Cole seus cenários Gherkin e gere stubs de testes prontos para Python, Java, JavaScript, Go e mais
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-6">
        <UnitTestsPagePanel />
      </div>
    </div>
  );
}
