from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
import logging
from . import db
from .schemas import ChatRequest, ChatResponse, ProductOut, OrderOut, HealthResponse
from .config import API_TITLE, API_VERSION, LOG_LEVEL
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

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="AI-powered customer support chatbot for shoe store with RAG capabilities"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
)

# Serve frontend
app.mount("/web", StaticFiles(directory="frontend", html=True), name="web")


@app.on_event("startup")
async def on_startup():
    """Initialize database on application startup"""
    try:
        db.init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


@app.get("/health", response_model=HealthResponse)
def health():
    """Health check endpoint with database connectivity status"""
    try:
        # Test database connection
        db_status = db.check_db_health()
        return {
            "status": "healthy" if db_status else "degraded",
            "database": "connected" if db_status else "disconnected",
            "version": API_VERSION
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "error",
            "version": API_VERSION
        }


@app.get("/products", response_model=List[ProductOut])
def products():
    """Get list of all available products"""
    try:
        rows = db.list_products()
        return [
            {
                "product_id": p.product_id,
                "name": p.name,
                "description": p.description,
                "price": p.price
            }
            for p in rows
        ]
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch products")


@app.get("/orders/{user}", response_model=List[OrderOut])
def orders(user: str):
    """Get latest order for a specific user"""
    try:
        if not user or len(user.strip()) == 0:
            raise HTTPException(status_code=400, detail="User parameter is required")
        
        latest = db.get_latest_order(user.strip())
        if not latest:
            return []
        
        return [{
            "order_id": latest.order_id,
            "user_name": latest.user_name,
            "product_name": latest.product.name if latest.product else "",
            "status": latest.status
        }]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching orders for user {user}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch orders")


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Main chat endpoint for customer support interactions.
    Handles order status, product queries, warranty info, and general questions.
    """
    try:
        user, message = req.user.strip(), req.message.strip()
        
        # Validation
        if not user or not message:
            raise HTTPException(
                status_code=400,
                detail="Both 'user' and 'message' fields are required and cannot be empty"
            )
        
        if len(message) > 1000:
            raise HTTPException(
                status_code=400,
                detail="Message is too long. Maximum 1000 characters allowed"
            )

        logger.info(f"Chat request from user '{user}': {message[:50]}...")

        # Save user message
        db.save_message(user, "user", message)

        # Get conversation history
        history = db.get_last_messages(user, limit=6)
        history_block = format_history_for_prompt(history)

        # Tool routing
        tool_text = None
        answered_by_tool = False

        # Order status query
        if is_order_status_query(message):
            order_id = extract_order_id(message)
            order = db.get_order_by_id(order_id) if order_id else db.get_latest_order(user)
            tool_text = tool_answer_order(order)
            answer = f"{tool_text} If you need more details, I can provide tracking info."
            answered_by_tool = True
            logger.info(f"Order status query handled for user '{user}'")

        # Product query
        elif is_product_query(message):
            name = extract_product_name(message)
            product = db.get_product_by_name(name) if name else None
            tool_text = tool_answer_product(product)
            answer = tool_text
            answered_by_tool = True
            logger.info(f"Product query handled for user '{user}'")

        # Warranty query
        elif is_warranty_query(message):
            tool_text = tool_answer_warranty()
            answer = tool_text
            answered_by_tool = True
            logger.info(f"Warranty query handled for user '{user}'")

        # LLM fallback for general questions
        if not answered_by_tool:
            prompt = build_prompt(history_block, message, tool_text)
            answer = generate_answer(prompt)
            logger.info(f"LLM generated answer for user '{user}'")

        # Save assistant response
        db.save_message(user, "assistant", answer)
        
        return ChatResponse(answer=answer)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again."
        )
