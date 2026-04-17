#!/usr/bin/env python3
"""
BIST - BDD Intelligent Self-healing Tests
The AI-powered testing agent you own.

Commands:
  bist generate  --user-story STORY  --output tests/login.feature
  bist execute   --feature tests/login.feature  --env https://staging.app.com
  bist full      --user-story STORY  --env https://staging.app.com
  bist evaluate  --story STORY  --bdd tests/login.feature
  bist stats
  bist report
"""

__version__ = "0.1.0"
__author__ = "QA Lab"
__license__ = "MIT"

import sys
import time
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

console = Console()


# ── CLI group ────────────────────────────────────────────────────────────────

@click.group()
@click.version_option(__version__, prog_name="bist")
def cli():
    """BIST — BDD Intelligent Self-healing Tests."""


# ── generate ─────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--user-story", "-s", required=True,
              help="User story text or path to a .md / .txt file")
@click.option("--output", "-o", default=None,
              help="Output .feature file path (auto-named if omitted)")
@click.option("--model", "-m", default="sonnet",
              help="LLM model: sonnet | opus | haiku | flash | pro")
@click.option("--threshold", "-t", default=7.0, type=float,
              help="Minimum quality score 0–10  (default 7.0)")
@click.option("--max-attempts", default=5, type=int,
              help="Max refinement attempts (default 5)")
@click.option("--until-converged", is_flag=True,
              help="Keep refining until threshold is met (max 50)")
@click.option("--research", is_flag=True,
              help="Enable auto-research before first generation")
@click.option("--verbose", "-v", is_flag=True)
def generate(user_story, output, model, threshold, max_attempts, until_converged, research, verbose):
    """Generate a .feature file from a user story using AI + auto-refinement."""
    from bist.bist_agent import BISTAgent

    story_path = Path(user_story)
    if story_path.exists():
        user_story = story_path.read_text(encoding="utf-8").strip()

    console.print(Panel(
        f"[bold cyan]BIST Generate[/bold cyan]  model={model}  threshold={threshold}",
        subtitle=user_story[:80],
    ))

    agent = BISTAgent(
        model=model,
        threshold=threshold,
        max_attempts=max_attempts,
        verbose=verbose,
        enable_research=research,
        until_converged=until_converged,
    )

    with console.status("Generating BDD scenarios..."):
        result = agent.generate(user_story, output_path=output)

    if not result.bdd_text:
        console.print("[red]Generation failed.[/red]")
        sys.exit(1)

    converged = "[green]converged[/green]" if result.converged else "[yellow]not converged[/yellow]"
    console.print(f"\nScore: [bold]{result.score_final:.1f}/10[/bold] | {converged}")
    console.print(f"Attempts: {result.attempts} | Tokens: {result.total_tokens} | {result.duration_seconds:.1f}s")
    console.print(f"[green]Saved:[/green] {result.feature_path}")
    console.print("\n" + result.bdd_text)


# ── execute ───────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--feature", "-f", required=True, help="Path to .feature file")
@click.option("--env", "-e", required=True, help="Target environment URL")
@click.option("--headless/--headed", default=True)
@click.option("--no-heal", is_flag=True, help="Disable AI self-healing")
@click.option("--report", "report_fmt", default="html",
              type=click.Choice(["html", "json", "github", "all"]))
@click.option("--output-dir", default="bist_output")
@click.option("--parallel", "-p", default=1, type=int,
              help="Max concurrent browser instances (default 1)")
