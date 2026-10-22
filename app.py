import os
import sys

# Memastikan direktori root berada dalam sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from api.index import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"============================================================")
    print(f" Sistem Pemantau Kualitas Udara Pekanbaru & Kebijakan PCR ")
    print(f" Berjalan di: http://localhost:{port} ")
    print(f"============================================================")
    app.run(host="0.0.0.0", port=port, debug=True)
