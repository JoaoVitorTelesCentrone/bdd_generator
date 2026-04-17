"""Slack and Discord webhook notifications for BIST run summaries."""

import json
import os
from typing import Optional


class BISTNotifier:
    def __init__(
        self,
        slack_webhook: Optional[str] = None,
        discord_webhook: Optional[str] = None,
    ):
        self.slack_webhook = slack_webhook or os.environ.get("BIST_SLACK_WEBHOOK", "")
        self.discord_webhook = discord_webhook or os.environ.get("BIST_DISCORD_WEBHOOK", "")

    @property
    def enabled(self) -> bool:
        return bool(self.slack_webhook or self.discord_webhook)

    def notify(self, result, report_path: str = "") -> None:
        """Synchronous wrapper — creates event loop if needed."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import threading
                out = {}
                def _run():
                    out["result"] = asyncio.run(self._notify_async(result, report_path))
                t = threading.Thread(target=_run, daemon=True)
                t.start()
                t.join(timeout=10)
            else:
                loop.run_until_complete(self._notify_async(result, report_path))
        except RuntimeError:
            asyncio.run(self._notify_async(result, report_path))

    async def notify_async(self, result, report_path: str = "") -> None:
        await self._notify_async(result, report_path)

    async def _notify_async(self, result, report_path: str = "") -> None:
        if not self.enabled:
            return
        summary = _build_summary(result, report_path)
        import asyncio
        tasks = []
        if self.slack_webhook:
            tasks.append(self._post_slack(summary))
        if self.discord_webhook:
            tasks.append(self._post_discord(summary))
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _post_slack(self, summary: dict) -> None:
        try:
            import aiohttp
            payload = {
                "text": summary["text"],
                "attachments": [
                    {
                        "color": summary["color"],
                        "fields": summary["fields"],
                        "footer": "BIST — BDD Intelligent Self-healing Tests",
                    }
                ],
            }
            async with aiohttp.ClientSession() as session:
                await session.post(
                    self.slack_webhook,
                    data=json.dumps(payload),
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10),
                )
        except Exception:
            pass

    async def _post_discord(self, summary: dict) -> None:
        try:
            import aiohttp
            color_hex = {"#22c55e": 0x22C55E, "#ef4444": 0xEF4444}.get(summary["color"], 0x6366F1)
            payload = {
                "embeds": [
                    {
                        "title": summary["title"],
                        "description": summary["text"],
                        "color": color_hex,
                        "fields": [
                            {"name": f["title"], "value": f["value"], "inline": True}
                            for f in summary["fields"]
                        ],
                        "footer": {"text": "BIST — BDD Intelligent Self-healing Tests"},
                    }
                ]
            }
            async with aiohttp.ClientSession() as session:
                await session.post(
                    self.discord_webhook,
                    data=json.dumps(payload),
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10),
                )
        except Exception:
            pass


def _build_summary(result, report_path: str) -> dict:
    total = len(result.scenarios)
    passed = sum(1 for s in result.scenarios if s.status == "passed")
    failed = total - passed
    pass_rate = (passed / total * 100) if total else 0
    status = result.status.upper()
    color = "#22c55e" if result.status == "passed" else "#ef4444"
    icon = "✅" if result.status == "passed" else "❌"

    text = f"{icon} *BIST Run {status}* — {result.env_url}"
    report_line = f"\n<{report_path}|View Report>" if report_path else ""

    fields = [
        {"title": "Scenarios", "value": str(total), "short": True},
        {"title": "Passed", "value": str(passed), "short": True},
        {"title": "Failed", "value": str(failed), "short": True},
        {"title": "Pass Rate", "value": f"{pass_rate:.0f}%", "short": True},
        {"title": "Duration", "value": f"{result.duration_ms:,}ms", "short": True},
    ]
    if report_path:
        fields.append({"title": "Report", "value": report_path, "short": False})

    return {
        "title": f"BIST Run {status}",
        "text": text + report_line,
        "color": color,
        "fields": fields,
    }
