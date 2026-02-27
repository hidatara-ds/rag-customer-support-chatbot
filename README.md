# Customer Support Chatbot Project

A customer support chatbot for a shoe store running locally with FastAPI + Ollama. This project stores conversation history in a database and provides a REST API that can be integrated with other applications.

## 1. Installation & Local Environment Requirements
- Python 3.11 (recommended) and virtual environment
  - macOS/Linux: `python -m venv .venv && source .venv/bin/activate`
  - Windows (PowerShell): `python -m venv .venv; .\\.venv\\Scripts\\Activate.ps1`
- Clone repository
  ```bash
  git clone <your-repo-url>
  cd Customer-Support-Chatbot-Project
  ```
- Install dependencies
  ```bash
  pip install -r requirements.txt
  ```
- Install Ollama and local LLM model
  - Install Ollama: see official documentation (`https://ollama.com`)
  - Run server: `ollama serve`
  - Pull model: `ollama pull llama3.2:3b`
- Setup database
  - Default: SQLite (automatically created and seeded on first run)
  - Optional: MySQL (set ENV `DATABASE_URL`, example `mysql+pymysql://root:root@127.0.0.1:3306/shoe_support`)
- Run application (REST API on localhost)
  ```bash
  uvicorn app.main:app --reload
  # API     : http://localhost:8000
  # Docs    : http://localhost:8000/docs (Swagger UI for API testing)
  # OpenAPI : http://localhost:8000/openapi.json (JSON spec for BE/FE)
  # Web UI  : http://localhost:8000/web
  ```
- Optional (bonus): Docker
  ```bash
  docker compose up --build
  # Services: api + db (MySQL 8) + ollama
  ```

## 2. Database Design
Purpose: store chat history so conversation context can be reused by the LLM.

- Challenge-required table: `chat_history`
  - Columns: `id` (primary key), `user_message`, `bot_response`, `timestamp`

Example SQL schema:
```sql
CREATE TABLE IF NOT EXISTS chat_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_message TEXT NOT NULL,
  bot_response TEXT NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```
Note: This repository implementation already stores conversations in the `conversations` table (with user/assistant roles) and also has catalog tables (`products`, `product_sizes`) and orders (`orders`).

## 3. Libraries and Frameworks Used
- FastAPI: REST API
- Uvicorn: ASGI server
- SQLAlchemy: ORM/database access
- PyMySQL: MySQL driver (optional)
- Pydantic: request/response schema
- Requests: HTTP client (calling Ollama API)
- python-dotenv: load environment variables
- cryptography: modern MySQL auth support
- Ollama: local LLM runtime

(As per `requirements.txt`.)

## 4. LLM Model Used
- Llama 3.2 (3B) via Ollama (running locally)
- Reason: lightweight, open-source, and meets challenge requirements for local LLM

## 5. Questions That Can Be Answered
- Order status
  - Examples: "Where is my order?", "status of sela's order", "check order #12"
- Product information
  - Examples: "What are the advantages of Air Max 90?", "details of Ultraboost 22"
- Size availability & stock per size
  - Examples: "How much stock for Ultraboost 22 size 42?", "what sizes are available?"
- Warranty policy
  - Examples: "How do I claim warranty?"
- Note: can be expanded for other questions as needed.

Demo users (seed) for order checking: `adit`, `sela`, `gilang`. When testing order status/delivery, set the `user` field in the payload to match these names.

## 6. Tool Calls Available
- Order Status Lookup
  - Chatbot calls external function to check order status based on intent (regex) and/or `order_id` extracted from message. If `order_id` is not available, system uses the last order belonging to `user` in the payload.
  - Standard status output: `processing`, `shipped`, `delivered`, along with product name.
  - Example payload:
    ```json
    { "user": "sela", "message": "order status" }
    ```
- Catalog Lookup (expandable)
  - Product details, available sizes, stock per size.
- Warranty Info (expandable)
  - Returns fixed warranty policy text.

Additional: Swagger docs at `http://localhost:8000/docs` can be used for interactive endpoint testing, and OpenAPI JSON specification is available at `http://localhost:8000/openapi.json` for BE/FE integration needs (generate client or import to Postman/Insomnia).

## Endpoints & Quick Docs
- Endpoints: `GET /health`, `GET /products`, `GET /orders/{user}`, `POST /chat`
- Docs: `http://localhost:8000/docs` (interactive testing), OpenAPI: `/openapi.json`
- UI: `http://localhost:8000/web`

## Features
- RAG focus: catalog data from DB, LLM as complement.
- Simple web UI at `/web`, configuration via ENV.
- Ready-to-use intents: order status, product info, size/stock, warranty.

