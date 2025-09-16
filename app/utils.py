import re
from typing import List, Optional
from .models import Conversation, Order, Product

ORDER_PAT = re.compile(r"(?:order|pesanan)\s*#?\s*(\d+)", re.IGNORECASE)
CATEGORY_PAT = re.compile(r"\b(running|casual|basketball|skate|hiking|training)\b", re.IGNORECASE)
BRAND_PAT = re.compile(r"\b(nike|adidas|converse|vans|new balance|reebok|salomon)\b", re.IGNORECASE)
SIZE_NUM_PAT = re.compile(r"(?:ukuran|size)\s*([0-9]{2})", re.IGNORECASE)

PRODUCT_PAT = re.compile(
    r"(air\s*max\s*90|ultraboost\s*22|chuck\s*taylor\s*all\s*star|vans\s*old\s*skool|"
    r"air\s*jordan\s*1\s*mid|kyrie\s*flytrap\s*6|nb\s*990v5|nb\s*574\s*core|gazelle|"
    r"pegasus\s*40|metcon\s*9|nano\s*x3|terrex\s*swift\s*r3|salomon\s*xa\s*pro\s*3d|"
    r"blazer\s*mid\s*'?\s*77|sk8-?hi)",
    re.IGNORECASE
)

# -------- intents ----------
def is_order_status_query(t:str)->bool:
    keys=["where is my order","order status","status pesanan","dimana pesanan","pesanan saya","cek pesanan","track order","lacak pesanan"]
    return any(k in t.lower() for k in keys) or bool(ORDER_PAT.search(t))

def is_category_list_query(t:str)->bool:
    keys=["jenis sepatu apa saja","kategori apa saja","daftar kategori","jenis apa saja","kategori yang ada","jenis sepatu apa aja","kategori apa aja"]
    return any(k in t.lower() for k in keys)

def is_category_inventory_query(t:str)->bool:
    return bool(CATEGORY_PAT.search(t)) and any(k in t.lower() for k in ["ada apa","apa saja","daftar","list"])

def is_category_size_inventory_query(t:str)->bool:
    return bool(CATEGORY_PAT.search(t)) and bool(SIZE_NUM_PAT.search(t))

def is_size_inventory_query(t:str)->bool:
    return bool(SIZE_NUM_PAT.search(t)) and any(k in t.lower() for k in ["ada apa","apa saja","list","daftar"])

def is_brand_inventory_query(t:str)->bool:
    return bool(BRAND_PAT.search(t)) and any(k in t.lower() for k in ["ada apa","apa saja","list","daftar"])

def is_price_query(t:str)->bool:
    keys=["harga berapa","berapa harganya","price list","daftar harga","kisaran harga","range harga","harga kategori"]
    return any(k in t.lower() for k in keys)

def is_size_stock_query(t:str)->bool:
    keys=["berapa stok ukuran","stok ukuran","ukuran 39 ada berapa","size 42 ada berapa"]
    return any(k in t.lower() for k in keys) or bool(SIZE_NUM_PAT.search(t))

def is_size_query(t:str)->bool:
    keys=["ukuran apa saja","size apa saja","ukuran ready","size ready","tersedia ukuran"]
    return any(k in t.lower() for k in keys) or (("ukuran" in t.lower() or "size" in t.lower()) and bool(PRODUCT_PAT.search(t)))

def is_other_products_query(t:str)->bool:
    keys=["selain","ada sepatu apa lagi","rekomendasi lain","alternatif lain"]
    return any(k in t.lower() for k in keys)

def is_product_query(t:str)->bool:
    keys=["kelebihan","fitur","advantages","apa itu","apa keunggulan","jelasin","tell me about","produk","product","sepatu"]
    return any(k in t.lower() for k in keys) or bool(PRODUCT_PAT.search(t))

def is_warranty_query(t:str)->bool:
    keys=["warranty","garansi","klaim garansi","claim warranty","retur","pengembalian"]
    return any(k in t.lower() for k in keys)

# -------- extractors ----------
def extract_order_id(t:str)->Optional[int]:
    m=ORDER_PAT.search(t); 
    if m:
        try: return int(m.group(1))
        except: return None
    return None
def extract_category(t:str)->Optional[str]:
    m=CATEGORY_PAT.search(t); return m.group(1) if m else None
def extract_brand(t:str)->Optional[str]:
    m=BRAND_PAT.search(t); 
    if not m: return None
    b=m.group(1)
    return "New Balance" if b.lower()=="new balance" else b.title()
def extract_product_name(t:str)->Optional[str]:
    m=PRODUCT_PAT.search(t); return m.group(1) if m else None
def extract_size_num(t:str)->Optional[int]:
    m=SIZE_NUM_PAT.search(t)
    if m:
        try: return int(m.group(1))
        except: return None
    return None

