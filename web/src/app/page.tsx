import Link from "next/link";
import { Terminal, ArrowRight, CheckCircle, AlertTriangle } from "lucide-react";

/* ─── Reusable primitives ──────────────────────────────────────────────────── */

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-2 mb-6">
      <span className="text-[#3d5a44] font-mono text-xs select-none">$</span>
      <span className="text-xs font-mono text-[#5a7a65] tracking-widest uppercase">{children}</span>
      <div className="flex-1 h-px bg-[#a3fb73]/10" />
    </div>
  );
}

/* ─── Landing Page ─────────────────────────────────────────────────────────── */

export default function LandingPage() {
  return (
    <div className="flex-1 flex flex-col overflow-hidden">

      {/* ════════════════════════════════════════════════════════════════
          HERO — full viewport
      ════════════════════════════════════════════════════════════════ */}
      <section className="relative min-h-[92vh] flex flex-col justify-center overflow-hidden">

        {/* Background glow */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2
                          w-[600px] h-[400px] rounded-full
                          bg-[#a3fb73]/4 blur-[120px]" />
        </div>

        <div className="relative z-10 max-w-5xl mx-auto px-4 sm:px-8 py-20">

          {/* Tagline pill */}
          <div className="inline-flex items-center gap-2 mb-10
                          border border-[#a3fb73]/25 bg-[#a3fb73]/5
                          rounded-full px-4 py-1.5 text-xs font-mono text-[#7a9b87]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#a3fb73] animate-pulse-lime" />
            Business Intelligence Software Testing
          </div>

          {/* Main headline */}
          <h1 className="font-['Share_Tech_Mono',_'Consolas',_monospace]
                         text-5xl sm:text-6xl md:text-7xl lg:text-8xl
                         leading-[1.05] tracking-tight mb-8">
            <span className="text-[#eef9e8]">Seus testes</span>
            <br />
            <span className="text-[#eef9e8]">estão</span>{" "}
            <span className="text-[#a3fb73]">mentindo</span>
            <br />
            <span className="text-[#eef9e8]">para você.</span>
            <span className="text-[#a3fb73] animate-cursor-blink ml-2 text-7xl">▮</span>
          </h1>

          {/* Subheadline */}
          <p className="text-base sm:text-lg text-[#7a9b87] font-mono leading-relaxed max-w-2xl mb-12">
            O BIST transforma ruído de QA em inteligência de negócio.{" "}
            <span className="text-[#eef9e8]">Pare de validar se funciona.</span>{" "}
            Comece a entender{" "}
            <span className="italic text-[#a3fb73]">por que</span>{" "}
            falha — e o que isso revela sobre seu produto.
          </p>

          {/* CTA row */}
          <div className="flex flex-wrap items-center gap-4">
            <Link
              href="/generate"
              className="btn-primary text-sm py-3 px-7 gap-2.5
                         shadow-[0_0_40px_rgba(163,251,115,0.18)]
                         hover:shadow-[0_0_60px_rgba(163,251,115,0.28)]
                         transition-all duration-300"
            >
              <Terminal className="w-4 h-4" />
              Gerar BDD agora
              <ArrowRight className="w-4 h-4" />
            </Link>
            <a
              href="#problem"
              className="text-sm font-mono text-[#5a7a65] hover:text-[#a3fb73]
                         transition-colors flex items-center gap-1.5"
            >
              Saiba mais
              <span className="text-[10px]">↓</span>
            </a>
          </div>

          {/* Tagline strip */}
          <div className="mt-16 pt-8 border-t border-[#a3fb73]/8">
            <p className="text-xs font-mono text-[#3d5a44] italic">
              &ldquo;Teste é dado. Dado é decisão. Decisão é vantagem.&rdquo;
            </p>
          </div>
        </div>

        {/* Bottom fade */}
        <div className="absolute bottom-0 left-0 right-0 h-24
                        bg-gradient-to-t from-[#1a2c21] to-transparent pointer-events-none" />
      </section>

      {/* ════════════════════════════════════════════════════════════════
          PROBLEM — os três modos de falha
      ════════════════════════════════════════════════════════════════ */}
      <section id="problem" className="py-24 px-4 sm:px-8">
        <div className="max-w-5xl mx-auto">
          <SectionLabel>o problema real</SectionLabel>

          <h2 className="font-['Share_Tech_Mono',_'Consolas',_monospace]
                         text-3xl sm:text-4xl text-[#eef9e8] mb-4 leading-tight">
            A maioria dos times de QA<br />
            <span className="text-[#5a7a65]">ainda opera no escuro.</span>
          </h2>
          <p className="text-sm font-mono text-[#5a7a65] mb-14">
            Não é falta de ferramenta. É falta de <span className="text-[#a3fb73]">leitura</span>.
          </p>

          {/* Three failure modes — terminal output style */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-16">
            {[
              {
                code: "ERR_01",
                title: "Executam testes",
                body: "mas não enxergam padrões",
                detail: "O pipeline fica verde. A produção quebra na segunda.",
              },
              {
                code: "ERR_02",
                title: "Encontram bugs",
                body: "mas não preveem riscos",
                detail: "Cada bug é uma surpresa. Nenhum bug é uma lição.",
              },
              {
                code: "ERR_03",
                title: "Coletam dados",
                body: "mas não geram insights",
                detail: "Dashboards cheios. Decisões no escuro.",
              },
            ].map(({ code, title, body, detail }) => (
              <div key={code}
                   className="card-terminal p-5 space-y-4 border-[#a3fb73]/10
                              hover:border-[#a3fb73]/25 transition-colors duration-300">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-3.5 h-3.5 text-[#f59e0b]" />
                  <span className="text-[10px] font-mono text-[#f59e0b] tracking-widest">{code}</span>
                </div>
                <div>
                  <p className="text-base font-mono font-semibold text-[#eef9e8] leading-snug">
                    {title},
                  </p>
                  <p className="text-base font-mono text-[#5a7a65] leading-snug">
                    {body}.
                  </p>
                </div>
                <p className="text-xs font-mono text-[#3d5a44] leading-relaxed border-t border-[#a3fb73]/8 pt-3">
                  {detail}
                </p>
              </div>
            ))}
          </div>

          {/* Pivot */}
          <div className="card p-8 text-center border-[#a3fb73]/20
                          bg-[#a3fb73]/4 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-[#a3fb73]/3 to-transparent pointer-events-none" />
            <p className="relative text-2xl sm:text-3xl font-['Share_Tech_Mono',_'Consolas',_monospace]
                          text-[#a3fb73] mb-4">
              O BIST muda o jogo.
            </p>
            <div className="relative space-y-1 text-sm font-mono text-[#7a9b87]">
              <p>Cada teste vira <span className="text-[#eef9e8]">contexto.</span></p>
              <p>Cada falha vira <span className="text-[#eef9e8]">aprendizado.</span></p>
              <p>Cada dado vira <span className="text-[#eef9e8]">decisão.</span></p>
            </div>
          </div>
        </div>
      </section>

      {/* ════════════════════════════════════════════════════════════════
          DIFERENCIAÇÃO
      ════════════════════════════════════════════════════════════════ */}
      <section className="py-24 px-4 sm:px-8 border-y border-[#a3fb73]/8">
        <div className="max-w-5xl mx-auto">
          <SectionLabel>diferenciação</SectionLabel>

          {/* The contrast statement */}
          <div className="mb-16 space-y-2">
            <p className="font-mono text-xl sm:text-2xl">
              <span className="text-[#5a7a65] line-through decoration-[#5a7a65]/50">
                Ferramentas tradicionais EXECUTAM testes.
              </span>
            </p>
            <p className="font-['Share_Tech_Mono',_'Consolas',_monospace] text-3xl sm:text-5xl text-[#a3fb73]">
              O BIST CONSTRÓI inteligência.
            </p>
          </div>

          {/* Benefits */}
          <div className="space-y-4 mb-16">
            {[
              "Visualize padrões que nenhum dashboard de CI/CD mostra",
              "Antecipe riscos antes que virem incidentes",
              "Conecte qualidade com negócio — cada métrica tem um porquê",
            ].map((text, i) => (
              <div key={i}
                   className="flex items-start gap-4 p-5 card
                              hover:border-[#a3fb73]/30 transition-colors duration-200">
                <CheckCircle className="w-5 h-5 text-[#a3fb73] flex-shrink-0 mt-0.5" />
                <p className="font-mono text-[#c8e8c8] text-sm leading-relaxed">{text}</p>
              </div>
            ))}
          </div>

          {/* Closing statement */}
          <div className="text-center space-y-2">
            <p className="font-mono text-[#5a7a65] text-sm">
              Isso não é automação melhorada.
            </p>
            <p className="font-['Share_Tech_Mono',_'Consolas',_monospace] text-xl text-[#eef9e8]">
              É QA com propósito estratégico.
            </p>
          </div>
        </div>
      </section>

      {/* ════════════════════════════════════════════════════════════════
          BIST ACRONYM — ancoragem do nome
      ════════════════════════════════════════════════════════════════ */}
      <section className="py-24 px-4 sm:px-8">
        <div className="max-w-5xl mx-auto">
          <SectionLabel>o nome</SectionLabel>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <p className="text-sm font-mono text-[#5a7a65] mb-6">
                BIST não é sigla por acaso.
              </p>
              {/* Acronym breakdown */}
              <div className="card-terminal p-6 space-y-3">
                {[
                  { letter: "B", word: "Business",     rest: "porque qualidade é estratégia de negócio" },
                  { letter: "I", word: "Intelligence",  rest: "porque execução sem leitura é ruído" },
                  { letter: "S", word: "Software",      rest: "porque o contexto é sempre técnico" },
                  { letter: "T", word: "Testing",       rest: "porque teste é o meio, não o fim" },
                ].map(({ letter, word, rest }) => (
                  <div key={letter} className="flex items-baseline gap-3">
                    <span className="font-['Share_Tech_Mono',_'Consolas',_monospace]
                                     text-3xl text-[#a3fb73] w-8 flex-shrink-0 leading-none">
                      {letter}
                    </span>
                    <div>
                      <span className="font-mono text-sm font-semibold text-[#eef9e8]">{word}</span>
                      <span className="font-mono text-xs text-[#3d5a44] ml-2">// {rest}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="space-y-5">
              <p className="font-mono text-[#7a9b87] text-sm leading-loose">
                Porque teste sem inteligência{" "}
                <span className="text-[#eef9e8]">é só checklist.</span>
              </p>
              <p className="font-mono text-[#5a7a65] text-sm leading-loose">
                E checklist não escala.{" "}
                <span className="text-[#5a7a65]">Não prevê.</span>{" "}
                <span className="text-[#5a7a65]">Não protege.</span>
              </p>
              <div className="border-l-2 border-[#a3fb73] pl-5 py-2">
                <p className="font-mono text-sm text-[#c8e8c8] italic leading-loose">
                  &ldquo;BIST transforma dados de teste em inteligência de negócio — pra você
                  parar de descobrir bugs em produção e começar a prever comportamentos
                  antes que custem caro.&rdquo;
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ════════════════════════════════════════════════════════════════
          BEFORE / AFTER — terminal diff
      ════════════════════════════════════════════════════════════════ */}
      <section className="py-24 px-4 sm:px-8 border-t border-[#a3fb73]/8">
        <div className="max-w-5xl mx-auto">
          <SectionLabel>transformação</SectionLabel>

          <h2 className="font-['Share_Tech_Mono',_'Consolas',_monospace]
                         text-3xl sm:text-4xl text-[#eef9e8] mb-12 leading-tight">
            Antes e depois<br />
            <span className="text-[#5a7a65] text-2xl">com o BIST.</span>
          </h2>

          {/* Diff-style table */}
          <div className="card-terminal overflow-hidden">
            <div className="flex items-center gap-1.5 px-4 py-2.5 border-b border-[#a3fb73]/10 bg-[#243d2c]/50">
              <div className="w-2.5 h-2.5 rounded-full bg-red-500/50" />
              <div className="w-2.5 h-2.5 rounded-full bg-[#f59e0b]/50" />
              <div className="w-2.5 h-2.5 rounded-full bg-[#a3fb73]/50" />
              <span className="text-[10px] font-mono text-[#3d5a44] ml-2">bist --diff before after</span>
            </div>

            <div className="p-0">
              {/* Header row */}
              <div className="grid grid-cols-2 border-b border-[#a3fb73]/10">
                <div className="px-5 py-2.5 bg-red-500/5 border-r border-[#a3fb73]/8">
                  <span className="text-xs font-mono text-red-400 tracking-widest uppercase">
                    − antes
                  </span>
                </div>
                <div className="px-5 py-2.5 bg-[#a3fb73]/4">
                  <span className="text-xs font-mono text-[#a3fb73] tracking-widest uppercase">
                    + depois com bist
                  </span>
                </div>
              </div>

              {[
                ["QA reativo",            "QA preditivo"],
                ["Checklist de testes",   "Inteligência comportamental"],
                ['"Passou/Falhou"',       '"Por que? Em que contexto?"'],
                ["Ferramenta de execução","Plataforma de decisão"],
                ["Validação técnica",     "Validação de negócio"],
              ].map(([before, after], i) => (
                <div
                  key={i}
                  className={`grid grid-cols-2 ${i < 4 ? "border-b border-[#a3fb73]/6" : ""}`}
                >
                  <div className="px-5 py-3.5 bg-red-500/3 border-r border-[#a3fb73]/8
                                  flex items-center gap-2">
                    <span className="text-[#5a7a65] font-mono text-xs select-none">−</span>
                    <span className="font-mono text-sm text-[#5a7a65]">{before}</span>
                  </div>
                  <div className="px-5 py-3.5 bg-[#a3fb73]/2 flex items-center gap-2">
                    <span className="text-[#a3fb73] font-mono text-xs select-none">+</span>
                    <span className="font-mono text-sm text-[#c8e8c8]">{after}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ════════════════════════════════════════════════════════════════
          AUDIÊNCIAS — proposta de valor em camadas
      ════════════════════════════════════════════════════════════════ */}
      <section className="py-24 px-4 sm:px-8">
        <div className="max-w-5xl mx-auto">
          <SectionLabel>para quem é</SectionLabel>

          <h2 className="font-['Share_Tech_Mono',_'Consolas',_monospace]
                         text-3xl sm:text-4xl text-[#eef9e8] mb-12 leading-tight">
            Fala a língua<br />
            <span className="text-[#5a7a65]">de quem decide.</span>
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {[
              {
                role: "desenvolvedor",
                prompt: "> dev",
                headline: "Menos surpresas em produção.",
                body: "Mais confiança em deploys.",
                color: "text-[#60a5fa]",
                accent: "border-[#60a5fa]/20 hover:border-[#60a5fa]/40",
              },
              {
                role: "qa engineer",
                prompt: "> qa",
                headline: "Saia do operacional.",
                body: "Entre no estratégico. Seus testes agora falam a língua do C-level.",
                color: "text-[#a3fb73]",
                accent: "border-[#a3fb73]/20 hover:border-[#a3fb73]/40",
              },
              {
                role: "product / negócio",
                prompt: "> product",
                headline: "Qualidade deixa de ser custo invisível.",
                body: "Vira métrica de risco mensurável.",
                color: "text-[#c4b5fd]",
                accent: "border-[#c4b5fd]/20 hover:border-[#c4b5fd]/40",
              },
              {
                role: "liderança técnica",
                prompt: "> cto",
                headline: "Previsibilidade.",
                body: "Isso é o que separa times que entregam dos que apagam incêndio.",
                color: "text-[#f59e0b]",
                accent: "border-[#f59e0b]/20 hover:border-[#f59e0b]/40",
              },
            ].map(({ prompt, headline, body, color, accent }) => (
              <div
                key={prompt}
                className={`card-terminal p-6 space-y-3 border transition-colors duration-200 ${accent}`}
              >
                <span className={`text-xs font-mono tracking-widest ${color}`}>{prompt}</span>
                <p className="font-mono font-semibold text-[#eef9e8] text-sm leading-snug">
                  {headline}
                </p>
                <p className="font-mono text-xs text-[#7a9b87] leading-relaxed">{body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ════════════════════════════════════════════════════════════════
          MANIFESTO — versão ultra-agressiva
      ════════════════════════════════════════════════════════════════ */}
      <section className="py-24 px-4 sm:px-8 border-y border-[#a3fb73]/8
                           bg-[#a3fb73]/2 relative overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 right-0 w-96 h-96 rounded-full
                          bg-[#a3fb73]/3 blur-[100px]" />
        </div>

        <div className="relative z-10 max-w-3xl mx-auto">
          <SectionLabel>manifesto</SectionLabel>

          <div className="card-terminal p-8 sm:p-10 space-y-6">
            {/* Terminal header */}
            <div className="flex items-center gap-2 border-b border-[#a3fb73]/10 pb-4">
              <span className="text-[#a3fb73] font-mono text-xs">bist</span>
              <span className="text-[#5a7a65] font-mono text-xs">--manifesto</span>
            </div>

            <p className="font-['Share_Tech_Mono',_'Consolas',_monospace]
                           text-2xl sm:text-3xl text-[#a3fb73] leading-tight">
              QA hoje é teatro<br />de segurança.
            </p>

            <p className="font-mono text-sm text-[#7a9b87] leading-loose">
              Você roda testes, bate a meta de cobertura, celebra o pipeline verde.
            </p>
            <p className="font-mono text-sm text-[#eef9e8] leading-loose">
              E mesmo assim... o sistema quebra em produção.
            </p>

            <div className="border-l-2 border-[#a3fb73]/30 pl-5 space-y-2 py-2">
              <p className="font-mono text-sm text-[#5a7a65] leading-loose">Por quê?</p>
              <p className="font-mono text-sm text-[#eef9e8] leading-loose font-semibold">
                Porque execução não é inteligência.
              </p>
              <p className="font-mono text-sm text-[#7a9b87] leading-loose">
                Você tem dados. Não tem leitura.
              </p>
            </div>

            <p className="font-['Share_Tech_Mono',_'Consolas',_monospace]
                           text-xl text-[#a3fb73]">
              O BIST acaba com essa ilusão.
            </p>

            <div className="space-y-3 pt-2">
              {[
                "Falhou? Por que falhou agora e não antes?",
                "Passou? Passou sob quais condições? Isso é replicável?",
                "Cobertura alta? Mas cobre os fluxos que IMPORTAM ou só os fáceis de automatizar?",
              ].map((q, i) => (
                <div key={i} className="flex items-baseline gap-3">
                  <span className="text-[#a3fb73] font-mono text-xs select-none flex-shrink-0">›</span>
                  <p className="font-mono text-sm text-[#7a9b87] leading-relaxed">{q}</p>
                </div>
              ))}
            </div>

            <div className="border-t border-[#a3fb73]/10 pt-6">
              <p className="font-mono text-sm text-[#5a7a65] mb-3">
                Se o seu QA não responde essas perguntas,{" "}
                <span className="text-[#eef9e8]">você tem automação. Não tem qualidade.</span>
              </p>
              <p className="font-['Share_Tech_Mono',_'Consolas',_monospace]
                             text-lg sm:text-xl text-[#a3fb73]">
                BIST é pra quem quer parar de reagir<br />e começar a antecipar.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ════════════════════════════════════════════════════════════════
          CTA FINAL
      ════════════════════════════════════════════════════════════════ */}
      <section className="py-32 px-4 sm:px-8 relative overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2
                          w-[500px] h-[300px] rounded-full
                          bg-[#a3fb73]/5 blur-[100px]" />
        </div>

        <div className="relative z-10 max-w-3xl mx-auto text-center space-y-8">

          <p className="text-xs font-mono text-[#3d5a44] tracking-widest uppercase">$ bist --cta</p>

          <h2 className="font-['Share_Tech_Mono',_'Consolas',_monospace]
                         text-4xl sm:text-5xl md:text-6xl text-[#eef9e8] leading-tight">
            Pare de testar às cegas.
            <br />
            <span className="text-[#a3fb73]">Comece a testar com visão.</span>
          </h2>

          <p className="font-mono text-sm text-[#5a7a65] max-w-md mx-auto leading-relaxed">
            Se você ainda mede qualidade por{" "}
            <span className="text-[#eef9e8]">&ldquo;passou/falhou&rdquo;</span>,
            já está dois anos atrasado.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/generate"
              className="btn-primary text-sm py-3.5 px-8 gap-3
                         shadow-[0_0_50px_rgba(163,251,115,0.2)]
                         hover:shadow-[0_0_80px_rgba(163,251,115,0.32)]
                         transition-all duration-300 w-full sm:w-auto"
            >
              <Terminal className="w-4 h-4" />
              Gerar BDD agora
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/evaluate"
              className="btn-secondary text-sm py-3.5 px-8 w-full sm:w-auto"
            >
              Avaliar BDD existente
            </Link>
          </div>

          {/* Taglines A/B */}
          <div className="pt-8 border-t border-[#a3fb73]/8 space-y-2">
            <p className="text-xs font-mono text-[#3d5a44] italic">
              &ldquo;De executor de testes a arquiteto de confiabilidade.&rdquo;
            </p>
          </div>
        </div>
      </section>

    </div>
  );
}
