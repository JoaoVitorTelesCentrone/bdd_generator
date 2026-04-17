"""Playwright-based test executor with AI self-healing for broken selectors."""

import asyncio
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .bist_parser import Feature, Scenario, Step, parse_feature_file
from .bist_database import BISTDatabase

# Playwright is an optional runtime dependency.
# Provide a fallback so unit tests without playwright still run correctly.
try:
    from playwright.async_api import TimeoutError as PlaywrightTimeout
except ImportError:
    PlaywrightTimeout = Exception  # type: ignore[misc,assignment]


def _load_retry_config() -> dict:
    """Load retry config from .bist.yml if present in cwd or project root."""
    for candidate in (Path(".bist.yml"), Path(__file__).parent.parent / ".bist.yml"):
        if candidate.exists():
            try:
                import yaml  # type: ignore
                data = yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}
                return data.get("retry", {})
            except Exception:
                pass
    return {}


@dataclass
class StepResult:
    step_text: str
    keyword: str
    status: str  # passed | failed | skipped
    duration_ms: int = 0
    error: str = ""
    screenshot_path: str = ""
    healed: bool = False


@dataclass
class ScenarioResult:
    name: str
    status: str  # passed | failed | skipped
    duration_ms: int = 0
    steps: list[StepResult] = field(default_factory=list)
    video_path: str = ""
    error: str = ""


@dataclass
class ExecutionResult:
    feature_path: str
    env_url: str
    status: str  # passed | failed
    duration_ms: int = 0
    scenarios: list[ScenarioResult] = field(default_factory=list)
    run_id: Optional[int] = None


class StepExecutionError(Exception):
    pass


