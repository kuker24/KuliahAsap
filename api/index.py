import os
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from flask import Flask, render_template, jsonify, request

current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, "templates")

app = Flask(__name__, template_folder=template_dir)

# Daftar Lokasi Pemantauan di Kota Pekanbaru
MONITORED_LOCATIONS = [
    {
        "id": "pcr_rumbai",
        "name": "Kampus PCR (Rumbai)",
        "subdistrict": "Rumbai / Umban Sari",
        "lat": 0.5700,
        "lon": 101.4260,
        "is_campus": True,
        "description": "Lokasi Utama Kampus Politeknik Caltex Riau (Patokan Keputusan)"
    },
    {
        "id": "panam",
        "name": "Panam / Tuah Madani",
        "subdistrict": "Bina Widya / Tampan",
        "lat": 0.4678,
        "lon": 101.3785,
        "is_campus": False,
        "description": "Area Tempat Tinggal Banyak Mahasiswa (Koridor HR. Soebrantas)"
    },
    {
        "id": "kota_pusat",
        "name": "Pekanbaru Kota (Pusat)",
        "subdistrict": "Sukajadi / Senapelan Selatan",
        "lat": 0.5333,
        "lon": 101.4500,
        "is_campus": False,
        "description": "Kawasan Sudirman, Pusat Bisnis & Pemerintahan Kota"
    },
    {
        "id": "marpoyan_damai",
        "name": "Marpoyan Damai / Bandara",
        "subdistrict": "Marpoyan Damai",
        "lat": 0.4614,
        "lon": 101.4447,
        "is_campus": False,
        "description": "Kawasan Selatan Sekitar Bandara Sultan Syarif Kasim II"
    },
    {
        "id": "tenayan_raya",
        "name": "Tenayan Raya / Kulim",
        "subdistrict": "Tenayan Raya",
        "lat": 0.5189,
        "lon": 101.5234,
        "is_campus": False,
        "description": "Kawasan Perkantoran Pemko & Area Industri Timur"
    },
    {
        "id": "payung_sekaki",
        "name": "Payung Sekaki / Labuh Baru",
        "subdistrict": "Payung Sekaki",
        "lat": 0.5250,
        "lon": 101.4080,
        "is_campus": False,
        "description": "Pintu Gerbang Barat Pekanbaru / Perbatasan Kampar"
    },
    {
        "id": "senapelan_siak",
        "name": "Senapelan / Jembatan Siak",
        "subdistrict": "Senapelan",
        "lat": 0.5400,
        "lon": 101.4400,
        "is_campus": False,
        "description": "Jalur Penghubung Utama Pusat Kota Menuju Rumbai (Siak I-IV)"
    },
    {
        "id": "rumbai_pesisir",
        "name": "Rumbai Pesisir / Muara Fajar",
        "subdistrict": "Rumbai Pesisir",
        "lat": 0.6000,
        "lon": 101.4500,
        "is_campus": False,
        "description": "Kawasan Utara Pekanbaru Menuju Jalur Tol Pekanbaru-Dumai"
    }
]

# Cache sederhana dalam memori (60 detik)
_cache = {
    "timestamp": 0,
    "data": None
}

def get_aqi_category(us_aqi):
    """Kategori standar US AQI (EPA)"""
    if us_aqi is None:
        return {"category": "Tidak Diketahui", "color": "gray", "level": 0}
    if us_aqi <= 50:
        return {"category": "Baik (Good)", "color": "emerald", "level": 1}
    elif us_aqi <= 100:
        return {"category": "Sedang (Moderate)", "color": "yellow", "level": 2}
    elif us_aqi <= 150:
        return {"category": "Tidak Sehat bagi Kelompok Sensitif", "color": "amber", "level": 3}
    elif us_aqi <= 200:
        return {"category": "Tidak Sehat (Unhealthy)", "color": "orange", "level": 4}
    elif us_aqi <= 300:
        return {"category": "Sangat Tidak Sehat (Very Unhealthy)", "color": "red", "level": 5}
    else:
        return {"category": "Berbahaya (Hazardous)", "color": "purple", "level": 6}

