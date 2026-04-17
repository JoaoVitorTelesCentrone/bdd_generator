import Link from "next/link";
import { ArrowRight, CheckCircle, AlertTriangle, TrendingUp } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex-1 flex flex-col">

      {/* ── Hero ───────────────────────────────────────────────────────── */}
      <section className="relative py-24 sm:py-32 px-4 sm:px-8 overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 right-0 w-[500px] h-[500px] rounded-full bg-[#a3fb73]/8 blur-[120px] -translate-y-1/3 translate-x-1/4" />
        </div>

        <div className="relative max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 mb-8 border border-bist-border bg-bist-surface rounded-full px-4 py-1.5 text-xs text-bist-muted">
            <span className="w-1.5 h-1.5 rounded-full bg-[#a3fb73] animate-pulse-accent" />
            Business Intelligence Software Testing
          </div>

          <h1 className="text-4xl sm:text-6xl md:text-7xl font-semibold text-bist-primary leading-[1.08] tracking-tight mb-6">
            Seus testes estão
            <br />
            <span className="text-transparent bg-clip-text" style={{ backgroundImage: "linear-gradient(135deg, #1a2c21 0%, #4D6B57 100%)" }}>
              mentindo
            </span>{" "}
            para você.
          </h1>

          <p className="text-base sm:text-lg text-bist-muted leading-relaxed max-w-2xl mb-10">
            O BIST transforma ruído de QA em inteligência de negócio.{" "}
            <span className="text-bist-primary font-medium">Pare de validar se funciona.</span>{" "}
            Comece a entender <em className="text-bist-primary not-italic font-medium">por que</em> falha — e o que isso revela sobre seu produto.
          </p>

          <div className="flex flex-wrap items-center gap-3">
            <Link href="/generate" className="btn-primary text-sm py-3 px-6 gap-2">
              Gerar BDD agora
              <ArrowRight className="w-4 h-4" />
            </Link>
            <a href="#problema" className="btn-secondary text-sm py-3 px-6">
              Saiba mais
            </a>
          </div>

          <p className="mt-12 text-xs text-bist-dim italic">
            &ldquo;Teste é dado. Dado é decisão. Decisão é vantagem.&rdquo;
          </p>
        </div>
      </section>

      {/* ── Problema ────────────────────────────────────────────────────── */}
      <section id="problema" className="py-20 px-4 sm:px-8 bg-bist-surface border-y border-bist-border">
        <div className="max-w-4xl mx-auto">
          <p className="section-label mb-3">O problema real</p>

          <h2 className="text-2xl sm:text-3xl font-semibold text-bist-primary mb-3 leading-tight">
            A maioria dos times de QA ainda opera no escuro.
          </h2>
          <p className="text-bist-muted text-sm mb-12">
            Não é falta de ferramenta. É falta de <span className="text-bist-primary font-medium">leitura</span>.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
            {[
              {
                code: "ERR 01",
                title: "Executam testes,",
                body: "mas não enxergam padrões.",
                detail: "O pipeline fica verde. A produção quebra na segunda.",
              },
              {
                code: "ERR 02",
                title: "Encontram bugs,",
                body: "mas não preveem riscos.",
                detail: "Cada bug é uma surpresa. Nenhum bug é uma lição.",
              },
              {
                code: "ERR 03",
                title: "Coletam dados,",
                body: "mas não geram insights.",
                detail: "Dashboards cheios. Decisões no escuro.",
              },
            ].map(({ code, title, body, detail }) => (
              <div key={code} className="card p-5 space-y-3 hover:border-bist-muted transition-colors">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                  <span className="text-[10px] font-code font-semibold text-amber-600 tracking-widest">{code}</span>
                </div>
                <div>
                  <p className="text-sm font-semibold text-bist-primary leading-snug">{title}</p>
                  <p className="text-sm text-bist-muted leading-snug">{body}</p>
                </div>
                <p className="text-xs text-bist-dim leading-relaxed border-t border-bist-border2 pt-3">{detail}</p>
              </div>
            ))}
          </div>

          <div className="card p-8 text-center bg-gradient-to-br from-[#a3fb73]/8 to-transparent border-[#a3fb73]/30">
            <p className="text-xl sm:text-2xl font-semibold text-bist-primary mb-3">O BIST muda o jogo.</p>
            <div className="space-y-1 text-sm text-bist-muted">
              <p>Cada teste vira <span className="text-bist-primary font-medium">contexto.</span></p>
              <p>Cada falha vira <span className="text-bist-primary font-medium">aprendizado.</span></p>
              <p>Cada dado vira <span className="text-bist-primary font-medium">decisão.</span></p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Diferenciação ───────────────────────────────────────────────── */}
      <section className="py-20 px-4 sm:px-8">
        <div className="max-w-4xl mx-auto">
          <p className="section-label mb-3">Diferenciação</p>

          <div className="mb-12 space-y-1">
            <p className="text-lg text-bist-dim line-through decoration-bist-dim/40">
              Ferramentas tradicionais executam testes.
            </p>
            <p className="text-3xl sm:text-4xl font-bold text-bist-primary leading-tight">
              O BIST constrói inteligência.
            </p>
          </div>

          <div className="space-y-3 mb-12">
            {[
              "Visualize padrões que nenhum dashboard de CI/CD mostra",
              "Antecipe riscos antes que virem incidentes",
              "Conecte qualidade com negócio — cada métrica tem um porquê",
            ].map((text, i) => (
              <div key={i} className="flex items-start gap-3 p-4 card hover:border-bist-muted transition-colors">
                <CheckCircle className="w-4 h-4 text-[#2D6A3F] flex-shrink-0 mt-0.5" />
                <p className="text-sm text-bist-mid leading-relaxed">{text}</p>
              </div>
            ))}
          </div>

          <div className="text-center space-y-1">
            <p className="text-sm text-bist-muted">Isso não é automação melhorada.</p>
            <p className="text-lg font-semibold text-bist-primary">É QA com propósito estratégico.</p>
          </div>
        </div>
      </section>

      {/* ── Acrônimo BIST ───────────────────────────────────────────────── */}
      <section className="py-20 px-4 sm:px-8 bg-bist-surface border-y border-bist-border">
        <div className="max-w-4xl mx-auto">
          <p className="section-label mb-3">O nome</p>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
            <div>
              <p className="text-sm text-bist-muted mb-6">BIST não é sigla por acaso.</p>
              <div className="card p-5 space-y-4">
                {[
                  { letter: "B", word: "Business",    rest: "qualidade é estratégia de negócio" },
                  { letter: "I", word: "Intelligence", rest: "execução sem leitura é ruído" },
                  { letter: "S", word: "Software",     rest: "o contexto é sempre técnico" },
                  { letter: "T", word: "Testing",      rest: "teste é o meio, não o fim" },
                ].map(({ letter, word, rest }) => (
                  <div key={letter} className="flex items-baseline gap-4">
                    <span className="font-code text-2xl font-bold text-[#a3fb73] w-7 flex-shrink-0 leading-none"
                          style={{ textShadow: "0 0 20px rgba(163,251,115,0.4)" }}>
                      {letter}
                    </span>
                    <div>
                      <span className="text-sm font-semibold text-bist-primary">{word}</span>
                      <span className="text-xs text-bist-dim ml-2">— {rest}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="space-y-4 pt-8">
              <p className="text-bist-muted text-sm leading-loose">
                Porque teste sem inteligência{" "}
                <span className="text-bist-primary font-medium">é só checklist.</span>
              </p>
              <p className="text-bist-dim text-sm leading-loose">
                E checklist não escala. Não prevê. Não protege.
              </p>
              <blockquote className="border-l-2 border-[#a3fb73] pl-4 py-1">
                <p className="text-sm text-bist-mid leading-loose italic">
                  &ldquo;BIST transforma dados de teste em inteligência de negócio — pra você
                  parar de descobrir bugs em produção e começar a prever comportamentos
                  antes que custem caro.&rdquo;
                </p>
              </blockquote>
            </div>
          </div>
        </div>
      </section>

      {/* ── Antes/Depois ────────────────────────────────────────────────── */}
      <section className="py-20 px-4 sm:px-8">
        <div className="max-w-4xl mx-auto">
          <p className="section-label mb-3">Transformação</p>

          <h2 className="text-2xl sm:text-3xl font-semibold text-bist-primary mb-10 leading-tight">
            Antes e depois com o BIST.
          </h2>

          <div className="card overflow-hidden">
            <div className="grid grid-cols-2 border-b border-bist-border bg-bist-surface2">
              <div className="px-5 py-3 border-r border-bist-border">
                <span className="text-xs font-code font-semibold text-red-500 tracking-widest uppercase">− antes</span>
              </div>
              <div className="px-5 py-3">
                <span className="text-xs font-code font-semibold text-[#2D6A3F] tracking-widest uppercase">+ depois com BIST</span>
              </div>
            </div>
            {[
              ["QA reativo",             "QA preditivo"],
              ["Checklist de testes",    "Inteligência comportamental"],
              ['"Passou/Falhou"',        '"Por que? Em que contexto?"'],
              ["Ferramenta de execução", "Plataforma de decisão"],
              ["Validação técnica",      "Validação de negócio"],
            ].map(([before, after], i) => (
              <div key={i} className={`grid grid-cols-2 ${i < 4 ? "border-b border-bist-border2" : ""}`}>
                <div className="px-5 py-3.5 border-r border-bist-border2 flex items-center gap-2 bg-red-50/30">
                  <span className="text-red-400 text-xs select-none">−</span>
                  <span className="text-sm text-bist-dim">{before}</span>
                </div>
                <div className="px-5 py-3.5 flex items-center gap-2 bg-[#a3fb73]/4">
                  <span className="text-[#2D6A3F] text-xs select-none">+</span>
                  <span className="text-sm text-bist-mid font-medium">{after}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Para quem é ─────────────────────────────────────────────────── */}
      <section className="py-20 px-4 sm:px-8 bg-bist-surface border-y border-bist-border">
        <div className="max-w-4xl mx-auto">
          <p className="section-label mb-3">Para quem é</p>

          <h2 className="text-2xl sm:text-3xl font-semibold text-bist-primary mb-10 leading-tight">
            Fala a língua de quem decide.
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {[
              {
                role: "Desenvolvedor",
                headline: "Menos surpresas em produção.",
                body: "Mais confiança em deploys.",
                dot: "bg-blue-400",
              },
              {
                role: "QA Engineer",
                headline: "Saia do operacional.",
                body: "Entre no estratégico. Seus testes agora falam a língua do C-level.",
                dot: "bg-[#a3fb73]",
              },
              {
                role: "Product / Negócio",
                headline: "Qualidade deixa de ser custo invisível.",
                body: "Vira métrica de risco mensurável.",
                dot: "bg-violet-400",
              },
              {
                role: "Liderança Técnica",
                headline: "Previsibilidade.",
                body: "Isso é o que separa times que entregam dos que apagam incêndio.",
                dot: "bg-amber-400",
              },
            ].map(({ role, headline, body, dot }) => (
              <div key={role} className="card p-5 space-y-2 hover:border-bist-muted transition-colors">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`w-2 h-2 rounded-full ${dot}`} />
                  <span className="text-xs font-code text-bist-muted tracking-widest">{role}</span>
                </div>
                <p className="text-sm font-semibold text-bist-primary leading-snug">{headline}</p>
                <p className="text-xs text-bist-muted leading-relaxed">{body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Manifesto ───────────────────────────────────────────────────── */}
      <section className="py-20 px-4 sm:px-8">
        <div className="max-w-3xl mx-auto">
          <p className="section-label mb-8">Manifesto</p>

          <div className="card p-8 sm:p-10 space-y-6">
            <p className="text-2xl sm:text-3xl font-bold text-bist-primary leading-tight">
              QA hoje é teatro de segurança.
            </p>

            <p className="text-sm text-bist-muted leading-loose">
              Você roda testes, bate a meta de cobertura, celebra o pipeline verde.
            </p>
            <p className="text-sm text-bist-primary font-medium leading-loose">
              E mesmo assim... o sistema quebra em produção.
            </p>

            <div className="border-l-2 border-bist-border pl-5 space-y-2 py-1">
              <p className="text-sm text-bist-muted leading-loose">Por quê?</p>
              <p className="text-sm text-bist-primary font-semibold leading-loose">Porque execução não é inteligência.</p>
              <p className="text-sm text-bist-muted leading-loose">Você tem dados. Não tem leitura.</p>
            </div>

            <p className="text-xl font-bold text-bist-primary">O BIST acaba com essa ilusão.</p>

            <div className="space-y-3 pt-1">
              {[
                "Falhou? Por que falhou agora e não antes?",
                "Passou? Passou sob quais condições? Isso é replicável?",
                "Cobertura alta? Mas cobre os fluxos que importam ou só os fáceis de automatizar?",
              ].map((q, i) => (
                <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-bist-surface2 border border-bist-border2">
                  <TrendingUp className="w-3.5 h-3.5 text-[#2D6A3F] flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-bist-mid leading-relaxed">{q}</p>
                </div>
              ))}
            </div>

            <div className="border-t border-bist-border pt-6">
              <p className="text-sm text-bist-muted mb-3">
                Se o seu QA não responde essas perguntas,{" "}
                <span className="text-bist-primary font-medium">você tem automação. Não tem qualidade.</span>
              </p>
              <p className="text-lg font-semibold text-bist-primary">
                BIST é pra quem quer parar de reagir e começar a antecipar.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA Final ───────────────────────────────────────────────────── */}
      <section className="py-24 px-4 sm:px-8 bg-bist-primary relative overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute -top-32 -right-32 w-96 h-96 rounded-full bg-[#a3fb73]/10 blur-[80px]" />
          <div className="absolute -bottom-16 -left-16 w-64 h-64 rounded-full bg-[#a3fb73]/6 blur-[60px]" />
        </div>

        <div className="relative max-w-3xl mx-auto text-center space-y-8">
          <h2 className="text-3xl sm:text-5xl font-bold text-white leading-tight">
            Pare de testar às cegas.
            <br />
            <span style={{ color: "#a3fb73" }}>Comece a testar com visão.</span>
          </h2>

          <p className="text-sm text-[#7A9B87] max-w-md mx-auto leading-relaxed">
            Se você ainda mede qualidade por <span className="text-white">&ldquo;passou/falhou&rdquo;</span>,
            já está dois anos atrasado.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link href="/generate" className="btn-primary text-sm py-3 px-8 gap-2 w-full sm:w-auto">
              Gerar BDD agora
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link href="/evaluate" className="inline-flex items-center justify-center text-sm py-3 px-8 rounded-lg border border-white/20 text-white hover:border-white/40 transition-colors w-full sm:w-auto">
              Avaliar BDD existente
            </Link>
          </div>

          <p className="text-xs italic" style={{ color: "#4D6B57" }}>
            &ldquo;De executor de testes a arquiteto de confiabilidade.&rdquo;
          </p>
        </div>
      </section>

    </div>
  );
}
