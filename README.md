# Shoe Store Support Chatbot

A FastAPI-based customer support chatbot grounded by a MySQL/SQLite catalog.
It answers about products, sizes, per-size stock, categories, brands, price lists,
order status, and warranty. LLM is served by Ollama (Llama 3).

## Features
- RAG-first: database answers are always preferred over LLM generations.
- Product catalog with realistic data (16+ SKUs) and **per-size stock** (`product_sizes`).
- Intents: category listing, brand listing, price list, product details, size availability,
  per-size stock, alternatives, order status, and warranty.
- Simple web UI (static) with fixed input at the bottom (mobile-friendly).
- Configurable via environment variables.

## Quickstart (Docker)
```bash
docker compose up --build
# API: http://localhost:8000
# UI : http://localhost:8000/web
```

## Local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=sqlite:///./data/shoe_support.db
export OLLAMA_HOST=http://127.0.0.1:11434
export OLLAMA_MODEL=llama3.2:3b
uvicorn app.main:app --reload
```

## API

POST /chat → { "user": "gilang", "message": "Ukuran 42 untuk Ultraboost 22 ada berapa?" }

GET /products → list products

GET /orders/{user} → latest order for a user

GET /health → basic healthcheck

## Structure
```bash
app/
  main.py       # routing + tool-first intent
  db.py         # SQLAlchemy + RAG queries
  models.py     # Product, ProductSize, Order, Conversation
  utils.py      # intent detectors + tool answer formatters
  llm.py        # Ollama client
frontend/       # static UI
data/           # optional SQL seeds
```

## Testing

Run pytest (TBD). See tests/ folder.