def evaluate_pcr_policy(us_aqi):
    """
    Logika penentuan skema perkuliahan sesuai Keputusan Direktur PCR 
    (Surat Tanggal 22 Oktober 2026 / LLDIKTI XVII No. 1607/DST/LL17/HK.04/2026)
    """
    if us_aqi is None:
        return {
            "tier": 0,
            "status": "DATA TIDAK TERSEDIA",
            "badge_color": "gray",
            "badge_class": "bg-slate-100 text-slate-800 border-slate-300",
            "header_bg": "from-slate-700 to-slate-900",
            "keterangan": "Tidak dapat mengambil data sensor kualitas udara terkini.",
            "operational_rules": [
                "Periksa kembali koneksi internet atau gunakan pemantauan manual internal PCR."
            ],
            "schedule_link_label": "Buka Jadwal Perkuliahan BAAK",
            "schedule_url": "https://baak.pcr.ac.id/jadwal-perkuliahan/",
            "action_code": "UNKNOWN"
        }

    if us_aqi < 190:
        return {
            "tier": 1,
            "status": "Perkuliahan Normal",
            "threshold_label": "< 190",
            "badge_color": "emerald",
            "badge_class": "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
            "header_bg": "from-emerald-950/80 to-slate-900",
            "accent_color": "text-emerald-400",
            "keterangan": "Perkuliahan dan kegiatan operasional dilaksanakan secara tatap muka dengan skema jam normal.",
            "operational_rules": [
                "Perkuliahan tatap muka berjalan penuh sesuai jadwal jam normal.",
                "Perkuliahan dilakukan di dalam ruangan dan laboratorium tertutup.",
                "Seluruh kegiatan luar ruangan (outdoor) diminimalkan atau disesuaikan.",
                "Wajib menggunakan masker selama berada di area perkuliahan offline."
            ],
            "schedule_link_label": "Link Jadwal Perkuliahan Normal BAAK",
            "schedule_url": "https://baak.pcr.ac.id/jadwal-perkuliahan/",
            "action_code": "NORMAL_OFFLINE"
        }
    elif 190 <= us_aqi <= 210:
        return {
            "tier": 2,
            "status": "Pengurangan Durasi Tatap Muka (50%)",
            "threshold_label": "190 – 210",
            "badge_color": "amber",
            "badge_class": "bg-amber-500/15 text-amber-400 border-amber-500/30",
            "header_bg": "from-amber-950/80 to-slate-900",
            "accent_color": "text-amber-400",
            "keterangan": "Durasi tatap muka dikurangi 50% dari jam normal (09.00 - 16.30 WIB).",
            "operational_rules": [
                "Perkuliahan dimulai pukul 09.00 - 16.30 WIB demi keselamatan dan kesehatan perjalanan.",
                "Durasi perkuliahan tatap muka dipadatkan sebesar 50% dari alokasi waktu normal.",
                "Dosen memadatkan materi / pengurangan data percobaan serta memberikan tugas/analisis di luar jam perkuliahan.",
                "Perkuliahan wajib dilakukan di dalam ruangan dan laboratorium tertutup.",
                "Aktivitas di luar ruangan (outdoor) diminimalkan.",
                "Wajib menggunakan masker selama berada di kampus."
            ],
            "schedule_link_label": "Link Jadwal Pengurangan Durasi 50% BAAK",
            "schedule_url": "https://baak.pcr.ac.id/jadwal-perkuliahan/",
            "action_code": "REDUCED_OFFLINE_50"
        }
    else:  # > 210
        return {
            "tier": 3,
            "status": "Pembelajaran Online (PJJ) 100%",
            "threshold_label": "> 210",
            "badge_color": "rose",
            "badge_class": "bg-rose-500/15 text-rose-400 border-rose-500/30",
            "header_bg": "from-rose-950/80 to-slate-900",
            "accent_color": "text-rose-400",
            "keterangan": "Seluruh kegiatan perkuliahan dialihkan secara penuh ke Pembelajaran Jarak Jauh (PJJ) / Daring.",
            "operational_rules": [
                "Tidak ada perkuliahan tatap muka di kampus PCR (100% Online).",
                "Seluruh kelas dilaksanakan melalui platform PJJ resmi PCR (E-learning/Zoom/Google Meet).",
                "Mahasiswa dan staf tidak perlu melakukan perjalanan fisik ke kampus.",
                "Hindari seluruh aktivitas di luar ruangan demi perlindungan pernapasan."
            ],
            "schedule_link_label": "Akses Portal Perkuliahan & BAAK PCR",
            "schedule_url": "https://baak.pcr.ac.id/jadwal-perkuliahan/",
            "action_code": "ONLINE_PJJ_100"
        }

