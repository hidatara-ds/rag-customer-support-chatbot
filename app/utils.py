import re
from typing import List, Optional
from .config import MEMORY_TURNS
from .models import Conversation, Order, Product

ORDER_PAT = re.compile(r"(?:order|pesanan)\s*#?\s*(\d+)", re.IGNORECASE)
PRODUCT_PAT = re.compile(r"(espresso|latte|cold\s*brew)", re.IGNORECASE)

def is_order_status_query(text: str) -> bool:
    keys = ["where is my order", "order status", "status pesanan", "dimana pesanan", "pesanan saya", "cek pesanan"]
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
        return "I couldn’t find any order for your account yet."
    prod = order.product.name if order.product else "your item"
    return f"Your order #{order.order_id} ({prod}) is currently **{order.status}**."

def tool_answer_product(p: Optional[Product]) -> str:
    if not p:
        return "I couldn’t find that product in our catalog."
    return f"{p.name}: {p.description} (Price: ${p.price:.2f})."

def tool_answer_warranty() -> str:
    return (
        "Our products include a **1-year limited warranty**. "
        "To claim, please provide your order number and purchase receipt. "
        "You can start a claim via this chat or email support@coffeestore.test."
    )

def format_history_for_prompt(history: List[Conversation]) -> str:
    """
    Take N interactions (Q/A). Default MEMORY_TURNS = 3 (=> 6 messages max).
    Ensure chronological order.
    """
    if not history:
        return ""
    lines = []
    # history is already chronological
    selected = history[-(MEMORY_TURNS*2):]  # roughly 3 Q/A = 6 messages
    for msg in selected:
        role = "User" if msg.role == "user" else "Assistant"
        lines.append(f"{role}: {msg.message}")
    return "\n".join(lines)

def build_prompt(history_block: str, user_message: str, tool_context: Optional[str]) -> str:
    sys = (
        "You are a helpful customer support assistant for an online coffee store. "
        "Answer concisely and accurately. If a tool result is provided, prefer it over assumptions."
    )
    tool = f"\nTOOL_INFO: {tool_context}" if tool_context else ""
    return f"{sys}\n\n{history_block}\nUser: {user_message}{tool}\nAssistant:"
