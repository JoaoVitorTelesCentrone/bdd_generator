"""
Tests for bist/bist_executor.py — Playwright runner with AI self-healing.

Cenários cobertos:
  - Step de navegação chama page.goto com URL resolvida
  - Step de clique chama page.click com seletor correto
  - Step de preenchimento chama page.fill com seletor e valor
  - Step de asserção de texto chama page.wait_for_selector
  - Step desconhecido retorna status "skipped"
  - Falha no clique sem self-heal → status "failed" com mensagem de erro
  - Falha no clique com self-heal → tenta seletores alternativos do Claude
  - Screenshot é capturado quando step falha
  - Step healed=True quando alternativa funcionou
  - _extract_selector extrai texto entre aspas como seletor "text=..."
  - _extract_url resolve URL relativa contra env_url
  - Passos de Background são executados antes dos passos do cenário
  - Cenário falho pula steps restantes como "skipped"
  - StepResult acumula duration_ms
"""
import sys, os, asyncio, textwrap
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, call

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest
from bist.bist_executor import BISTExecutor, StepResult, ScenarioResult
from bist.bist_parser import Step, Feature, Scenario
from bist.bist_database import BISTDatabase


# ── helpers ───────────────────────────────────────────────────────────────────

def _run(coro):
    return asyncio.run(coro)


def _mock_page():
    page = MagicMock()
    page.goto = AsyncMock()
    page.click = AsyncMock()
    page.fill = AsyncMock()
    page.wait_for_selector = AsyncMock()
    page.select_option = AsyncMock()
    page.check = AsyncMock()
    page.uncheck = AsyncMock()
    page.screenshot = AsyncMock()
    page.content = AsyncMock(return_value="<html><button>Submit</button></html>")
    locator = MagicMock()
    locator.count = AsyncMock(return_value=0)
    page.locator = MagicMock(return_value=locator)
    return page


@pytest.fixture
def executor(tmp_path):
    db = BISTDatabase(db_path=tmp_path / "test.db")
    return BISTExecutor(
        db=db,
        screenshots_dir=str(tmp_path / "shots"),
        videos_dir=str(tmp_path / "videos"),
        self_heal=False,
        timeout_ms=5000,
    )


@pytest.fixture
def healing_executor(tmp_path):
    db = BISTDatabase(db_path=tmp_path / "test.db")
    return BISTExecutor(
        db=db,
        screenshots_dir=str(tmp_path / "shots"),
        videos_dir=str(tmp_path / "videos"),
        self_heal=True,
        timeout_ms=5000,
    )


def _step(keyword: str, text: str) -> Step:
    return Step(keyword=keyword, text=text)


def _execute(executor, step, env_url="http://example.com"):
    page = _mock_page()
    result = _run(executor._execute_step(page, step, env_url, "Test Scenario", 0))
    return result, page


# ── navigation ────────────────────────────────────────────────────────────────

class TestNavigationStep:
    """Cenário: Step de navegação chama page.goto com URL correta"""

    def test_navigate_to_absolute_url(self, executor):
        result, page = _execute(executor, _step("When", 'I navigate to "https://staging.app.com"'))
        page.goto.assert_called_once()
        url_arg = page.goto.call_args[0][0]
        assert url_arg == "https://staging.app.com"
        assert result.status == "passed"

    def test_navigate_to_relative_path(self, executor):
        result, page = _execute(
            executor,
            _step("When", 'I navigate to "/login"'),
            env_url="https://myapp.com",
        )
        url_arg = page.goto.call_args[0][0]
        assert url_arg == "https://myapp.com/login"

    def test_go_to_keyword_triggers_navigation(self, executor):
        result, page = _execute(executor, _step("Given", 'I go to "https://app.com"'))
        page.goto.assert_called_once()
        assert result.status == "passed"

    def test_visit_keyword_triggers_navigation(self, executor):
        result, page = _execute(executor, _step("Given", 'I visit "https://app.com/home"'))
        page.goto.assert_called_once()

    @pytest.mark.parametrize("kw_text", [
        "navego para",
        "acesso a página",
    ])
    def test_portuguese_navigation_keywords(self, executor, kw_text):
        result, page = _execute(executor, _step("Dado", f'{kw_text} "https://app.com"'))
        page.goto.assert_called_once()