def fetch_single_location(loc):
    """Mengambil data kualitas udara dari Open-Meteo per titik dengan retry"""
    url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={loc['lat']}&longitude={loc['lon']}&current=us_aqi,pm2_5,pm10"
    )
    
    # Retry hingga 2 kali jika ada kendala koneksi
    for attempt in range(2):
        try:
            res = requests.get(url, timeout=8)
            if res.status_code == 200:
                data = res.json()
                curr = data.get("current", {})
                us_aqi = curr.get("us_aqi")
                pm2_5 = curr.get("pm2_5")
                pm10 = curr.get("pm10")
                
                category_info = get_aqi_category(us_aqi)
                
                # Evaluasi risiko perjalanan dari wilayah ini
                travel_warning = None
                if us_aqi and us_aqi >= 200:
                    travel_warning = "Kabut asap sangat tebal di wilayah ini. Jarak pandang rendah; jika harus menuju kampus PCR gunakan masker N95/KN95 dan nyalakan lampu kendaraan."
                elif us_aqi and us_aqi >= 150:
                    travel_warning = "Kualitas udara tidak sehat. Wajib menggunakan masker saat bepergian."

                return {
                    **loc,
                    "us_aqi": us_aqi,
                    "pm2_5": pm2_5,
                    "pm10": pm10,
                    "category": category_info["category"],
                    "color": category_info["color"],
                    "travel_warning": travel_warning,
                    "status": "ok"
                }
        except Exception:
            time.sleep(0.3)
            continue

    return {
        **loc,
        "us_aqi": None,
        "pm2_5": None,
        "pm10": None,
        "category": "Gagal Mengambil Data",
        "color": "gray",
        "travel_warning": None,
        "status": "error"
    }

def get_all_locations_data(force_refresh=False):
    """Mengambil seluruh titik lokasi di Pekanbaru secara paralel dengan cache"""
    global _cache
    now = time.time()
    if not force_refresh and _cache["data"] and (now - _cache["timestamp"] < 60):
        return _cache["data"]

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(fetch_single_location, MONITORED_LOCATIONS))

    # Temukan data Kampus PCR (penentu utama)
    campus_location = next((r for r in results if r["is_campus"]), results[0])
    campus_aqi = campus_location.get("us_aqi")
    campus_policy = evaluate_pcr_policy(campus_aqi)

    # Identifikasi wilayah dengan tingkat polusi tertinggi
    valid_results = [r for r in results if r.get("us_aqi") is not None]
    highest_location = max(valid_results, key=lambda x: x["us_aqi"]) if valid_results else campus_location
    avg_aqi = round(sum(r["us_aqi"] for r in valid_results) / len(valid_results), 1) if valid_results else 0

    response_payload = {
        "timestamp": datetime.now().strftime("%d %B %Y, %H:%M:%S WIB"),
        "campus": campus_location,
        "campus_policy": campus_policy,
        "highest_location": highest_location,
        "average_aqi": avg_aqi,
        "locations": results,
        "official_reference": {
            "title": "Surat Kebijakan Operasional Perkuliahan PCR Akibat Penurunan Kualitas Udara",
            "director": "Direktur Politeknik Caltex Riau",
            "memo_date": "22 Oktober 2026",
            "effective_date": "Senin, 26 Oktober 2026",
            "basis": [
                "Surat Imbauan LLDIKTI Wilayah XVII Nomor 1607/DST/LL17/HK.04/2026",
                "Rapat Akademik Politeknik Caltex Riau tanggal 20 Oktober 2026"
            ],
            "baak_schedule_url": "https://baak.pcr.ac.id/jadwal-perkuliahan/"
        }
    }

    _cache["timestamp"] = now
    _cache["data"] = response_payload
    return response_payload

@app.route("/")
def index():
    """Halaman Dashboard Web Utama"""
    data = get_all_locations_data()
    return render_template("index.html", data=data)

@app.route("/api/status")
def api_status():
    """Endpoint JSON API untuk konsumsi frontend atau aplikasi eksternal"""
    force = request.args.get("refresh", "false").lower() == "true"
    simulated_aqi = request.args.get("simulate_aqi")

    data = get_all_locations_data(force_refresh=force)
    
    # Jika mode simulasi diaktifkan lewat query param ?simulate_aqi=205
    if simulated_aqi is not None:
        try:
            val = float(simulated_aqi)
            sim_policy = evaluate_pcr_policy(val)
            sim_data = dict(data)
            sim_data["is_simulated"] = True
            sim_data["simulated_aqi"] = val
            sim_data["campus_policy"] = sim_policy
            return jsonify(sim_data)
        except ValueError:
            pass

    return jsonify(data)

@app.route("/api/evaluate")
def api_evaluate():
    """Evaluasi skema PCR berdasarkan input nilai AQ US Index custom"""
    try:
        aqi_val = float(request.args.get("aqi", 0))
        policy = evaluate_pcr_policy(aqi_val)
        return jsonify({
            "input_aqi": aqi_val,
            "policy": policy
        })
    except (ValueError, TypeError):
        return jsonify({"error": "Parameter 'aqi' harus berupa angka numerik."}), 400

if __name__ == "__main__":
    # Menjalankan server lokal di port 5000
    print("Menjalankan Pemantau Kualitas Udara PCR Pekanbaru di http://localhost:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=True)