class BISTExecutor:
    def __init__(
        self,
        db: Optional[BISTDatabase] = None,
        screenshots_dir: str = "bist_output/screenshots",
        videos_dir: str = "bist_output/videos",
        headless: bool = True,
        timeout_ms: int = 10000,
        self_heal: bool = True,
        parallel: int = 1,
    ):
        self.db = db or BISTDatabase()
        self.screenshots_dir = Path(screenshots_dir)
        self.videos_dir = Path(videos_dir)
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.self_heal = self_heal
        self.parallel = max(1, parallel)
        self._claude_client = None
        retry_cfg = _load_retry_config()
        self._retry_max = int(retry_cfg.get("max_attempts", 1))
        raw_backoff = retry_cfg.get("backoff_seconds", [0])
        self._retry_backoff: list[float] = [float(x) for x in raw_backoff]

    # ── Self-healing helpers ───────────────────────────────────────────────────

    def _get_claude_client(self):
        if self._claude_client is None:
            try:
                import anthropic
                root = Path(__file__).parent.parent
                if str(root) not in sys.path:
                    sys.path.insert(0, str(root))
                from src.auth.config import get_api_key
                api_key = get_api_key("ANTHROPIC_API_KEY")
                if api_key:
                    self._claude_client = anthropic.Anthropic(api_key=api_key)
            except Exception:
                pass
        return self._claude_client

    def _suggest_selectors(self, page_html: str, step_text: str, failed_selector: str) -> list[str]:
        client = self._get_claude_client()
        if not client:
            return []
        try:
            snippet = page_html[:3000]
            prompt = (
                f"A Playwright step failed because selector '{failed_selector}' was not found.\n"
                f"Step: '{step_text}'\n\nHTML snippet:\n{snippet}\n\n"
                "Suggest up to 3 alternative CSS selectors or text locators. "
                "Return ONLY a JSON array of strings, e.g.: [\"button[type='submit']\", \"text=Submit\"]"
            )
            response = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass
        return []

    # ── Step parsing helpers ───────────────────────────────────────────────────

    def _extract_quoted(self, text: str) -> list[str]:
        return re.findall(r'"([^"]+)"', text)

    def _extract_selector(self, text: str) -> str:
        quoted = self._extract_quoted(text)
        if quoted:
            val = quoted[0]
            # Treat as CSS only when the value unambiguously looks like a selector:
            # starts with #, ., [, or already prefixed with "text="
            if re.match(r'^[#.\[]', val) or val.startswith("text="):
                return val
            return f"text={val}"
        lower = text.lower()
        for kw in ("button", "link", "input", "field", "checkbox", "dropdown", "select"):
            if kw in lower:
                return kw
        return text

    def _extract_url(self, text: str, env_url: str = "") -> str:
        quoted = self._extract_quoted(text)
        if quoted:
            val = quoted[0]
            if val.startswith("http"):
                return val
            return env_url.rstrip("/") + "/" + val.lstrip("/")
        url_match = re.search(r'https?://\S+', text)
        if url_match:
            return url_match.group()
        path_match = re.search(r'(/\S*)', text)
        if path_match:
            return env_url.rstrip("/") + path_match.group()
        return env_url

    def _extract_text(self, text: str) -> str:
        quoted = self._extract_quoted(text)
        return quoted[0] if quoted else text

    # ── Playwright wrappers with healing ─────────────────────────────────────

    def _pattern_key(self, step_text: str) -> str:
        """Normalise step text into a cache key (strip dynamic values)."""
        return re.sub(r'"[^"]*"', '"*"', step_text.lower().strip())

    async def _alternatives(self, page, step_text: str, failed_selector: str) -> list[str]:
        """Return candidate selectors: cached first, then Claude suggestions."""
        pattern = self._pattern_key(step_text)
        cached = self.db.get_cached_selectors(pattern)
        filtered = [s for s in cached if s != failed_selector]
        ai_suggestions = []
        if self.self_heal:
            html = await page.content()
            ai_suggestions = self._suggest_selectors(html, step_text, failed_selector)
        return filtered + [s for s in ai_suggestions if s not in filtered]

    async def _click_with_healing(
        self, page, selector: str, step_text: str, scenario_id: Optional[int] = None
    ) -> bool:
        try:
            await page.click(selector, timeout=self.timeout_ms)
            self.db.cache_selector(self._pattern_key(step_text), selector)
            return False
        except PlaywrightTimeout:
            for alt in await self._alternatives(page, step_text, selector):
                try:
                    await page.click(alt, timeout=self.timeout_ms)
                    self.db.cache_selector(self._pattern_key(step_text), alt)
                    self.db.log_healing(scenario_id, step_text, selector, alt)
                    return True
                except Exception:
                    continue
            raise

    async def _fill_with_healing(
        self, page, selector: str, value: str, step_text: str, scenario_id: Optional[int] = None
    ) -> bool:
        try:
            await page.fill(selector, value, timeout=self.timeout_ms)
            self.db.cache_selector(self._pattern_key(step_text), selector)
            return False
        except PlaywrightTimeout:
            for alt in await self._alternatives(page, step_text, selector):
                try:
                    await page.fill(alt, value, timeout=self.timeout_ms)
                    self.db.cache_selector(self._pattern_key(step_text), alt)
                    self.db.log_healing(scenario_id, step_text, selector, alt)
                    return True
                except Exception:
                    continue
            raise

    # ── Step execution ────────────────────────────────────────────────────────

    async def _execute_step_once(
        self,
        page,
        step: Step,
        env_url: str,
        scenario_name: str,
        idx: int,
        scenario_id: Optional[int] = None,
    ) -> StepResult:
        full_text = step.full_text()
        lower = step.text.lower()
        result = StepResult(step_text=full_text, keyword=step.keyword, status="failed")
        t0 = time.time()
        healed = False

        try:
            if any(k in lower for k in ("navigate to", "go to", "visit", "open", "acesso", "navego")):
                url = self._extract_url(step.text, env_url)
                await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)

            elif any(k in lower for k in ("click", "press", "tap", "clico", "pressiono")):
                selector = self._extract_selector(step.text)
                healed = await self._click_with_healing(page, selector, full_text, scenario_id)

            elif any(k in lower for k in ("fill", "type", "enter", "preencho", "digito")):
                quoted = self._extract_quoted(step.text)
                if len(quoted) >= 2:
                    selector = self._extract_selector(quoted[0])
                    value = quoted[1]
                else:
                    selector = self._extract_selector(step.text)
                    value = quoted[0] if quoted else ""
                healed = await self._fill_with_healing(page, selector, value, full_text, scenario_id)

            elif any(k in lower for k in ("not see", "not visible", "hidden", "não vejo")):
                text = self._extract_text(step.text)
                count = await page.locator(f"text={text}").count()
                if count > 0:
                    raise StepExecutionError(f"Expected '{text}' to not be visible, but it was found")

            elif any(k in lower for k in ("see", "contain", "have text", "show", "display",
                                           "vejo", "exibe", "should see")):
                text = self._extract_text(step.text)
                await page.wait_for_selector(f"text={text}", timeout=self.timeout_ms)

            elif any(k in lower for k in ("wait for", "aguardo")):
                text = self._extract_text(step.text)
                await page.wait_for_selector(f"text={text}", timeout=self.timeout_ms)

            elif any(k in lower for k in ("select", "choose", "seleciono", "escolho")):
                quoted = self._extract_quoted(step.text)
                if len(quoted) >= 2:
                    selector = self._extract_selector(quoted[0])
                    await page.select_option(selector, label=quoted[1], timeout=self.timeout_ms)

            elif any(k in lower for k in ("check", "marcar", "marco")):
                await page.check(self._extract_selector(step.text), timeout=self.timeout_ms)

            elif any(k in lower for k in ("uncheck", "desmarco")):
                await page.uncheck(self._extract_selector(step.text), timeout=self.timeout_ms)

            else:
                result.status = "skipped"
                result.duration_ms = int((time.time() - t0) * 1000)
                return result

            result.status = "passed"
            result.healed = healed

        except (StepExecutionError, Exception) as e:
            result.status = "failed"
            result.error = str(e)
            try:
                self.screenshots_dir.mkdir(parents=True, exist_ok=True)
                safe = re.sub(r"[^\w]", "_", scenario_name)[:40]
                shot_path = self.screenshots_dir / f"{safe}_step{idx}_fail.png"
                await page.screenshot(path=str(shot_path))
                result.screenshot_path = str(shot_path)
            except Exception:
                pass

        result.duration_ms = int((time.time() - t0) * 1000)
        return result

    async def _execute_step(
        self,
        page,
        step: Step,
        env_url: str,
        scenario_name: str,
        idx: int,
        scenario_id: Optional[int] = None,
    ) -> StepResult:
        """Execute step with exponential-backoff retry from .bist.yml config."""
        max_attempts = max(1, self._retry_max)
        backoff = self._retry_backoff

        last_result: Optional[StepResult] = None
        for attempt in range(max_attempts):
            last_result = await self._execute_step_once(
                page, step, env_url, scenario_name, idx, scenario_id
            )
            if last_result.status != "failed":
                return last_result
            if attempt < max_attempts - 1:
                delay = backoff[attempt] if attempt < len(backoff) else backoff[-1]
                if delay > 0:
                    await asyncio.sleep(delay)

        return last_result  # type: ignore[return-value]

    # ── Scenario runner ───────────────────────────────────────────────────────

    async def _run_scenario(
        self,
        browser,
        feature: Feature,
        scenario: Scenario,
        env_url: str,
        run_id: int,
        semaphore: Optional[asyncio.Semaphore] = None,
    ) -> ScenarioResult:
        async def _inner():
            sc_result = ScenarioResult(name=scenario.name, status="running")
            t0 = time.time()
            scenario_id = self.db.create_scenario(run_id, scenario.name)

            self.videos_dir.mkdir(parents=True, exist_ok=True)
            safe = re.sub(r"[^\w]", "_", scenario.name)[:40]
            video_dir = self.videos_dir / safe

            context = await browser.new_context(
                record_video_dir=str(video_dir),
                record_video_size={"width": 1280, "height": 720},
            )
            page = await context.new_page()

            all_steps = list(feature.background_steps) + list(scenario.steps)
            failed = False

            for idx, step in enumerate(all_steps):
                if failed:
                    sr = StepResult(step_text=step.full_text(), keyword=step.keyword, status="skipped")
                else:
                    sr = await self._execute_step(
                        page, step, env_url, scenario.name, idx, scenario_id
                    )
                    if sr.status == "failed":
                        failed = True
                        sc_result.error = sr.error

                sc_result.steps.append(sr)
                self.db.create_step(scenario_id, sr.step_text, sr.status, sr.duration_ms, sr.screenshot_path)

            await context.close()

            try:
                videos = list(video_dir.glob("*.webm")) if video_dir.exists() else []
                if videos:
                    sc_result.video_path = str(videos[0])
            except Exception:
                pass

            sc_result.status = "failed" if failed else "passed"
            sc_result.duration_ms = int((time.time() - t0) * 1000)
            self.db.finish_scenario(
                scenario_id, sc_result.status, sc_result.duration_ms, sc_result.error, sc_result.video_path
            )
            return sc_result

        if semaphore:
            async with semaphore:
                return await _inner()
        return await _inner()

    # ── Public API ────────────────────────────────────────────────────────────

    async def execute_async(self, feature_path: str, env_url: str) -> ExecutionResult:
        from playwright.async_api import async_playwright

        feature = parse_feature_file(feature_path)
        run_id = self.db.create_run(env_url, feature_path)
        t0 = time.time()

        result = ExecutionResult(
            feature_path=feature_path,
            env_url=env_url,
            status="passed",
            run_id=run_id,
        )

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=self.headless)

            if self.parallel > 1:
                semaphore = asyncio.Semaphore(self.parallel)
                tasks = [
                    self._run_scenario(browser, feature, sc, env_url, run_id, semaphore)
                    for sc in feature.scenarios
                ]
                sc_results = await asyncio.gather(*tasks, return_exceptions=False)
                result.scenarios = list(sc_results)
            else:
                for scenario in feature.scenarios:
                    sc_result = await self._run_scenario(browser, feature, scenario, env_url, run_id)
                    result.scenarios.append(sc_result)

            await browser.close()

        for sc in result.scenarios:
            if sc.status == "failed":
                result.status = "failed"

        result.duration_ms = int((time.time() - t0) * 1000)
        self.db.finish_run(run_id, result.status, result.duration_ms)
        return result

    def execute(self, feature_path: str, env_url: str) -> ExecutionResult:
        return asyncio.run(self.execute_async(feature_path, env_url))
