"""
BDD Generator CLI
Usage: python -m src.cli [COMMAND] [OPTIONS]
"""
import csv
import sys
import random
import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .generators.base import BaseLLMGenerator
from .generators.claude_generator import ClaudeGenerator
from .generators.gemini_generator import GeminiGenerator
from .evaluators.scorer import BDDScorer
from .refinement.loop import RefinementLoop
from .research.auto_researcher import AutoResearcher
from .study.analyzer import BatchAnalyzer, load_study_context
from .utils.logger import AttemptLogger
from .utils.prompts import PromptTemplates
from .auth.config import (
    load_config, save_config, clear_auth, is_authenticated,
    get_plan, Config, AuthState, MANAGED_API_URL,
)
from .auth.client import validate_token, get_quota, managed_generate, QuotaExceededError, AuthError

# Gemini model aliases
_GEMINI_ALIASES = {
    "flash", "flash-lite", "pro", "flash-1.5",
    "gemini-2.0-flash", "gemini-2.0-flash-lite",
    "gemini-1.5-pro", "gemini-1.5-flash",
}


def _is_gemini(model: str) -> bool:
    return model in _GEMINI_ALIASES or model.startswith("gemini")

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

app = typer.Typer(
    name="bdd-generator",
    help="Gerador de cenários BDD com auto-refinamento (Claude ou Gemini)",
    add_completion=False,
)
console = Console()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _load_dataset(path: str) -> list[dict]:
    """Load user stories from a CSV file."""
    issues = []
    try:
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = (row.get("title") or row.get("Title") or "").strip()
                desc  = (row.get("description") or row.get("Description") or "").strip()
                pts   = (row.get("storypoints") or row.get("story_points") or "N/A").strip()
                if title:
                    issues.append({"title": title, "description": desc, "storypoints": pts})
    except FileNotFoundError:
        console.print(f"[red]Arquivo não encontrado:[/red] {path}")
        raise typer.Exit(1)
    return issues


def _save_feature(bdd_text: str, output_dir: Path, filename: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    with open(path, "w", encoding="utf-8") as f:
        f.write(bdd_text)
    return path


def _make_generator(model: str, max_tokens: int = 4096) -> BaseLLMGenerator:
    if _is_gemini(model):
        return GeminiGenerator(model=model, max_tokens=max_tokens)
    return ClaudeGenerator(model=model, max_tokens=max_tokens)


def _new_run_dir(prefix: str = "run") -> Path:
    """Creates and returns a fresh timestamped folder inside results/."""
    ts = time.strftime("%Y%m%d_%H%M%S")
    run_dir = Path("results") / f"{prefix}_{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def _make_loop(
    model: str,
    threshold: float,
    max_attempts: int,
    verbose: bool,
    log_dir: str = "results/experiments",
    enable_research: bool = False,
) -> RefinementLoop:
    generator  = _make_generator(model)
    scorer     = BDDScorer(threshold=threshold)
    logger     = AttemptLogger(log_dir=log_dir, verbose=verbose)
    researcher = AutoResearcher(generator=generator, verbose=verbose) if enable_research else None
    return RefinementLoop(
        generator=generator,
        scorer=scorer,
        max_attempts=max_attempts,
        logger=logger,
        verbose=verbose,
        researcher=researcher,
    )