# -------- tool answers ----------
def tool_answer_list(title: str, prods: List[Product]) -> str:
    if not prods:
        return f"Tidak ditemukan item untuk {title}."
    lines = [f"- {p.name} ({p.brand}, {p.category}) — ${p.price:.2f} | size: {p.sizes}" for p in prods]
    return f"{title}:\n" + "\n".join(lines)

def tool_answer_order(order: Optional[Order]) -> str:
    if not order:
        return "Saya belum menemukan pesanan aktif untuk akun Anda."
    prod = order.product.name if order.product else "produk Anda"
    return f"Pesanan #{order.order_id} ({prod}) saat ini berstatus **{order.status}**."

def tool_answer_product(p: Optional[Product]) -> str:
    if not p:
        return "Produk yang Anda cari belum ada di katalog kami."
    return (f"{p.name} ({p.brand}, {p.category}) — {p.description} "
            f"Harga: ${p.price:.2f}. Ukuran ready: {p.sizes}. Stok total: {p.stock_total} pasang.")

def tool_answer_warranty() -> str:
    return ("Untuk pembelian sepatu, kami menyediakan **retur/penukaran 30 hari** dan **garansi 1 tahun** "
            "untuk cacat produksi. Siapkan nomor pesanan dan bukti pembelian. "
            "Anda bisa mulai klaim lewat chat ini atau email ke support@shoestore.test.")

def tool_answer_sizes(p: Optional[Product]) -> str:
    if not p:
        return "Saya tidak menemukan produk tersebut. Bisa sebutkan nama produk lengkapnya?"
    return f"Ukuran {p.name} yang ready: {p.sizes}. Stok total saat ini: {p.stock_total}."

def tool_answer_size_stock_exact(p: Optional[Product], size: Optional[int], exact_stock: Optional[int]) -> str:
    if not p:
        return "Saya tidak menemukan produk tersebut. Bisa sebutkan nama produk lengkapnya?"
    if size is None:
        return f"Untuk stok per ukuran {p.name}, mohon sebutkan ukurannya. Ukuran ready: {p.sizes}."
    if str(size) not in (p.sizes or ""):
        return f"Ukuran {size} untuk {p.name} tidak tertera pada daftar ready: {p.sizes}."
    qty = 0 if exact_stock is None else int(exact_stock)
    return f"Stok ukuran {size} untuk {p.name}: **{qty}** pasang."

def tool_answer_categories(categories: List[str]) -> str:
    if not categories: return "Kategori belum tersedia."
    return "Kategori yang tersedia: " + ", ".join(sorted(categories)) + "."

def tool_answer_pricelist(rows: List[tuple], cat: Optional[str]) -> str:
    if not rows: return "Belum ada data harga untuk permintaan tersebut."
    head = f"Daftar harga{f' kategori {cat}' if cat else ''}:"
    lines = [f"- {name}: ${price:.2f}" for name, price in rows]
    return head + "\n" + "\n".join(lines)

def tool_answer_other_products(current_name: Optional[str], others: List[str]) -> str:
    if not others: return "Saat ini belum ada rekomendasi lain."
    if current_name:
        return f"Selain {current_name}, Anda bisa cek: " + ", ".join(others) + "."
    return "Rekomendasi lain: " + ", ".join(others) + "."

# -------- prompt ----------
def format_history_for_prompt(history: List[Conversation]) -> str:
    if not history: return ""
    lines = []
    for msg in history:
        role = "User" if msg.role == "user" else "Assistant"
        lines.append(f"{role}: {msg.message}")
    return "\n".join(lines)

def build_prompt(history_block: str, user_message: str, tool_context: Optional[str]) -> str:
    sys = (
        "Kamu adalah asisten Customer Support untuk toko sepatu online. "
        "Jawab **dalam Bahasa Indonesia**, ringkas, jelas, sopan. "
        "Selalu dasarkan jawaban pada data katalog (TOOL_INFO) jika tersedia; jangan mengarang. "
        "Jika pertanyaan masih terkait produk, ukuran, harga, pesanan, retur/garansi, kategori, brand, atau rekomendasi, "
        "tetap usahakan menjawab. Jika benar-benar di luar konteks, jelaskan keterbatasanmu."
    )
    tool = f"\nTOOL_INFO:\n{tool_context}" if tool_context else ""
    return f"{sys}\n\n{history_block}\nUser: {user_message}{tool}\nAssistant:"

def tool_answer_sizes(p: Optional[Product]) -> str:
    if not p:
        return "Saya tidak menemukan produk tersebut. Bisa sebutkan nama produk lengkapnya?"
    # tampilkan ringkasan stok per-ukuran jika tersedia (via DB helper)
    try:
        from . import db
        # ambil semua size (urut)
        size_map = {}
        for s in db.search_products_fuzzy(p.name)[:1]:  # ambil objek sama
            pass
        # gunakan helper langsung:
        # (kita bikin helper baru di db.py kalau belum ada)
    except Exception:
        size_map = {}

    note = f"Ukuran {p.name} yang ready: {p.sizes}. Stok total: {p.stock_total}."
    return note
