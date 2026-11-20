# PRD 02 — Vehicle Tracking: Real-time CV Engine + Replay Showcase

**Version:** 1.0 · **Priority:** P0 (featured) · **Mode:** Actual local/edge inference engine, Vercel video+metadata replay

## 1. Problem / positioning
A technically rigorous vehicle detection and tracking system based on YOLO11 (often called YOLOv11) and DeepSORT, with reproducible inference, evaluation, event outputs and an intuitive browser viewer. It demonstrates Python, computer vision, edge computing and metrics instrumentation. **Public showcase is not live inference**; it replays genuine precomputed engine output with transparent timestamps and source provenance.

**Baseline that already runs today (repo as-is):** `System_public.py` batch-processes videos from `Source/`, runs YOLO11 + DeepSORT, filters tracks against an AOI polygon (`AOI/aoi.txt`), flags vehicles as *stuck* when centroid movement stays below 2px for ≥15 consecutive frames, aggregates stuck vehicles into a class-weighted **congestion index** (LANCAR/SEDANG/MACET), and pushes a Telegram alert with a frame snapshot when the level is MACET (5-minute cooldown, `/start /stop /status /current /help` bot commands in `telegram_bot.py`). This congestion + alert pipeline is the real, working core; line-crossing counting described later in this document is a **future extension**, not yet implemented.

## 2. Stakeholders and target use
- Engineering reviewer checks tracking pipeline, model version, reproducibility and quantitative metrics.
- General visitor watches detections, IDs, count trends and system limitations without specialized hardware.
- Operator (real-mode local) loads a file/camera, configures ROI/line, starts/stops processing, exports events.

## 3. Goals (targets)
| ID | Goal | Evidence |
|---|---|---|
| G1 | Fully reproducible inference CLI on a documented sample video | command + deterministic export schema |
| G2 | Browser timeline synchronized to event JSON within 1 display frame at specified FPS tolerance | Playwright/frame tests |
| G3 | Tracking and line-crossing counting do not double count stable IDs | unit and golden tests |
| G4 | Report throughput and accuracy with hardware/dataset details, not marketing estimates | benchmark report |
| G5 | Public demo runs on Vercel without GPU, VPS or Python server | fixture/replay-only smoke test |
| G6 | No publication of unlicensed or identifiable media without consent | media checklist |
| G7 | Congestion index (weighted stuck-vehicle count) matches manual review on a sample clip | golden test on `classify_congestion_bobot` |
| G8 | No secret (Telegram bot token) committed in plaintext source before any publication | secret scan; `System_public.py:17` currently fails this |

## 4. Functional boundaries
| Feature | Real implementation | Public showcase | Priority |
|---|---|---|---|
| Video file ingest | OpenCV decoder, batch loop over `Source/` (today); file validation (target) | versioned sample clip | P0 |
| Object detection | YOLO11 model in Python runtime (`Models/best.pt`, already working) | detections exported as sidecar JSON | P0 |
| Multi-object tracking | DeepSORT associating boxes IDs (already working) | rendered/replayed ID overlays | P0 |
| AOI zone filtering | polygon containment (`AOI/aoi.txt`, already working) | inspect overlay + optional preset selection | P0 |
| Stuck-vehicle detection | pixel-distance/frame-persistence heuristic (already working) | replayed stuck markers | P0 |
| Congestion index | class-weighted LANCAR/SEDANG/MACET classifier (already working) | synchronized charts and level badge | P0 |
| Telegram alert | bot notification + snapshot, cooldown (already working, token needs hardening) | simulated/replayed alert card | P0 |
| Crossing line counting | stable track IDs, direction rules — **not implemented yet**, future extension | playback counter overlay | P1 |
| Timeline chart | derived events + snapshot metrics | synchronized charts and tables | P1 |
| CSV/JSON export | actual engine events — no export today, target contract only | download sample export | P1 |
| Batch benchmark | scripts over labeled dataset | benchmark report if measured | P1 |
| Source camera / Raspberry Pi | device adapter, optional documented example | not connected on public demo | P2 |
| Network live stream, multi-camera | optional future | not promised | P2 |

## 5. What will be demonstrated truthfully?
- Replay video clip **really processed by local Python engine** (`System_public.py`) and exported event file.
- Primary overlay: AOI polygon, per-vehicle box/ID, stuck markers, and the live congestion level/index badge — drawn from actual recorded run data, not invented.
- Secondary (future, only if crossing-line feature is later implemented): direction counters; must not be shown until that feature exists.
- `Recorded inference`, `Sample dataset`, recording date and inference model/weights version displayed.
- Telegram alert shown in the showcase is a **replayed/simulated card** (same copy the real bot sends), never a live message sent from the public demo.
- If only synthetic example used during initial build, banner must say **Synthetic demo events**, not claim real inference.
- No `LIVE` indicators, live camera icons, or uptime/inference FPS claims without actual measured evidence.

