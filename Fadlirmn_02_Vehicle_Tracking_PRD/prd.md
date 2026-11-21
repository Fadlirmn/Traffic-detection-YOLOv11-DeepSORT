# PRD — Vehicle Tracking (YOLO11 + DeepSORT)

**Fadlirmn — Individual Project PRD** · Version 1.0 · 2026-11-20
**Priority:** P0 (featured portfolio project) · **Mode:** real local/edge CV engine + Vercel replay showcase

## 1. Tujuan paket
Source code nyata (CV pipeline, congestion logic, alerting) + showcase demo di Vercel/serverless **tanpa VPS**, memakai data sintetis/replay yang dilabeli jujur. Stack: Python + YOLO11 + DeepSORT (+ target FastAPI/SvelteKit untuk demo).

## 2. Problem / positioning
Sistem deteksi & tracking kendaraan (YOLO11 + DeepSORT) dengan inference reproducible, event output dan viewer browser. Membuktikan kompetensi Python, computer vision, edge computing, metrics instrumentation. **Showcase publik bukan live inference** — replay output engine asli dengan timestamp & provenance transparan.

**Baseline yang sudah berjalan hari ini (repo as-is):** `System_public.py` batch-process video dari `Source/` → YOLO11 + DeepSORT → filter track via AOI polygon (`AOI/aoi.txt`) → flag *stuck* jika centroid gerak <2px selama ≥15 frame berturut → agregasi jadi **congestion index** berbobot kelas (LANCAR/SEDANG/MACET) → kirim alert Telegram + snapshot saat MACET (cooldown 5 menit; command `/start /stop /status /current /help` di `telegram_bot.py`). Ini adalah core nyata yang bekerja. **Line-crossing counting adalah future extension, belum diimplementasikan.**

## 3. Goals (target, bukan hasil aktual)
| ID | Goal | Evidence |
|---|---|---|
| G1 | Inference CLI reproducible di sample video | command + deterministic export schema |
| G2 | Timeline browser sinkron dengan event JSON (toleransi 1 frame) | Playwright/frame tests |
| G3 | Tracking & counting tidak double-count ID stabil | unit + golden tests |
| G4 | Throughput/akurasi dilaporkan dengan hardware/dataset detail, bukan estimasi marketing | benchmark report |
| G5 | Demo publik jalan di Vercel tanpa GPU/VPS/Python server | fixture/replay-only smoke test |
| G6 | Tidak publikasi media unlicensed/identifiable tanpa consent | media checklist |
| G7 | Congestion index (weighted stuck count) match manual review di sample clip | golden test `classify_congestion_bobot` |
| G8 | Tidak ada pattern hardcoded-secret untuk Telegram token sebelum publikasi | secret scan — **`System_public.py:17` masih assignment literal (`"***"` placeholder), perlu pindah ke env sebelum token asli ditempel** |

## 4. Functional boundaries
| Feature | Real implementation | Public showcase | Priority |
|---|---|---|---|
| Video ingest | OpenCV batch loop `Source/` (sudah jalan) | sample clip versioned | P0 |
| Object detection | YOLO11 (`Models/best.pt`, sudah jalan) | detections JSON sidecar | P0 |
| Multi-object tracking | DeepSORT ID (sudah jalan) | overlay ID replay | P0 |
| AOI zone filtering | polygon containment `AOI/aoi.txt` (sudah jalan) | overlay + preset selection | P0 |
| Stuck-vehicle detection | pixel-distance/frame-persistence (sudah jalan) | stuck markers replay | P0 |
| Congestion index | class-weighted LANCAR/SEDANG/MACET (sudah jalan) | chart + level badge sinkron | P0 |
| Telegram alert | bot + snapshot + cooldown (sudah jalan, token perlu hardening) | simulated/replayed alert card | P0 |
| Crossing line counting | **belum diimplementasikan**, future extension | playback counter overlay | P1 |
| Timeline chart | event + snapshot metrics turunan | chart & table sinkron | P1 |
| CSV/JSON export | belum ada export hari ini, target contract saja | download sample export | P1 |
| Camera / Raspberry Pi | device adapter opsional | tidak terhubung di demo publik | P2 |
| Live stream, multi-camera | future opsional | tidak dijanjikan | P2 |

