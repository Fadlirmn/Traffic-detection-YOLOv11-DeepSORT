# Cross-project technical architecture & decisions

## 1. Stack selection matrix

| Layer | Siakad AI | Vehicle Tracking | Price Monitor | Infra Case Study |
|---|---|---|---|---|
| Public UI | SvelteKit + Svelte 5 + TS + Tailwind | Same | Same | Same |
| Public hosting | Vercel | Vercel | Vercel | Vercel |
| Demo API | SvelteKit `+server.ts`, JSON fixtures | Replay manifest & stateless API | Fixture-based API / browser session | Versioned build/trace JSON |
| Real backend | Go + chi, pgx/sqlc | Python CLI/service + OpenCV | Python FastAPI + SQLAlchemy | shell/config/workflows, optional exporter |
| Real persistent data | PostgreSQL | SQLite or PostgreSQL for metadata | PostgreSQL | JSON outputs, logs in local tools |
| Real auth | Firebase Auth verified by Go Admin SDK | optional local service token | Firebase Auth (optional) + role enforcement | GitHub OIDC for CI deploy |
| Queue/worker | none required; async AI via bounded request | local process/edge, no Vercel worker | Celery + Redis | GitHub Actions jobs |
| Video/storage | static screenshots | compressed MP4/WebM and tracking JSON in static/Blob | JSON/CSV demo exports | static sanitized logs |
| Provider | Gemini behind server adapter | local YOLO11 + DeepSORT | authorized data feeds/import, Telegram optional | Vercel/GitHub CI metadata |
| Testing | Go test, Testcontainers optional, Vitest, Playwright | pytest + benchmark/replay tests + Playwright | pytest + integration worker, Playwright | actionlint, shellcheck, policy tests |

> Database suggestions apply to **real-mode source**. Demo does not require a public production database; can use deterministic static fixtures. If persistent cross-session interactive demo features later become essential, add a *separate sandbox database* with hard quotas and short retention only.

## 2. Monorepo or multi-repo
**Preferred:** 1 public repo/project for each technical case study, with a common reusable pattern but no forced shared runtime. Example:
```
siakad-ai/
  apps/web/                   # SvelteKit demo and optional real-client mode
  services/api-go/            # actual Go HTTP API
  packages/contracts/         # OpenAPI schemas + generated clients
  fixtures/                   # sample-only dataset
  docs/                       # PRD, ADRs, diagrams, runbook
  .github/workflows/
```
For CV repo, replace `services/api-go/` with `engine/` and `scripts/`; for price monitor, use `services/api/` and `services/worker/`.

## 3. Routing architecture
- Web: SvelteKit server-side rendering for initial content, client navigation for charts/replays.
- Route handlers: validation, permission check, content shaping, pagination. No long background jobs.
- Asset delivery: small JSON versioned as deploy assets; larger MP4 WebM served from object storage/CDN (Vercel Blob or other serverless storage). License/rights checked.
- Preview deploys: separate environment variables; no production secrets on untrusted fork PRs.
- Deploy gating: build, typecheck, tests, contract validation, Playwright smoke, then promote.

## 4. Public demo safety by runtime
| Workload | Appropriate for Vercel | Approved alternative |
|---|---|---|
| Static HTML / SSR / short API | Yes | N/A |
| Fixture read/filter/search | Yes | N/A |
| Tiny validated simulation request | Yes, bounded time/resource | Local browser pure function |
| PostgreSQL request (if needed) | Yes, with safe connection pooling | Prefer fixture |
| Periodic small trigger | Possible with platform Cron constraints | Not required for demo |
| Long Python browser automation | **Not as public demo** | Real-mode local/optional job compute |
| Continuous YOLO inference | **Not on Vercel** | Local workstation / Raspberry Pi |
| Redis long-lived workers | **Not on Vercel** | Local via Docker Compose |
| Upload arbitrary huge videos | Avoid | Capped uploads to isolated object storage, or no public uploads |

Do not rely on in-memory process state across requests, writeable app filesystem, long-running processes or persistent websocket connections for the demo. Check current plan limits at release rather than hardcoding outdated function duration assumptions.

## 5. Architecture Decision Records (ADRs)
### ADR-001: Hosting public UI on Vercel
**Decision:** SvelteKit adapter-vercel; no server ownership. **Reason:** low operational overhead, SSR + API, preview deployments. **Tradeoff:** function and request limits, no continuous worker. **Mitigation:** fixtures, replay and local real-mode engine.

### ADR-002: Source real / demo synthetic
**Decision:** preserve production-grade core and provide `demo` adapter with versioned synthetic data. **Reason:** technical credibility without always-on infrastructure. **Tradeoff:** demo does not prove production traffic. **Mitigation:** local repro instructions, realistic tests, sample evidence; never mislabel simulations as live.

### ADR-003: Role handling
**Decision:** real mode validates Firebase ID token server-side; demo offers explicitly fake roles with no protected actions. **Reason:** useful UX walkthrough, no public credentials. **Tradeoff:** demo role selection is not authentication; UI clearly says so.

### ADR-004: Data storage
**Decision:** Postgres for relational/historical use cases; SQLite or Postgres for CV metadata, no persistent database in public demo unless truly needed. **Reason:** correctness and cost containment.

### ADR-005: Bound external AI & notifications
**Decision:** interface providers + fixtures, timeouts, caps, retries only when idempotent. **Reason:** never expose paid credentials or incur unpredictable expenses from portfolio visitors.

### ADR-006: Honest observability
**Decision:** infra website uses **recorded example logs/traces** labeled as examples; local workflows create fresh artifacts reviewers can reproduce. **Reason:** no fabricated live uptime.

## 6. Security and privacy baseline
- All env secrets server-only; no `PUBLIC_`/`VITE_` prefix for secrets; `.env.example` contains dummy placeholders.
- Token verify via official SDK and allowlist/roles at server. Firestore security rules when SDK used client-side. Firebase Admin server credentials not exposed to browser; rules do not apply to privileged Admin SDK accesses, so manual authorization is essential.
- Authorization checked per endpoint/resource; deny by default; admin role is never UI-only.
- API: input schema, max request size, rate limiting (upstream/edge appropriate), constant-time comparisons for secrets, CORS restricted where applicable.
- Data: synthetic people and prices; anonymize capture; do not publish sessions, tokens, access credentials.
- SCA dependency scan, secret scan, CodeQL when supported; scheduled update review.
- Protect costs: quota limiting, max upload sizes, cache public fixture results, disable on-demand paid AI in guest demo by default.

## 7. Local development paths
**Option A: demo-only:** `pnpm install && pnpm dev` (must function offline with fixtures); `pnpm test` and `pnpm exec playwright test`.

**Option B: real backend:** follow per-project `docker compose up -d postgres [redis]`, migrations, seed, start Go/Python service, then `DATA_MODE=real pnpm dev`. Local workloads may require GPU/CPU model weights; provide CPU small sample fallback for CV.

**No VPS** is required in either path.

## 8. Dependency policy
- Prefer supported stable versions when implementation begins, pinned by lockfiles. SvelteKit/Svelte/TS/Vercel adapters and Firebase Admin compatibility verified during scaffold.
- Node LTS supported by SvelteKit/Vercel; Go current supported release; Python stable supported by ML ecosystem; do not pin arbitrary versions before compatibility check.
- Renovate or Dependabot monthly review; breaking upgrades via PR + CI; no `latest` image tags in reproducible guides.
