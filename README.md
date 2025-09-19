# Customer Support Chatbot Project

Chatbot dukungan pelanggan untuk toko sepatu yang berjalan lokal dengan FastAPI + Ollama. Proyek ini menyimpan riwayat percakapan di database dan menyediakan REST API yang dapat diintegrasikan dengan aplikasi lain.

## 1. Cara Instalasi & Requirement pada Environment Local
- Python 3.11 (disarankan) dan virtual environment
  - macOS/Linux: `python -m venv .venv && source .venv/bin/activate`
  - Windows (PowerShell): `python -m venv .venv; .\\.venv\\Scripts\\Activate.ps1`
- Clone repository
  ```bash
  git clone <your-repo-url>
  cd Customer-Support-Chatbot-Project
  ```
- Instal dependensi
  ```bash
  pip install -r requirements.txt
  ```
- Instal Ollama dan model LLM lokal
  - Install Ollama: lihat dokumentasi resmi (`https://ollama.com`)
  - Jalankan server: `ollama serve`
  - Pull model: `ollama pull llama3.2:3b`
- Setup database
  - Default: SQLite (otomatis dibuat dan di-seed saat pertama kali jalan)
  - Opsional: MySQL (set ENV `DATABASE_URL`, contoh `mysql+pymysql://root:root@127.0.0.1:3306/shoe_support`)
- Jalankan aplikasi (REST API di localhost)
  ```bash
  uvicorn app.main:app --reload
  # API     : http://localhost:8000
  # Docs    : http://localhost:8000/docs (Swagger UI untuk test API)
  # OpenAPI : http://localhost:8000/openapi.json (spec JSON untuk BE/FE)
  # Web UI  : http://localhost:8000/web
  ```
- Opsional (nilai tambah): Docker
  ```bash
  docker compose up --build
  # Services: api + db (MySQL 8) + ollama
  ```

## 2. Desain Database
Tujuan: menyimpan history chat agar konteks percakapan dapat dipakai ulang oleh LLM.

- Tabel yang diminta challenge: `chat_history`
  - Kolom: `id` (primary key), `user_message`, `bot_response`, `timestamp`

Contoh SQL schema:
```sql
CREATE TABLE IF NOT EXISTS chat_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_message TEXT NOT NULL,
  bot_response TEXT NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```
Catatan: Implementasi pada repo ini sudah menyimpan percakapan ke tabel `conversations` (dengan peran user/assistant) dan juga memiliki tabel katalog (`products`, `product_sizes`) serta pesanan (`orders`).

## 3. List Library dan Framework yang Digunakan
- FastAPI: REST API
- Uvicorn: ASGI server
- SQLAlchemy: ORM/database access
- PyMySQL: driver MySQL (opsional)
- Pydantic: schema request/response
- Requests: HTTP client (memanggil Ollama API)
- python-dotenv: memuat variabel lingkungan
- cryptography: dukungan auth MySQL modern
- Ollama: runtime LLM lokal

(Sesuai `requirements.txt`.)

## 4. Model LLM yang Digunakan
- Llama 3.2 (3B) via Ollama (berjalan lokal)
- Alasan: ringan, open-source, dan memenuhi syarat challenge untuk LLM lokal

## 5. Daftar Pertanyaan yang Dapat Dijawab
- Status pesanan
  - Contoh: "Dimana pesanan saya?", "status pesanan sela", "cek order #12"
- Informasi produk
  - Contoh: "Apa kelebihan Air Max 90?", "detail Ultraboost 22"
- Ketersediaan ukuran & stok per-ukuran
  - Contoh: "Ultraboost 22 ukuran 42 stoknya berapa?", "ukuran apa saja yang ready?"
- Kebijakan garansi
  - Contoh: "Bagaimana cara saya meng-claim garansi?"
- Catatan: dapat diperluas untuk pertanyaan lain sesuai kebutuhan.

Pengguna demo (seed) untuk cek pesanan: `adit`, `sela`, `gilang`. Saat menguji status/delivery pesanan, set field `user` pada payload sesuai nama tersebut.

## 6. Daftar Tool Call yang Dapat Dilakukan
- Order Status Lookup
  - Chatbot memanggil fungsi eksternal untuk mengecek status pesanan berdasarkan intent (regex) dan/atau `order_id` yang diekstrak dari pesan. Jika `order_id` tidak ada, sistem memakai pesanan terakhir milik `user` pada payload.
  - Output status standar: `processing`, `shipped`, `delivered`, beserta nama produk.
  - Contoh payload:
    ```json
    { "user": "sela", "message": "status pesanan" }
    ```
- Catalog Lookup (bisa diperluas)
  - Detail produk, ukuran ready, stok per-ukuran.
- Warranty Info (bisa diperluas)
  - Mengembalikan teks kebijakan garansi tetap.

Tambahan: Dok Swagger di `http://localhost:8000/docs` dapat dipakai untuk pengujian endpoint interaktif, dan spesifikasi OpenAPI JSON tersedia di `http://localhost:8000/openapi.json` untuk kebutuhan integrasi BE/FE (generate client atau import ke Postman/Insomnia).

## Endpoint & Docs Singkat
- Endpoint: `GET /health`, `GET /products`, `GET /orders/{user}`, `POST /chat`
- Docs: `http://localhost:8000/docs` (uji interaktif), OpenAPI: `/openapi.json`
- UI: `http://localhost:8000/web`

## Fitur
- Fokus RAG: data katalog dari DB, LLM sebagai pelengkap.
- UI web sederhana di `/web`, konfigurasi via ENV.
- Intent siap pakai: status pesanan, info produk, ukuran/stok, garansi.

## Struktur Folder
```bash
app/ (main.py, db.py, models.py, utils.py, schemas.py, config.py, llm.py)
frontend/ (index.html)
data/ (database.mysql.sql)
Dockerfile, docker-compose.yml, requirements.txt, LICENSE
```

## Persyaratan & ENV Singkat
- Python 3.11+, Ollama (model `llama3.2:3b`), SQLite (default) / MySQL (opsional)
- ENV utama: `DATABASE_URL`, `OLLAMA_HOST`, `OLLAMA_MODEL`, `MAX_HISTORY_MESSAGES`

## Cara Menjalankan Singkat
- Lokal: `uvicorn app.main:app --reload`
- Docker: `docker compose up --build`
- Lihat detail langkah di bagian 1 (Instalasi)

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

## Fungsi Tool (Ringkas)
- Order Status Lookup: cek status berdasarkan `order_id` atau pesanan terakhir milik `user`.
- Catalog Lookup: detail produk, ukuran ready, stok per-ukuran.
- Warranty Info: teks kebijakan garansi tetap.

Contoh payload uji status pesanan:
```json
{ "user": "sela", "message": "status pesanan" }
```
Pengguna demo: `adit`, `sela`, `gilang`.

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