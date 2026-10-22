# Sistem Pemantauan Kualitas Udara Pekanbaru & Kebijakan Perkuliahan PCR 🎓💨

Aplikasi Python berbasis web (*Vercel-ready serverless*) dan CLI untuk memantau indeks kualitas udara (*AQ US Index* & PM2.5) secara *real-time* di berbagai titik Kota Pekanbaru, serta menentukan skema perkuliahan Politeknik Caltex Riau (PCR) secara otomatis.

---

## 📌 Dasar & Rujukan Kebijakan Resmi

Sistem ini menerapkan logika keputusan operasional perkuliahan berdasarkan:
* **Surat Edaran Direktur Politeknik Caltex Riau (PCR)** tanggal **22 Oktober 2026**.
* Menindaklanjuti **Surat Imbauan LLDIKTI Wilayah XVII Nomor 1607/DST/LL17/HK.04/2026**.
* Hasil Rapat Akademik PCR tanggal 20 Oktober 2026.

### Matriks Aturan Perkuliahan PCR:

| AQ US Index | Skema Perkuliahan & Aktivitas | Keterangan & Ketentuan Operasional |
| :---: | :--- | :--- |
| **< 190** | **Perkuliahan Normal** | Perkuliahan & operasional tatap muka jam normal di dalam ruangan/lab tertutup. Aktivitas *outdoor* diminimalkan. **Wajib masker**. |
| **190 – 210** | **Pengurangan Durasi Tatap Muka (50%)** | Durasi tatap muka dikurangi **50%**. Perkuliahan dimulai pukul **09.00 - 16.30 WIB**. Dosen memadatkan materi/tugas di luar jam kuliah. **Wajib masker**. |
| **> 210** | **Pembelajaran Online (PJJ) 100%** | Seluruh perkuliahan dialihkan **100% Daring / PJJ** (E-learning/Zoom/Google Meet). Tidak ada perkuliahan tatap muka di kampus. |

---

## 📍 8 Titik Pemantauan di Kota Pekanbaru

1. **Kampus PCR (Rumbai / Umban Sari)** *(Titik Acuan Utama Keputusan Kampus)*
2. **Panam / Tuah Madani** *(Koridor HR. Soebrantas - Pemukiman Mahasiswa)*
3. **Pekanbaru Kota (Pusat)** *(Jl. Sudirman / Sukajadi / Pusat Pemerintahan)*
4. **Marpoyan Damai** *(Area Selatan / Sekitar Bandara SSK II)*
5. **Tenayan Raya / Kulim** *(Kawasan Industri Timur / Perkantoran Pemko)*
6. **Payung Sekaki / Labuh Baru** *(Pintu Masuk Barat / Batas Kampar)*
7. **Senapelan / Jembatan Siak** *(Jalur Utama Penghubung Kota ke Rumbai)*
8. **Rumbai Pesisir / Muara Fajar** *(Kawasan Utara Menuju Tol Pekanbaru-Dumai)*

---

## 🚀 Fitur Unggulan

* **Dashboard Web Modern & Responsif**: Dibangun dengan Tailwind CSS (tampilan elegan, rapi di HP maupun Laptop).
* **Otomasi Status PCR**: Banner interaktif yang langsung menampilkan keputusan kampus (Normal / 50% Durasi / PJJ 100%).
* **Peringatan Keselamatan Perjalanan (*Commute Advisory*)**: Memberikan notifikasi khusus jika mahasiswa/staf berangkat dari wilayah berkabut asap pekat dengan jarak pandang rendah.
* **Mode Simulasi Interaktif**: Fitur uji coba langsung di web untuk mensimulasikan skenario kualitas udara (misal: AQI 165, 200, atau 235).
* **Tautan Langsung BAAK PCR**: Terintegrasi ke tautan jadwal resmi (`https://baak.pcr.ac.id/jadwal-perkuliahan/`).
* **Endpoint API JSON**: Tersedia `/api/status` untuk integrasi bot Telegram, WhatsApp, atau sistem kampus lainnya.
* **Dual Run Mode**: Bisa dijalankan sebagai antarmuka Web (`app.py`) maupun Terminal CLI (`cli.py`).

---

## 🛠️ Cara Menjalankan Secara Lokal

### 1. Pastikan Dependensi Terinstal
```bash
pip install -r requirements.txt
```

### 2. Menjalankan Dashboard Web
```bash
python app.py
```
Buka browser di: **[http://localhost:5000](http://localhost:5000)**

### 3. Menjalankan di Terminal (CLI)
* **Pengecekan Kualitas Udara Real-Time:**
  ```bash
  python cli.py
  ```
* **Simulasi Uji Kebijakan Nilai Tertentu (contoh AQI = 195):**
  ```bash
  python cli.py --test 195
  ```

---

## 🌐 Cara Deploy ke Vercel (Online Web)

Proyek ini sudah dilengkapi konfigurasi serverless Vercel (`vercel.json` dan `api/index.py`).

### Opsi A: Deploy via GitHub (Paling Mudah)
1. Inisialisasi Git dan commit file proyek:
   ```bash
   git init
   git add .
   git commit -m "feat: sistem pantau kualitas udara pekanbaru & kuliah PCR"
   ```
2. Buat repositori baru di GitHub (misal: `pcr-kuliahasap`) dan lakukan push:
   ```bash
   git remote add origin https://github.com/USERNAME/pcr-kuliahasap.git
   git branch -M main
   git push -u origin main
   ```
3. Buka dashboard [Vercel](https://vercel.com).
4. Klik **"Add New..."** → **"Project"**.
5. Pilih repositori GitHub Anda, biarkan pengaturan default, lalu klik **"Deploy"**.
6. Selesai! Web Anda akan langsung aktif dengan domain `.vercel.app`.

### Opsi B: Deploy via Vercel CLI
1. Instal Vercel CLI (jika belum ada):
   ```bash
   npm i -g vercel
   ```
2. Jalankan perintah di folder proyek:
   ```bash
   vercel
   ```
3. Ikuti petunjuk di terminal untuk proses *linking* dan deploy.

---

## 📡 Endpoint API

* `GET /api/status`: Mengambil status perkuliahan kampus PCR dan data 8 wilayah Pekanbaru dalam format JSON.
  * Tambahkan `?refresh=true` untuk memaksa update data terbaru.
  * Tambahkan `?simulate_aqi=205` untuk mode simulasi.
* `GET /api/evaluate?aqi=215`: Mengevaluasi kebijakan skema perkuliahan untuk nilai AQI tertentu.