# ── click ─────────────────────────────────────────────────────────────────────

class TestClickStep:
    """Cenário: Step de clique chama page.click com seletor correto"""

    def test_click_with_quoted_text_selector(self, executor):
        result, page = _execute(executor, _step("When", 'I click "Submit"'))
        page.click.assert_called_once()
        selector = page.click.call_args[0][0]
        assert "Submit" in selector
        assert result.status == "passed"

    def test_click_with_css_selector(self, executor):
        result, page = _execute(executor, _step("When", 'I click "#login-btn"'))
        selector = page.click.call_args[0][0]
        assert "#login-btn" in selector

    def test_press_keyword_triggers_click(self, executor):
        result, page = _execute(executor, _step("When", 'I press "Enter"'))
        page.click.assert_called_once()

    def test_clico_pt_triggers_click(self, executor):
        result, page = _execute(executor, _step("Quando", 'clico no botão "Entrar"'))
        page.click.assert_called_once()


# ── fill ──────────────────────────────────────────────────────────────────────

class TestFillStep:
    """Cenário: Step de preenchimento chama page.fill com seletor e valor"""

    def test_fill_with_two_quoted_values(self, executor):
        result, page = _execute(
            executor,
            _step("When", 'I fill "email" with "user@test.com"'),
        )
        page.fill.assert_called_once()
        assert result.status == "passed"

    def test_fill_value_is_second_quoted(self, executor):
        result, page = _execute(
            executor,
            _step("When", 'I fill "password" with "secret123"'),
        )
        fill_args = page.fill.call_args[0]
        assert fill_args[1] == "secret123"

    def test_type_keyword_triggers_fill(self, executor):
        result, page = _execute(executor, _step("When", 'I type "hello" into "search"'))
        page.fill.assert_called_once()

    def test_preencho_pt_triggers_fill(self, executor):
        result, page = _execute(
            executor,
            _step("Quando", 'preencho o campo "email" com "test@test.com"'),
        )
        page.fill.assert_called_once()


# ── assertions ────────────────────────────────────────────────────────────────

class TestAssertionStep:
    """Cenário: Step de asserção chama page.wait_for_selector"""

    def test_see_text_triggers_wait_for_selector(self, executor):
        result, page = _execute(executor, _step("Then", 'I should see "Dashboard"'))
        page.wait_for_selector.assert_called_once()
        assert result.status == "passed"

    def test_contain_keyword(self, executor):
        result, page = _execute(executor, _step("Then", 'page should contain "Welcome"'))
        page.wait_for_selector.assert_called_once()

    def test_vejo_pt_triggers_assertion(self, executor):
        result, page = _execute(executor, _step("Então", 'vejo "Bem-vindo"'))
        page.wait_for_selector.assert_called_once()

    def test_not_see_passes_when_element_absent(self, executor):
        result, page = _execute(executor, _step("Then", 'I should not see "Error"'))
        # locator.count returns 0 by default → element absent → passed
        assert result.status == "passed"

    def test_not_see_fails_when_element_present(self, executor):
        page = _mock_page()
        locator = MagicMock()
        locator.count = AsyncMock(return_value=1)
        page.locator = MagicMock(return_value=locator)
        step = _step("Then", 'I should not see "Error message"')
        result = _run(executor._execute_step(page, step, "http://example.com", "S", 0))
        assert result.status == "failed"


# ── unknown step ──────────────────────────────────────────────────────────────

