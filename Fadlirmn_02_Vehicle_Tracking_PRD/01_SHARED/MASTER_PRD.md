# Master PRD — Fadlirmn Engineering Portfolio Program

## 0. Metadata
- Product owner/developer: Fadlirmn (single maintainer)
- Date: 2026-11-20; version: 1.0; state: target specification
- Target audience: recruiter, hiring manager, technical interviewer, open-source reviewer
- Language UI: English default; bahasa Indonesia optional
- Deliverable: empat demo project Vercel + empat repository transparan, engineering-oriented + case studies
- Constraint P0: **no required VPS**; public demo serverless-first, real implementation available in source/reproducible locally

## 1. Masalah
Recruiter sulit mengevaluasi proyek yang hanya punya kode tanpa walkthrough, demo, testing, architecture dan penjelasan pengambilan keputusan. Sebaliknya demo yang hanya mock UI tanpa real core engineering pun tidak meyakinkan. Paket ini menghubungkan dua kebutuhan: **real source** dan **safe hosted demonstration**.

## 2. Tujuan terukur (target; belum hasil aktual)
| ID | Target | Validasi |
|---|---|---|
| G1 | Empat project memiliki link demo, source, diagram, hasil pengujian, README | Audit portfolio |
| G2 | Pengunjung pertama berhasil menjalankan skenario utama <= 90 detik tanpa login | 5 usability sessions |
| G3 | Semua build, lint, typecheck, unit tests dan e2e demo lolos CI | GitHub Actions |
| G4 | Tidak ada secret/PII/credentials di repo maupun payload demo | Secret scan + review |
| G5 | Demo dapat dipakai saat layanan eksternal down/kuota habis | Fixture-only smoke test |
| G6 | Halaman utama LCP <= 2.5s target pada kondisi pengujian ditetapkan | Lighthouse CI, mobile throttling |
| G7 | Setiap repo menyediakan cara menjalankan core source secara lokal | Fresh clone rehearsal |
| G8 | Klaim metrik didukung test/evidence atau diberi label "sample/illustrative" | Evidence review |

## 3. Scope & out-of-scope
**In:** sistem fitur inti nyata + API/domain contracts + reproducible local stack + stateless/public demo + fixtures + technical case study + CI/CD + accessibility + basic analytics anonim jika diaktifkan.

**Out:** multi-tenant production SaaS, uptime SLA komersial, scraping terjadwal publik tanpa izin, inferensi video berat di serverless, admin self-signup, pemrosesan data pribadi asli, deployment VPS, implementasi multi-region, billing, kompleksitas Kubernetes.

## 4. Product positioning
| Project | Kompetensi yang dibuktikan | Visitor experience utama | Real architecture di repo |
|---|---|---|---|
| Siakad AI | Go REST, RBAC, relational data, AI boundary, testing | Role switch / akademik / AI preview | Go API + PostgreSQL + Firebase Auth + Gemini adapter |
| Vehicle Tracking | Python CV, tracking, edge pipeline, measurement | Video replay + boxes/count chart + analytics | Python inference + DeepSORT + export tool |
| Price Monitor | Python backend, scheduling, jobs, retries, notifications | Price history + simulated run + alert preview | FastAPI + Postgres + Celery/Redis + integrations |
| Infra & DevOps | CI/CD, deploy, observability, hardening, incident response | Interactive architecture + sample build traces | Docker Compose + workflow YAML + configs/runbooks |

## 5. Personas & jobs to be done
- **Visitor / Recruiter:** memahami problem, menguji demo dalam < 2 menit, membuka GitHub, melihat tantangan dan dampak.
- **Engineering reviewer:** menelusuri domain model, API, auth boundaries, failures, test cases, deployment tradeoffs.
- **Maintainer (single):** update fixture, audit dependencies, publish tanpa mengurus always-on server.

## 6. Global page information architecture
- `/` landing: hero, concise capability, project grid, tech stack, featured links.
- `/projects/{slug}` per case study: problem → responsibilities → architecture → what is real/demonstrated → demo walkthrough → measurable results → risks/limitations → code.
- Demo aplikasi di subdomain/host Vercel terpisah atau paths, bergantung repo. Disarankan **empat Vercel projects terpisah**.
- Setiap demo: header `Demo data`, `Reset demo`, `Source code`, `Architecture`, `Limitations`.
- Tidak mengharuskan login untuk melihat/mencoba scenario utama.

