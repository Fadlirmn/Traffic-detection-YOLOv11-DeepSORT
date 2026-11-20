# Vehicle Tracking — YOLO11 + DeepSORT

**Fadlirmn — Individual Project PRD Package**  
Version: 1.0.0 · Date: 20 November 2026

## Tujuan paket

Paket mandiri untuk mengimplementasikan **source code nyata** dan membuat **showcase demo di Vercel/serverless tanpa VPS**. Kode bisnis, API, model data, testing, validation, security, dan adapter produksi harus riil. Showcase publik menggunakan data sintetis / replay dengan label yang jujur.

## Stack utama

Python + YOLO11 + DeepSORT + FastAPI + SvelteKit. Pilihan versi runtime dan layanan akhir perlu dicek lagi saat development.

## Mulai dari sini

1. Baca [`03_VEHICLE_TRACKING/PRD.md`](03_VEHICLE_TRACKING/PRD.md) untuk tujuan, fitur, user journey, acceptance criteria, NFR, pengujian, dan roadmap project.
2. Baca [`03_VEHICLE_TRACKING/SCHEMAS_AND_PIPELINE.md`](03_VEHICLE_TRACKING/SCHEMAS_AND_PIPELINE.md) untuk spesifikasi teknis, kontrak, skema dan pipeline.
3. Baca [`01_SHARED/TECH_STACK_ARCHITECTURE.md`](01_SHARED/TECH_STACK_ARCHITECTURE.md) untuk pola arsitektur dual-mode `real` vs `demo` dan deployment serverless.
4. Baca [`01_SHARED/DEMO_SECURITY_QA.md`](01_SHARED/DEMO_SECURITY_QA.md) untuk quality gates, keamanan, dan batasan demo.
5. Gunakan [`01_SHARED/DELIVERY_ROADMAP.md`](01_SHARED/DELIVERY_ROADMAP.md) sebagai konteks milestone lintas portfolio dan [`06_TEMPLATES`](06_TEMPLATES) untuk repository template.

## Isi folder

- `03_VEHICLE_TRACKING/`: **PRD dan spesifikasi teknis khusus project ini**.
- `01_SHARED/`: standar arsitektur, keamanan, QA, master context dan roadmap (disalin supaya paket berdiri sendiri).
- `06_TEMPLATES/`: template README, ADR, dan release checklist.
- `MANIFEST.md`: daftar file dan checksum ringkas.

## Batas demo yang wajib dijaga

- Hosting showcase: Vercel serverless/static (tanpa VPS).
- Gunakan data demo sintetis, hindari PII dan kredensial produksi.
- Pekerjaan berat, browser automation, workers long-running, dan computer vision inference tidak diklaim berjalan live di Vercel jika hanya fixture/replay.
- Pisahkan `demo` adapter dan `real` adapter; real implementation bisa dijalankan lokal/target managed services jika suatu saat diperlukan.
- Preview persona demo **bukan** bukti autentikasi atau RBAC yang sungguhan.

> Dokumen ini adalah target implementasi. Bukan arsip source code yang sudah selesai atau bukti audit repo yang sudah dilakukan.
