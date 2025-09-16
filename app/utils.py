import re
from typing import List, Optional
from .models import Conversation, Order, Product

# Tangkap "order #123" atau "pesanan 123"
ORDER_PAT = re.compile(r"(?:order|pesanan)\s*#?\s*(\d+)", re.IGNORECASE)
PRODUCT_PAT = re.compile(r"(espresso|latte|cold\s*brew)", re.IGNORECASE)

def is_order_status_query(text: str) -> bool:
    keys = ["where is my order", "order status", "status pesanan", "dimana pesanan", "pesanan saya", "cek pesanan"]
    return any(k in text.lower() for k in keys) or bool(ORDER_PAT.search(text))

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

def is_product_query(text: str) -> bool:
    keys = ["kelebihan", "fitur", "advantages", "what is", "tell me about", "product"]
    return any(k in text.lower() for k in keys) or bool(PRODUCT_PAT.search(text))

def extract_product_name(text: str) -> Optional[str]:
    m = PRODUCT_PAT.search(text)
    return m.group(1) if m else None

def is_warranty_query(text: str) -> bool:
    keys = ["warranty", "garansi", "klaim garansi", "claim warranty"]
    return any(k in text.lower() for k in keys)

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
    return (
        "Our products include a **1-year limited warranty**. "
        "To claim, please provide your order number and purchase receipt. "
        "You can start a claim via this chat or email support@coffeestore.test."
    )

def format_history_for_prompt(history: List[Conversation]) -> str:
    """
    Ambil N interaksi (Q/A). Default MEMORY_TURNS = 3 (=> 6 pesan max).
    Pastikan urut kronologis.
    """
    if not history:
        return ""
    lines = []
    # history sudah kronologis
    selected = history[-(MEMORY_TURNS*2):]  # kira-kira 3 Q/A = 6 messages
    for msg in selected:
        role = "User" if msg.role == "user" else "Assistant"
        lines.append(f"{role}: {msg.message}")
    return "\n".join(lines)

def build_prompt(history_block: str, user_message: str, tool_context: Optional[str]) -> str:
    sys = (
        "You are a helpful customer support assistant for an online coffee store. "
        "Answer concisely and accurately. If a tool result is provided, prefer it over assumptions."
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
