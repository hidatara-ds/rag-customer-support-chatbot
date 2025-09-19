# Shoe Store Support Chatbot

Chatbot dukungan pelanggan berbasis FastAPI dengan katalog MySQL/SQLite. Menjawab pertanyaan seputar produk, ukuran, stok per-ukuran, kategori, brand, daftar harga, status pesanan, dan garansi. LLM disajikan via Ollama (Llama 3).

## Fitur
- **RAG-first**: jawaban dari database diutamakan, LLM sebagai fallback.
- **Katalog realistis** (16+ SKU) dengan stok per-ukuran lewat tabel `product_sizes`.
- **Intent siap pakai**: kategori, brand, price list, detail produk, ketersediaan ukuran, stok per-ukuran, rekomendasi/alternatif, status pesanan, garansi.
- **UI web sederhana** (static) di route `/web`, ramah mobile.
- **Konfigurasi via ENV**: database, model LLM, batas riwayat percakapan.

## Struktur Folder
```bash
app/
  main.py       # routing FastAPI + flow intent/tool-first
  db.py         # SQLAlchemy engine, seed data, dan query RAG
  models.py     # ORM: Product, ProductSize, Order, Conversation
  utils.py      # deteksi intent, ekstraktor, formatter jawaban tool
  schemas.py    # Pydantic schema untuk request/response
  config.py     # pembacaan variabel lingkungan (ENV)
  llm.py        # klien Ollama (HTTP generate)
frontend/
  index.html    # UI chat static
data/
  shoe_support.db      # SQLite (opsional, otomatis dibuat/di-seed)
  database.mysql.sql   # contoh SQL (opsional)
Dockerfile
docker-compose.yml
requirements.txt
README.md
LICENSE
```

## Persyaratan
- Python 3.11+
- Ollama (lokal atau container) dengan model `llama3.2:3b` atau setara
- MySQL 8 (opsional; default menggunakan SQLite)

## Variabel Lingkungan (ENV)
- `DATABASE_URL` (default: `sqlite:///./data/shoe_support.db`)
  - Contoh MySQL: `mysql+pymysql://root:root@127.0.0.1:3306/shoe_support`
- `OLLAMA_HOST` (default: `http://127.0.0.1:11434`)
- `OLLAMA_MODEL` (default: `llama3.2:3b`)
- `MAX_HISTORY_MESSAGES` (default: `30`) — jumlah total pesan (user+assistant) yang dikirim ke LLM.

## Menjalankan dengan Docker (Disarankan)
```bash
docker compose up --build
# API: http://localhost:8000
# UI : http://localhost:8000/web
```
`docker-compose.yml` menyertakan 3 service: `db` (MySQL 8), `api` (FastAPI), `ollama` (server LLM). API menunggu DB sehat dan Ollama start.

## Menjalankan Lokal (Tanpa Docker)
### macOS/Linux (bash/zsh)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=sqlite:///./data/shoe_support.db
export OLLAMA_HOST=http://127.0.0.1:11434
export OLLAMA_MODEL=llama3.2:3b
uvicorn app.main:app --reload
```

### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL = "sqlite:///./data/shoe_support.db"
$env:OLLAMA_HOST = "http://127.0.0.1:11434"
$env:OLLAMA_MODEL = "llama3.2:3b"
uvicorn app.main:app --reload
```

Catatan: Saat pertama kali start, tabel dan data contoh akan otomatis dibuat/di-seed (jika kosong).

## Endpoint API
- `GET /health` → kesehatan sederhana
- `GET /products` → daftar produk ringkas
- `GET /orders/{user}` → pesanan terakhir untuk user
- `POST /chat` → obrolan chatbot (RAG-first)

### Skema `POST /chat`
Request:
```json
{
  "user": "gilang",
  "message": "Ukuran 42 untuk Ultraboost 22 ada berapa?"
}
```
Response:
```json
{ "answer": "Stok Ultraboost 22 ukuran 42: 4 pasang." }
```

Contoh cURL:
```bash
curl -s http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"user":"gilang","message":"Jenis sepatu apa saja?"}'
```

## Dokumentasi API (Swagger / OpenAPI)
- Buka `http://localhost:8000/docs` untuk mencoba endpoint secara interaktif (Swagger UI). Anda dapat mengisi body request, menekan tombol "Execute", dan melihat response langsung.
- Spesifikasi OpenAPI tersedia di `http://localhost:8000/openapi.json`. Ini berguna untuk:
  - Integrasi BE/FE (generate client dengan tool seperti `openapi-generator`/`swagger-codegen`)
  - Import ke Postman/Insomnia untuk koleksi request otomatis

Contoh mengambil OpenAPI JSON:
```bash
curl -s http://localhost:8000/openapi.json | jq '.info, .paths["/chat"]'
```