## 6. Technology choices
| Layer | Today (repo as-is) | Target | Notes |
|---|---|---|---|
| Engine | Python 3.x, two flat scripts (`System_public.py`, `telegram_bot.py`) | modular pipeline, typed models | target adds `engine/` package structure |
| Detector | Ultralytics YOLO11, `Models/best.pt` | same | validate commercial/open-source license and model weights |
| Tracker | `deep-sort-realtime` | DeepSORT maintained compatible implementation | check license/dependency API, freeze model seed |
| Image/video | OpenCV, NumPy | same | pre/postprocessing and video IO |
| Zone/alert logic | AOI polygon containment + weighted congestion index, in-process | same logic, extracted into testable module | `load_aoi`, `point_in_aoi`, `classify_congestion_bobot` |
| Notification | `pyTelegramBotAPI` (`telebot`), hardcoded token | same, token from env/secret store | **security gap today**, see §17 |
| Schemas | none — no export file written | Pydantic v2 + JSON Schema | versioned exchange format, not started |
| Metadata storage | none — in-memory dicts only | SQLite for local single-file usage; optional PostgreSQL adapter | no public DB needed |
| CLI | none — hardcoded paths/constants at top of `System_public.py` | Typer or argparse | reproducible headless execution |
| Demo UI | none | SvelteKit 5/TS/Tailwind + Canvas overlay | media time drives event selector |
| Hosting | none (local execution only) | Vercel + static JSON and compressed media/CDN | no GPU compute |
| Analysis | none | Pandas optional offline, plotting/JSON exporter | never required at request time |
| Test | none | pytest, golden fixtures, format/lint, Playwright | deterministic visual/event tests |

## 7. Pipeline architecture

**Today (real, running now):**
```
Source/*.mp4 -> OpenCV decode -> YOLO11 detect -> DeepSORT track
 -> AOI polygon filter (per-track centroid) -> stuck-frame counter (<2px, >=15 frames)
 -> class-weighted congestion index -> LANCAR/SEDANG/MACET
 -> overlay drawn on frame (frames/latest.jpg) -> Telegram alert if MACET (cooldown 5min)
```
No event file is written; state lives only in-process (`last_positions`, `stuck_frames` dicts) for the duration of the run.

**Target (future extension, not built):**
```
source (file/camera) -> decode -> frame normalization -> detector
 -> confidence/NMS -> tracker -> track state and aging
 -> ROI/line-crossing event processor (optional add-on) -> counts & statistics
 -> writer (JSONL/CSV, timing, metrics) -> visualization export

Public showcase:
pre-recorded MP4/WebM + event JSON + metadata manifest
 -> Vercel static/CDN -> browser media element
 -> frame-time-indexed overlay -> congestion/timeline/table
```

### Source engine conventions
- Pipeline stages are separate interfaces; tracking is stateful only within a local processing session.
- Frames carry source frame index, PTS/video timestamp, resolution and orientation.
- Preprocess preserves mapping from model input pixels to original frame boxes.
- Count cross-line transitions with hysteresis/previous-side state; avoid oscillation/double count.
- Out-of-order, dropped, and uncertain frames handled explicitly; never invent IDs on display.
- Reproducibility requires pinned weights fingerprint, tracker configuration, seed (where relevant), input hash and hardware notes.

## 8. User stories
**US-00 Operator receives congestion alert (P0, already real today):** operator runs `python System_public.py` against clips in `Source/` → system tracks vehicles in the AOI, flags stuck ones, computes the weighted index → when level reaches MACET, Telegram group receives a snapshot + caption (vehicle weight total, level, vehicle count, timestamp), rate-limited to once per 5 minutes. Operator can also query `/status` and `/current` on demand. Acceptance: alert only fires on real MACET transition, never duplicated within cooldown; `/current` returns the latest processed frame.

**US-01 Public replay (P0):** guest opens demo → first example loads → press play → bounding boxes, track IDs and the AOI polygon follow vehicle positions, congestion badge updates with the replayed level. Acceptance: current position queried from `<video>` `currentTime`, event buckets indexed using manifest FPS/time; controls support pause, seek, speed 0.5/1/1.5, keyboard and reduced motion.

**US-02 Congestion explanation (P0):** guest opens the congestion breakdown panel → sees per-class stuck counts, the weighted index formula applied, and the resulting LANCAR/SEDANG/MACET level over time. Acceptance: index recomputation in the UI matches the recorded run's values for the loaded recording. *(Future, only once crossing-line counting is implemented — P1: a direction-crossing table with timestamp/track ID/class/side transition, additive to this panel, not a replacement.)*

