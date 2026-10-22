import sys
import argparse
from api.index import get_all_locations_data, evaluate_pcr_policy

def print_separator(char="=", length=75):
    print(char * length)

def run_cli():
    # Mengatasi encoding di console Windows jika perlu
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        description="Sistem Pengecekan Kualitas Udara Pekanbaru & Kebijakan Perkuliahan PCR"
    )
    parser.add_argument(
        "--test",
        type=float,
        help="Simulasi pengujian nilai AQ US Index custom (contoh: --test 195)"
    )
    args = parser.parse_args()

    print_separator("=")
    print("  SISTEM PEMANTAUAN KUALITAS UDARA PEKANBARU & KEBIJAKAN KULIAH PCR")
    print("  Berdasarkan Surat Edaran Direktur PCR (22 Oktober 2026)")
    print("  Menindaklanjuti Surat LLDIKTI XVII No. 1607/DST/LL17/HK.04/2026")
    print_separator("=")

    if args.test is not None:
        print(f"\n[MODE SIMULASI]: Menguji Nilai AQ US Index = {args.test}\n")
        policy = evaluate_pcr_policy(args.test)
        print_separator("-")
        print(f"STATUS KEPUTUSAN : {policy['status']}")
        print(f"AMBANG BATAS     : {policy.get('threshold_label', '-')}")
        print(f"KETERANGAN       : {policy['keterangan']}")
        print_separator("-")
        print("KETENTUAN OPERASIONAL:")
        for rule in policy['operational_rules']:
            print(f"  * {rule}")
        print(f"\nLink Jadwal BAAK : {policy['schedule_url']}")
        print_separator("=")
        return

    print("\nMengambil data kualitas udara terkini di berbagai wilayah Pekanbaru...\n")
    data = get_all_locations_data(force_refresh=True)

    # Tabel Data Stasiun Wilayah Pekanbaru
    print(f"{'Wilayah':<28} | {'AQ US':<7} | {'PM2.5':<10} | {'Status Udara':<24}")
    print_separator("-")
    for loc in data["locations"]:
        name = loc["name"]
        if loc.get("is_campus"):
            name += " *"
        aqi_str = str(loc["us_aqi"]) if loc["us_aqi"] is not None else "--"
        pm25_str = f"{loc['pm2_5']} ug/m3" if loc["pm2_5"] is not None else "--"
        cat = loc["category"]
        print(f"{name:<28} | {aqi_str:<7} | {pm25_str:<10} | {cat:<24}")
    print_separator("-")
    print("(*) Titik Acuan Utama Keputusan Kampus PCR (Rumbai)")

    # Peringatan Keselamatan Perjalanan (Origin Check)
    high_risk_locs = [
        loc for loc in data["locations"] 
        if loc.get("us_aqi") and loc["us_aqi"] >= 180 and not loc.get("is_campus")
    ]
    if high_risk_locs:
        print("\n[PERINGATAN KESELAMATAN PERJALANAN / COMMUTE ADVISORY]:")
        for loc in high_risk_locs:
            print(f"  [!] {loc['name']} (AQI {loc['us_aqi']}): {loc['travel_warning']}")

    # Keputusan Resmi PCR
    campus_aqi = data["campus"].get("us_aqi")
    policy = data["campus_policy"]

    print("\n" + "=" * 75)
    print("  HASIL EVALUASI KEBIJAKAN OPERASIONAL PERKULIAHAN PCR")
    print("=" * 75)
    print(f"  Nilai AQ US Kampus PCR : {campus_aqi} ({data['campus']['category']})")
    print(f"  Status Kebijakan       : {policy['status']}")
    print(f"  Keterangan             : {policy['keterangan']}")
    print("-" * 75)
    print("  Ketentuan Operasional:")
    for rule in policy["operational_rules"]:
        print(f"    - {rule}")
    print(f"\n  Tautan Resmi BAAK      : {policy['schedule_url']}")
    print(f"  Waktu Pemantauan       : {data['timestamp']}")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    run_cli()
