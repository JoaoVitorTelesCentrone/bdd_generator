"""HTML, JSON, and GitHub Actions report generation for BIST runs."""

import json
import time
from pathlib import Path
from typing import Optional

from .bist_executor import ExecutionResult


class BISTReporter:
    def __init__(self, output_dir: str = "bist_output/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ── Public API ────────────────────────────────────────────────────────────

    def json_report(self, result: ExecutionResult, path: Optional[str] = None) -> str:
        out = Path(path) if path else self.output_dir / f"report_{_ts()}.json"
        out.write_text(
            json.dumps(self._to_dict(result), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return str(out)

    def html_report(self, result: ExecutionResult, path: Optional[str] = None) -> str:
        out = Path(path) if path else self.output_dir / f"report_{_ts()}.html"
        out.write_text(self._build_html(result), encoding="utf-8")
        return str(out)

    def github_annotations(self, result: ExecutionResult) -> str:
        lines = []
        for sc in result.scenarios:
            if sc.status == "failed":
                for step in sc.steps:
                    if step.status == "failed":
                        lines.append(
                            f"::error title=BIST Failure::{sc.name} — {step.step_text}: {step.error}"
                        )
        return "\n".join(lines)

    # ── Serialisation ─────────────────────────────────────────────────────────

    def _to_dict(self, result: ExecutionResult) -> dict:
        total = len(result.scenarios)
        passed = sum(1 for s in result.scenarios if s.status == "passed")
        return {
            "feature": result.feature_path,
            "env": result.env_url,
            "status": result.status,
            "run_id": result.run_id,
            "duration_ms": result.duration_ms,
            "summary": {"total": total, "passed": passed, "failed": total - passed},
            "scenarios": [
                {
                    "name": s.name,
                    "status": s.status,
                    "duration_ms": s.duration_ms,
                    "error": s.error,
                    "video": s.video_path,
                    "steps": [
                        {
                            "text": st.step_text,
                            "status": st.status,
                            "duration_ms": st.duration_ms,
                            "error": st.error,
                            "screenshot": st.screenshot_path,
                            "healed": st.healed,
                        }
                        for st in s.steps
                    ],
                }
                for s in result.scenarios
            ],
        }

    # ── HTML ──────────────────────────────────────────────────────────────────

    def _build_html(self, result: ExecutionResult) -> str:
        data = self._to_dict(result)
        summary = data["summary"]
        pass_rate = (summary["passed"] / summary["total"] * 100) if summary["total"] else 0
        status_color = "#22c55e" if result.status == "passed" else "#ef4444"

        scenarios_html = "".join(self._scenario_html(sc) for sc in data["scenarios"])

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>BIST Report</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f9fafb;color:#111827;padding:24px}}
    .wrap{{max-width:960px;margin:0 auto}}
    .header{{background:#1e1b4b;color:#fff;border-radius:12px;padding:28px;margin-bottom:24px}}
    .header h1{{font-size:22px;margin-bottom:8px}}
    .meta{{opacity:.7;font-size:13px;margin-bottom:20px}}
    .stats{{display:flex;gap:32px;flex-wrap:wrap}}
    .stat .val{{font-size:30px;font-weight:700}}
    .stat .lbl{{font-size:12px;opacity:.65;margin-top:2px}}
    .card{{border:1px solid #e5e7eb;border-radius:8px;padding:16px;margin-bottom:12px;background:#fff}}
    .sc-title{{font-weight:600;font-size:15px;margin-bottom:8px;display:flex;align-items:center;gap:8px}}
    .sc-meta{{color:#6b7280;font-size:12px;margin-bottom:10px}}
    .step{{padding:4px 0 4px 12px;font-size:13px;border-left:3px solid #e5e7eb;margin:3px 0}}
    .step.passed{{border-color:#22c55e;color:#166534}}
    .step.failed{{border-color:#ef4444;color:#991b1b}}
    .step.skipped{{border-color:#f59e0b;color:#92400e}}
    .step-err{{font-size:11px;color:#dc2626;margin-top:2px;margin-left:12px}}
    .badge{{display:inline-block;padding:1px 7px;border-radius:9999px;font-size:11px;font-weight:600}}
    .badge.passed{{background:#dcfce7;color:#166534}}
    .badge.failed{{background:#fee2e2;color:#991b1b}}
    .badge.skipped{{background:#fef9c3;color:#713f12}}
    .healed{{background:#fef3c7;color:#78350f;padding:1px 5px;border-radius:3px;font-size:10px;margin-left:6px}}
    a{{color:#6366f1;text-decoration:none}}
  </style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <h1>BIST Test Report</h1>
    <div class="meta">{result.feature_path} &rarr; {result.env_url}</div>
    <div class="stats">
      <div class="stat"><div class="val" style="color:{status_color}">{result.status.upper()}</div><div class="lbl">Status</div></div>
      <div class="stat"><div class="val">{summary['total']}</div><div class="lbl">Scenarios</div></div>
      <div class="stat"><div class="val" style="color:#22c55e">{summary['passed']}</div><div class="lbl">Passed</div></div>
      <div class="stat"><div class="val" style="color:#ef4444">{summary['failed']}</div><div class="lbl">Failed</div></div>
      <div class="stat"><div class="val">{pass_rate:.0f}%</div><div class="lbl">Pass Rate</div></div>
      <div class="stat"><div class="val">{result.duration_ms:,}ms</div><div class="lbl">Duration</div></div>
    </div>
  </div>
  {scenarios_html}
</div>
</body>
</html>"""

    def _scenario_html(self, sc: dict) -> str:
        icon = "✓" if sc["status"] == "passed" else "✗"
        video_link = f'<a href="{sc["video"]}" target="_blank">[video]</a>' if sc.get("video") else ""
        steps_html = "".join(self._step_html(st) for st in sc["steps"])
        return f"""
<div class="card">
  <div class="sc-title">
    <span class="badge {sc['status']}">{icon} {sc['status']}</span>
    {sc['name']} {video_link}
  </div>
  <div class="sc-meta">{sc['duration_ms']}ms{(' — ' + sc['error']) if sc.get('error') else ''}</div>
  {steps_html}
</div>"""

    def _step_html(self, st: dict) -> str:
        healed = '<span class="healed">healed</span>' if st.get("healed") else ""
        shot = f' <a href="{st["screenshot"]}" target="_blank">[screenshot]</a>' if st.get("screenshot") else ""
        err = f'<div class="step-err">{st["error"]}</div>' if st.get("error") else ""
        return f'<div class="step {st["status"]}">{st["text"]} <span style="opacity:.5;font-size:11px">({st["duration_ms"]}ms)</span>{healed}{shot}{err}</div>'


def _ts() -> str:
    return time.strftime("%Y%m%d_%H%M%S")
