C:\geosdi\
├── 📄 README.md                          ← Dokumentasi utama
├── 📄 .env                               ← Konfigurasi (rahasia)
├── 📄 .env.example                       ← Template konfigurasi
├── 📄 docker-compose.yml                 ← Services (Postgres, Neo4j, dll)
├── 📄 geosdi.ps1                         ← Script helper
│
├── 📂 data/
│   ├── raw/                              ← Data mentah (GeoJSON provinsi, CSV WKP)
│   └── processed/                        ← Data bersih (GeoJSON, HTML, PNG)
│
├── 📂 docs/                              ← Dokumentasi filosofis & teknis
│
├── 📂 notebooks/
│   ├── 01_data_exploration.ipynb         ← Eksplorasi awal
│   └── 02_interactive_map.ipynb          ← Peta interaktif
│
├── 📂 scripts/
│   └── geosdi-tunnel.ps1                 ← Manager tunnel + uvicorn
│
├── 📂 src/
│   ├── layer7_interface/
│   │   ├── api/                          ← FastAPI (endpoints JSON)
│   │   └── web/                          ← Web UI (Jinja2 + HTML + JS)
│   │       ├── app.py
│   │       ├── static/
│   │       │   ├── css/style.css
│   │       │   └── js/map.js
│   │       └── templates/
│   │           ├── base.html
│   │           ├── index.html
│   │           ├── dashboard.html
│   │           └── about.html
│   │
│   └── shared/
│       ├── config.py                     ← Baca .env
│       └── logger.py                     ← Logging terstruktur
│
├── 📂 tools/
│   └── cloudflared.exe                   ← Portable (tidak install)
│
└── 📂 logs/                              ← Log files