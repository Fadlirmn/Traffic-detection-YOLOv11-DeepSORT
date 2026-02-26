import os
import cv2
import numpy as np
import threading
import time
from datetime import datetime
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from telegram_bot import TelegramBot  # pastikan file telegram_bot.py ada

# --- Konfigurasi ---
MODEL_PATH = "Models/best.pt"
AOI_FILE = "AOI/aoi.txt"
INPUT_FOLDER = "Source"
OUTPUT_FOLDER = "Output"
SNAPSHOT_FOLDER = "Output/Snapshots"
TELEGRAM_TOKEN = "***"  # ganti dengan token asli bot

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(SNAPSHOT_FOLDER, exist_ok=True)
os.makedirs("frames", exist_ok=True)

# --- Parameter ---
STUCK_THRESHOLD = 2
STUCK_FRAMES_REQUIRED = 15
CONF_THRESHOLD = 0.53
NOTIFICATION_COOLDOWN = 300  # detik

# --- Kelas kendaraan ---
CLASS_NAMES = {0: "bus", 1: "car", 2: "motobike", 3: "truck"}
VEHICLE_IDS = [0, 1, 2, 3]

# --- Data tracking posisi kendaraan ---
last_positions = {}
stuck_frames = {}

# --- Data notifikasi ---
last_notification_time = 0

# --- Load model dan tracker ---
model = YOLO(MODEL_PATH)
tracker = DeepSort(max_age=25)

# --- Fungsi hitung indeks kemacetan berbasis bobot luas kendaraan ---
def classify_congestion_bobot(stuck_counts,
                              bobot_motor=0.18, bobot_car=1.0,
                              bobot_bus=4.60, bobot_truck=3.13):
    """
    Hitung total bobot kendaraan yang diam di dalam AoI.
    Ambang:  >=4  -> MACET  (70% dari 5 dibulatkan ke 4)
             >=3  -> SEDANG
             <3   -> LANCAR
    """
    bobot_map = {0: bobot_bus, 1: bobot_car, 2: bobot_motor, 3: bobot_truck}
    index = 0.0
    for cls_id, count in stuck_counts.items():
        bobot = bobot_map.get(cls_id, 1.0)
        index += bobot * count

    # ambang macet: 70% dari 5 = 3.5 → dibulatkan ke atas jadi 4
    macet_threshold = 4
    sedang_threshold = 2

    if index >= macet_threshold:
        return {'index': index, 'level': 'MACET'}
    elif index >= sedang_threshold:
        return {'index': index, 'level': 'SEDANG'}
    else:
        return {'index': index, 'level': 'LANCAR'}

# --- Fungsi baca AOI ---
def load_aoi(file_path):
    polygons = []
    pts = []
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                if pts:
                    polygons.append(np.array(pts, dtype=np.int32))
                    pts = []
                continue
            x, y = map(int, line.split(","))
            pts.append([x, y])
    if pts:
        polygons.append(np.array(pts, dtype=np.int32))
    return polygons

# --- Fungsi cek titik dalam AOI ---
def point_in_aoi(point, polygons):
    for poly in polygons:
        if cv2.pointPolygonTest(poly, point, False) >= 0:
            return True
    return False

# --- Fungsi kirim notifikasi Telegram ---
def send_telegram(bot, frame, congestion, vehicle_count, video_name):
    global last_notification_time
    now = time.time()

    if now - last_notification_time < NOTIFICATION_COOLDOWN:
        return  # masih cooldown

    snapshot_path = os.path.join(SNAPSHOT_FOLDER, f"jam_{int(now)}.jpg")
    cv2.imwrite(snapshot_path, frame)

    msg = (f"🚨 ALERT: Kemacetan terdeteksi!\n"
           f"📂 Video: {video_name}\n"
           f"📊 Bobot Total: {congestion['index']:.1f}\n"
           f"📌 Level: {congestion['level']}\n"
           f"🚗 Jumlah Kendaraan: {vehicle_count}\n"
           f"⏰ Waktu: {datetime.now().strftime('%H:%M:%S')}")

    threading.Thread(target=bot.send_photo, args=(msg, snapshot_path)).start()
    last_notification_time = now