def execute(feature, env, headless, no_heal, report_fmt, output_dir, parallel):
    """Execute a .feature file against a live environment using Playwright."""
    from bist.bist_executor import BISTExecutor
    from bist.bist_reporter import BISTReporter
    from bist.bist_database import BISTDatabase
    from bist.bist_notifier import BISTNotifier

    if not Path(feature).exists():
        console.print(f"[red]Feature file not found:[/red] {feature}")
        sys.exit(1)

    db = BISTDatabase()
    executor = BISTExecutor(
        db=db,
        screenshots_dir=f"{output_dir}/screenshots",
        videos_dir=f"{output_dir}/videos",
        headless=headless,
        self_heal=not no_heal,
        parallel=parallel,
    )
    reporter = BISTReporter(output_dir=f"{output_dir}/reports")

    console.print(Panel(
        f"[bold cyan]BIST Execute[/bold cyan]  {feature} → {env}"
        + (f"  parallel={parallel}" if parallel > 1 else "")
    ))

    with console.status("Running Playwright tests..."):
        result = executor.execute(feature, env)

    _print_summary(result)

    html_path = ""
    if report_fmt in ("html", "all"):
        html_path = reporter.html_report(result)
        console.print(f"[green]HTML:[/green] {html_path}")
    if report_fmt in ("json", "all"):
        console.print(f"[green]JSON:[/green] {reporter.json_report(result)}")
    if report_fmt in ("github", "all"):
        annotations = reporter.github_annotations(result)
        if annotations:
            click.echo(annotations)

    notifier = BISTNotifier()
    if notifier.enabled:
        with console.status("Sending notifications..."):
            notifier.notify(result, html_path)

    sys.exit(0 if result.status == "passed" else 1)


# ── full ──────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--user-story", "-s", required=True)
@click.option("--env", "-e", required=True, help="Target environment URL")
@click.option("--model", "-m", default="sonnet")
@click.option("--threshold", "-t", default=7.0, type=float)
@click.option("--max-attempts", default=5, type=int)
@click.option("--headless/--headed", default=True)
@click.option("--no-heal", is_flag=True)
@click.option("--output-dir", default="bist_output")
@click.option("--parallel", "-p", default=1, type=int,
              help="Max concurrent browser instances (default 1)")
@click.option("--verbose", "-v", is_flag=True)
def full(user_story, env, model, threshold, max_attempts, headless, no_heal, output_dir, parallel, verbose):
    """Full pipeline: generate .feature from story → execute against environment."""
    from bist.bist_agent import BISTAgent
    from bist.bist_executor import BISTExecutor
    from bist.bist_reporter import BISTReporter
    from bist.bist_database import BISTDatabase
    from bist.bist_notifier import BISTNotifier

    story_path = Path(user_story)
    if story_path.exists():
        user_story = story_path.read_text(encoding="utf-8").strip()

    console.print(Panel(
        f"[bold cyan]BIST Full Pipeline[/bold cyan]\n"
        f"model={model}  threshold={threshold}  env={env}"
    ))

    # Step 1: Generate
    console.print("\n[bold]Step 1/2[/bold] — Generating BDD scenarios...")
    agent = BISTAgent(
        model=model,
        threshold=threshold,
        max_attempts=max_attempts,
        verbose=verbose,
    )
    with console.status("Generating..."):
        gen = agent.generate(user_story)

    if not gen.bdd_text:
        console.print("[red]Generation failed.[/red]")
        sys.exit(1)

    converged = "[green]converged[/green]" if gen.converged else "[yellow]not converged[/yellow]"
    console.print(f"[green]✓[/green] Score {gen.score_final:.1f}/10 | {converged} | {gen.feature_path}")

    # Step 2: Execute
    console.print("\n[bold]Step 2/2[/bold] — Running Playwright tests...")
    db = BISTDatabase()
    executor = BISTExecutor(
        db=db,
        screenshots_dir=f"{output_dir}/screenshots",
        videos_dir=f"{output_dir}/videos",
        headless=headless,
        self_heal=not no_heal,
        parallel=parallel,
    )
    reporter = BISTReporter(output_dir=f"{output_dir}/reports")

    with console.status("Executing..."):
        exec_result = executor.execute(gen.feature_path, env)

    _print_summary(exec_result)
    html_path = reporter.html_report(exec_result)
    console.print(f"[green]HTML:[/green] {html_path}")
    console.print(f"[green]JSON:[/green] {reporter.json_report(exec_result)}")

    notifier = BISTNotifier()
    if notifier.enabled:
        with console.status("Sending notifications..."):
            notifier.notify(exec_result, html_path)

    sys.exit(0 if exec_result.status == "passed" else 1)


