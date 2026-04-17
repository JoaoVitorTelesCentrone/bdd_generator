"""
Tests for bist/bist_reporter.py — HTML, JSON, and GitHub Actions reports.

Cenários cobertos:
  - json_report cria arquivo JSON válido no disco
  - JSON contém summary com total/passed/failed corretos
  - JSON contém lista de scenarios com steps aninhados
  - json_report usa path fornecido quando especificado
  - html_report cria arquivo HTML no disco
  - HTML contém status do run (PASSED / FAILED)
  - HTML contém nomes dos cenários
  - HTML marca steps healed com badge especial
  - HTML inclui link para screenshot quando presente
  - github_annotations retorna string vazia quando tudo passa
  - github_annotations emite ::error para cada step falho
  - Múltiplas falhas geram múltiplas anotações
  - pass_rate é 100% para runs totalmente passando
  - pass_rate é 0% para runs totalmente falhando
"""
import sys, os, json, textwrap
from pathlib import Path
from dataclasses import dataclass, field
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest
from bist.bist_reporter import BISTReporter
from bist.bist_executor import ExecutionResult, ScenarioResult, StepResult


# ── factories ─────────────────────────────────────────────────────────────────

def _step(text="Given step", status="passed", error="", screenshot="", healed=False) -> StepResult:
    return StepResult(
        step_text=text,
        keyword=text.split()[0],
        status=status,
        duration_ms=50,
        error=error,
        screenshot_path=screenshot,
        healed=healed,
    )


def _scenario(name="Login", status="passed", steps=None, error="", video="") -> ScenarioResult:
    return ScenarioResult(
        name=name,
        status=status,
        duration_ms=200,
        steps=steps or [_step()],
        error=error,
        video_path=video,
    )


def _result(
    feature="tests/login.feature",
    env="https://staging.app.com",
    status="passed",
    scenarios=None,
    run_id=1,
) -> ExecutionResult:
    return ExecutionResult(
        feature_path=feature,
        env_url=env,
        status=status,
        duration_ms=500,
        scenarios=scenarios or [_scenario()],
        run_id=run_id,
    )


@pytest.fixture
def reporter(tmp_path):
    return BISTReporter(output_dir=str(tmp_path / "reports"))


# ── JSON report ───────────────────────────────────────────────────────────────

class TestJsonReport:
    """Cenário: json_report cria arquivo JSON válido"""

    def test_creates_json_file(self, reporter, tmp_path):
        result = _result()
        path = reporter.json_report(result)
        assert Path(path).exists()
        assert path.endswith(".json")

    def test_output_is_valid_json(self, reporter):
        result = _result()
        path = reporter.json_report(result)
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_summary_total_correct(self, reporter):
        result = _result(scenarios=[_scenario("A"), _scenario("B"), _scenario("C")])
        data = json.loads(Path(reporter.json_report(result)).read_text())
        assert data["summary"]["total"] == 3

    def test_summary_passed_count(self, reporter):
        result = _result(scenarios=[
            _scenario("A", status="passed"),
            _scenario("B", status="passed"),
            _scenario("C", status="failed"),
        ])
        data = json.loads(Path(reporter.json_report(result)).read_text())
        assert data["summary"]["passed"] == 2
        assert data["summary"]["failed"] == 1

    def test_summary_all_failed(self, reporter):
        result = _result(
            status="failed",
            scenarios=[_scenario("A", "failed"), _scenario("B", "failed")],
        )
        data = json.loads(Path(reporter.json_report(result)).read_text())
        assert data["summary"]["passed"] == 0
        assert data["summary"]["failed"] == 2

    def test_scenarios_present_in_json(self, reporter):
        result = _result(scenarios=[_scenario("Login"), _scenario("Checkout")])
        data = json.loads(Path(reporter.json_report(result)).read_text())
        names = [s["name"] for s in data["scenarios"]]
        assert "Login" in names
        assert "Checkout" in names

    def test_steps_nested_in_scenarios(self, reporter):
        steps = [_step("Given step 1"), _step("When action"), _step("Then result")]
        result = _result(scenarios=[_scenario("Scenario", steps=steps)])
        data = json.loads(Path(reporter.json_report(result)).read_text())
        assert len(data["scenarios"][0]["steps"]) == 3

    def test_env_url_in_json(self, reporter):
        result = _result(env="https://prod.myapp.com")
        data = json.loads(Path(reporter.json_report(result)).read_text())
        assert data["env"] == "https://prod.myapp.com"

    def test_run_id_in_json(self, reporter):
        result = _result(run_id=42)
        data = json.loads(Path(reporter.json_report(result)).read_text())
        assert data["run_id"] == 42

    def test_healed_flag_in_step_json(self, reporter):
        step = _step("When I click submit", healed=True)
        result = _result(scenarios=[_scenario(steps=[step])])
        data = json.loads(Path(reporter.json_report(result)).read_text())
        assert data["scenarios"][0]["steps"][0]["healed"] is True

    def test_uses_provided_path(self, reporter, tmp_path):
        custom_path = str(tmp_path / "custom_report.json")
        result = _result()
        path = reporter.json_report(result, path=custom_path)
        assert path == custom_path
        assert Path(custom_path).exists()


# ── HTML report ───────────────────────────────────────────────────────────────