## 7. UI / UX global
- Design: technical/editorial, high contrast, purposeful data visualizations, tanpa Material UI; Tailwind CSS + komponen headless / custom.
- Layout: responsive (375, 768, 1280, 1440px), sticky nav hanya jika membantu.
- States wajib: loading/skeleton, zero, error + retry, offline/missing data, permission denied (jika relevan).
- A11y: keyboard usable, visible focus, semantic labels, charts memiliki tabel/tekstual alternatif, captions/transcript video, prefers-reduced-motion.
- Copy: label demo berkaitan dengan simulasi, bukan menyembunyikan. Semua metrik sample dilabeli.
- Multi-language optional/future, default English untuk recruiter global.

## 8. Dual-mode architecture rules
```
shared domain contracts / types / fixtures
          │
   ┌──────┴────────┐
   │               │
Real implementation   Demo adapter (SvelteKit on Vercel)
Go/Python + DB        synthetic JSON / read-only serverless handlers
   │               │
local/optional managed    publicly hosted; no job runners
```

- Domain logic & core rules tidak diduplikasi sembarangan. Jika backend Go/Python, TypeScript contract harus dipastikan konsisten via OpenAPI/JSON Schema yang diuji.
- `DATA_MODE=demo|real` di-validate server-side; demo deployment selalu `demo`; mode real tidak otomatis terbuka oleh query param.
- Fixtures readonly, seeded dan versioned. Jika simulasi mengubah status, state hanya browser-local/session dengan tombol reset; hindari global state memory dalam function.
- API demo: status code, shape, validation, pagination tetap menyerupai real; simulated latency boleh digunakan hanya jika jelas sebagai simulasi.
- Never connect demo route to production databases/external scraping by accident. Deny egress/permissions where practical.

## 9. Common domain interfaces
- `Repository<T>`: domain-specific repository abstraction (database adapter vs fixture adapter).
- `Clock`, `IdGenerator`, `ExternalProvider`, `EventPublisher` diinjeksikan untuk determinisme test.
- Error envelope seragam: `{ "error": { "code": "VALIDATION_ERROR", "message": "...", "requestId": "...", "details": [] } }`.
- `X-Request-ID`; `Cache-Control` sesuai sensitivitas; timestamps ISO8601 UTC.
- Pagination stable cursor atau page-based yang konsisten per service; limit dan max limit terdokumentasi.
- Contract schemas checked in CI; no leaking stack traces to client.

## 10. Dependencies & integration decisions
- Frontend: SvelteKit (compatible stable current), Svelte 5 + TypeScript strict + Tailwind CSS; Vite; `@sveltejs/adapter-vercel`.
- Forms/validation: Zod at server boundary; no trusting client validations alone.
- Test: Vitest, Playwright, Testing Library; backend-specific tests.
- Docs: Mermaid/C4, OpenAPI 3.1, ADRs, CHANGELOG and screenshots.
- CI/CD: GitHub Actions + Vercel preview deployment; protected main recommended.
- Auth: Firebase Auth only where demonstration needs named identities; otherwise guest personas with synthetic data. Never fake production user auth.
- Data: case-specific; choose relational data when relations matter; avoid forcing Firestore everywhere.

## 11. Definition of done (applies to all)
- [ ] Real core actually runs using documented commands, realistic error paths and tests.
- [ ] Public demo loads without external paid APIs and without sign-in.
- [ ] Badge/text clearly differentiates demo and real execution.
- [ ] Source and demo links bidirectional.
- [ ] At least three scripted walkthrough use-cases.
- [ ] CI green; no high/critical exploitable known vulnerabilities at release.
- [ ] Security baseline and secret scans done.
- [ ] Responsive/a11y tests run; no keyboard traps.
- [ ] Architecture diagram plus two ADRs (at minimum).
- [ ] Known limitations and cost assumptions disclosed.
- [ ] Screenshot + short demo clip + README reproducer.

## 12. Product risks
- **Demo perceived fake:** minimize by showing exact source path and real-vs-replay boundaries.
- **Costs/quota:** fixture-first, disable providers by default, rate limits, cost alarms, avoid periodic demo writes.
- **CV licensing:** validate model weights/software license and source video usage rights before public release.
- **Scraping compliance:** prefer permitted source/import; avoid CAPTCHA bypass, account misuse or aggressive collection.
- **Personal data:** synthetic data only; telemetry opt-in/anonymous if used.
- **Maintenance:** pin lockfiles, automated dependency updates, minimal external dependencies.

## 13. Portfolio evaluation rubric
| Category | Weight | Evidence |
|---|---:|---|
| Engineering correctness & tests | 25% | CI, tests, contracts, security review |
| Demo usability | 20% | e2e, visitor task walkthrough |
| System design | 20% | diagrams, ADR, tradeoff discussions |
| Originality/problem relevance | 15% | real user problem, clear decisions |
| Documentation | 10% | README, API, screenshots |
| Operational maturity | 10% | deploy process, runbooks, observability |

Do not publish a numeric "quality score" without actual review against the rubric.