# ── evaluate ──────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--story", "-s", required=True, help="User story text")
@click.option("--bdd", "-b", required=True, help="Path to .feature file or raw BDD text")
@click.option("--threshold", "-t", default=7.0, type=float)
def evaluate(story, bdd, threshold):
    """Evaluate existing BDD scenarios without generating new ones."""
    from src.evaluators.scorer import BDDScorer

    bdd_path = Path(bdd)
    bdd_text = bdd_path.read_text(encoding="utf-8") if bdd_path.exists() else bdd

    scorer = BDDScorer(threshold=threshold)
    console.print(scorer.score(story, bdd_text).summary())


# ── stats ─────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--limit", "-n", default=20, type=int, help="Rows to show (default 20)")
def stats(limit):
    """Show test run history from the local SQLite database."""
    from bist.bist_database import BISTDatabase

    runs = BISTDatabase().get_runs(limit=limit)
    if not runs:
        console.print("[yellow]No test runs found.[/yellow]")
        return

    tbl = Table(title="BIST Test History", show_lines=True)
    tbl.add_column("ID", style="dim", justify="right")
    tbl.add_column("Date")
    tbl.add_column("Environment")
    tbl.add_column("Feature")
    tbl.add_column("Status")
    tbl.add_column("Duration", justify="right")

    for run in runs:
        sc = "green" if run["status"] == "passed" else ("yellow" if run["status"] == "running" else "red")
        ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(run["started_at"]))
        tbl.add_row(
            str(run["id"]),
            ts,
            run["env_url"][:40],
            Path(run["feature_path"]).name if run["feature_path"] else "-",
            f"[{sc}]{run['status']}[/{sc}]",
            f"{run['duration_ms']:,}ms",
        )

    console.print(tbl)


# ── report ────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--run-id", "-r", default=None, type=int,
              help="Run ID to report (defaults to most recent)")
@click.option("--format", "fmt", default="html",
              type=click.Choice(["html", "json"]))
@click.option("--output", "-o", default=None, help="Output file path")
def report(run_id, fmt, output):
    """Generate a report from a past test run stored in the database."""
    from bist.bist_database import BISTDatabase
    from bist.bist_reporter import BISTReporter

    db = BISTDatabase()
    if run_id is None:
        runs = db.get_runs(limit=1)
        if not runs:
            console.print("[yellow]No runs found.[/yellow]")
            return
        run_id = runs[0]["id"]

    data = db.get_run_detail(run_id)
    if not data:
        console.print(f"[red]Run {run_id} not found.[/red]")
        return

    result = _db_to_result(data)
    reporter = BISTReporter()
    path = reporter.html_report(result, output) if fmt == "html" else reporter.json_report(result, output)
    console.print(f"[green]Report saved:[/green] {path}")


# ── baseline ──────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--feature", "-f", required=True, help="Path to .feature file")
@click.option("--env", "-e", required=True, help="Target environment URL")
@click.option("--headless/--headed", default=True)
@click.option("--output-dir", default="bist_output")
def baseline(feature, env, headless, output_dir):
    """Capture baseline screenshots for visual regression testing."""
    import asyncio
    from playwright.async_api import async_playwright
    from bist.bist_parser import parse_feature_file
    from bist.bist_visual import BISTVisual

    if not Path(feature).exists():
        console.print(f"[red]Feature file not found:[/red] {feature}")
        sys.exit(1)

    visual = BISTVisual(baselines_dir=f"{output_dir}/baselines")
    feature_obj = parse_feature_file(feature)
    captured = 0

    async def _capture():
        nonlocal captured
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=headless)
            for scenario in feature_obj.scenarios:
                context = await browser.new_context()
                page = await context.new_page()
                all_steps = list(feature_obj.background_steps) + list(scenario.steps)
                for idx, step in enumerate(all_steps):
                    await visual.capture_baseline(page, scenario.name, idx)
                    captured += 1
                await context.close()
            await browser.close()

    console.print(Panel(f"[bold cyan]BIST Baseline[/bold cyan]  {feature} → {env}"))
    with console.status("Capturing baselines..."):
        asyncio.run(_capture())

    console.print(f"[green]Captured {captured} baseline screenshots → {output_dir}/baselines[/green]")


