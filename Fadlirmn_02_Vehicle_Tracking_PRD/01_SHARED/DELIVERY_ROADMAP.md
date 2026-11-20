# Cross-project delivery roadmap

> Milestones are **effort estimates, not promised delivery dates**. Scope for one developer; work in vertical slices. `P0` blocks first public showcase; `P1` deepens engineering; `P2` is optional polish.

## Stage 0 — Foundation (4–7 focused development sessions)
- Repo layout and shared documentation conventions; Node/tool version pinning; `.editorconfig`, Git hooks optional.
- SvelteKit skeleton + adapter-vercel + Tailwind + component tokens.
- Shared domain contract/fixture conventions, demo banner and `resetDemo()`.
- Vitest, Playwright, lint/typecheck, Github Actions and Vercel preview test.
- Done: `pnpm dev` runs on new clone with sample fixture even offline.

## Stage 1 — Siakad AI (10–18 sessions)
- Slice A: ERD, migration, seed and Go API read endpoints (P0).
- Slice B: real write flows + RBAC, validation and tests (P0).
- Slice C: demo persona view and fixture services (P0).
- Slice D: Gemini bounded adapter, deterministic explanation replay; test (P1).
- Slice E: architecture and case-study polish (P0).
- Demo walkthrough: switch Admin/Student → explore enrollments → inspect GPA/AI explanation (labeled mock/replay).

## Stage 2 — Price Monitor (9–16 sessions)
- Slice A: product/variant snapshots, history and source adapter interface.
- Slice B: real worker pipeline with retry/idempotence, tests and SQLite? **PostgreSQL is canonical**.
- Slice C: dashboard filters, trend graphs and alert rules; synthetic seeded histories.
- Slice D: simulate run and preview notification (no real Telegram in public demo).
- Slice E: failure modes, ToS, worker architecture case study.
- Demo walkthrough: choose product → see price changes → simulate check → inspect alert/failed job.

## Stage 3 — Vehicle Tracking (9–18 sessions, subject to datasets/hardware)
- Slice A: model loading, detection/tracking interface and reproducible inference CLI.
- Slice B: event schema, aggregated metrics, prerecorded media generation with consent/rights.
- Slice C: browser replay with timeline, bounding boxes and synchronized counts.
- Slice D: benchmark script (capture exact hardware/environment and sample size).
- Slice E: video player keyboard, captions, limitations and Docker/local guide.
- Demo walkthrough: play replay → inspect tracking IDs → compare counts and analysis.

## Stage 4 — Infrastructure/DevOps (5–10 sessions)
- Slice A: Docker Compose local stacks and scripted setup for other apps.
- Slice B: actual CI workflows, build artifacts, SCA, smoke tests.
- Slice C: incident + recovery runbooks, diagrams and ADRs.
- Slice D: Vercel-hosted *case study* with replay build timeline and sanitized example traces.
- Demo walkthrough: architecture overview → inspect pipeline and sample failure/recovery → follow reproducible setup.

## Milestone acceptance
| Milestone | Release evidence |
|---|---|
| M0 | shared demo shell + green CI + deploy preview |
| M1 | Siakad real API tests + public fixture demo |
| M2 | Price worker local smoke + simulator showcase |
| M3 | CV inference local replay export + web replay |
| M4 | Infra scripts CI checked + case study online |
| M5 | Portfolio page with four entries, screenshots, architecture and metrics evidence |

## Dependency map
```
Shared contracts, CI, fixtures ───┬── Siakad
                                ├── Price Monitor
                                └── Vehicle Tracking
                                        │
Outputs from real repos/CI ─────────────┴──> Infra case study
```

## How to work with AI/Zed
For each session, provide only the current PRD and its data/API companion. Follow this repeatable implementation loop:
1. Pick one `P0` user story.
2. Define acceptance test and contracts first.
3. Implement real core + unit test.
4. Implement demo adapter using same response contract.
5. Add integration/e2e tests and update README/ADR.
6. Review against Security QA and deploy preview.

Do not build all screens first and leave real backend as placeholders. Real business logic in the repo is a major evaluation criterion.
