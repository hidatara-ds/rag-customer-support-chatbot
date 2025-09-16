from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
import logging

from . import db
from .schemas import ChatRequest, ChatResponse, ProductOut, OrderOut
from .utils import (
    # intents
    is_order_status_query, is_category_list_query, is_category_inventory_query,
    is_category_size_inventory_query, is_size_inventory_query, is_brand_inventory_query,
    is_price_query, is_size_stock_query, is_size_query, is_other_products_query,
    is_product_query, is_warranty_query,
    # extractors
    extract_order_id, extract_category, extract_size_num, extract_product_name, extract_brand,
    # tool answers
    tool_answer_order, tool_answer_categories, tool_answer_pricelist,
    tool_answer_size_stock_exact, tool_answer_sizes, tool_answer_other_products, tool_answer_product, tool_answer_list,
    # prompt
    format_history_for_prompt, build_prompt
)
from .llm import generate_answer

logger = logging.getLogger("uvicorn")

app = FastAPI(title="Shoe Store Support Chatbot", version="1.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
)

app.mount("/web", StaticFiles(directory="frontend", html=True), name="web")

@app.on_event("startup")
async def on_startup():
    try:
        db.init_db()
        logger.info("DB initialized")
    except Exception as e:
        logger.warning(f"DB init failed (server will still run): {e}")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/products", response_model=List[ProductOut])
def products():
    rows = db.list_products()
    return [{"product_id": p.product_id, "name": p.name, "description": p.description, "price": p.price} for p in rows]

@app.get("/orders/{user}", response_model=List[OrderOut])
def orders(user: str):
    latest = db.get_latest_order(user)
    if not latest:
        return []
    return [{
        "order_id": latest.order_id,
        "user_name": latest.user_name,
        "product_name": latest.product.name if latest.product else "",
        "status": latest.status
    }]

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    user, message = req.user.strip(), req.message.strip()
    if not user or not message:
        raise HTTPException(status_code=400, detail="user and message are required")

    db.save_message(user, "user", message)
    history = db.get_last_messages(user, limit=None)
    history_block = format_history_for_prompt(history)

    tool_text = None
    answered = False

    if is_order_status_query(message):
        oid = extract_order_id(message)
        order = db.get_order_by_id(oid) if oid else db.get_latest_order(user)
        tool_text = tool_answer_order(order)
        answer = f"{tool_text} Jika perlu nomor resi/track detail, saya bisa bantu."
        answered = True

    elif is_category_list_query(message):
        cats = db.list_categories()
        tool_text = tool_answer_categories(cats)
        answer = tool_text
        answered = True

    elif is_category_inventory_query(message):
        cat = extract_category(message)
        prods = db.list_products_by_category(cat) if cat else []
        tool_text = tool_answer_list(f"Pilihan sepatu kategori {cat}", prods)
        answer = tool_text
        answered = True

    elif is_category_size_inventory_query(message):
        cat = extract_category(message)
        size = extract_size_num(message)
        prods = db.list_by_category_and_size(cat, size) if (cat and size) else []
        tool_text = tool_answer_list(f"Sepatu kategori {cat} ukuran {size}", prods)
        answer = tool_text
        answered = True

    elif is_size_inventory_query(message):
        size = extract_size_num(message)
        prods = db.list_by_size(size) if size else []
        tool_text = tool_answer_list(f"Sepatu ukuran {size}", prods)
        answer = tool_text
        answered = True

    elif is_brand_inventory_query(message):
        brand = extract_brand(message)
        prods = db.list_products_by_brand(brand) if brand else []
        tool_text = tool_answer_list(f"Sepatu brand {brand}", prods)
        answer = tool_text
        answered = True

    elif is_price_query(message):
        cat = extract_category(message)
        rows = db.list_price_list(cat)
        tool_text = tool_answer_pricelist(rows, cat)
        answer = tool_text
        answered = True

    elif is_size_stock_query(message):
        name = extract_product_name(message)
        p = db.get_product_by_name(name) or (db.search_products_fuzzy(message)[0] if db.search_products_fuzzy(message) else None)
        size = extract_size_num(message)
        exact = db.get_stock_for_product_size(p, size) if (p and size) else None
        tool_text = tool_answer_size_stock_exact(p, size, exact)
        answer = tool_text
        answered = True

    elif is_size_query(message):
        name = extract_product_name(message)
        p = db.get_product_by_name(name) or (db.search_products_fuzzy(message)[0] if db.search_products_fuzzy(message) else None)
        tool_text = tool_answer_sizes(p)
        answer = tool_text
        answered = True

    elif is_other_products_query(message):
        current = extract_product_name(message)
        others = db.list_other_products(current or "", limit=5, same_category_first=True)
        tool_text = tool_answer_other_products(current, others)
        answer = tool_text
        answered = True

    elif is_product_query(message):
        name = extract_product_name(message)
        p = db.get_product_by_name(name)
        if not p:
            found = db.search_products_fuzzy(message)
            p = found[0] if found else None
        tool_text = tool_answer_product(p)
        answer = tool_text
        answered = True

    elif is_warranty_query(message):
        from .utils import tool_answer_warranty
        tool_text = tool_answer_warranty()
        answer = tool_text
        answered = True

    if not answered:
        sample = db.search_products_fuzzy(message)[:5]
        if sample:
            tool_text = tool_answer_list("Hasil katalog yang mungkin relevan", sample)
        prompt = build_prompt(history_block, message, tool_text)
        answer = generate_answer(prompt)

    db.save_message(user, "assistant", answer)
    return ChatResponse(answer=answer)
