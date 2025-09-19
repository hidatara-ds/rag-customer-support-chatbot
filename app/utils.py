# app/utils.py — MINIMAL RAG (fix imports)
from __future__ import annotations

import re
from typing import Iterable, List, Optional
from .models import Conversation, Product
from .config import MAX_HISTORY_MESSAGES

# ---------- Regex dasar ----------
ORDER_PAT   = re.compile(r"(?:order|pesanan)\s*#?\s*(\d+)", re.IGNORECASE)
PRODUCT_PAT = re.compile(r"([a-zA-Z]+(?:\s+[a-zA-Z0-9']+){0,3})", re.IGNORECASE)
SIZE_NUM_PAT = re.compile(r"\b(?:size|ukuran)\s*(\d{2})\b", re.IGNORECASE)

# Regex kategori/brand disediakan agar extractor tetap ada (kompatibel),
# tapi INTENT terkait kita nonaktifkan supaya fallback ke LLM.
CATEGORY_PAT = re.compile(r"\b(running|casual|basketball|skate|hiking|training)\b", re.IGNORECASE)
BRAND_PAT    = re.compile(r"\b(Nike|Adidas|Converse|Vans|Reebok|Salomon|New\s*Balance)\b", re.IGNORECASE)

# ---------- INTENT aktif (yang butuh presisi DB) ----------
def is_order_status_query(t: str) -> bool:
    keys = ["where is my order", "order status", "status pesanan", "dimana pesanan", "pesanan saya", "cek pesanan"]
    return any(k in t.lower() for k in keys) or bool(ORDER_PAT.search(t))

def is_size_stock_query(t: str) -> bool:
    keys = ["berapa stok ukuran", "stok ukuran", "ukuran", "size"]
    return any(k in t.lower() for k in keys) and bool(SIZE_NUM_PAT.search(t))

def is_size_query(t: str) -> bool:
    keys = ["ukuran apa saja", "size apa saja", "ukuran ready", "size ready", "tersedia ukuran"]
    return any(k in t.lower() for k in keys)

def is_warranty_query(t: str) -> bool:
    keys = ["warranty", "garansi", "klaim garansi", "claim warranty", "retur", "pengembalian"]
    return any(k in t.lower() for k in keys)

# ---------- INTENT nonaktif (biarkan LLM berpikir) ----------
def is_category_list_query(_: str) -> bool:            return False
def is_category_inventory_query(_: str) -> bool:       return False
def is_category_size_inventory_query(_: str) -> bool:  return False
def is_size_inventory_query(_: str) -> bool:           return False
def is_brand_inventory_query(_: str) -> bool:          return False
def is_price_query(_: str) -> bool:                    return False
def is_other_products_query(_: str) -> bool:           return False
def is_product_query(_: str) -> bool:                  return False

# ---------- EXTRACTORS minimal ----------
def extract_order_id(t: str) -> Optional[int]:
    m = ORDER_PAT.search(t)
    if not m: return None
    try:
        return int(m.group(1))
    except Exception:
        return None

def extract_product_name(t: str) -> Optional[str]:
    m = PRODUCT_PAT.search(t)
    return m.group(1) if m else None

def extract_size_num(t: str) -> Optional[int]:
    m = SIZE_NUM_PAT.search(t)
    if not m: return None
    try:
        return int(m.group(1))
    except Exception:
        return None

# 👇 dua extractor ini dikembalikan supaya import di main.py tidak error
def extract_category(t: str) -> Optional[str]:
    m = CATEGORY_PAT.search(t)
    return m.group(1) if m else None  # dipakai hanya jika kamu aktifkan lagi intent kategori

def extract_brand(t: str) -> Optional[str]:
    m = BRAND_PAT.search(t)
    if not m: return None
    b = m.group(1)
    return "New Balance" if b.lower().replace(" ", "") == "newbalance" else b.title()

# ---------- TOOL ANSWERS (presisi dari DB) ----------
def tool_answer_sizes(p: Optional[Product]) -> str:
    if not p:
        return "Saya tidak menemukan produk tersebut. Bisa sebutkan nama produk lengkapnya?"
    return f"Ukuran {p.name} yang ready: {p.sizes}. Stok total: {p.stock_total} pasang."

