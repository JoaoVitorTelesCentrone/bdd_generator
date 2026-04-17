"""
Tests for bist/bist_notifier.py — BISTNotifier and _build_summary.

Cenários cobertos:
  BISTNotifier.enabled:
    - False quando nenhum webhook configurado
    - True quando slack_webhook fornecido
    - True quando discord_webhook fornecido
    - Lê webhooks das variáveis de ambiente
  _build_summary:
    - Run passed → color verde
    - Run failed → color vermelho
    - Título contém status em maiúsculas
    - text contém env_url
    - pass_rate 100% quando todos passaram
    - pass_rate 0% quando todos falharam
    - pass_rate parcial calculado corretamente
    - Campos Scenarios/Passed/Failed/Duration presentes
    - Report incluído nos fields quando report_path fornecido
    - Report ausente dos fields quando report_path vazio
    - Cenários vazios não levantam exceção
  notify_async:
    - Não faz nada quando notifier está desativado
    - Chama _post_slack quando slack_webhook configurado
    - Chama _post_discord quando discord_webhook configurado
    - Chama ambos quando dois webhooks configurados
    - _post_slack lida com exceção silenciosamente
    - _post_discord lida com exceção silenciosamente
"""
import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest
from bist.bist_notifier import BISTNotifier, _build_summary


# ── helpers ───────────────────────────────────────────────────────────────────

def _mock_scenario(status: str) -> MagicMock:
    sc = MagicMock()
    sc.status = status
    return sc


def _mock_result(
    status: str = "passed",
    passed: int = 3,
    failed: int = 0,
    env_url: str = "https://staging.example.com",
    duration_ms: int = 5000,
) -> MagicMock:
    scenarios = [_mock_scenario("passed") for _ in range(passed)]
    scenarios += [_mock_scenario("failed") for _ in range(failed)]
    result = MagicMock()
    result.status = status
    result.env_url = env_url
    result.duration_ms = duration_ms
    result.scenarios = scenarios
    return result


# ── BISTNotifier.enabled ──────────────────────────────────────────────────────

class TestEnabled:

    def test_disabled_when_no_webhooks(self):
        env = {"BIST_SLACK_WEBHOOK": "", "BIST_DISCORD_WEBHOOK": ""}
        with patch.dict(os.environ, env):
            notifier = BISTNotifier()
        assert notifier.enabled is False

    def test_enabled_with_slack_webhook(self):
        notifier = BISTNotifier(slack_webhook="https://hooks.slack.com/test")
        assert notifier.enabled is True

    def test_enabled_with_discord_webhook(self):
        notifier = BISTNotifier(discord_webhook="https://discord.com/api/webhooks/test")
        assert notifier.enabled is True

    def test_enabled_with_both_webhooks(self):
        notifier = BISTNotifier(
            slack_webhook="https://hooks.slack.com/test",
            discord_webhook="https://discord.com/api/webhooks/test",
        )
        assert notifier.enabled is True

    def test_reads_slack_from_env(self):
        with patch.dict(os.environ, {"BIST_SLACK_WEBHOOK": "https://hooks.slack.com/env"}):
            notifier = BISTNotifier()
        assert notifier.enabled is True

    def test_reads_discord_from_env(self):
        with patch.dict(os.environ, {"BIST_DISCORD_WEBHOOK": "https://discord.com/env"}):
            notifier = BISTNotifier()
        assert notifier.enabled is True

    def test_constructor_param_overrides_env(self):
        with patch.dict(os.environ, {"BIST_SLACK_WEBHOOK": ""}):
            notifier = BISTNotifier(slack_webhook="https://hooks.slack.com/direct")
        assert notifier.slack_webhook == "https://hooks.slack.com/direct"


# ── _build_summary ────────────────────────────────────────────────────────────