class TestHtmlReport:
    """Cenário: html_report cria arquivo HTML legível"""

    def test_creates_html_file(self, reporter):
        result = _result()
        path = reporter.html_report(result)
        assert Path(path).exists()
        assert path.endswith(".html")

    def test_html_contains_doctype(self, reporter):
        result = _result()
        html = Path(reporter.html_report(result)).read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in html

    def test_html_contains_passed_status(self, reporter):
        result = _result(status="passed")
        html = Path(reporter.html_report(result)).read_text(encoding="utf-8")
        assert "PASSED" in html

    def test_html_contains_failed_status(self, reporter):
        result = _result(status="failed")
        html = Path(reporter.html_report(result)).read_text(encoding="utf-8")
        assert "FAILED" in html

    def test_html_contains_scenario_name(self, reporter):
        result = _result(scenarios=[_scenario("User Login Flow")])
        html = Path(reporter.html_report(result)).read_text(encoding="utf-8")
        assert "User Login Flow" in html

    def test_html_contains_env_url(self, reporter):
        result = _result(env="https://staging.myapp.com")
        html = Path(reporter.html_report(result)).read_text(encoding="utf-8")
        assert "staging.myapp.com" in html

    def test_html_marks_healed_steps(self, reporter):
        step = _step("When I click button", healed=True)
        result = _result(scenarios=[_scenario(steps=[step])])
        html = Path(reporter.html_report(result)).read_text(encoding="utf-8")
        assert "healed" in html

    def test_html_includes_screenshot_link(self, reporter):
        step = _step("Then see result", status="failed", screenshot="/shots/fail.png")
        result = _result(scenarios=[_scenario(steps=[step])])
        html = Path(reporter.html_report(result)).read_text(encoding="utf-8")
        assert "/shots/fail.png" in html

    def test_html_includes_video_link(self, reporter):
        scenario = _scenario(video="/videos/login.webm")
        result = _result(scenarios=[scenario])
        html = Path(reporter.html_report(result)).read_text(encoding="utf-8")
        assert "login.webm" in html

    def test_html_shows_pass_rate_100(self, reporter):
        result = _result(scenarios=[_scenario("A", "passed"), _scenario("B", "passed")])
        html = Path(reporter.html_report(result)).read_text(encoding="utf-8")
        assert "100%" in html

    def test_html_shows_pass_rate_0(self, reporter):
        result = _result(
            status="failed",
            scenarios=[_scenario("A", "failed"), _scenario("B", "failed")],
        )
        html = Path(reporter.html_report(result)).read_text(encoding="utf-8")
        assert "0%" in html

    def test_uses_provided_path(self, reporter, tmp_path):
        custom = str(tmp_path / "my_report.html")
        result = _result()
        path = reporter.html_report(result, path=custom)
        assert path == custom
        assert Path(custom).exists()


# ── GitHub annotations ────────────────────────────────────────────────────────

class TestGithubAnnotations:
    """Cenário: github_annotations emite ::error para cada step falho"""

    def test_empty_string_when_all_pass(self, reporter):
        result = _result(scenarios=[_scenario("Login", status="passed")])
        annotations = reporter.github_annotations(result)
        assert annotations == ""

    def test_error_annotation_for_failed_step(self, reporter):
        step = _step("When I click missing button", status="failed", error="Element not found")
        scenario = _scenario("Login", status="failed", steps=[step])
        result = _result(status="failed", scenarios=[scenario])
        annotations = reporter.github_annotations(result)
        assert "::error" in annotations
        assert "Login" in annotations

    def test_annotation_contains_step_text(self, reporter):
        step = _step('When I fill "email" with bad data', status="failed", error="ValidationError")
        scenario = _scenario("Form submit", status="failed", steps=[step])
        result = _result(status="failed", scenarios=[scenario])
        annotations = reporter.github_annotations(result)
        assert "email" in annotations

    def test_annotation_contains_error_message(self, reporter):
        step = _step("Then I see Dashboard", status="failed", error="Timeout: Dashboard not found")
        scenario = _scenario("S", status="failed", steps=[step])
        result = _result(status="failed", scenarios=[scenario])
        annotations = reporter.github_annotations(result)
        assert "Timeout" in annotations

    def test_multiple_failures_produce_multiple_annotations(self, reporter):
        steps = [
            _step("Given setup", status="passed"),
            _step("When action 1", status="failed", error="err1"),
            _step("When action 2", status="failed", error="err2"),
        ]
        scenario = _scenario("Multi-fail", status="failed", steps=steps)
        result = _result(status="failed", scenarios=[scenario])
        annotations = reporter.github_annotations(result)
        assert annotations.count("::error") == 2

    def test_passing_steps_do_not_generate_annotations(self, reporter):
        steps = [
            _step("Given I am on page", status="passed"),
            _step("When I click OK", status="passed"),
            _step("Then I see Dashboard", status="passed"),
        ]
        result = _result(scenarios=[_scenario("S", status="passed", steps=steps)])
        assert reporter.github_annotations(result) == ""

    def test_annotations_from_multiple_scenarios(self, reporter):
        sc1 = _scenario("S1", status="failed", steps=[
            _step("When fail 1", status="failed", error="e1"),
        ])
        sc2 = _scenario("S2", status="failed", steps=[
            _step("When fail 2", status="failed", error="e2"),
        ])
        result = _result(status="failed", scenarios=[sc1, sc2])
        annotations = reporter.github_annotations(result)
        assert annotations.count("::error") == 2
        assert "S1" in annotations
        assert "S2" in annotations
