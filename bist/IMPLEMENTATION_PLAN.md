# BIST - Implementation Plan

## Overview

BIST currently has only a stub entry point (`bist.py`) importing from a non-existent `qalab_complete_system` module.
The existing BDD-GENERATOR project already has a working FastAPI backend + Next.js frontend that generates and evaluates BDD.
This plan integrates both into a working BIST package, then layers in the roadmap features.

---

## Current State

| Component | Status |
|-----------|--------|
| `bist/bist.py` | Stub only — `qalab_complete_system` doesn't exist |
| `backend/` | FastAPI with `/api/generate`, `/api/evaluate`, `/api/models` |
| `web/` | Next.js 14 + Tailwind with GeneratePanel, EvaluatePanel |
| `src/` | Python modules: generators, evaluators, refinement, auth, utils |
| Database | None — no persistence layer yet |
| CLI | None functional |

---

## Phase 1 — Core BIST Package (Week 1)

**Goal:** Make `bist` a real, working CLI that wraps the existing system.

### 1.1 Replace `bist.py` stub

Create the actual CLI using Click, wiring into the existing `src/` modules.

```
bist/
├── bist.py           # CLI entry point (Click)
├── bist_agent.py     # Core agent: generate → execute → report
├── bist_executor.py  # Playwright test execution + self-healing
├── bist_database.py  # SQLite persistence (test runs, results)
├── bist_parser.py    # .feature file parser (Gherkin)
└── bist_reporter.py  # HTML + JSON report generation
```

### 1.2 CLI Commands

```bash
bist generate --user-story stories/login.md --output tests/login.feature
bist execute  --feature tests/login.feature --env https://staging.app.com
bist full     --user-story stories/login.md --env https://staging.app.com
bist evaluate --feature tests/login.feature
bist stats    # Show test history from SQLite
bist report   # Generate HTML report from last run
```

### 1.3 `bist_agent.py` — Core Agent

Wraps the existing `src/generators` and `src/evaluators` modules.

- Call `src/generators` to produce BDD from user story
- Run quality loop via `src/refinement` until score ≥ threshold
- Persist generated scenario to `.feature` file
- Hand off to `bist_executor.py`

### 1.4 `bist_executor.py` — Playwright Runner

- Parse `.feature` file via `bist_parser.py`
- Map Gherkin steps to Playwright actions
- Self-healing: on selector failure, ask Claude to suggest alternative
- Record video + screenshot per scenario
- Return structured result object

### 1.5 `bist_database.py` — SQLite Layer

Tables:
- `test_runs(id, started_at, env_url, status, duration_ms)`
- `scenarios(id, run_id, name, status, duration_ms, error, video_path)`
- `steps(id, scenario_id, step_text, status, duration_ms, screenshot_path)`

### 1.6 `bist_reporter.py` — Reports

- JSON report (machine-readable, for CI)
- HTML report (human-readable, with screenshots/video links)
- GitHub Actions annotation format (for PR comments)

---

## Phase 2 — Polish (Week 2–3)

### 2.1 Visual Regression Testing

- Capture baseline screenshots on first run
- Diff against baseline on subsequent runs using Pillow/pixelmatch
- Flag visual changes above threshold as failures
- Commands: `bist baseline --feature ...` and `bist visual-diff`

### 2.2 Self-healing Improvements

- Store successful selectors in SQLite (`selector_cache` table)
- On failure, try cached alternatives before calling Claude
- Log healing events for audit trail

### 2.3 Parallel Execution

- Use `asyncio` + Playwright async API
- `--parallel N` flag to limit concurrent browser instances
- Aggregate results from parallel workers into single report

### 2.4 Slack/Discord Webhooks

- `bist_notifier.py` module
- Config via env vars: `BIST_SLACK_WEBHOOK`, `BIST_DISCORD_WEBHOOK`
- Send summary after each `full` or `execute` run
- Include pass rate, duration, link to HTML report

### 2.5 Advanced Retry Strategies

- Per-step retry with exponential backoff
- Configurable via `.bist.yml` config file:
  ```yaml
  retry:
    max_attempts: 3
    backoff_seconds: [2, 5, 10]
    on: [selector_timeout, network_error]
  ```

---

## Phase 3 — REST API + Dashboard (Month 2)

### 3.1 REST API (FastAPI extension)

Extend the existing `backend/main.py` with BIST-specific routes:

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/bist/run` | Trigger full pipeline async |
| GET | `/api/bist/runs` | List all test runs |
| GET | `/api/bist/runs/{id}` | Run details + scenarios |
| GET | `/api/bist/stats` | Flaky tests, trends |
| WS | `/ws/bist/run/{id}` | Live log stream during run |

### 3.2 Web Dashboard (Next.js extension)

Add routes to existing `web/src/app/`:

```
web/src/app/
├── runs/
│   ├── page.tsx          # Run history table
│   └── [id]/
│       └── page.tsx      # Run detail: scenarios, steps, video
├── stats/
│   └── page.tsx          # Charts: pass rate over time, flaky tests
└── components/
    ├── RunHistory.tsx
    ├── ScenarioDetail.tsx
    ├── StepTimeline.tsx
    └── FlakyChart.tsx
```

### 3.3 PostgreSQL Support

- Add `DATABASE_URL` env var support to `bist_database.py`
- Use SQLAlchemy with async driver
- Provide migration scripts (Alembic)
- SQLite remains default for local use

---

## Phase 4 — SaaS Ready (Month 3–4, Optional)

### 4.1 Multi-tenancy

- `tenants` table; all other tables scoped by `tenant_id`
- API key auth per tenant
- Isolated test result storage per tenant

### 4.2 Billing (Stripe)

- Usage metering: count Claude API calls per tenant
- Stripe webhook handler for subscription events
- Enforce limits by tier (Free/Pro/Business)

### 4.3 SSO/SAML

- OAuth2 via existing `src/auth` module
- SAML for enterprise (python3-saml)

---

## File Creation Order

```
Week 1:
1. bist/bist_database.py
2. bist/bist_parser.py
3. bist/bist_executor.py
4. bist/bist_agent.py
5. bist/bist_reporter.py
6. bist/bist.py            (replace stub)
7. bist/requirements.txt
8. bist/.bist.yml.example

Week 2:
9.  bist/bist_notifier.py
10. bist/bist_visual.py

Month 2:
11. backend/presentation/bist_router.py
12. web/src/app/runs/
13. web/src/app/stats/
```

---

## Dependencies to Add

```
# bist/requirements.txt additions
playwright>=1.49.0
anthropic>=0.43.0
click>=8.1.7
Pillow>=10.0.0       # visual regression
aiohttp>=3.9.0       # webhooks
sqlalchemy>=2.0.0    # db abstraction (Phase 3)
alembic>=1.13.0      # migrations (Phase 3)
```

---

## Integration with Existing Code

| BIST module | Uses from existing codebase |
|-------------|----------------------------|
| `bist_agent.py` | `src/generators/`, `src/refinement/`, `src/evaluators/` |
| `bist.py` (CLI) | Mirrors `src/cli.py` commands but adds `execute` and `full` |
| `bist_reporter.py` | Extends `backend/presentation/` response models |
| Dashboard | Extends `web/src/app/` with new routes |

---

## Success Criteria per Phase

| Phase | Done When |
|-------|-----------|
| 1 | `bist full --user-story ... --env ...` runs end-to-end and saves result to SQLite |
| 2 | Parallel runs work, Slack notification sent, visual diff flags a changed button |
| 3 | Dashboard shows live run status via WebSocket; PostgreSQL option works |
| 4 | Two tenants isolated; Stripe webhook toggles feature access |