# ── visual-diff ────────────────────────────────────────────────────────────────

@cli.command("visual-diff")
@click.option("--feature", "-f", required=True, help="Path to .feature file")
@click.option("--env", "-e", required=True, help="Target environment URL")
@click.option("--threshold", "-t", default=0.01, type=float,
              help="Max allowed diff ratio 0–1 (default 0.01 = 1%)")
@click.option("--headless/--headed", default=True)
@click.option("--output-dir", default="bist_output")
def visual_diff(feature, env, threshold, headless, output_dir):
    """Run visual regression diff against captured baselines."""
    import asyncio
    from playwright.async_api import async_playwright
    from bist.bist_parser import parse_feature_file
    from bist.bist_visual import BISTVisual
    from rich.table import Table as RTable

    if not Path(feature).exists():
        console.print(f"[red]Feature file not found:[/red] {feature}")
        sys.exit(1)

    visual = BISTVisual(
        baselines_dir=f"{output_dir}/baselines",
        current_dir=f"{output_dir}/visual_current",
        diffs_dir=f"{output_dir}/visual_diffs",
        threshold=threshold,
    )
    feature_obj = parse_feature_file(feature)
    results = []

    async def _diff():
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=headless)
            for scenario in feature_obj.scenarios:
                context = await browser.new_context()
                page = await context.new_page()
                all_steps = list(feature_obj.background_steps) + list(scenario.steps)
                for idx, step in enumerate(all_steps):
                    r = await visual.compare(page, scenario.name, idx, threshold)
                    results.append(r)
                await context.close()
            await browser.close()

    console.print(Panel(f"[bold cyan]BIST Visual Diff[/bold cyan]  threshold={threshold:.1%}"))
    with console.status("Comparing screenshots..."):
        asyncio.run(_diff())

    tbl = RTable(title="Visual Diff Results", show_lines=True)
    tbl.add_column("Scenario")
    tbl.add_column("Step", justify="right")
    tbl.add_column("Diff %", justify="right")
    tbl.add_column("Status")
    tbl.add_column("Diff Image")

    failures = 0
    for r in results:
        sc = "green" if r.passed else "red"
        label = "[green]PASS[/green]" if r.passed else "[red]FAIL[/red]"
        if not r.passed:
            failures += 1
        tbl.add_row(
            r.scenario_name[:45],
            str(r.step_idx),
            f"[{sc}]{r.diff_ratio:.2%}[/{sc}]",
            label,
            Path(r.diff_path).name if r.diff_path else "-",
        )

    console.print(tbl)
    if failures:
        console.print(f"[red]{failures} visual regression(s) detected.[/red]")
        sys.exit(1)
    else:
        console.print("[green]All visual checks passed.[/green]")


# ── e2e subgroup ─────────────────────────────────────────────────────────────

@cli.group()
def e2e():
    """End-to-end test commands."""


@e2e.command("execute")
@click.option("--feature", "-f", required=True, help="Path to .feature file")
@click.option("--env", "-e", required=True, help="Target environment URL")
@click.option("--headless/--headed", default=True)
@click.option("--no-heal", is_flag=True, help="Disable AI self-healing")
@click.option("--report", "report_fmt", default="html",
              type=click.Choice(["html", "json", "github", "all"]))
@click.option("--output-dir", default="bist_output")
@click.option("--parallel", "-p", default=1, type=int,
              help="Max concurrent browser instances (default 1)")
