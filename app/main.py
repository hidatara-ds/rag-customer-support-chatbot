from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
import logging

from . import db
from .schemas import ChatRequest, ChatResponse, ProductOut, OrderOut
from .utils import (
    is_order_status_query, extract_order_id, is_product_query, extract_product_name,
    is_warranty_query, tool_answer_order, tool_answer_product, tool_answer_warranty,
    format_history_for_prompt, build_prompt
)
from .llm import generate_answer

logger = logging.getLogger("uvicorn")

app = FastAPI(title="Shoe Store Support Chatbot", version="1.1.0")

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

    # save user msg
    db.save_message(user, "user", message)

    # history (unlimited in DB; untuk prompt pakai MAX_HISTORY_MESSAGES)
    history = db.get_last_messages(user, limit=None)
    history_block = format_history_for_prompt(history)

    # tool routing
    tool_text = None
    answered_by_tool = False

    if is_order_status_query(message):
        order_id = extract_order_id(message)
        order = db.get_order_by_id(order_id) if order_id else db.get_latest_order(user)
        tool_text = tool_answer_order(order)
        answer = f"{tool_text} If you need more details, I can provide tracking info."
        answered_by_tool = True

    elif is_product_query(message):
        name = extract_product_name(message)
        product = db.get_product_by_name(name) if name else None
        tool_text = tool_answer_product(product)
        answer = tool_text
        answered_by_tool = True

    elif is_warranty_query(message):
        tool_text = tool_answer_warranty()
        answer = tool_text
        answered_by_tool = True

    if not answered_by_tool:
        prompt = build_prompt(history_block, message, tool_text)
        answer = generate_answer(prompt)

    db.save_message(user, "assistant", answer)
    return ChatResponse(answer=answer)
