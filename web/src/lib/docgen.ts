import type { HistoryEntry } from "./history";

export interface GenOptions {
  includeIndex: boolean;
  includeStats: boolean;
  groupByModel: boolean;
  includeDate: boolean;
  onlyCritical: boolean;
  onlyApproved: boolean;
  filename: string;
}

export type DocFormat = "markdown" | "html" | "feature" | "txt";

function fmt(ts: number) {
  return new Date(ts).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

function header(e: HistoryEntry) {
  return `Feature: ${e.feature_name}\nGerado em: ${fmt(e.timestamp)}\nModelo: ${e.model}\nScore: ${e.score.score_final.toFixed(1)}/10 (${e.score.aprovado ? "APROVADO" : "REPROVADO"})\nCenários: ${e.scenario_count}\nTags: ${e.tags.join(" ") || "—"}`;
}

// ── Markdown ──────────────────────────────────────────────────────────────────

export function generateMarkdown(entries: HistoryEntry[], opts: GenOptions): string {
  const date = new Date().toLocaleDateString("pt-BR", { dateStyle: "long" });
  const lines: string[] = [];

  lines.push(`# Documentação de Regressão — BIST`);
  lines.push(`\n> Gerado automaticamente em ${date} · BIST v1.0 · ${entries.length} features · ${entries.reduce((s, e) => s + e.scenario_count, 0)} cenários\n`);

  if (opts.includeIndex) {
    lines.push(`---\n## Índice\n`);
    entries.forEach((e, i) => {
      lines.push(`${i + 1}. [${e.feature_name}](#feature-${i + 1}) — ${e.scenario_count} cenários — Score ${e.score.score_final.toFixed(1)}`);
    });
    lines.push("");
  }

  if (opts.includeStats) {
    const total = entries.length;
    const scenarios = entries.reduce((s, e) => s + e.scenario_count, 0);
    const approved = entries.filter(e => e.score.aprovado).length;
    const avg = entries.reduce((s, e) => s + e.score.score_final, 0) / total;

    lines.push(`---\n## Estatísticas\n`);
    lines.push(`| Métrica | Valor |`);
    lines.push(`|---|---|`);
    lines.push(`| Total de features | ${total} |`);
    lines.push(`| Total de cenários | ${scenarios} |`);
    lines.push(`| Aprovados | ${approved} / ${total} (${Math.round(approved/total*100)}%) |`);
    lines.push(`| Score médio | ${avg.toFixed(2)}/10 |`);
    lines.push("");

    lines.push(`| Feature | Score | Status | Cenários | Modelo | Data |`);
    lines.push(`|---|---|---|---|---|---|`);
    for (const e of entries) {
      lines.push(`| ${e.feature_name} | ${e.score.score_final.toFixed(1)} | ${e.score.aprovado ? "✅" : "❌"} | ${e.scenario_count} | ${e.model} | ${fmt(e.timestamp)} |`);
    }
    lines.push("");
  }

  lines.push(`---\n## Features\n`);
  entries.forEach((e, i) => {
    lines.push(`### ${i + 1}. ${e.feature_name}`);
    lines.push(`\n\`\`\`\n${header(e)}\n\`\`\`\n`);
    lines.push(`\`\`\`gherkin\n${e.bdd_text}\n\`\`\`\n`);
    lines.push("---\n");
  });

  lines.push(`\n*Documento gerado pelo BIST — Business Intelligence Software Testing · ${date}*`);
  return lines.join("\n");
}

// ── HTML ──────────────────────────────────────────────────────────────────────

export function generateHTML(entries: HistoryEntry[], opts: GenOptions): string {
  const date = new Date().toLocaleDateString("pt-BR", { dateStyle: "long" });
  const total = entries.length;
  const scenarios = entries.reduce((s, e) => s + e.scenario_count, 0);
  const approved = entries.filter(e => e.score.aprovado).length;
  const avg = entries.reduce((s, e) => s + e.score.score_final, 0) / (total || 1);

  const escHtml = (s: string) => s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");

  const colorLine = (line: string): string => {
    const l = escHtml(line);
    if (/^\s*#/.test(line)) return `<span class="c-comment">${l}</span>`;
    if (/^\s*@/.test(line)) return `<span class="c-tag">${l}</span>`;
    if (/^\s*(Funcionalidade|Feature)\s*:/i.test(line)) return `<span class="c-feature">${l}</span>`;
    if (/^\s*(Cen[aá]rio|Scenario|Background|Contexto)\s*[:|]/i.test(line)) return `<span class="c-scenario">${l}</span>`;
    if (/^\s*(Dado|Quando|Então|Given|When|Then)\b/i.test(line)) return `<span class="c-step">${l}</span>`;
    if (/^\s*(E\b|Mas\b|And\b|But\b)/i.test(line)) return `<span class="c-and">${l}</span>`;
    if (/^\s*\|/.test(line)) return `<span class="c-table">${l}</span>`;
    return l;
  };

  const bddHtml = (bdd: string) =>
    bdd.split("\n").map(ln => `<div class="ln">${colorLine(ln) || "&nbsp;"}</div>`).join("");

  const featureCards = entries.map((e, i) => `
    <section class="feature" id="f${i+1}">
      <div class="feature-header">
        <span class="badge ${e.score.aprovado ? "badge-ok" : "badge-fail"}">${e.score.aprovado ? "APROVADO" : "REPROVADO"}</span>
        <h2>${i+1}. ${escHtml(e.feature_name)}</h2>
        <div class="meta">
          <span>📅 ${fmt(e.timestamp)}</span>
          <span>🤖 ${e.model}</span>
          <span>🏷 ${e.tags.map(t=>`<code>${t}</code>`).join(" ") || "—"}</span>
          <span>📐 ${e.scenario_count} cenários</span>
          <span class="score ${e.score.aprovado ? "score-ok" : "score-fail"}">⭐ ${e.score.score_final.toFixed(1)}/10</span>
        </div>
      </div>
      <div class="metrics">
        ${[
          ["Cobertura", e.score.cobertura, "30%"],
          ["Estrutura GWT", e.score.estrutura, "30%"],
          ["Clareza", e.score.clareza, "20%"],
          ["Executabilidade", e.score.executabilidade, "20%"],
        ].map(([l,v,w]) => `<div class="metric"><span>${l} <em>${w}</em></span><div class="bar"><div class="bar-fill" style="width:${(Number(v)/10*100).toFixed(0)}%;background:${Number(v)>=8?"#a3fb73":Number(v)>=6?"#7dd151":"#f59e0b"}"></div></div><span class="mv">${Number(v).toFixed(1)}</span></div>`).join("")}
      </div>
      <pre class="bdd">${bddHtml(e.bdd_text)}</pre>
    </section>`).join("\n");

  const indexHtml = opts.includeIndex ? `
    <nav class="toc">
      <h2>Índice</h2>
      <ol>${entries.map((e,i) => `<li><a href="#f${i+1}">${escHtml(e.feature_name)}</a> <span class="toc-score">${e.score.score_final.toFixed(1)}</span></li>`).join("")}</ol>
    </nav>` : "";

  const statsHtml = opts.includeStats ? `
    <section class="stats-section">
      <h2>Estatísticas de Cobertura</h2>
      <div class="stat-grid">
        <div class="stat-card"><span>${total}</span><label>Features</label></div>
        <div class="stat-card"><span>${scenarios}</span><label>Cenários</label></div>
        <div class="stat-card"><span>${approved}/${total}</span><label>Aprovados</label></div>
        <div class="stat-card"><span>${avg.toFixed(1)}</span><label>Score médio</label></div>
      </div>
    </section>` : "";

  return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Documentação de Regressão — BIST</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  :root{--bg:#1a2c21;--surface:#243d2c;--lime:#a3fb73;--text:#eef9e8;--muted:#7a9b87;--dim:#5a7a65}
  body{background:var(--bg);color:var(--text);font-family:'Consolas','JetBrains Mono',monospace;font-size:14px;line-height:1.6;padding:2rem}
  @media print{body{background:#fff;color:#000}pre,code{background:#f5f5f5!important;border-color:#ccc!important}header,nav{break-after:page}}
  header{border:1px solid rgba(163,251,115,.2);border-radius:8px;padding:2.5rem;margin-bottom:2rem;text-align:center;background:rgba(163,251,115,.04)}
  header h1{font-size:2rem;color:var(--lime);letter-spacing:.15em;margin-bottom:.5rem}
  header .sub{color:var(--dim);font-size:.8rem;letter-spacing:.1em}
  h2{color:var(--lime);font-size:1rem;text-transform:uppercase;letter-spacing:.1em;margin-bottom:1rem}
  .toc{border:1px solid rgba(163,251,115,.15);border-radius:6px;padding:1.5rem 2rem;margin-bottom:2rem}
  .toc ol{margin-top:.75rem;padding-left:1.25rem;display:grid;grid-template-columns:1fr 1fr;gap:.25rem}
  .toc a{color:var(--muted);text-decoration:none;font-size:.85rem}.toc a:hover{color:var(--lime)}
  .toc-score{color:var(--dim);font-size:.75rem;margin-left:.5rem}
  .stats-section{margin-bottom:2rem}
  .stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-top:.75rem}
  .stat-card{border:1px solid rgba(163,251,115,.15);border-radius:6px;padding:1rem;text-align:center}
  .stat-card span{display:block;font-size:1.75rem;color:var(--lime);font-weight:700}
  .stat-card label{font-size:.75rem;color:var(--dim);text-transform:uppercase;letter-spacing:.05em}
  .feature{border:1px solid rgba(163,251,115,.15);border-radius:8px;margin-bottom:1.5rem;overflow:hidden}
  .feature-header{padding:1.25rem 1.5rem;background:rgba(36,61,44,.5);border-bottom:1px solid rgba(163,251,115,.1)}
  .feature-header h2{font-size:1rem;color:var(--text);margin:.4rem 0;text-transform:none;letter-spacing:0}
  .badge{font-size:.65rem;padding:.2rem .5rem;border-radius:2px;letter-spacing:.08em;font-weight:700}
  .badge-ok{background:rgba(163,251,115,.12);color:var(--lime);border:1px solid rgba(163,251,115,.3)}
  .badge-fail{background:rgba(239,68,68,.12);color:#f87171;border:1px solid rgba(239,68,68,.25)}
  .meta{display:flex;flex-wrap:wrap;gap:.75rem;margin-top:.5rem;font-size:.75rem;color:var(--dim)}
  .meta code{background:rgba(163,251,115,.08);color:var(--muted);padding:.1rem .3rem;border-radius:3px;font-size:.7rem}
  .score{font-weight:700}.score-ok{color:var(--lime)}.score-fail{color:#f87171}
  .metrics{padding:1rem 1.5rem;display:grid;gap:.5rem;border-bottom:1px solid rgba(163,251,115,.08);background:rgba(26,44,33,.4)}
  .metric{display:grid;grid-template-columns:150px 1fr 3rem;align-items:center;gap:.75rem;font-size:.75rem}
  .metric em{color:var(--dim);font-style:normal}
  .bar{height:6px;background:rgba(163,251,115,.08);border-radius:3px;overflow:hidden}
  .bar-fill{height:100%;border-radius:3px}
  .mv{text-align:right;color:var(--muted)}
  pre.bdd{background:var(--bg);padding:1.25rem 1.5rem;overflow-x:auto;font-size:.8rem;line-height:1.7}
  .ln{white-space:pre}
  .c-feature{color:#a3fb73;font-weight:600}.c-scenario{color:#7dd151;font-weight:600}
  .c-step{color:#c4e8a8}.c-and{color:#b2e89a}.c-string{color:#eef9e8;font-style:italic}
  .c-comment{color:#5a7a65;font-style:italic}.c-tag{color:#a3fb73;opacity:.65}.c-table{color:#7a9b87}
  footer{margin-top:3rem;padding-top:1rem;border-top:1px solid rgba(163,251,115,.1);text-align:center;font-size:.7rem;color:var(--dim)}
</style>
</head>
<body>
<header>
  <h1>BIST▮</h1>
  <div class="sub">Documentação de Regressão · Gerado em ${date} · ${total} features · ${scenarios} cenários</div>
</header>
${indexHtml}
${statsHtml}
<main>
${featureCards}
</main>
<footer>Documento gerado automaticamente pelo BIST — Business Intelligence Software Testing · ${date}</footer>
</body>
</html>`;
}

// ── Gherkin (.feature) ────────────────────────────────────────────────────────

export function generateFeature(entries: HistoryEntry[]): string {
  const date = new Date().toLocaleDateString("pt-BR");
  return [
    `# Regressão consolidada — BIST`,
    `# Gerado em: ${date} — ${entries.length} features — ${entries.reduce((s,e)=>s+e.scenario_count,0)} cenários`,
    ``,
    ...entries.map((e, i) => [
      `# ════════════════════════════════════════`,
      `# Feature ${i+1}/${entries.length}: ${e.feature_name}`,
      `# Score: ${e.score.score_final.toFixed(1)}/10 | Modelo: ${e.model} | ${fmt(e.timestamp)}`,
      `# ════════════════════════════════════════`,
      ``,
      e.bdd_text,
      ``,
    ].join("\n")),
  ].join("\n");
}

// ── Plain text ────────────────────────────────────────────────────────────────

export function generateTxt(entries: HistoryEntry[], opts: GenOptions): string {
  const date = new Date().toLocaleDateString("pt-BR", { dateStyle: "long" });
  const sep = "═".repeat(65);
  const thin = "─".repeat(65);
  const lines: string[] = [];

  lines.push(sep);
  lines.push("  DOCUMENTAÇÃO DE REGRESSÃO — BIST");
  lines.push(`  Gerado em: ${date}`);
  lines.push(`  ${entries.length} features · ${entries.reduce((s,e)=>s+e.scenario_count,0)} cenários`);
  lines.push(sep);

  if (opts.includeStats) {
    const approved = entries.filter(e => e.score.aprovado).length;
    const avg = entries.reduce((s,e)=>s+e.score.score_final,0)/(entries.length||1);
    lines.push(`\nESTATÍSTICAS`);
    lines.push(thin);
    lines.push(`Total de features:  ${entries.length}`);
    lines.push(`Total de cenários:  ${entries.reduce((s,e)=>s+e.scenario_count,0)}`);
    lines.push(`Aprovados:          ${approved}/${entries.length}`);
    lines.push(`Score médio:        ${avg.toFixed(2)}/10`);
  }

  entries.forEach((e, i) => {
    lines.push(`\n${sep}`);
    lines.push(`${i+1}. ${e.feature_name.toUpperCase()}`);
    lines.push(thin);
    lines.push(header(e));
    lines.push(thin);
    lines.push(e.bdd_text);
  });

  lines.push(`\n${sep}`);
  lines.push(`Documento gerado pelo BIST · ${date}`);
  return lines.join("\n");
}

// ── Download helper ───────────────────────────────────────────────────────────

export function downloadFile(content: string, filename: string, mime: string) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export function buildDoc(entries: HistoryEntry[], format: DocFormat, opts: GenOptions): { content: string; mime: string; ext: string } {
  switch (format) {
    case "markdown": return { content: generateMarkdown(entries, opts), mime: "text/markdown", ext: "md" };
    case "html":     return { content: generateHTML(entries, opts),     mime: "text/html",     ext: "html" };
    case "feature":  return { content: generateFeature(entries),        mime: "text/plain",    ext: "feature" };
    case "txt":      return { content: generateTxt(entries, opts),      mime: "text/plain",    ext: "txt" };
  }
}