# --- Main ---
def main():
    bot = TelegramBot(TELEGRAM_TOKEN, min_vehicles=2)

    threading.Thread(target=bot.start_polling, daemon=True).start()
    time.sleep(2)
    print("[INFO] Telegram bot aktif")

    aoi_polygons = load_aoi(AOI_FILE)

    total_start_time = time.time()
    video_durations = {}

    for file in os.listdir(INPUT_FOLDER):
        if not file.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
            continue

        video_path = os.path.join(INPUT_FOLDER, file)
        cap = cv2.VideoCapture(video_path)

        start_time = time.time()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame)[0]
            detections = []
            for box in results.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                if cls_id not in VEHICLE_IDS or conf < CONF_THRESHOLD:
                    continue
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                w, h = x2 - x1, y2 - y1
                detections.append(([x1, y1, w, h], conf, cls_id))

            tracks = tracker.update_tracks(detections, frame=frame) if detections else []

            stuck_counts = {cls: 0 for cls in VEHICLE_IDS}
            vehicle_count = 0

            for track in tracks:
                if not track.is_confirmed():
                    continue
                x1, y1, x2, y2 = map(int, track.to_ltrb())
                cls_id = track.det_class if hasattr(track, "det_class") else -1
                label = f"{CLASS_NAMES.get(cls_id, 'obj')}-{track.track_id}"

                cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
                if not point_in_aoi((cx, cy), aoi_polygons):
                    continue

                vehicle_count += 1

                if track.track_id in last_positions:
                    last_cx, last_cy = last_positions[track.track_id]
                    dist = np.sqrt((cx - last_cx) ** 2 + (cy - last_cy) ** 2)
                    if dist < STUCK_THRESHOLD:
                        stuck_frames[track.track_id] = stuck_frames.get(track.track_id, 0) + 1
                    else:
                        stuck_frames[track.track_id] = 0
                else:
                    stuck_frames[track.track_id] = 0

                last_positions[track.track_id] = (cx, cy)

                if stuck_frames[track.track_id] >= STUCK_FRAMES_REQUIRED:
                    if cls_id in stuck_counts:
                        stuck_counts[cls_id] += 1

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
                cv2.putText(frame, label, (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)

            # Hitung indeks kemacetan berbasis bobot
            congestion = classify_congestion_bobot(stuck_counts)
            level = congestion['level']

            if level == "LANCAR":
                color = (0, 255, 0)
            elif level == "SEDANG":
                color = (0, 255, 255)
            else:
                color = (0, 0, 255)
                send_telegram(bot, frame, congestion, vehicle_count, file)

            cv2.putText(frame,
                        f"Traffic: {level} (Bobot={congestion['index']:.1f})",
                        (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3)
            cv2.putText(frame, f"Vehicles: {vehicle_count}",
                        (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 3)
            cv2.putText(frame, f"Video: {file}",
                        (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200,200,200), 2)

            for poly in aoi_polygons:
                cv2.polylines(frame, [poly], isClosed=True, color=(255, 0, 0), thickness=2)

            bot.update_status(vehicle_count, frame=frame, congestion=congestion)

            frame_path = os.path.join("frames", "latest.jpg")
            cv2.imwrite(frame_path, frame)

        cap.release()
        video_durations[file] = time.time() - start_time

    total_duration = time.time() - total_start_time
    print("Selesai semua video.")
    print("\nRingkasan durasi per video:")
    for vid, dur in video_durations.items():
        print(f"- {vid}: {dur:.2f} detik")
    print(f"\nTotal durasi pemrosesan semua video: {total_duration:.2f} detik.")

if __name__ == "__main__":
    main()
