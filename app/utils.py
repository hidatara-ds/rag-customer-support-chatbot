import re
from typing import List, Optional
from .models import Conversation, Order, Product

# Tangkap "order #123" atau "pesanan 123"
ORDER_PAT = re.compile(r"(?:order|pesanan)\s*#?\s*(\d+)", re.IGNORECASE)

# Produk sepatu populer; bisa ditambah sesuai kebutuhan
PRODUCT_PAT = re.compile(
    r"(air\s*max\s*90|ultraboost\s*22|chuck\s*taylor\s*all\s*star|vans\s*old\s*skool)",
    re.IGNORECASE
)

def is_order_status_query(text: str) -> bool:
    keys = [
        "where is my order", "order status", "status pesanan",
        "dimana pesanan", "pesanan saya", "cek pesanan", "track order", "lacak pesanan"
    ]
    return any(k in text.lower() for k in keys) or bool(ORDER_PAT.search(text))

def extract_order_id(text: str) -> Optional[int]:
    m = ORDER_PAT.search(text)
    if m:
        try:
            return int(m.group(1))
        except:
            return None
    return None

def is_product_query(text: str) -> bool:
    keys = ["kelebihan", "fitur", "advantages", "what is", "tell me about", "product", "sepatu"]
    return any(k in text.lower() for k in keys) or bool(PRODUCT_PAT.search(text))

def extract_product_name(text: str) -> Optional[str]:
    m = PRODUCT_PAT.search(text)
    return m.group(1) if m else None

def is_warranty_query(text: str) -> bool:
    keys = ["warranty", "garansi", "klaim garansi", "claim warranty", "retur", "pengembalian"]
    return any(k in text.lower() for k in keys)

def tool_answer_order(order: Optional[Order]) -> str:
    if not order:
        return "I couldn’t find any order for your account yet."
    prod = order.product.name if order.product else "your item"
    return f"Your order #{order.order_id} ({prod}) is currently **{order.status}**."

def tool_answer_product(p: Optional[Product]) -> str:
    if not p:
        return "I couldn’t find that product in our catalog."
    return f"{p.name}: {p.description} (Price: ${p.price:.2f})."

def tool_answer_warranty() -> str:
    return (
        "For footwear purchases, we provide a **30-day return/exchange window** and a **1-year limited warranty** "
        "against manufacturing defects. To claim, please provide your order number and proof of purchase. "
        "You can start a claim via this chat or email support@shoestore.test."
    )

def format_history_for_prompt(history: List[Conversation]) -> str:
    if not history:
        return ""
    lines = []
    for msg in history:  # history sudah kronologis
        role = "User" if msg.role == "user" else "Assistant"
        lines.append(f"{role}: {msg.message}")
    return "\n".join(lines)

def build_prompt(history_block: str, user_message: str, tool_context: Optional[str]) -> str:
    sys = (
        "You are a helpful customer support assistant for an online shoe store. "
        "Answer concisely and accurately. If a tool result is provided, prefer it over assumptions."
    )
    tool = f"\nTOOL_INFO: {tool_context}" if tool_context else ""
    return f"{sys}\n\n{history_block}\nUser: {user_message}{tool}\nAssistant:"
