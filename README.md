# 🚦 Traffic Monitoring & Congestion Detection System

Sistem deteksi dan monitoring kemacetan lalu lintas berbasis video, menggunakan:

- 🎯 YOLO11 (Ultralytics) untuk deteksi kendaraan
- 🔄 Deep SORT untuk tracking kendaraan antar frame
- 📍 Area of Interest (AOI) untuk membatasi area analisis
- 📊 Perhitungan indeks kemacetan berbasis bobot kendaraan
- 🤖 Integrasi notifikasi otomatis melalui Telegram Bot
- 🖥️ Dashboard web untuk replay hasil deteksi + pratinjau notifikasi Telegram

---

## 🧰 Tech Stack

**Computer vision / backend** (`System_public.py`, `telegram_bot.py`)

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Ultralytics YOLO11](https://img.shields.io/badge/Ultralytics%20YOLO11-111F68?style=for-the-badge&logo=ultralytics&logoColor=white)](https://github.com/ultralytics/ultralytics)
[![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)
[![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot%20API-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://github.com/eternnoir/pyTelegramBotAPI)

Tracking pakai [deep-sort-realtime](https://github.com/levan92/deep_sort_realtime) (belum ada logo resminya di badge).

**Dashboard web** (`docs/`)

[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/docs/Web/HTML)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css&logoColor=white)](https://developer.mozilla.org/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/docs/Web/JavaScript)
[![Google Fonts](https://img.shields.io/badge/Google%20Fonts-4285F4?style=for-the-badge&logo=googlefonts&logoColor=white)](https://fonts.google.com/)

Vanilla, tanpa framework dan tanpa build step — `<video>` native untuk replay rekaman hasil inference.

**Tooling & hosting**

[![FFmpeg](https://img.shields.io/badge/FFmpeg-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-222222?style=for-the-badge&logo=githubpages&logoColor=white)](https://pages.github.com/)
[![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com/)

---

## 🧠 Arsitektur Sistem

Sistem terdiri dari dua file utama:

- `System_public.py` → Proses utama deteksi & analisis video
- `telegram_bot.py` → Modul bot Telegram untuk notifikasi dan kontrol

---

## 🖼️ Dashboard Web (Replay & Notifikasi)

Folder `docs/` berisi dashboard statis (tanpa server/backend) yang me-replay hasil inference asli dan menampilkan pratinjau notifikasi Telegram yang sinkron dengan waktu video.

| Dashboard — hasil deteksi | Notifikasi — pratinjau Telegram |
|---|---|
| ![Dashboard](screenshots/dashboard-dark.png) | ![Notifikasi](screenshots/notifications-dark.png) |

<details>
<summary>Mode terang & tampilan mobile</summary>

| Mode terang | Mobile |
|---|---|
| ![Dashboard mode terang](screenshots/dashboard-light.png) | ![Tampilan mobile](screenshots/mobile-dark.png) |

</details>

Buka langsung `docs/index.html` di browser (tanpa server), atau host sebagai situs statis:

- **GitHub Pages** — di repo Settings → Pages, pilih source branch `main` folder `/docs` (tidak perlu konfigurasi tambahan).
- **Vercel** — import repo ini, set *Root Directory* ke `docs`.

Data pada dashboard berasal dari rekaman hasil inference asli (`out_split_6.mp4`), bukan kamera langsung — overlay box/AOI/status sudah terbakar langsung di video, dan notifikasi Telegram-nya adalah pratinjau statis yang muncul otomatis saat pemutaran video mencapai momen macet pada rekaman tersebut.

---

## ⚙️ Fitur Utama

### 🚗 1. Deteksi Kendaraan

Menggunakan model YOLO untuk mendeteksi:
- Bus
- Car
- Motor
- Truck

Model yang digunakan:

```
Models/best.pt
```

---

### 🔄 2. Tracking Kendaraan

Menggunakan Deep SORT untuk:
- Memberikan ID unik tiap kendaraan
- Melacak pergerakan kendaraan antar frame
- Mendeteksi kendaraan yang berhenti (stuck)

---

### 📍 3. Area of Interest (AOI)

File konfigurasi:

```
AOI/aoi.txt
```

Format:

```
x1,y1
x2,y2
x3,y3
x4,y4

x1,y1
x2,y2
...
```

Setiap blok kosong memisahkan polygon baru.

---

### 📊 4. Perhitungan Indeks Kemacetan

| Kendaraan | Bobot |
|---|---|
| Motor | 0.18 |
| Mobil | 1.0 |
| Truck | 3.13 |
| Bus | 4.60 |

Klasifikasi:

- **MACET** → Index ≥ 4
- **SEDANG** → Index ≥ 2
- **LANCAR** → Index < 2

Kendaraan dianggap "stuck" jika:
- Pergerakan < 2 piksel
- Selama ≥ 15 frame berturut-turut

---

### 🤖 5. Notifikasi Telegram

Command yang tersedia: `/start` · `/stop` · `/status` · `/current` · `/help`

Notifikasi otomatis dikirim saat level kemacetan = **MACET**. Cooldown notifikasi: 5 menit.

---

## 📁 Struktur Folder

```
project/
│
├── System_public.py
├── telegram_bot.py
│
├── Models/
│   └── best.pt
│
├── AOI/
│   └── aoi.txt
│
├── Source/              # Input video
├── Output/
│   └── Snapshots/       # Screenshot saat macet
│
├── frames/
│   └── latest.jpg
│
├── docs/                # Dashboard web (replay + notifikasi), siap host di GitHub Pages/Vercel
│   ├── index.html
│   ├── traffic-result.mp4
│   ├── traffic-poster.jpg
│   └── alert-snapshot-1.jpg
│
└── screenshots/         # Screenshot dashboard untuk dokumentasi README ini
```

---

## 🛠️ Instalasi

### Install Dependencies

```bash
pip install ultralytics opencv-python numpy deep-sort-realtime pyTelegramBotAPI
```

---

## 🔐 Konfigurasi Telegram

Di dalam `System_public.py`:

```python
TELEGRAM_TOKEN = "ISI_TOKEN_BOT_ANDA"
```

Tambahkan bot ke grup Telegram dan kirim:

```
/start
```

---

## ▶️ Cara Menjalankan

Masukkan video ke folder:

```
Source/
```

Jalankan:

```bash
python System_public.py
```

---

## 📌 Catatan

- Pastikan model `best.pt` sudah dilatih untuk kendaraan
- Sistem optimal untuk kamera statis
- AOI harus sesuai perspektif kamera
- Dashboard di `docs/` adalah replay statis dari hasil rekaman, bukan koneksi langsung ke kamera/bot