**US-03 Analyze performance (P1):** guest views measured throughput and evaluation table. Acceptance: report states test machine (Raspberry Pi 5 if actually used), model weights, input size, FPS methodology, warmup and dataset samples; unmeasured values labeled N/A, not guessed.

**US-04 Local inference (P1, target — not implemented):** developer runs `python -m tracker infer --input samples/vehicles.mp4 --config configs/demo.yaml --output out/run` → output manifest and events → replay app loads compatible bundle. Today's real entry point is simply `python System_public.py`, which batch-processes every video in `Source/` with constants hardcoded at the top of the file — no CLI flags, no manifest/event output yet. Acceptance (once built): exit nonzero on invalid inputs; processing errors recorded; JSON Schema validates output; published media rights checked.

**US-05 ROI preset (P0):** guest chooses a precomputed AOI preset → replay filters view to that scenario; does **not** imply running new inference. Acceptance: congestion values agree with matching precomputed events; if no matching preset data, toggle is disabled.

## 9. Frontend IA
- `/` intro, recording status (pre-recorded), source code & explanation.
- `/demo` video player, overlays, time scrubber, playback speed, track class filter, direction counts.
- `/demo/events` searchable event table with CSV export and filters.
- `/demo/analytics` volume over time, class distribution, track lifespan, performance evidence.
- `/methodology` dataset/sample details, model/tracker configuration, evaluation metrics, limitations.
- `/architecture` pipeline graphic and implementation details.

## 10. Domain business rules

**Already real today:**
- Entity class taxonomy: model class IDs `{0: bus, 1: car, 2: motobike, 3: truck}` (note: `motobike` is a typo in the current code for `motorbike`/`motorcycle` — cleanup item before any public schema export, to avoid baking the typo into a versioned contract).
- AOI membership: a track counts only if its box centroid falls inside at least one AOI polygon (`cv2.pointPolygonTest >= 0`); polygons loaded from blank-line-separated `x,y` pairs in `AOI/aoi.txt`.
- Stuck criterion: a track is "stuck" once its centroid moves `< 2px` between frames for `>= 15` consecutive frames; movement resets the counter.
- Congestion index: `index = Σ (class_weight × stuck_count_for_class)` with weights `{motor: 0.18, car: 1.0, truck: 3.13, bus: 4.60}`.
- Congestion level: `index >= 4` → MACET, `index >= 2` → SEDANG, else LANCAR.
- Alert rule: Telegram alert fires only on MACET, at most once per 300s (cooldown), always attaching the current frame snapshot.
- Each detection: frame index, box in original dimensions, label, score 0..1 (score gate currently `conf >= 0.53`).
- Each track: stable `track_id` within run (from DeepSORT), confirmed-only tracks are considered.

**Future — not implemented in current repo (only if crossing-line counting is added later):**
- Each crossing: unique event `runId:trackId:lineId:direction:crossingSequence`, timestamp and source.
- One physical vehicle might be assigned two IDs after occlusion; disclose limitation and evaluate ID switches.
- Aggregate count uses unique finalized crossing events, no incremental count based on bounding box count.
- Bounding boxes clipped to valid coordinates, never negative/NaN; time base monotonic.

## 11. Evaluation & benchmark plan
No benchmark or test infrastructure exists today — `classify_congestion_bobot`, `load_aoi`, `point_in_aoi` and the stuck-frame logic have zero automated coverage. Building golden tests for these four functions is a prerequisite before any metric is published (see §16 rollout, task 0/1).

Report only observed results using explicit standardized protocol:
- Data: source/right-to-use, sample count, clip duration, annotations if accuracy metrics computed.
- Devices: CPU/GPU model, RAM, OS, package versions; note Raspberry Pi 5 exact configuration only if tested.
- Performance: latency p50/p95 in ms per frame, throughput FPS, decode/inference/tracker breakdown; 3 runs, warmup defined.
- Detection: precision, recall, mAP only if labeled ground truth exists and correct evaluation code used.
- Tracking: IDF1/MOTA/HOTA/ID switches only if valid ground truth and methodology; otherwise report `not measured`.
- Counting: MAE/MAPE (avoid MAPE at zero denominator), per-direction count error vs ground truth.
- Export benchmark artifacts as checked-in sanitized Markdown/JSON with date.

## 12. Media & data safety
- Only approved/synthetic/public-rights source videos; check faces, license plates, GPS and metadata; blur/anonymize if necessary.
- Avoid exposing surveillance equipment credentials, camera URLs, private scenes or location histories.
- No public arbitrary video upload for first release, which reduces malicious media handling/cost.
- Clip optimized for bandwidth, poster thumbnail, captions or description for accessibility, 720p max initially.
- Stable manifest hash validates JSON and video pairing; graceful fallback if media unavailable.