def _run_batch_internal(
    issues: list,
    output_path: Path,
    model: str,
    threshold: float,
    max_attempts: int,
    verbose: bool,
    research: bool,
    until_converged: bool,
    study_context: Optional[str] = None,
) -> None:
    """Core batch logic, shared by `batch` and `pipeline` commands."""
    import csv as _csv
    import re as _re

    output_path.parent.mkdir(parents=True, exist_ok=True)
    features_dir = output_path.parent / "features"
    features_dir.mkdir(exist_ok=True)

    loop = _make_loop(model, threshold, max_attempts, verbose, log_dir=str(output_path.parent), enable_research=research)

    fieldnames = [
        "story_id", "title", "model", "score_final", "cobertura", "clareza",
        "estrutura", "executabilidade", "tentativas", "tokens_usados",
        "tokens_research", "tempo_segundos", "aprovado", "convergiu", "feature_file",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = _csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, issue in enumerate(issues, 1):
            story = issue["title"]
            if issue["description"]:
                story += f". {issue['description'][:300]}"

            console.print(f"\n[{i}/{len(issues)}] {issue['title'][:70]}")

            result = loop.run(
                story,
                context=study_context,
                enable_research=research,
                until_converged=until_converged,
            )

            feature_file = ""
            feature_filename = "sem BDD"
            if result.bdd_text:
                safe_name = _re.sub(r"[^\w\s-]", "", issue["title"].lower())
                safe_name = _re.sub(r"[\s-]+", "_", safe_name)[:50]
                feature_filename = f"{i:03d}_{safe_name}.feature"
                feature_path = features_dir / feature_filename
                feature_path.write_text(
                    f"# Story: {issue['title']}\n"
                    f"# Model: {model} | Score: {result.score.score_final:.1f}/10\n\n"
                    + result.bdd_text,
                    encoding="utf-8",
                )
                txt_path = features_dir / f"{i:03d}_{safe_name}.txt"
                txt_path.write_text(
                    f"TÍTULO:\n{issue['title']}\n\n"
                    f"DESCRIÇÃO:\n{issue['description'] or '(sem descrição)'}\n\n"
                    f"STORY POINTS: {issue['storypoints']}\n\n"
                    f"USER STORY ENVIADA AO MODELO:\n{story}\n",
                    encoding="utf-8",
                )
                feature_file = str(feature_path)

            row = {
                "story_id":        i,
                "title":           issue["title"][:150],
                "model":           model,
                "score_final":     result.score.score_final,
                "cobertura":       result.score.cobertura,
                "clareza":         result.score.clareza,
                "estrutura":       result.score.estrutura,
                "executabilidade": result.score.executabilidade,
                "tentativas":      result.attempts,
                "tokens_usados":   result.total_tokens,
                "tokens_research": result.research_tokens,
                "tempo_segundos":  round(result.total_duration_seconds, 2),
                "aprovado":        result.score.aprovado,
                "convergiu":       result.converged,
                "feature_file":    feature_file,
            }
            writer.writerow(row)
            f.flush()

            converged_label = "[green]✓[/green]" if result.converged else "[yellow]✗[/yellow]"
            status = "[green]✓[/green]" if result.score.aprovado else "[red]✗[/red]"
            console.print(
                f"  {status} Score: {result.score.score_final:.1f} "
                f"| tentativas: {result.attempts} "
                f"| convergiu: {converged_label} "
                f"| {feature_filename}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# Commands
# ─────────────────────────────────────────────────────────────────────────────

@app.command()
def generate(
    story: str = typer.Option(..., "--story", "-s", help="User story para gerar BDD"),
    model: str = typer.Option("flash", "--model", "-m", help="Gemini: flash | pro | flash-lite  /  Claude: sonnet | opus | haiku"),
    threshold: float = typer.Option(7.0, "--threshold", "-t", help="Score mínimo (0-10)"),
    max_attempts: int = typer.Option(5, "--max-attempts", help="Máximo de tentativas (ignorado com --until-converged)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Pasta de saída (padrão: results/generate_<timestamp>/)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Mostrar tentativas"),
    research: bool = typer.Option(False, "--research", "-r", help="Habilitar auto-research antes da geração"),
    until_converged: bool = typer.Option(False, "--until-converged", "-u", help="Refinar até atingir threshold (max 50 tentativas)"),
):
    """Gera cenários BDD para uma user story com auto-refinamento."""
    run_dir = Path(output) if output else _new_run_dir("generate")

    research_label = " | [yellow]Auto-Research ON[/yellow]" if research else ""
    converge_label = " | [magenta]Until-Converged ON[/magenta]" if until_converged else ""
    console.print(Panel(
        f"[bold cyan]BDD Generator[/bold cyan] | Modelo: {model} | Threshold: {threshold}{research_label}{converge_label}"
    ))
    console.print(f"[bold]User Story:[/bold] {story}\n")

    loop = _make_loop(model, threshold, max_attempts, verbose, log_dir=str(run_dir), enable_research=research)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as p:
        p.add_task(
            "Pesquisando user story..." if research else "Gerando cenários BDD...",
            total=None,
        )
        result = loop.run(story, enable_research=research, until_converged=until_converged)
        p.stop()

    console.print(result.score.summary())
    research_info = f" | Research: {result.research_tokens} tokens" if result.research_tokens else ""
    converged_label = "[green]convergiu[/green]" if result.converged else "[yellow]não convergiu[/yellow]"
    console.print(
        f"\n[dim]Tentativas: {result.attempts} | Tokens: {result.total_tokens}"
        f"{research_info} | {result.total_duration_seconds:.1f}s | {converged_label}[/dim]"
    )

    if result.bdd_text:
        console.print("\n[bold green]Cenários gerados:[/bold green]")
        console.print(result.bdd_text)

        path = _save_feature(result.bdd_text, run_dir, "bdd.feature")
        console.print(f"\n[green]Salvo em:[/green] {path}")
    else:
        console.print("[red]Falha na geração.[/red]")
        raise typer.Exit(1)


@app.command()
def evaluate(
    story: str = typer.Option(..., "--story", "-s", help="User story"),
    bdd: str = typer.Option(..., "--bdd", "-b", help="Arquivo .feature ou texto BDD"),
    threshold: float = typer.Option(7.0, "--threshold", "-t"),
):
    """Avalia cenários BDD existentes sem gerar novos."""
    if Path(bdd).exists():
        bdd_text = Path(bdd).read_text(encoding="utf-8")
    else:
        bdd_text = bdd

    scorer = BDDScorer(threshold=threshold)
    score  = scorer.score(story, bdd_text)
    console.print(score.summary())


@app.command()
def batch(
    input: str = typer.Option(..., "--input", "-i", help="CSV com user stories"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Pasta de saída (padrão: results/batch_<timestamp>/)"),
    model: str = typer.Option("flash", "--model", "-m", help="Gemini: flash | pro | flash-lite  /  Claude: sonnet | opus | haiku"),
    threshold: float = typer.Option(7.0, "--threshold", "-t"),
    max_attempts: int = typer.Option(3, "--max-attempts", help="Máximo de tentativas por story (ignorado com --until-converged)"),
    sample: Optional[int] = typer.Option(None, "--sample", help="Processar N histórias"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    research: bool = typer.Option(False, "--research", "-r", help="Habilitar auto-research antes de cada geração"),
    until_converged: bool = typer.Option(False, "--until-converged", "-u", help="Só avança para próxima story após atingir threshold (max 50 tentativas)"),
    learn_from: Optional[str] = typer.Option(None, "--learn-from", "-l", help="JSON de insights gerado pelo comando study (few-shot)"),
):
    """Processa um CSV de user stories em lote. Salva métricas em CSV e cenários em .feature."""
    issues = _load_dataset(input)
    if sample:
        issues = random.sample(issues, min(sample, len(issues)))

    # Load few-shot context from study file
    study_context: Optional[str] = None
    if learn_from:
        if not Path(learn_from).exists():
            console.print(f"[red]Arquivo de insights não encontrado:[/red] {learn_from}")
            raise typer.Exit(1)
        study_context = load_study_context(learn_from)
        console.print(f"[green]Insights carregados de:[/green] {learn_from}")

    flags = []
    if research:        flags.append("[yellow]auto-research[/yellow]")
    if until_converged: flags.append("[magenta]until-converged[/magenta]")
    if learn_from:      flags.append("[green]few-shot[/green]")
    flags_label = f"  ({', '.join(flags)})" if flags else ""
    console.print(
        f"[bold]Processando {len(issues)} histórias[/bold] com modelo [cyan]{model}[/cyan]{flags_label}"
    )

    run_dir = Path(output) if output else _new_run_dir("batch")
    output_path = run_dir / "batch_results.csv"
    _run_batch_internal(
        issues=issues,
        output_path=output_path,
        model=model,
        threshold=threshold,
        max_attempts=max_attempts,
        verbose=verbose,
        research=research,
        until_converged=until_converged,
        study_context=study_context,
    )
    console.print(f"\n[green]Pasta:[/green]    {run_dir}/")
    console.print(f"[green]Métricas:[/green] {output_path.name}")
    console.print(f"[green]Cenários:[/green] features/")


@app.command()
def compare(
    input: str = typer.Option(..., "--input", "-i", help="CSV com user stories"),
    models: str = typer.Option("flash,pro,flash-lite", "--models", help="Modelos separados por vírgula"),
    sample: int = typer.Option(10, "--sample-size", help="Histórias por modelo"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Pasta de saída (padrão: results/compare_<timestamp>/)"),
    threshold: float = typer.Option(7.0, "--threshold", "-t"),
    max_attempts: int = typer.Option(3, "--max-attempts"),
):
    """Compara múltiplos modelos no mesmo dataset."""
    issues = _load_dataset(input)
    model_list = [m.strip() for m in models.split(",")]
    sample_issues = random.sample(issues, min(sample, len(issues)))

    console.print(f"[bold]Comparando modelos:[/bold] {', '.join(model_list)}")
    console.print(f"[bold]Histórias por modelo:[/bold] {len(sample_issues)}\n")

    run_dir = Path(output) if output else _new_run_dir("compare")
    output_path = run_dir / "compare_results.csv"

    import csv as _csv
    fieldnames = [
        "model", "story_id", "title", "score_final", "cobertura", "clareza",
        "estrutura", "executabilidade", "tentativas", "tokens_usados",
        "tempo_segundos", "aprovado",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = _csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for model in model_list:
            console.print(f"\n[cyan bold]Modelo: {model}[/cyan bold]")
            loop = _make_loop(model, threshold, max_attempts, verbose=False)

            for i, issue in enumerate(sample_issues, 1):
                story = issue["title"]
                if issue["description"]:
                    story += f". {issue['description'][:300]}"

                result = loop.run(story)
                row = {
                    "model":         model,
                    "story_id":      i,
                    "title":         issue["title"][:150],
                    "score_final":   result.score.score_final,
                    "cobertura":     result.score.cobertura,
                    "clareza":       result.score.clareza,
                    "estrutura":     result.score.estrutura,
                    "executabilidade": result.score.executabilidade,
                    "tentativas":    result.attempts,
                    "tokens_usados": result.total_tokens,
                    "tempo_segundos": round(result.total_duration_seconds, 2),
                    "aprovado":      result.score.aprovado,
                }
                writer.writerow(row)
                f.flush()

                status = "[green]✓[/green]" if result.score.aprovado else "[yellow]✗[/yellow]"
                console.print(f"  [{i}/{len(sample_issues)}] {status} {result.score.score_final:.1f}")

    console.print(f"\n[green]Pasta:[/green]    {run_dir}/")
    console.print(f"[green]Resultados:[/green] {output_path.name}")


@app.command()
def experiment(
    dataset: str = typer.Option(..., "--dataset", "-d", help="CSV do dataset"),
    models: str = typer.Option("flash,pro,flash-lite", "--models"),
    sample_size: int = typer.Option(100, "--sample-size"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Pasta de saída (padrão: results/experiment_<timestamp>/)"),
    threshold: float = typer.Option(7.0, "--threshold", "-t"),
    max_attempts: int = typer.Option(5, "--max-attempts"),
):
    """Executa experimento científico completo (variáveis independentes x dependentes)."""
    console.print(Panel("[bold cyan]Experimento BDD Generator[/bold cyan]"))
    console.print(f"Dataset: {dataset}")
    console.print(f"Modelos: {models}")
    console.print(f"Amostras: {sample_size} por modelo\n")

    issues = _load_dataset(dataset)
    model_list = [m.strip() for m in models.split(",")]
    sample_issues = random.sample(issues, min(sample_size, len(issues)))

    run_dir = Path(output) if output else _new_run_dir("experiment")
    output_path = run_dir / "experiment_results.csv"

    import csv as _csv
    fieldnames = [
        "story_id", "title", "description", "storypoints", "model",
        "score_final", "cobertura", "clareza", "estrutura", "executabilidade",
        "tentativas", "tokens_usados", "tempo_segundos", "aprovado",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = _csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for model in model_list:
            console.print(f"\n[cyan bold]=== Modelo: {model} ===[/cyan bold]")
            loop = _make_loop(model, threshold, max_attempts, verbose=False)
            approved = 0

            for i, issue in enumerate(sample_issues, 1):
                story = issue["title"]
                if issue["description"]:
                    story += f". {issue['description'][:400]}"

                result = loop.run(story)

                if result.score.aprovado:
                    approved += 1

                row = {
                    "story_id":      i,
                    "title":         issue["title"][:150],
                    "description":   issue["description"][:300],
                    "storypoints":   issue["storypoints"],
                    "model":         model,
                    "score_final":   result.score.score_final,
                    "cobertura":     result.score.cobertura,
                    "clareza":       result.score.clareza,
                    "estrutura":     result.score.estrutura,
                    "executabilidade": result.score.executabilidade,
                    "tentativas":    result.attempts,
                    "tokens_usados": result.total_tokens,
                    "tempo_segundos": round(result.total_duration_seconds, 2),
                    "aprovado":      result.score.aprovado,
                }
                writer.writerow(row)
                f.flush()

                if i % 10 == 0:
                    console.print(f"  {i}/{len(sample_issues)} | Aprovados: {approved}/{i} ({100*approved/i:.0f}%)")

            console.print(f"  [bold]Resultado {model}:[/bold] {approved}/{len(sample_issues)} aprovados ({100*approved/len(sample_issues):.1f}%)")

    console.print(f"\n[green]Pasta:[/green]      {run_dir}/")
    console.print(f"[green]Experimento:[/green] {output_path.name}")


@app.command()
def study(
    results: str = typer.Option(..., "--results", "-r", help="CSV gerado pelo comando batch"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Arquivo de saída (padrão: results/study_<timestamp>/insights.json)"),
    model: str = typer.Option("flash", "--model", "-m"),
    top_n: int = typer.Option(5, "--top-n", help="Quantos melhores BDDs analisar"),
    bottom_n: int = typer.Option(3, "--bottom-n", help="Quantos piores BDDs analisar (anti-padrões)"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """Analisa resultados de um batch e gera insights para melhorar gerações futuras."""
    if not Path(results).exists():
        console.print(f"[red]Arquivo não encontrado:[/red] {results}")
        raise typer.Exit(1)

    if output:
        insights_path = Path(output)
        insights_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        run_dir = _new_run_dir("study")
        insights_path = run_dir / "insights.json"

    console.print(Panel(
        f"[bold cyan]BDD Study[/bold cyan] | Modelo: {model} | Top: {top_n} | Bottom: {bottom_n}"
    ))
    console.print(f"[bold]Analisando:[/bold] {results}\n")

    generator = _make_generator(model)
    analyzer  = BatchAnalyzer(generator=generator, verbose=verbose)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as p:
        p.add_task("Analisando BDDs e gerando insights...", total=None)
        study_result = analyzer.analyze(
            results_csv=results,
            output_path=str(insights_path),
            top_n=top_n,
            bottom_n=bottom_n,
        )

    console.print("\n[bold green]Insights gerados:[/bold green]")
    console.print(study_result.insights[:1500] + ("..." if len(study_result.insights) > 1500 else ""))
    console.print(
        f"\n[dim]Tokens: {study_result.input_tokens + study_result.output_tokens} "
        f"| {study_result.duration_seconds:.1f}s[/dim]"
    )
    console.print(f"\n[green]Salvo em:[/green] {study_result.output_path}")
    console.print(
        f"\n[dim]Use no próximo batch com:[/dim] "
        f"[cyan]--learn-from {study_result.output_path}[/cyan]"
    )


@app.command()
def pipeline(
    input: str = typer.Option(..., "--input", "-i", help="CSV com user stories"),
    output_dir: Optional[str] = typer.Option(None, "--output-dir", "-o", help="Pasta raiz (padrão: results/pipeline_<timestamp>/)"),
    model: str = typer.Option("flash", "--model", "-m", help="Gemini: flash | pro | flash-lite  /  Claude: sonnet | opus | haiku"),
    threshold: float = typer.Option(7.0, "--threshold", "-t", help="Score mínimo (0-10)"),
    max_attempts: int = typer.Option(3, "--max-attempts", help="Máximo de tentativas por story"),
    sample: Optional[int] = typer.Option(None, "--sample", help="Processar N histórias (mesmo sample nas duas fases)"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    research: bool = typer.Option(False, "--research", "-r", help="Habilitar auto-research em ambas as fases"),
    until_converged: bool = typer.Option(False, "--until-converged", "-u", help="Refinar até atingir threshold (max 50 tentativas)"),
    study_model: str = typer.Option("flash", "--study-model", help="Modelo para a fase de estudo (pode ser diferente do batch)"),
    top_n: int = typer.Option(5, "--top-n", help="Quantos melhores BDDs analisar no study"),
    bottom_n: int = typer.Option(3, "--bottom-n", help="Quantos piores BDDs analisar no study"),
):
    """Pipeline completo: gera BDD → estuda resultados → gera novamente com os insights aprendidos."""
    base = Path(output_dir) if output_dir else _new_run_dir("pipeline")
    run1_csv      = base / "run1" / "batch_results.csv"
    insights_path = base / "study_insights.json"
    run2_csv      = base / "run2" / "batch_results.csv"

    issues = _load_dataset(input)
    if sample:
        issues = random.sample(issues, min(sample, len(issues)))

    flags = []
    if research:        flags.append("[yellow]auto-research[/yellow]")
    if until_converged: flags.append("[magenta]until-converged[/magenta]")
    flags_label = f"  ({', '.join(flags)})" if flags else ""

    console.print(Panel(
        f"[bold cyan]BDD Pipeline[/bold cyan] | Modelo: {model} | Study: {study_model} | Threshold: {threshold}{flags_label}"
    ))
    console.print(f"[bold]Dataset:[/bold] {input} | {len(issues)} histórias\n")

    # ── Fase 1: Geração inicial ───────────────────────────────────────────────
    console.print(Panel("[bold]Fase 1/3 — Geração inicial[/bold]", style="blue"))
    _run_batch_internal(
        issues=issues,
        output_path=run1_csv,
        model=model,
        threshold=threshold,
        max_attempts=max_attempts,
        verbose=verbose,
        research=research,
        until_converged=until_converged,
    )
    console.print(f"\n[green]Fase 1 concluída:[/green] {run1_csv}\n")

    # ── Fase 2: Estudo dos resultados ─────────────────────────────────────────
    console.print(Panel("[bold]Fase 2/3 — Estudo e extração de insights[/bold]", style="yellow"))
    generator = _make_generator(study_model)
    analyzer  = BatchAnalyzer(generator=generator, verbose=verbose)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as p:
        p.add_task("Analisando BDDs e gerando insights...", total=None)
        study_result = analyzer.analyze(
            results_csv=str(run1_csv),
            output_path=str(insights_path),
            top_n=top_n,
            bottom_n=bottom_n,
        )

    console.print("\n[bold green]Insights gerados:[/bold green]")
    console.print(study_result.insights[:1000] + ("..." if len(study_result.insights) > 1000 else ""))
    console.print(f"\n[green]Fase 2 concluída:[/green] {insights_path}\n")

    # ── Fase 3: Re-geração com insights ──────────────────────────────────────
    console.print(Panel("[bold]Fase 3/3 — Re-geração com insights aprendidos[/bold]", style="green"))
    study_context = load_study_context(str(insights_path))
    _run_batch_internal(
        issues=issues,
        output_path=run2_csv,
        model=model,
        threshold=threshold,
        max_attempts=max_attempts,
        verbose=verbose,
        research=research,
        until_converged=until_converged,
        study_context=study_context,
    )
    console.print(f"\n[green]Fase 3 concluída:[/green] {run2_csv}\n")

    # ── Resumo comparativo ────────────────────────────────────────────────────
    import csv as _csv

    def _avg_score(csv_path: Path) -> float:
        scores = []
        try:
            with open(csv_path, encoding="utf-8") as f:
                for row in _csv.DictReader(f):
                    try:
                        scores.append(float(row["score_final"]))
                    except (KeyError, ValueError):
                        pass
        except FileNotFoundError:
            pass
        return sum(scores) / len(scores) if scores else 0.0

    avg1 = _avg_score(run1_csv)
    avg2 = _avg_score(run2_csv)
    delta = avg2 - avg1
    delta_color = "green" if delta >= 0 else "red"
    delta_sign  = "+" if delta >= 0 else ""

    console.print(Panel(
        f"[bold]Score médio Fase 1:[/bold] {avg1:.2f}/10\n"
        f"[bold]Score médio Fase 3:[/bold] {avg2:.2f}/10\n"
        f"[bold]Variação:[/bold] [{delta_color}]{delta_sign}{delta:.2f}[/{delta_color}]\n\n"
        f"[dim]Run 1:    {run1_csv}\n"
        f"Insights: {insights_path}\n"
        f"Run 2:    {run2_csv}[/dim]",
        title="[bold cyan]Resultado do Pipeline[/bold cyan]",
    ))


# ─────────────────────────────────────────────────────────────────────────────
# Subapp: auth
# ─────────────────────────────────────────────────────────────────────────────

auth_app = typer.Typer(help="Autenticação com a plataforma BDD Generator (modo managed).")
app.add_typer(auth_app, name="auth")


@auth_app.command("login")
def auth_login(
    token: str = typer.Option(..., "--token", "-t", help="API token gerado em bdd-generator.com/settings/tokens"),
    api_url: str = typer.Option(MANAGED_API_URL, "--api-url", hidden=True),
):
    """Autentica o CLI com sua conta BDD Generator (modo managed)."""
    console.print("[dim]Validando token...[/dim]")

    user_info = validate_token(token, api_url)
    if not user_info:
        console.print("[red]Token inválido ou expirado.[/red]")
        console.print("[dim]Gere um novo em: bdd-generator.com/settings/tokens[/dim]")
        raise typer.Exit(1)

    auth = AuthState(
        token=token,
        user_email=user_info.get("email", ""),
        user_name=user_info.get("name", ""),
        plan=user_info.get("plan", "free"),
        api_url=api_url,
    )
    save_config(Config(mode="managed", auth=auth))

    plan_label = "[magenta]Pro[/magenta]" if auth.plan == "pro" else "[yellow]Free[/yellow]"
    console.print(Panel(
        f"[green]Autenticado com sucesso![/green]\n\n"
        f"  Usuário: [bold]{auth.user_name}[/bold] ({auth.user_email})\n"
        f"  Plano:   {plan_label}",
        title="bdd auth login",
    ))


@auth_app.command("logout")
def auth_logout():
    """Remove as credenciais salvas e volta para o modo BYOK."""
    config = load_config()
    if config.mode == "byok":
        console.print("[yellow]Você não está autenticado.[/yellow]")
        return
    clear_auth()
    console.print("[green]Sessão encerrada. Voltando para modo BYOK.[/green]")


@auth_app.command("status")
def auth_status():
    """Exibe o modo atual (BYOK ou managed) e informações do usuário."""
    config = load_config()

    if config.mode == "byok" or not config.auth:
        console.print(Panel(
            "[cyan]Modo:[/cyan] [bold]BYOK[/bold] (Bring Your Own Key)\n\n"
            "Você está usando sua própria API key (GEMINI_API_KEY / ANTHROPIC_API_KEY).\n"
            "Para usar o modo managed: [bold]bdd auth login --token <TOKEN>[/bold]",
            title="bdd auth status",
        ))
        return

    plan_label = "[magenta]Pro ♾ ilimitado[/magenta]" if config.auth.plan == "pro" else "[yellow]Free[/yellow]"
    quota = get_quota()

    quota_str = ""
    if quota:
        if quota.tokens_limit == -1:
            quota_str = "\n  Tokens:  [magenta]ilimitado[/magenta]"
        else:
            pct = int((quota.tokens_used / quota.tokens_limit) * 100) if quota.tokens_limit > 0 else 0
            bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
            quota_str = (
                f"\n  Tokens:  {quota.tokens_used:,} / {quota.tokens_limit:,} ({pct}%)"
                f"\n           [{bar}]"
                f"\n  Gerações: {quota.generations_used}"
                f"\n  Reset:   {quota.reset_at[:10]}"
            )

    console.print(Panel(
        f"[cyan]Modo:[/cyan] [bold]Managed[/bold]\n\n"
        f"  Usuário: [bold]{config.auth.user_name}[/bold] ({config.auth.user_email})\n"
        f"  Plano:   {plan_label}"
        f"{quota_str}",
        title="bdd auth status",
    ))


@auth_app.command("quota")
def auth_quota():
    """Exibe a cota de tokens do mês atual (apenas modo managed)."""
    if not is_authenticated():
        console.print("[yellow]Você está em modo BYOK — sem cota.[/yellow]")
        console.print("[dim]Para usar modo managed: bdd auth login --token <TOKEN>[/dim]")
        return

    quota = get_quota()
    if not quota:
        console.print("[red]Não foi possível obter a cota. Verifique sua conexão.[/red]")
        raise typer.Exit(1)

    if quota.tokens_limit == -1:
        console.print("[magenta]Plano Pro — tokens ilimitados.[/magenta]")
        return

    used_pct = int((quota.tokens_used / quota.tokens_limit) * 100) if quota.tokens_limit > 0 else 0
    remaining = quota.tokens_remaining
    color = "green" if used_pct < 70 else "yellow" if used_pct < 90 else "red"

    console.print(Panel(
        f"  Tokens usados:     [{color}]{quota.tokens_used:,}[/{color}] / {quota.tokens_limit:,}\n"
        f"  Tokens restantes:  [bold]{remaining:,}[/bold]\n"
        f"  Gerações este mês: {quota.generations_used}\n"
        f"  Reset em:          {quota.reset_at[:10]}",
        title="[bold]Cota Mensal[/bold]",
    ))


if __name__ == "__main__":
    app()