def tool_answer_size_stock_exact(p: Optional[Product], size: Optional[int], exact: Optional[int]) -> str:
    if not p or not size:
        return "Sebutkan nama produk dan ukuran yang ingin dicek ya."
    if exact is None:
        return f"Data stok ukuran {size} untuk {p.name} belum tersedia."
    return f"Stok {p.name} ukuran {size}: {int(exact)} pasang."

def tool_answer_product(p: Optional[Product]) -> str:
    if not p:
        return "Produk yang Anda cari belum ada di katalog kami."
    return (f"{p.name} ({p.brand}/{p.category}) — {p.description} "
            f"Harga: ${p.price:.2f}. Ukuran ready: {p.sizes}. Stok total: {p.stock_total} pasang.")

def tool_answer_warranty() -> str:
    return ("Garansi terbatas 1 tahun untuk cacat pabrik. "
            "Untuk klaim, siapkan nomor pesanan dan bukti pembelian. "
            "Bisa diajukan lewat chat ini atau email ke support@shoestore.test.")

# ---------- STUB kompat (agar main.py aman meski intent di atas nonaktif) ----------
def tool_answer_order(order) -> str:
    if not order:
        return "Saya belum menemukan pesanan aktif untuk akun Anda."
    prod = getattr(getattr(order, "product", None), "name", "produk Anda")
    return f"Pesanan #{order.order_id} ({prod}) saat ini berstatus {order.status}."

def tool_answer_categories(_: List[str]) -> str:
    return "Kategori akan saya sampaikan jika diperlukan."
def tool_answer_pricelist(_: List[tuple], __: Optional[str]) -> str:
    return "Daftar harga akan saya sampaikan jika diperlukan."
def tool_answer_other_products(current_name: Optional[str], others: List[str]) -> str:
    if not others: return "Saat ini belum ada rekomendasi lain."
    base = f"Selain {current_name}, " if current_name else ""
    return base + "coba juga: " + ", ".join(others)
def tool_answer_list(title: str, prods: Iterable[Product]) -> str:
    items = list(prods)
    if not items: return f"{title}: (tidak ada data)"
    lines = [title + ":"] + [f"- {p.name} — ${p.price:.2f}" for p in items[:6]]
    return "\n".join(lines)

# ---------- PROMPT fallback (LLM) ----------
def format_history_for_prompt(history: List[Conversation]) -> str:
    if not history: return ""
    selected = history[-MAX_HISTORY_MESSAGES:]
    lines: List[str] = []
    for msg in selected:
        role = "User" if msg.role == "user" else "Assistant"
        lines.append(f"{role}: {msg.message}")
    return "\n".join(lines)

_FEW_SHOTS = """
User: Sepatu hiking ukuran 41 ada apa?
Assistant: Untuk hiking ukuran 41, bisa sebutkan preferensi merek atau kisaran harga? Saya bantu carikan yang sesuai.

User: Ultraboost 22 size 42 stoknya berapa?
Assistant: Baik, saya cek stok pastinya. Kalau size 42 kosong, apakah mau alternatif ukuran terdekat?

User: Ada promo?
Assistant: Saya tidak punya data promo real-time. Tapi saya bisa sarankan model paling terjangkau di kategori yang kamu mau.
"""

def build_prompt(history_block: str, user_message: str, tool_context: Optional[str]) -> str:
    sys = ("Peran: Asisten CS toko sepatu (Bahasa Indonesia). "
           "Gunakan TOOL_INFO jika tersedia. Jika tidak ada, jawab natural, ramah, "
           "tanpa mengarang angka. Akhiri dengan 1 tindak lanjut singkat.")
    tool = f"\nTOOL_INFO (jangan ubah faktanya):\n{tool_context}" if tool_context else ""
    return f"{sys}\n\n{_FEW_SHOTS}\n\n{history_block}\nUser: {user_message}{tool}\nAssistant:"