## 13. NFR & quality
- Demo: first meaningful image within 3 sec target on test connection; mobile fallback for overlay-heavy viewer.
- Browser video/time sync: frame bucket tolerances and drift correction when seeking; overlay update via `requestVideoFrameCallback` when supported, fallback `timeupdate`/rAF carefully.
- A11y: playback keyboard, alternative table for boxes/events, captions/transcript of key visual events.
- Engine: logs per stage, resilient invalid frames, bounded video memory usage; configurable CPU fallback.
- Security: pinned dependencies, model weight verification by hash; sandbox untrusted media locally.
- Full screen and touch controls tested; render overlay with device-pixel-ratio awareness.

## 14. Acceptance matrix
| ID | Test | Expected |
|---|---|---|
| AC-01 | Open demo without backend/GPU | video and events work |
| AC-02 | Seek to 00:15 and pause | overlay matches frame index |
| AC-03 | Filter `motorcycle` | only relevant events/boxes show |
| AC-04 | Replay 3 times | counts stable, no duplicate event entries |
| AC-05 | Invalid event schema | safe error, no page crash |
| AC-06 | Offline/browser reload fixture | documented fallback or offline hint |
| AC-07 | Local inference invalid file | safe error + exit code |
| AC-08 | Detector output outside image bounds | values normalized/clipped |
| AC-09 | Keyboard-only player | usable with focus indicator |
| AC-10 | Public page claims | all replay/benchmark labels accurate |

## 15. Repository design

**Phase 0 (current, actual repo today):**
```
System_public.py      # main loop: YOLO + DeepSORT + AOI + congestion + telegram trigger
telegram_bot.py        # bot commands, alert send, cooldown/state
Models/best.pt
AOI/aoi.txt
Source/                # input videos (not committed)
Output/Snapshots/      # congestion snapshots
frames/latest.jpg
```

**Target (migration destination, incremental):**
```
engine/tracker/{detectors,trackers,events,geometry,congestion,io,cli}
engine/configs/
engine/tests/{unit,golden,integration}
apps/showcase/src/routes/{demo,analytics,methodology,architecture}
fixtures/replays/{sample-a/manifest.json,events.json,poster.webp}
media/{README,rights-manifest.md}  # large media on CDN or Git LFS where appropriate
scripts/{export-replay,benchmark,validate-manifest}
docs/{adr,methodology,benchmark-results}
```
`engine/tracker/congestion` is the extraction target for today's `classify_congestion_bobot`/AOI/stuck logic — move, don't rewrite, to keep behavior identical and testable.

Do not commit proprietary model weights or raw private footage to public repo. Provide verified download instructions and integrity hashes.

## 16. Rollout tasks
0. **Harden what already runs:** move Telegram token to env var/secret (fix `System_public.py:17`), fix `motobike` → `motorcycle` class-name typo, move hardcoded paths/thresholds into a config file.
1. Extract `load_aoi`, `point_in_aoi`, `classify_congestion_bobot` and stuck-frame logic into a testable module (`engine/tracker/congestion`); add unit/golden tests (no behavior change).
2. Freeze class taxonomy/event schema for congestion (stuck/level/alert), informed by the already-working logic.
3. Add CLI (`argparse`/Typer) over the existing loop; write manifest + congestion event export (JSONL/JSON), replacing hardcoded `Source/`/`Models/`/`AOI/` paths with flags/config.
4. Capture/export a sanctioned sample run (video + exported congestion events + Telegram-alert replay payload).
5. (Optional, P1) Implement crossing-line counting and its golden tests as an additive feature, once congestion export is stable.
6. Build Vercel replay UI: AOI overlay, congestion badge/timeline, replayed Telegram alert card.
7. Test timing (video/overlay sync).
8. Publish benchmark evidence (throughput, stuck/congestion accuracy on a labeled sample) or explicitly `not measured`.
9. Accessibility/media audit. 10. CI and README runbook. 11. Publish.

## 17. Risks
- **Telegram token hardcoded in plaintext source** (`System_public.py:17`): must move to env var/secret before any repo publication; treat current source as containing a live credential until rotated.
- AOI polygons are tied to a fixed camera perspective/resolution (`AOI/aoi.txt`); not portable across videos without recalibration — document this limitation, don't imply general applicability.
- Model class-name typo (`motobike`) risks baking an inconsistent taxonomy into any future exported schema; fix before freezing the event contract.
- Model weights and license restrictions: review and document; do not assume AGPL/commercial suitability.
- ID switches and occlusion: visualize limitations rather than conceal.
- Raspberry Pi performance: avoid promising real-time without hardware benchmark.
- Model inference in browser/serverless: not part of P0; no complex GPU serverless commitment.
- `deep-sort-realtime`/`pyTelegramBotAPI` dependency licenses not yet reviewed for public repo distribution.
