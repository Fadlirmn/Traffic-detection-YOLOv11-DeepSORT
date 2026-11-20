# Vehicle Tracking — replay contract, schema, processing and tests

> **Status note:** everything below is a **target contract**. The current repo (`System_public.py`) writes no manifest, no event file, nothing — state lives only in in-process dicts (`last_positions`, `stuck_frames`) and is discarded after each run. Fields here are designed so they can be derived from that existing in-memory state (and the already-working `load_aoi`/`point_in_aoi`/`classify_congestion_bobot` logic) without changing the congestion algorithm itself.

## 1. Export bundle
```
run-2026-demo/
  manifest.json
  events.jsonl
  tracks.jsonl
  detections.jsonl       # optional; large, may downsample for public overlay
  video.webm
  poster.webp
  aggregates.json
```
For public demo, bundle may be transformed into a seek-efficient **time-bucket JSON**; retain reference raw JSONL in repo or archive. Do not download a giant full detection JSON on first paint.

## 2. Manifest v1 example
```json
{
  "schemaVersion": "1.0.0",
  "runId": "sample-run-001",
  "mode": "recorded-inference",
  "createdAt": "2026-11-20T00:00:00Z",
  "source": {"name": "licensed-sample-clip", "rights": "document in media/rights-manifest.md", "sha256": "TO_BE_COMPUTED"},
  "video": {"asset": "video.webm", "width": 1280, "height": 720, "fpsNominal": 25, "durationMs": 60000},
  "model": {"name": "YOLO11", "weightsSha256": "TO_BE_COMPUTED", "inputSize": 640, "confidenceThreshold": 0.35},
  "tracker": {"name": "DeepSORT", "configVersion": "1"},
  "geometry": {"referenceWidth": 1280, "referenceHeight": 720, "aoiPolygons": [[[110,79],[268,55],[502,297],[272,421]]], "countLines": []},
  "congestion": {
    "classWeights": {"bus": 4.60, "car": 1.0, "motorcycle": 0.18, "truck": 3.13},
    "stuckThresholdPx": 2,
    "stuckFramesRequired": 15,
    "sedangThreshold": 2.0,
    "macetThreshold": 4.0
  },
  "provenance": {"engineGitCommit": "TO_BE_COMPUTED", "label": "Sample prerecorded output"},
  "files": {"events": "events.jsonl", "tracks": "tracks.jsonl", "aggregates": "aggregates.json"}
}
```
`TO_BE_COMPUTED` is **not** a real integrity hash and must be replaced for release. Sample illustrative values are not benchmark claims. `geometry.aoiPolygons` mirrors the real polygons already used in `AOI/aoi.txt`; `geometry.countLines` stays empty until crossing-line counting (future, P1) is implemented — never populate it with placeholder data. `congestion.*` mirrors the weights/thresholds already hardcoded in `System_public.py` today.

## 3. Event contracts
Tracking observation (JSON line):
```json
{"type":"track_observation","runId":"sample-run-001","frameIndex":128,"ptsMs":5120,"trackId":"42","objectClass":"car","confidence":0.91,"box":{"x":520,"y":310,"width":160,"height":90},"state":"confirmed","inAoi":true,"stuckFrames":4}
```

**Congestion snapshot (already-real logic, new contract — one per processed frame):**
```json
{"type":"congestion_snapshot","runId":"sample-run-001","frameIndex":128,"ptsMs":5120,"vehicleCount":6,"stuckCounts":{"bus":0,"car":1,"motorcycle":2,"truck":0},"weightedIndex":1.36,"level":"SEDANG"}
```

**Telegram alert (already-real logic, new contract — emitted when level transitions to MACET and cooldown has elapsed):**
```json
{"type":"telegram_alert","runId":"sample-run-001","ptsMs":182400,"level":"MACET","weightedIndex":4.6,"vehicleCount":5,"snapshotRef":"snapshots/jam_1732100000.jpg","cooldownSec":300}
```

**Crossing event (future — only if crossing-line counting is implemented; not in current repo):**
```json
{"type":"line_crossing","eventId":"sample-run-001:42:line-1:in:1","runId":"sample-run-001","ptsMs":6820,"trackId":"42","objectClass":"car","lineId":"line-1","direction":"in","confidence":0.91}
```
Rules: timestamps >=0, finite numeric values; `frameIndex` >=0, `trackId` scoped per run; frame coordinate system same as manifest, box constrained to frame; event unique; `out`/`in` direction only if line orientation is defined; `telegram_alert.ptsMs` spacing must respect `cooldownSec` (no two alerts closer than cooldown in the same run).

## 4. Data access API (demo)
| Method | Path | Result |
|---|---|---|
| GET | `/api/demo/runs` | list fixtures |
| GET | `/api/demo/runs/{runId}/manifest` | manifest, hashes and URL paths |
| GET | `/api/demo/runs/{runId}/events?fromMs=&toMs=&class=` | bounded events |
| GET | `/api/demo/runs/{runId}/congestion?bucketSec=30` | congestion snapshots + alert markers over time (primary chart data) |
| GET | `/api/demo/runs/{runId}/aggregates?bucketSec=30` | precomputed totals |
| GET | `/api/demo/runs/{runId}/export.csv` | labeled sample output |

`events` and any `line_crossing`-filtered query only return data once crossing-line counting (future, P1) exists; until then the endpoint returns an empty, schema-valid list rather than 404.

Only allowlisted `runId`, no arbitrary file paths or SSRF. Validate query bounds (`fromMs <= toMs`, max window). Prefer static manifest/index and browser fetch if simple.

## 5. Processing correctness
- Detector output classes map through versioned dictionary to stable class taxonomy.
- Tracker update uses each frame's detections once, not repeated on display.
- Crossing classifier: centroid/bottom-center configurable, `signedDistance` and crossing direction; minimum distance and frame persistence suppress jitter.
- `eventId` can be derived deterministically; idempotent event sink handles replay duplicates.
- Invalid/overlapping frames produce diagnostic counters and are excluded deliberately.
- Export includes engine commit, library versions, device info, config and source rights manifest.

## 6. Required tests
| Unit | Positive / negative cases |
|---|---|
| AOI containment (`point_in_aoi`) | point inside polygon, outside, on edge, multiple disjoint polygons, empty polygon list |
| Stuck-frame counter | resets on movement >=2px, accumulates on movement <2px, exactly reaches 15-frame threshold, track reappears after gap |
| Congestion classifier (`classify_congestion_bobot`) | boundary at index==2.0 (SEDANG), index==4.0 (MACET), index==0 (LANCAR), mixed-class weighted sum |
| Box mapper | resized input restored to original, clipped coordinates, empty list |
| Line crossing *(future, only once implemented)* | one crossing, backwards, jitter, stationary, track disappears/reappears |
| Event ID | deterministic, unique across direction/sequence/run |
| Tracker adapter | no detection, occlusion, low confidence, out-of-order frame |
| Export | stable schema, invalid float rejection, datetime correctness |
| Demo time index | play/seek/pause, 0ms, last frame, clip end |
| Aggregation | congestion snapshot table exactly equals recomputed values for selected window |
| Rendering | accessible controls and safe missing video fallback |

## 7. Reproducible commands (target CLI interface)
```
python -m tracker infer --input ./samples/licensed.mp4 --config ./configs/sample.yaml --output ./out/run-a
python -m tracker export-replay --run ./out/run-a --dest ./apps/showcase/static/replays/run-a
python -m tracker benchmark --input ./samples/licensed.mp4 --repeat 3 --output ./out/benchmark.json
python -m pytest
```
Commands describe the **contract to implement**; they are not asserted to exist yet.