## 5. Apa yang ditampilkan secara jujur
- Replay clip yang **benar-benar diproses** engine lokal (`System_public.py`) + exported event file.
- Overlay utama: AOI polygon, box/ID per kendaraan, stuck markers, badge/index congestion live — dari data run asli, bukan rekaan.
- Counter arah (future, hanya jika crossing-line sudah diimplementasikan) — jangan tampilkan sebelum fitur ada.
- Label `Recorded inference`, `Sample dataset`, tanggal rekam, versi model/weights ditampilkan.
- Alert Telegram di showcase = **replayed/simulated card** (copy sama dengan bot asli), bukan pesan live dari demo publik.
- Jika hanya pakai contoh sintetis saat build awal → banner **"Synthetic demo events"**, jangan klaim real inference.
- Tidak ada indikator `LIVE`, ikon kamera live, atau klaim FPS/uptime tanpa evidence terukur.

## 6. Technology choices
| Layer | Hari ini (repo as-is) | Target | Catatan |
|---|---|---|---|
| Engine | Python 3.x, 2 script flat (`System_public.py`, `telegram_bot.py`) | modular `engine/` package, typed models | |
| Detector | Ultralytics YOLO11, `Models/best.pt` | sama | cek lisensi model/software |
| Tracker | `deep-sort-realtime` | sama, versi terjaga | freeze model seed |
| Image/video | OpenCV, NumPy | sama | |
| Zone/alert logic | AOI polygon + weighted index, in-process | logic sama, diekstrak jadi module testable | `load_aoi`, `point_in_aoi`, `classify_congestion_bobot` |
| Notification | `pyTelegramBotAPI`, token hardcoded | sama, token dari env/secret | **gap keamanan, lihat §12** |
| Schemas | tidak ada export | Pydantic v2 + JSON Schema | versioned exchange format |
| Metadata storage | in-memory dict saja | SQLite lokal; opsional PostgreSQL | tidak perlu DB publik |
| CLI | tidak ada, hardcoded path/const | Typer/argparse | reproducible headless |
| Demo UI | tidak ada | SvelteKit 5/TS/Tailwind + Canvas overlay | media time drives event selector |
| Hosting | lokal only | Vercel + static JSON + CDN | tanpa GPU compute |
| Test | tidak ada | pytest, golden fixtures, Playwright | deterministic |

## 7. Pipeline architecture

**Hari ini (real, berjalan):**
```
Source/*.mp4 -> OpenCV decode -> YOLO11 detect -> DeepSORT track
 -> AOI polygon filter (per-track centroid) -> stuck-frame counter (<2px, >=15 frames)
 -> class-weighted congestion index -> LANCAR/SEDANG/MACET
 -> overlay (frames/latest.jpg) -> Telegram alert if MACET (cooldown 5min)
```
Tidak ada event file ditulis; state hanya in-process (`last_positions`, `stuck_frames`) selama run.

**Target (future, belum dibangun):**
```
source (file/camera) -> decode -> normalize -> detector -> NMS -> tracker
 -> track state/aging -> ROI/line-crossing (opsional) -> counts & stats
 -> writer (JSONL/CSV) -> visualization export

Public showcase:
pre-recorded MP4/WebM + event JSON + manifest -> Vercel CDN
 -> browser media element -> frame-time-indexed overlay -> congestion/timeline/table
```

Konvensi engine: stage terpisah per interface; tracking stateful hanya dalam 1 sesi lokal; frame carry source index/PTS/resolution; mapping pixel model↔frame asli dijaga; line-crossing count pakai hysteresis anti double-count; frame invalid/drop ditangani eksplisit, jangan invent ID; reproducibility butuh weights fingerprint, tracker config, seed, input hash, hardware notes.

## 8. Domain business rules

**Sudah real hari ini:**
- Class taxonomy: `{0: bus, 1: car, 2: motobike, 3: truck}` — **`motobike` typo** untuk `motorcycle`, bersihkan sebelum freeze schema publik.
- AOI membership: centroid box di dalam polygon (`cv2.pointPolygonTest >= 0`), polygon dari `AOI/aoi.txt`.
- Stuck: centroid gerak `<2px` antar frame selama `>=15` frame berturut; gerak mereset counter.
- Congestion index: `Σ (class_weight × stuck_count)`; weights `{motor: 0.18, car: 1.0, truck: 3.13, bus: 4.60}`.
- Level: `index >= 4` → MACET, `index >= 2` → SEDANG, else LANCAR.
- Alert: Telegram fire hanya saat MACET, max 1x/300s, selalu attach snapshot frame.
- Deteksi: frame index, box original dims, label, score (`conf >= 0.53`); track stabil dari DeepSORT, confirmed-only.

**Future — belum ada di repo (hanya jika crossing-line ditambahkan):**
- Crossing event unik: `runId:trackId:lineId:direction:crossingSequence` + timestamp.
- 1 kendaraan fisik bisa dapat 2 ID setelah occlusion — disclose limitation, jangan sembunyikan.
- Aggregate count dari unique finalized crossing event, bukan raw box count.
- Box diklip ke koordinat valid, time base monotonic.

