# 🚦 Traffic Monitoring & Congestion Detection System

Sistem ini adalah aplikasi **deteksi dan monitoring kemacetan lalu
lintas berbasis video** menggunakan:

-   🎯 YOLO (Ultralytics) untuk deteksi kendaraan\
-   🔄 Deep SORT untuk tracking kendaraan\
-   📍 Area of Interest (AOI) untuk membatasi area analisis\
-   📊 Perhitungan indeks kemacetan berbasis bobot kendaraan\
-   🤖 Integrasi notifikasi otomatis melalui Telegram Bot

------------------------------------------------------------------------

## 🧠 Arsitektur Sistem

Sistem terdiri dari dua file utama:

-   `System_public.py` → Proses utama deteksi & analisis video\
-   `telegram_bot.py` → Modul bot Telegram untuk notifikasi dan kontrol

------------------------------------------------------------------------

## ⚙️ Fitur Utama

### 🚗 1. Deteksi Kendaraan

Menggunakan model YOLO untuk mendeteksi: - Bus - Car - Motor - Truck

Model yang digunakan:

    Models/best.pt

------------------------------------------------------------------------

### 🔄 2. Tracking Kendaraan

Menggunakan Deep SORT untuk: - Memberikan ID unik tiap kendaraan -
Melacak pergerakan kendaraan antar frame - Mendeteksi kendaraan yang
berhenti (stuck)

------------------------------------------------------------------------

### 📍 3. Area of Interest (AOI)

File konfigurasi:

    AOI/aoi.txt

Format:

    x1,y1
    x2,y2
    x3,y3
    x4,y4

    x1,y1
    x2,y2
    ...

Setiap blok kosong memisahkan polygon baru.

------------------------------------------------------------------------

### 📊 4. Perhitungan Indeks Kemacetan

  Kendaraan   Bobot
  ----------- -------
  Motor       0.18
  Mobil       1.0
  Truck       3.13
  Bus         4.60

Klasifikasi:

-   **MACET** → Index ≥ 4\
-   **SEDANG** → Index ≥ 2\
-   **LANCAR** → Index \< 2

Kendaraan dianggap "stuck" jika: - Pergerakan \< 2 piksel - Selama ≥ 15
frame berturut-turut

------------------------------------------------------------------------

### 🤖 5. Notifikasi Telegram

Command yang tersedia: - `/start` - `/stop` - `/status` - `/current` -
`/help`

Notifikasi otomatis dikirim saat level kemacetan = **MACET** Cooldown
notifikasi: 5 menit

------------------------------------------------------------------------

## 📁 Struktur Folder

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
    ├── Source/            # Input video
    ├── Output/
    │   ├── Snapshots/     # Screenshot saat macet
    │
    ├── frames/
    │   └── latest.jpg

------------------------------------------------------------------------

## 🛠️ Instalasi

### Install Dependencies

``` bash
pip install ultralytics opencv-python numpy deep-sort-realtime pyTelegramBotAPI
```

------------------------------------------------------------------------

## 🔐 Konfigurasi Telegram

Di dalam `System_public.py`:

``` python
TELEGRAM_TOKEN = "ISI_TOKEN_BOT_ANDA"
```

Tambahkan bot ke grup Telegram dan kirim:

    /start

------------------------------------------------------------------------

## ▶️ Cara Menjalankan

Masukkan video ke folder:

    Source/

Jalankan:

``` bash
python System_public.py
```

------------------------------------------------------------------------

## 📌 Catatan

-   Pastikan model `best.pt` sudah dilatih untuk kendaraan
-   Sistem optimal untuk kamera statis
-   AOI harus sesuai perspektif kamera