def e2e_execute(feature, env, headless, no_heal, report_fmt, output_dir, parallel):
    """Execute a .feature file via the e2e subgroup (alias of `bist execute`)."""
    from bist.bist_executor import BISTExecutor
    from bist.bist_reporter import BISTReporter
    from bist.bist_database import BISTDatabase
    from bist.bist_notifier import BISTNotifier

    if not Path(feature).exists():
        console.print(f"[red]Feature file not found:[/red] {feature}")
        sys.exit(1)

    db = BISTDatabase()
    executor = BISTExecutor(
        db=db,
        screenshots_dir=f"{output_dir}/screenshots",
        videos_dir=f"{output_dir}/videos",
        headless=headless,
        self_heal=not no_heal,
        parallel=parallel,
    )
    reporter = BISTReporter(output_dir=f"{output_dir}/reports")

    console.print(Panel(
        f"[bold cyan]BIST e2e execute[/bold cyan]  {feature} → {env}"
        + (f"  parallel={parallel}" if parallel > 1 else "")
    ))

    with console.status("Running Playwright tests..."):
        result = executor.execute(feature, env)

    _print_summary(result)

    html_path = ""
    if report_fmt in ("html", "all"):
        html_path = reporter.html_report(result)
        console.print(f"[green]HTML:[/green] {html_path}")
    if report_fmt in ("json", "all"):
        console.print(f"[green]JSON:[/green] {reporter.json_report(result)}")
    if report_fmt in ("github", "all"):
        annotations = reporter.github_annotations(result)
        if annotations:
            click.echo(annotations)

    notifier = BISTNotifier()
    if notifier.enabled:
        with console.status("Sending notifications..."):
            notifier.notify(result, html_path)

    sys.exit(0 if result.status == "passed" else 1)


# ── helpers ───────────────────────────────────────────────────────────────────

def _print_summary(result) -> None:
    total = len(result.scenarios)
    passed = sum(1 for s in result.scenarios if s.status == "passed")

    tbl = Table(show_header=True, header_style="bold")
    tbl.add_column("Scenario")
    tbl.add_column("Status")
    tbl.add_column("Steps")
    tbl.add_column("Duration", justify="right")

    for sc in result.scenarios:
        sc_passed = sum(1 for s in sc.steps if s.status == "passed")
        sym = "[green]✓[/green]" if sc.status == "passed" else "[red]✗[/red]"
        tbl.add_row(sc.name[:55], sym, f"{sc_passed}/{len(sc.steps)}", f"{sc.duration_ms:,}ms")

    console.print(tbl)
    color = "green" if result.status == "passed" else "red"
    console.print(
        f"\n[{color}]{'PASSED' if result.status == 'passed' else 'FAILED'}[/{color}] "
        f"— {passed}/{total} scenarios | {result.duration_ms:,}ms"
    )


def _db_to_result(data: dict):
    from bist.bist_executor import ExecutionResult, ScenarioResult, StepResult

    scenarios = []
    for sc in data.get("scenarios", []):
        steps = [
            StepResult(
                step_text=st["step_text"],
                keyword=st["step_text"].split()[0] if st["step_text"] else "",
                status=st["status"],
                duration_ms=st["duration_ms"],
                screenshot_path=st.get("screenshot_path", ""),
            )
            for st in sc.get("steps", [])
        ]
        scenarios.append(ScenarioResult(
            name=sc["name"],
            status=sc["status"],
            duration_ms=sc["duration_ms"],
            steps=steps,
            video_path=sc.get("video_path", ""),
            error=sc.get("error", ""),
        ))

    return ExecutionResult(
        feature_path=data.get("feature_path", ""),
        env_url=data.get("env_url", ""),
        status=data.get("status", "unknown"),
        duration_ms=data.get("duration_ms", 0),
        scenarios=scenarios,
        run_id=data.get("id"),
    )


if __name__ == "__main__":
    cli()
