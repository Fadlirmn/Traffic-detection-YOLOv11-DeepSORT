# Demo policy, quality, security, and delivery requirements

## 1. Environments
| Environment | API/Storage | Allowed actions | Auth |
|---|---|---|---|
| `local-demo` | versioned fixtures | simulated state changes in browser | none |
| `local-real` | real service + local PostgreSQL/Redis or model runtime | real domain workflows | local Firebase/project config as applicable |
| `preview` | public demo fixture | guest scenarios only | none |
| `production-demo` | public demo fixture | guest scenarios only | none |
| `real-managed` (future optional) | isolated managed services | governed production workflow | Firebase + server-side RBAC |

**Hard invariants:** `VERCEL_ENV=production` can never auto-enable paid Gemini, actual scraping, real Telegram send, arbitrary file processing, unrestricted database write or background worker. Read/check `DATA_MODE` at process startup and fail closed on invalid values.

## 2. Demo feature semantics
- Every displayed time series bears `Synthetic sample`, `Captured benchmark (date, dataset)`, or `Pre-recorded` when applicable.
- Control buttons: `Try example`, `Simulate`, `Replay` — not `Run live scraping` or `Real-time tracking` for fake flows.
- Role switcher is a **tour persona**, not real login; do not issue fake JWTs or set bypass cookies.
- Mutations use `sessionStorage` or writable store, initialized from immutable fixture. On reload may reset; `Reset demo` restores exact baseline.
- No exposed public arbitrary commands. Serverless route list is allowlisted and read-only unless deterministic short simulated transformation.

## 3. Test pyramid and acceptance gates
| Scope | Tools/examples | Release gate |
|---|---|---|
| Static quality | ESLint, Prettier, `svelte-check`, `tsc` | 0 errors |
| Unit | Vitest / Go `go test` / pytest | 100% critical rules covered; project threshold defined |
| Contract | JSON Schema/OpenAPI, fixture validator, schema diff | pass |
| Integration | Postgres migrations rollback, auth denied tests, provider fakes | pass in CI |
| E2E | Playwright desktop/mobile; primary journey per persona | pass |
| Visual | Playwright screenshot snapshots for key pages | reviewed |
| Security | gitleaks/secret scan, dependency scan, malicious inputs | no untriaged high/critical issues |
| Accessibility | axe + manual keyboard + captions | no critical violations |
| Performance | Lighthouse CI mobile, media optimization | budget recorded and regressions investigated |

Suggested quality targets (not claimed current results): line >= 80% for domain/business logic; branches >= 70%, domain rules reach >= 90% in critical modules. Coverage percentage is not a substitute for meaningful assertions.

## 4. CI pipeline (GitHub Actions)
1. Checkout, lockfile frozen install, dependency cache.
2. Secret/dependency/license checks and type/lint.
3. Unit and contract tests.
4. Backend tests with ephemeral Postgres/Redis (only service projects needing them).
5. Build demo in `DATA_MODE=demo`.
6. Playwright smoke tests against local preview server or Vercel preview.
7. Vercel integration deploy after passing jobs; protected `main` recommends branch protection.
8. Release notes + screenshot/video update if user-facing changes.

**Never** provide deployment credentials to untrusted pull-request jobs. Pin action versions/commit hashes based on security policy.

## 5. Security threat scenarios
| Threat | Mitigation | Test |
|---|---|---|
| Hidden secret in browser bundle | server-only env, bundle scan | built bundle grep/canary |
| Demo endpoint calls costly paid service | provider disabled in public demo; spend cap | verify blocked even forged request |
| Unauthorized admin data | token verify + RBAC real mode | role matrix negative tests |
| SQL injection | parameterized SQL/sqlc or ORM | crafted input tests |
| Prompt injection in academic text | bounded context, no tool execution, output schema | adversarial documents |
| Malicious uploaded media | default no public upload; size/MIME validation | oversized/wrong-type tests |
| Fake uptime and unsupported performance claims | evidence labels and source | content review |
| Source/legal issues for scraped prices/video | approved sources only, licensing review | release checklist |
| Public abuse | stateless throttling appropriate for platform or no mutation | burst test |

## 6. Observability
- Request-level `requestId`, status, latency, route, mode; do not log tokens, academic PII, scraped credentials or full prompts.
- Log `provider=fixture` clearly in demo.
- Diagnostics for real workers include retry count, error classification, idempotency key, queue latency and retention policy.
- Uptime/latency charts shown publicly must be either genuinely sourced (with update time) or labelled sample replay.
- Error boundaries + friendly messages; Vercel build and runtime logs remain private.

## 7. Cost control
- Default demo costs: static delivery + small serverless reads; aim within chosen plan's limits, **not a claim of free/zero costs**.
- Disable background cron by default, avoid Firestore polling, apply cache headers to public immutable fixtures.
- Video: compressed derivatives + adaptive preview; check bandwidth/storage quotas and private/public visibility.
- Provider APIs: default off in public demo; if opt-in later, daily cap, per-IP quotas, timeout and admin kill-switch.
- Monthly manual check for Vercel usage and any enabled object storage/managed service bills.

## 8. Release checklist
- [ ] `DATA_MODE=demo` hardcoded for demo deployment.
- [ ] No live provider tokens in preview/prod demo.
- [ ] Every fixture tagged synthetic; privacy review complete.
- [ ] No advertised live model/tracker/scraper without live service.
- [ ] All major UI journeys covered E2E and keyboard tested.
- [ ] README real-mode commands tested on clean environment.
- [ ] Dependency/model/video legal rights reviewed.
- [ ] GitHub links, demo routes, screenshots and recorded evidence valid.
- [ ] Vercel env, function duration and storage allowances checked for current plan.