class TestUnknownStep:
    """Cenário: Step desconhecido retorna status 'skipped'"""

    def test_unknown_step_is_skipped(self, executor):
        result, page = _execute(executor, _step("And", "the universe is in order"))
        assert result.status == "skipped"
        page.click.assert_not_called()
        page.goto.assert_not_called()

    def test_skipped_step_does_not_interact_with_page(self, executor):
        result, page = _execute(executor, _step("But", "something philosophical"))
        page.fill.assert_not_called()
        page.wait_for_selector.assert_not_called()


# ── failure and screenshot ────────────────────────────────────────────────────

class TestStepFailure:
    """Cenário: Falha → status 'failed' com screenshot capturado"""

    def test_click_failure_sets_failed_status(self, executor):
        page = _mock_page()
        page.click = AsyncMock(side_effect=Exception("Element not found"))
        step = _step("When", 'I click "Ghost Button"')
        result = _run(executor._execute_step(page, step, "http://x.com", "S", 0))
        assert result.status == "failed"

    def test_failure_captures_error_message(self, executor):
        page = _mock_page()
        page.click = AsyncMock(side_effect=Exception("Timeout waiting for selector"))
        step = _step("When", 'I click "Submit"')
        result = _run(executor._execute_step(page, step, "http://x.com", "S", 0))
        assert result.error != ""

    def test_screenshot_taken_on_failure(self, executor, tmp_path):
        page = _mock_page()
        page.click = AsyncMock(side_effect=Exception("boom"))
        step = _step("When", 'I click "Submit"')
        result = _run(executor._execute_step(page, step, "http://x.com", "Scenario", 0))
        page.screenshot.assert_called_once()

    def test_screenshot_path_in_result(self, executor, tmp_path):
        page = _mock_page()
        page.click = AsyncMock(side_effect=Exception("boom"))
        page.screenshot = AsyncMock()
        step = _step("When", 'I click "Submit"')
        result = _run(executor._execute_step(page, step, "http://x.com", "Test Scenario", 1))
        assert result.screenshot_path != ""

    def test_duration_ms_is_non_negative(self, executor):
        result, _ = _execute(executor, _step("When", 'I click "OK"'))
        assert result.duration_ms >= 0


# ── self-healing ──────────────────────────────────────────────────────────────

class TestSelfHealing:
    """Cenário: Self-heal tenta seletores alternativos quando clique falha"""

    def test_heal_disabled_does_not_try_alternatives(self, executor):
        page = _mock_page()
        page.click = AsyncMock(side_effect=Exception("timeout"))
        step = _step("When", 'I click "Submit"')

        with patch.object(executor, "_suggest_selectors", return_value=["#btn"]) as mock_suggest:
            result = _run(executor._execute_step(page, step, "http://x.com", "S", 0))
            mock_suggest.assert_not_called()

        assert result.status == "failed"

    def test_heal_enabled_calls_suggest_selectors(self, healing_executor):
        page = _mock_page()
        page.click = AsyncMock(side_effect=Exception("timeout"))
        step = _step("When", 'I click "Submit"')

        with patch.object(healing_executor, "_suggest_selectors", return_value=[]) as mock_suggest:
            _run(healing_executor._execute_step(page, step, "http://x.com", "S", 0))
            mock_suggest.assert_called_once()

    def test_heal_succeeds_with_alternative_selector(self, healing_executor):
        page = _mock_page()
        call_count = {"n": 0}

        async def click_side_effect(sel, **kw):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise Exception("timeout on first selector")
            # second call (alternative) succeeds

        page.click = AsyncMock(side_effect=click_side_effect)
        step = _step("When", 'I click "Submit"')

        with patch.object(healing_executor, "_suggest_selectors", return_value=["#alternative"]):
            result = _run(healing_executor._execute_step(page, step, "http://x.com", "S", 0))

        assert result.status == "passed"
        assert result.healed is True

    def test_healed_false_on_normal_success(self, executor):
        result, _ = _execute(executor, _step("When", 'I click "OK"'))
        assert result.healed is False


# ── selector / URL extraction ─────────────────────────────────────────────────