## 9. Export contract (target — belum ada hari ini)

Bundle: `manifest.json`, `events.jsonl`, `tracks.jsonl`, `detections.jsonl` (opsional), `video.webm`, `poster.webp`, `aggregates.json`. `TO_BE_COMPUTED` hash placeholder wajib diganti sebelum release.

Manifest v1 (ringkas):
```json
{
  "schemaVersion": "1.0.0", "runId": "sample-run-001", "mode": "recorded-inference",
  "video": {"asset": "video.webm", "width": 1280, "height": 720, "fpsNominal": 25},
  "model": {"name": "YOLO11", "inputSize": 640, "confidenceThreshold": 0.35},
  "tracker": {"name": "DeepSORT"},
  "geometry": {"aoiPolygons": [[[110,79],[268,55],[502,297],[272,421]]], "countLines": []},
  "congestion": {"classWeights": {"bus":4.60,"car":1.0,"motorcycle":0.18,"truck":3.13},
    "stuckThresholdPx": 2, "stuckFramesRequired": 15, "sedangThreshold": 2.0, "macetThreshold": 4.0}
}
```
`countLines` tetap kosong sampai crossing-line benar diimplementasikan — jangan isi placeholder.

Event types: `track_observation`, `congestion_snapshot` (per frame — vehicleCount, stuckCounts, weightedIndex, level), `telegram_alert` (saat transisi ke MACET, respect cooldown), `line_crossing` (future only).

Demo API (read-only, allowlisted `runId`, no SSRF):
| Method | Path | Result |
|---|---|---|
| GET | `/api/demo/runs` | list fixtures |
| GET | `/api/demo/runs/{id}/manifest` | manifest + hash |
| GET | `/api/demo/runs/{id}/events?fromMs&toMs&class` | bounded events |
| GET | `/api/demo/runs/{id}/congestion?bucketSec=30` | snapshot + alert markers (chart utama) |
| GET | `/api/demo/runs/{id}/aggregates?bucketSec=30` | totals |
| GET | `/api/demo/runs/{id}/export.csv` | labeled sample output |

## 10. User stories (ringkas)
- **US-00 (P0, real hari ini):** operator run `python System_public.py` → track AOI → flag stuck → index → MACET → Telegram snapshot (cooldown 5min); `/status` `/current` on-demand.
- **US-01 (P0):** guest buka demo → play → box/ID/AOI polygon mengikuti posisi, badge congestion update dari replay.
- **US-02 (P0):** guest lihat breakdown congestion (stuck count per class, formula, level over time) — index UI harus match recorded run.
- **US-03 (P1):** guest lihat throughput/eval table — nyatakan device, model, methodology; unmeasured = N/A, bukan tebakan.
- **US-04 (P1, target):** `python -m tracker infer --input ... --config ... --output ...` → manifest+events; hari ini entry point hanya `python System_public.py` (no CLI flags).
- **US-05 (P0):** guest pilih AOI preset precomputed → filter view, tidak trigger inference baru.

## 11. Frontend IA (target)
`/` intro & source · `/demo` player+overlay+scrubber · `/demo/events` table+CSV export · `/demo/analytics` volume/class/lifespan/benchmark · `/methodology` dataset/model/metrics/limitation · `/architecture` pipeline diagram.

## 12. NFR, tes, acceptance
- First meaningful image <=3s target; overlay via `requestVideoFrameCallback` (fallback timeupdate/rAF); a11y keyboard+alt table+captions; logs per stage; pinned deps + model weight hash verification.
- Unit tests wajib (belum ada satupun hari ini): AOI containment, stuck-frame counter, congestion classifier (boundary 2.0/4.0/0), box mapper, event ID, tracker adapter edge cases, export schema, demo time index, aggregation match.
- Acceptance matrix: demo jalan tanpa backend/GPU; seek match frame; filter class benar; replay 3x no duplicate; invalid schema → safe error; offline fallback; invalid file → safe error+exit code; box out-of-bounds diklip; keyboard-only player; semua label klaim akurat.
- Benchmark: hanya report hasil terukur (latency p50/p95, FPS, device, dataset rights) — kalau belum diukur, tulis `not measured`, jangan tebak.

## 13. Media & data safety
Hanya video approved/synthetic/public-rights; cek wajah/plat/GPS, blur jika perlu; tidak expose kredensial kamera/lokasi privat; tidak ada upload publik arbitrary di rilis awal; clip dioptimasi bandwidth, 720p max awal; manifest hash validasi pairing video+JSON.