## UI Web
- Akses `http://localhost:8000/web`
- Input tetap di bawah layar, cocok untuk mobile
- Contoh prompt cepat tersedia di bawah input

## Data & Seed
- Tabel utama: `products`, `product_sizes` (stok per-ukuran), `orders`, `conversations`.
- Seed otomatis membuat 16+ produk dari berbagai kategori/brand, stok per-ukuran, dan contoh pesanan untuk user seperti `gilang`, `sela`.

## Arsitektur Singkat
- Intent dan ekstraksi (regex/heuristik) di `app/utils.py`.
- Query katalog/stock di `app/db.py` (SQLAlchemy). Jawaban tool (database) diformat lalu diprioritaskan.
- Jika tidak terjawab oleh tool, prompt gabungan (riwayat + konteks tool) dikirim ke Ollama via `app/llm.py`.
- Riwayat percakapan disimpan ke tabel `conversations`; jumlah yang dikirim ke LLM dibatasi `MAX_HISTORY_MESSAGES`.

## Fungsi Tool (Deterministic)
Tool dipanggil berdasarkan pola intent tertentu agar jawaban faktual selalu berasal dari database. Jika pertanyaan bersifat umum (bisa dijawab tanpa data presisi), model akan menjawab langsung tanpa tool.

- **OrderStatusChecker** — cek status pesanan (termasuk yang sudah dikirim/diantar)
  - Input:
    - `order_id` (opsional; contoh: `order #12` atau `pesanan #12`)
    - Jika `order_id` tidak ada, sistem cek pesanan terbaru berdasarkan `user` pada payload request
  - Output: status standar, mis. `processing`, `shipped`, `delivered` beserta label produk
  - Contoh prompt: "cek pesanan gilang", "status pesanan", "dimana pesanan saya?", "cek order #12"

- **CatalogLookup** — informasi produk, ukuran ready, stok per-ukuran
  - Varian:
    - Detail produk: nama/brand/kategori/deskripsi/harga/ukuran-ready
    - Ukuran tersedia: daftar ukuran yang ready untuk sebuah produk
    - Stok spesifik ukuran: stok exact untuk produk dan ukuran tertentu
  - Contoh prompt: "detail Air Max 90", "ukuran apa saja yang ready untuk Ultraboost 22?", "Ultraboost 22 ukuran 42 stoknya berapa?"

- **WarrantyInfo** — kebijakan garansi (teks tetap)
  - 1 tahun untuk cacat pabrik; ajukan via chat/email `support@shoestore.test` dengan nomor pesanan + bukti pembelian

### Kapan Tool Dipakai
- Pertanyaan yang butuh data presisi: status pesanan, stok per-ukuran, ketersediaan ukuran, daftar harga, filter kategori/brand/ukuran → tool dipanggil.
- Pertanyaan umum (cara pilih ukuran, perawatan, saran model kasual) → dijawab langsung oleh LLM (Bahasa Indonesia, ringkas, empatik), tanpa mengarang angka.

### Pengguna Demo (Seed) untuk Cek Pesanan
Tersedia user contoh: `adit`, `sela`, `gilang`. Untuk mengecek status/delivery pesanan, set kolom `user` pada payload sesuai nama user tersebut.

Contoh:
```bash
curl -s http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"user":"adit","message":"cek pesanan saya"}'

curl -s http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"user":"sela","message":"status pesanan"}'

# Atau langsung by order id (user bisa apa saja):
curl -s http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"user":"gilang","message":"cek pesanan saya"}'
```

Endpoint bantu:
- `GET /orders/{user}` → ambil pesanan terakhir untuk `adit|sela|gilang`.

### Contoh Interaksi
```json
POST /chat
{
  "user": "gilang",
  "message": "Ultraboost 22 ukuran 42 stoknya berapa?"
}

Response:
{
  "answer": "Stok Ultraboost 22 ukuran 42: 4 pasang. Mau dibantu cek warna atau ada alternatif serupa?"
}
```

## Pengembangan
- Versi API: lihat `app/main.py` → `FastAPI(..., version="1.5.0")`.
- Static UI di-mount di `/web` dengan `StaticFiles`.

## Troubleshooting
- Pastikan Ollama berjalan dan model tersedia (`OLLAMA_HOST` benar). Di Docker, service `ollama` otomatis expose `11434`.
- Untuk MySQL lokal, pastikan DSN `mysql+pymysql://...` valid dan user memiliki hak membuat tabel.
- Jika seed tidak muncul, hapus file SQLite `data/shoe_support.db` dan start ulang, atau pastikan DB kosong.

## Lisensi
Lihat file `LICENSE`.

## Testing
Rencana: pytest (TBD). Folder `tests/` belum disertakan.