class TestBuildSummary:

    def test_passed_run_has_green_color(self):
        result = _mock_result(status="passed")
        summary = _build_summary(result, "")
        assert summary["color"] == "#22c55e"

    def test_failed_run_has_red_color(self):
        result = _mock_result(status="failed", passed=1, failed=1)
        summary = _build_summary(result, "")
        assert summary["color"] == "#ef4444"

    def test_title_contains_passed_status(self):
        result = _mock_result(status="passed")
        summary = _build_summary(result, "")
        assert "PASSED" in summary["title"]

    def test_title_contains_failed_status(self):
        result = _mock_result(status="failed", passed=0, failed=2)
        summary = _build_summary(result, "")
        assert "FAILED" in summary["title"]

    def test_text_contains_env_url(self):
        result = _mock_result(env_url="https://staging.myapp.com")
        summary = _build_summary(result, "")
        assert "staging.myapp.com" in summary["text"]

    def test_pass_rate_100_all_passed(self):
        result = _mock_result(passed=4, failed=0)
        summary = _build_summary(result, "")
        field = next(f for f in summary["fields"] if f["title"] == "Pass Rate")
        assert "100%" in field["value"]

    def test_pass_rate_0_all_failed(self):
        result = _mock_result(status="failed", passed=0, failed=3)
        summary = _build_summary(result, "")
        field = next(f for f in summary["fields"] if f["title"] == "Pass Rate")
        assert "0%" in field["value"]

    def test_pass_rate_partial(self):
        result = _mock_result(passed=1, failed=1)
        summary = _build_summary(result, "")
        field = next(f for f in summary["fields"] if f["title"] == "Pass Rate")
        assert "50%" in field["value"]

    def test_fields_contain_required_titles(self):
        result = _mock_result(passed=2, failed=1)
        summary = _build_summary(result, "")
        titles = {f["title"] for f in summary["fields"]}
        assert {"Scenarios", "Passed", "Failed", "Duration"} <= titles

    def test_report_field_present_when_path_given(self):
        result = _mock_result()
        summary = _build_summary(result, "/reports/my_report.html")
        titles = [f["title"] for f in summary["fields"]]
        assert "Report" in titles

    def test_report_field_absent_when_path_empty(self):
        result = _mock_result()
        summary = _build_summary(result, "")
        titles = [f["title"] for f in summary["fields"]]
        assert "Report" not in titles

    def test_report_path_in_text_when_given(self):
        result = _mock_result()
        summary = _build_summary(result, "/reports/my_report.html")
        assert "/reports/my_report.html" in summary["text"]

    def test_empty_scenarios_does_not_raise(self):
        result = MagicMock()
        result.status = "passed"
        result.env_url = "https://x.com"
        result.duration_ms = 0
        result.scenarios = []
        summary = _build_summary(result, "")
        assert summary is not None

    def test_scenarios_count_in_fields(self):
        result = _mock_result(passed=3, failed=2)
        summary = _build_summary(result, "")
        scenarios_field = next(f for f in summary["fields"] if f["title"] == "Scenarios")
        assert scenarios_field["value"] == "5"

    def test_passed_count_in_fields(self):
        result = _mock_result(passed=3, failed=1)
        summary = _build_summary(result, "")
        passed_field = next(f for f in summary["fields"] if f["title"] == "Passed")
        assert passed_field["value"] == "3"

    def test_failed_count_in_fields(self):
        result = _mock_result(status="failed", passed=1, failed=2)
        summary = _build_summary(result, "")
        failed_field = next(f for f in summary["fields"] if f["title"] == "Failed")
        assert failed_field["value"] == "2"

    def test_duration_formatted_with_comma(self):
        result = _mock_result(duration_ms=12_345)
        summary = _build_summary(result, "")
        duration_field = next(f for f in summary["fields"] if f["title"] == "Duration")
        assert "12,345ms" in duration_field["value"]


# ── notify_async ──────────────────────────────────────────────────────────────

class TestNotifyAsync:

    def test_does_nothing_when_disabled(self):
        notifier = BISTNotifier()
        result = _mock_result()
        # Should complete without calling any HTTP method
        asyncio.run(notifier.notify_async(result))

    def test_calls_post_slack_only(self):
        notifier = BISTNotifier(slack_webhook="https://hooks.slack.com/test")
        result = _mock_result()

        with patch.object(notifier, "_post_slack", new_callable=AsyncMock) as mock_slack, \
             patch.object(notifier, "_post_discord", new_callable=AsyncMock) as mock_discord:
            asyncio.run(notifier.notify_async(result))

        mock_slack.assert_called_once()
        mock_discord.assert_not_called()

    def test_calls_post_discord_only(self):
        notifier = BISTNotifier(discord_webhook="https://discord.com/api/webhooks/test")
        result = _mock_result()

        with patch.object(notifier, "_post_slack", new_callable=AsyncMock) as mock_slack, \
             patch.object(notifier, "_post_discord", new_callable=AsyncMock) as mock_discord:
            asyncio.run(notifier.notify_async(result))

        mock_discord.assert_called_once()
        mock_slack.assert_not_called()

    def test_calls_both_when_both_configured(self):
        notifier = BISTNotifier(
            slack_webhook="https://hooks.slack.com/test",
            discord_webhook="https://discord.com/api/webhooks/test",
        )
        result = _mock_result()

        with patch.object(notifier, "_post_slack", new_callable=AsyncMock) as mock_slack, \
             patch.object(notifier, "_post_discord", new_callable=AsyncMock) as mock_discord:
            asyncio.run(notifier.notify_async(result))

        mock_slack.assert_called_once()
        mock_discord.assert_called_once()

    def test_slack_exception_does_not_propagate(self):
        """_post_slack swallows exceptions; notify_async must not raise."""
        notifier = BISTNotifier(slack_webhook="https://hooks.slack.com/test")
        result = _mock_result()

        async def _raise(*_a, **_kw):
            raise RuntimeError("network failure")

        with patch.object(notifier, "_post_slack", side_effect=_raise):
            asyncio.run(notifier.notify_async(result))  # must not raise

    def test_discord_exception_does_not_propagate(self):
        """_post_discord swallows exceptions; notify_async must not raise."""
        notifier = BISTNotifier(discord_webhook="https://discord.com/api/webhooks/test")
        result = _mock_result()

        async def _raise(*_a, **_kw):
            raise RuntimeError("network failure")

        with patch.object(notifier, "_post_discord", side_effect=_raise):
            asyncio.run(notifier.notify_async(result))  # must not raise

    def test_notify_async_passes_report_path(self):
        notifier = BISTNotifier(slack_webhook="https://hooks.slack.com/test")
        result = _mock_result()

        with patch.object(notifier, "_post_slack", new_callable=AsyncMock) as mock_slack:
            asyncio.run(notifier.notify_async(result, report_path="/reports/run.html"))

        mock_slack.assert_called_once()
        # Verify the summary passed to _post_slack contains the report path
        call_args = mock_slack.call_args[0][0]
        report_field_values = [f["value"] for f in call_args["fields"] if f["title"] == "Report"]
        assert any("/reports/run.html" in v for v in report_field_values)