## Folder Structure
```bash
app/ (main.py, db.py, models.py, utils.py, schemas.py, config.py, llm.py)
frontend/ (index.html)
data/ (database.mysql.sql)
Dockerfile, docker-compose.yml, requirements.txt, LICENSE
```

## Requirements & ENV Summary
- Python 3.11+, Ollama (model `llama3.2:3b`), SQLite (default) / MySQL (optional)
- Main ENV: `DATABASE_URL`, `OLLAMA_HOST`, `OLLAMA_MODEL`, `MAX_HISTORY_MESSAGES`

## Quick Start
- Local: `uvicorn app.main:app --reload`
- Docker: `docker compose up --build`
- See detailed steps in section 1 (Installation)

## API Endpoints
- `GET /health` → simple health check
- `GET /products` → brief product list
- `GET /orders/{user}` → last order for user
- `POST /chat` → chatbot conversation (RAG-first)

### `POST /chat` Schema
Request:
```json
{
  "user": "gilang",
  "message": "How much stock for size 42 Ultraboost 22?"
}
```
Response:
```json
{ "answer": "Ultraboost 22 size 42 stock: 4 pairs." }
```

Example cURL:
```bash
curl -s http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"user":"gilang","message":"What types of shoes are available?"}'
```

## API Documentation (Swagger / OpenAPI)
- Open `http://localhost:8000/docs` to try endpoints interactively (Swagger UI). You can fill in request body, press "Execute" button, and see response directly.
- OpenAPI specification available at `http://localhost:8000/openapi.json`. This is useful for:
  - BE/FE integration (generate client with tools like `openapi-generator`/`swagger-codegen`)
  - Import to Postman/Insomnia for automatic request collection

Example fetching OpenAPI JSON:
```bash
curl -s http://localhost:8000/openapi.json | jq '.info, .paths["/chat"]'
```

## Web UI
- Access `http://localhost:8000/web`
- Input stays at bottom of screen, suitable for mobile
- Quick prompt examples available below input

## Data & Seed
- Main tables: `products`, `product_sizes` (stock per size), `orders`, `conversations`.
- Seed automatically creates 16+ products from various categories/brands, stock per size, and sample orders for users like `gilang`, `sela`.

## Architecture Summary
- Intent and extraction (regex/heuristic) in `app/utils.py`.
- Catalog/stock queries in `app/db.py` (SQLAlchemy). Tool answers (database) are formatted and prioritized.
- If not answered by tool, combined prompt (history + tool context) is sent to Ollama via `app/llm.py`.
- Conversation history stored in `conversations` table; number sent to LLM limited by `MAX_HISTORY_MESSAGES`.

## Tool Functions (Summary)
- Order Status Lookup: check status based on `order_id` or user's last order.
- Catalog Lookup: product details, available sizes, stock per size.
- Warranty Info: fixed warranty policy text.

Example order status test payload:
```json
{ "user": "sela", "message": "order status" }
```
Demo users: `adit`, `sela`, `gilang`.

### When Tools Are Used
- Questions requiring precise data: order status, stock per size, size availability, price list, category/brand/size filter → tool is called.
- General questions (how to choose size, care tips, casual model suggestions) → answered directly by LLM (concise, empathetic), without fabricating numbers.

### Demo Users (Seed) for Order Checking
Available sample users: `adit`, `sela`, `gilang`. To check order status/delivery, set the `user` column in payload to match these user names.

Examples:
```bash
curl -s http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"user":"adit","message":"check my order"}'

curl -s http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"user":"sela","message":"order status"}'

# Or directly by order id (user can be anything):
curl -s http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"user":"gilang","message":"check my order"}'
```

Helper endpoint:
- `GET /orders/{user}` → get last order for `adit|sela|gilang`.

### Example Interaction
```json
POST /chat
{
  "user": "gilang",
  "message": "How much stock for Ultraboost 22 size 42?"
}

Response:
{
  "answer": "Ultraboost 22 size 42 stock: 4 pairs. Need help checking colors or similar alternatives?"
}
```

## Development
- API version: see `app/main.py` → `FastAPI(..., version="1.5.0")`.
- Static UI mounted at `/web` with `StaticFiles`.

## Troubleshooting
- Ensure Ollama is running and model is available (`OLLAMA_HOST` is correct). In Docker, `ollama` service automatically exposes `11434`.
- For local MySQL, ensure DSN `mysql+pymysql://...` is valid and user has rights to create tables.
- If seed doesn't appear, delete SQLite file `data/shoe_support.db` and restart, or ensure DB is empty.

## License
See `LICENSE` file.

## Testing
Planned: pytest (TBD). `tests/` folder not yet included.