## 14. Security & risks
- **Telegram token hardcoded sebagai literal string** (`System_public.py:17`, saat ini `TELEGRAM_TOKEN = "***"` — placeholder di repo publik, bukan token asli yang bocor) — pola hardcode ini tetap harus diganti ke env/secret sebelum siapa pun menempel token asli di baris itu.
- AOI polygon terikat perspektif/resolusi kamera tetap — tidak portable tanpa rekalibrasi, dokumentasikan limitasi.
- Typo kelas `motobike` berisiko terbawa ke schema versioned — fix sebelum freeze contract.
- Lisensi model weights & dependency (`deep-sort-realtime`, `pyTelegramBotAPI`) belum direview untuk distribusi publik.
- ID switch/occlusion: tampilkan limitasi, jangan sembunyikan. Jangan klaim real-time di Raspberry Pi tanpa benchmark. Inference di browser/serverless bukan scope P0.
- Dual-mode rule: `DATA_MODE=demo|real` validated server-side; demo deployment selalu `demo`; fixture readonly/versioned; tidak ada koneksi demo ke engine real/Telegram asli secara tidak sengaja.

## 15. Repository design
**Hari ini (actual):**
```
System_public.py  telegram_bot.py  Models/best.pt  AOI/aoi.txt
Source/  Output/Snapshots/  frames/latest.jpg
```
**Target (migrasi incremental):**
```
engine/tracker/{detectors,trackers,events,geometry,congestion,io,cli}
engine/configs/  engine/tests/{unit,golden,integration}
apps/showcase/src/routes/{demo,analytics,methodology,architecture}
fixtures/replays/{sample-a/manifest.json,events.json,poster.webp}
media/{README,rights-manifest.md}
scripts/{export-replay,benchmark,validate-manifest}
docs/{adr,methodology,benchmark-results}
```
`engine/tracker/congestion` = target ekstraksi `classify_congestion_bobot`/AOI/stuck logic — pindah, jangan rewrite, supaya behavior identik & testable. Jangan commit model weights proprietary/raw footage privat — sediakan instruksi download + integrity hash.

## 16. Rollout tasks (urutan)
0. Harden yang sudah jalan: token Telegram → env var, fix typo `motobike`→`motorcycle`, hardcoded path/threshold → config file.
1. Ekstrak `load_aoi`/`point_in_aoi`/`classify_congestion_bobot`/stuck-frame ke module testable + unit/golden test (no behavior change).
2. Freeze class taxonomy & event schema congestion (stuck/level/alert).
3. Tambah CLI (argparse/Typer) + manifest/event export (JSONL), ganti hardcoded path jadi flags/config.
4. Capture sample run resmi (video + congestion events + Telegram-alert replay payload).
5. (Opsional P1) Implement crossing-line counting + golden test, setelah congestion export stabil.
6. Bangun Vercel replay UI: AOI overlay, congestion badge/timeline, Telegram alert card replay.
7. Test sinkronisasi video/overlay.
8. Publish benchmark evidence atau `not measured`.
9. Audit a11y/media. 10. CI + README runbook. 11. Publish.

## 17. Dual-mode & deployment constraints (ringkas dari standar lintas-portfolio)
- Vercel: cocok untuk static/SSR/short API/fixture read; **tidak cocok** untuk continuous YOLO inference, Redis worker, long browser automation — itu tetap jalan lokal/edge device.
- Tidak ada state in-memory lintas request, filesystem writeable, atau proses long-running di demo.
- `VERCEL_ENV=production` tidak boleh auto-enable Telegram send asli, scraping asli, atau background worker.
- CI gate: lint/typecheck → unit/contract test → build `DATA_MODE=demo` → Playwright smoke → deploy preview. Secret scan wajib sebelum publish.

## 18. Release checklist
- [ ] `DATA_MODE=demo` hardcoded di demo deployment; token Telegram asli tidak ada di preview/prod demo.
- [ ] Semua fixture berlabel synthetic/recorded; privacy review AOI & video selesai.
- [ ] Tidak ada klaim live model/tracker tanpa live service sungguhan.
- [ ] Journey utama (replay, congestion panel, AOI preset) di-E2E + keyboard test.
- [ ] README real-mode (`python System_public.py`) diverifikasi jalan di clone bersih.
- [ ] Lisensi model weights, dependency, dan hak video direview.
- [ ] Link GitHub, demo route, screenshot, evidence benchmark valid.

> Dokumen ini target implementasi, bukan arsip source code final atau bukti audit repo yang sudah dilakukan.
