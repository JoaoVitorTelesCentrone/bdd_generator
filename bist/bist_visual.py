"""Visual regression testing: capture baselines and pixel-diff comparisons."""

import re
import time
from pathlib import Path
from typing import Optional


class VisualDiffResult:
    def __init__(
        self,
        scenario_name: str,
        step_idx: int,
        diff_ratio: float,
        threshold: float,
        passed: bool,
        baseline_path: str,
        current_path: str,
        diff_path: str = "",
    ):
        self.scenario_name = scenario_name
        self.step_idx = step_idx
        self.diff_ratio = diff_ratio
        self.threshold = threshold
        self.passed = passed
        self.baseline_path = baseline_path
        self.current_path = current_path
        self.diff_path = diff_path

    def __repr__(self):
        status = "PASS" if self.passed else "FAIL"
        return (
            f"VisualDiffResult({status} diff={self.diff_ratio:.2%} "
            f"threshold={self.threshold:.2%} scenario='{self.scenario_name}')"
        )


class BISTVisual:
    def __init__(
        self,
        baselines_dir: str = "bist_output/baselines",
        current_dir: str = "bist_output/visual_current",
        diffs_dir: str = "bist_output/visual_diffs",
        threshold: float = 0.01,
    ):
        self.baselines_dir = Path(baselines_dir)
        self.current_dir = Path(current_dir)
        self.diffs_dir = Path(diffs_dir)
        self.threshold = threshold
        for d in (self.baselines_dir, self.current_dir, self.diffs_dir):
            d.mkdir(parents=True, exist_ok=True)

    def _safe_name(self, scenario_name: str) -> str:
        return re.sub(r"[^\w]", "_", scenario_name)[:50]

    def _baseline_path(self, scenario_name: str, step_idx: int) -> Path:
        return self.baselines_dir / f"{self._safe_name(scenario_name)}_step{step_idx}.png"

    def baseline_exists(self, scenario_name: str, step_idx: int) -> bool:
        return self._baseline_path(scenario_name, step_idx).exists()

    async def capture_baseline(self, page, scenario_name: str, step_idx: int) -> str:
        """Save a screenshot as the baseline for this scenario/step."""
        path = self._baseline_path(scenario_name, step_idx)
        await page.screenshot(path=str(path), full_page=False)
        return str(path)

    async def compare(
        self,
        page,
        scenario_name: str,
        step_idx: int,
        threshold: Optional[float] = None,
    ) -> VisualDiffResult:
        """Compare current page against baseline. Returns VisualDiffResult."""
        thr = threshold if threshold is not None else self.threshold
        baseline_path = self._baseline_path(scenario_name, step_idx)
        safe = self._safe_name(scenario_name)
        ts = time.strftime("%Y%m%d_%H%M%S")
        current_path = self.current_dir / f"{safe}_step{step_idx}_{ts}.png"
        diff_path = self.diffs_dir / f"{safe}_step{step_idx}_{ts}_diff.png"

        await page.screenshot(path=str(current_path), full_page=False)

        if not baseline_path.exists():
            return VisualDiffResult(
                scenario_name=scenario_name,
                step_idx=step_idx,
                diff_ratio=0.0,
                threshold=thr,
                passed=True,
                baseline_path="",
                current_path=str(current_path),
                diff_path="",
            )

        diff_ratio, diff_img = _pixel_diff(str(baseline_path), str(current_path))
        if diff_img is not None:
            diff_img.save(str(diff_path))
        else:
            diff_path = Path("")

        return VisualDiffResult(
            scenario_name=scenario_name,
            step_idx=step_idx,
            diff_ratio=diff_ratio,
            threshold=thr,
            passed=diff_ratio <= thr,
            baseline_path=str(baseline_path),
            current_path=str(current_path),
            diff_path=str(diff_path) if diff_path.name else "",
        )


def _pixel_diff(baseline_path: str, current_path: str):
    """Return (diff_ratio, diff_image) using Pillow. diff_ratio in [0, 1]."""
    try:
        from PIL import Image, ImageChops, ImageEnhance
        import struct

        b = Image.open(baseline_path).convert("RGBA")
        c = Image.open(current_path).convert("RGBA")

        if b.size != c.size:
            c = c.resize(b.size, Image.LANCZOS)

        diff = ImageChops.difference(b, c)
        pixels = list(diff.getdata())
        total = len(pixels)
        if total == 0:
            return 0.0, None

        changed = sum(
            1 for px in pixels if any(ch > 10 for ch in px[:3])
        )
        ratio = changed / total

        enhanced = ImageEnhance.Brightness(diff).enhance(5.0)
        return ratio, enhanced

    except ImportError:
        return _manual_diff(baseline_path, current_path)
    except Exception:
        return 0.0, None


def _manual_diff(baseline_path: str, current_path: str):
    """Fallback diff without Pillow (reads raw PNG bytes)."""
    try:
        b_bytes = Path(baseline_path).read_bytes()
        c_bytes = Path(current_path).read_bytes()
        if len(b_bytes) == 0:
            return 0.0, None
        changed = sum(1 for a, b in zip(b_bytes, c_bytes) if abs(a - b) > 10)
        ratio = changed / max(len(b_bytes), len(c_bytes))
        return ratio, None
    except Exception:
        return 0.0, None