class TestExtraction:
    """Cenário: Helpers extraem seletor e URL corretamente"""

    def test_extract_selector_css_hash_preserved(self, executor):
        sel = executor._extract_selector('I click "#login-btn"')
        assert sel == "#login-btn"

    def test_extract_selector_css_dot_preserved(self, executor):
        sel = executor._extract_selector('I click ".submit-btn"')
        assert sel == ".submit-btn"

    def test_extract_selector_plain_text_becomes_text_locator(self, executor):
        sel = executor._extract_selector('I click "Submit"')
        assert sel == "text=Submit"

    def test_extract_url_absolute(self, executor):
        url = executor._extract_url('"https://prod.app.com/login"', "https://other.com")
        assert url == "https://prod.app.com/login"

    def test_extract_url_relative_prepends_env(self, executor):
        url = executor._extract_url('"/dashboard"', "https://myapp.com")
        assert url == "https://myapp.com/dashboard"

    def test_extract_text_returns_quoted_content(self, executor):
        text = executor._extract_text('I should see "Welcome back"')
        assert text == "Welcome back"


# ── background + scenario sequencing ─────────────────────────────────────────

class TestScenarioSequencing:
    """
    Cenário: Background steps executados antes dos steps do cenário
    Cenário: Cenário falho pula steps restantes como 'skipped'
    """

    def _make_feature_with_bg(self) -> Feature:
        feature = Feature(name="Auth")
        feature.background_steps = [
            Step(keyword="Given", text="I am on login page"),
        ]
        scenario = Scenario(name="Login")
        scenario.steps = [
            Step(keyword="When", text='I click "Login"'),
            Step(keyword="Then", text='I see "Dashboard"'),
        ]
        feature.scenarios.append(scenario)
        return feature

    def test_background_steps_run_before_scenario_steps(self, executor):
        """Background goto runs before scenario click."""
        run_order = []

        async def _tracked_step(page, step, *a, **kw):
            run_order.append(step.keyword + " " + step.text)
            return StepResult(step_text=step.full_text(), keyword=step.keyword, status="passed")

        feature = self._make_feature_with_bg()
        run_id = executor.db.create_run("http://x.com")
        sc_id = executor.db.create_scenario(run_id, "Login")

        async def _run_scenario():
            browser = MagicMock()
            context = MagicMock()
            page = _mock_page()
            context.new_page = AsyncMock(return_value=page)
            context.close = AsyncMock()
            browser.new_context = AsyncMock(return_value=context)

            with patch.object(executor, "_execute_step", side_effect=_tracked_step):
                return await executor._run_scenario(
                    browser, feature, feature.scenarios[0], "http://x.com", run_id
                )

        result = _run(_run_scenario())
        assert run_order[0] == "Given I am on login page"  # background first

    def test_failed_step_skips_remaining(self, executor):
        feature = Feature(name="Test")
        scenario = Scenario(name="Failing scenario")
        scenario.steps = [
            Step(keyword="Given", text="I am on page"),
            Step(keyword="When", text='I click "Missing Button"'),
            Step(keyword="Then", text='I see "Result"'),
        ]
        feature.scenarios.append(scenario)
        run_id = executor.db.create_run("http://x.com")

        async def _step_with_failure(page, step, *a, **kw):
            if "Missing Button" in step.text:
                return StepResult(
                    step_text=step.full_text(), keyword=step.keyword,
                    status="failed", error="not found"
                )
            return StepResult(step_text=step.full_text(), keyword=step.keyword, status="passed")

        async def _run_scenario():
            browser = MagicMock()
            context = MagicMock()
            page = _mock_page()
            context.new_page = AsyncMock(return_value=page)
            context.close = AsyncMock()
            browser.new_context = AsyncMock(return_value=context)

            with patch.object(executor, "_execute_step", side_effect=_step_with_failure):
                return await executor._run_scenario(
                    browser, feature, feature.scenarios[0], "http://x.com", run_id
                )

        result = _run(_run_scenario())
        statuses = [s.status for s in result.steps]
        assert result.status == "failed"
        assert statuses[-1] == "skipped"  # last step was skipped
