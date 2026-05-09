# rag-customer-support-chatbot

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black)
![License](https://img.shields.io/badge/license-MIT-green)

A customer support chatbot for a coffee store running locally with FastAPI + Ollama. This project uses a RAG-first architecture (Retrieval-Augmented Generation) where it looks up the database first before refining the answer with the LLM.

![Chatbot UI](assets/chatbot-ui.png)

## 1. Installation & Local Environment Requirements
- Python 3.11 (recommended) and virtual environment
  - macOS/Linux: `python -m venv .venv && source .venv/bin/activate`
  - Windows (PowerShell): `python -m venv .venv; .\\.venv\\Scripts\\Activate.ps1`
- Clone repository
  ```bash
  git clone https://github.com/hidatara-ds/Customer-Support-Chatbot-Project.git
  cd Customer-Support-Chatbot-Project
  ```
- Install dependencies
  ```bash
  pip install -r requirements.txt
  # Or use make
  make install
  ```
- Configure environment
  ```bash
  # Copy example env file
  cp .env.example .env
  # Edit .env with your configuration
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
  # Or use make
  make dev
  
  # API     : http://localhost:8000
  # Docs    : http://localhost:8000/docs (Swagger UI for API testing)
  # OpenAPI : http://localhost:8000/openapi.json (JSON spec for BE/FE)
  # Web UI  : http://localhost:8000/web
  ```
- Optional (bonus): Docker
  ```bash
  docker compose up --build
  # Or use make
  make docker-up
  
  # Services: api + db (MySQL 8) + ollama
  ```

## 2. Architecture Diagram

```mermaid
graph TD
    A[User] -->|Message| B(Intent Detection)
    B -->|Match| C{DB Lookup}
    B -->|No Match| D[LLM]
    C -->|Data Found| E[Tool Context]
    C -->|No Data| D
    E --> D
    D -->|Refined Response| F[Response to User]
```

## 3. Database Design
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

## 4. Libraries and Frameworks Used
- FastAPI: REST API framework
- Uvicorn: ASGI server
- SQLAlchemy: ORM/database access
- PyMySQL: MySQL driver (optional)
- Pydantic: request/response schema validation
- Requests: HTTP client (calling Ollama API)
- python-dotenv: load environment variables
- Ollama: local LLM runtime
- pytest: testing framework
- pytest-cov: test coverage reporting

(See `requirements.txt` for complete list.)

## 5. LLM Model Used
- Llama 3.2 (3B) via Ollama (running locally)
- Reason: lightweight, open-source, and meets challenge requirements for local LLM

## 6. Questions That Can Be Answered
- Order status
  - Examples: "Where is my order?", "status of sela's order", "check order #12"
- Product information
  - Examples: "What are the advantages of Air Max 90?", "details of Ultraboost 22"
- Size availability & stock per size
  - Examples: "How much stock for Ultraboost 22 size 42?", "what sizes are available?"
- Warranty policy
  - Examples: "How do I claim warranty?"
- Note: can be expanded for other questions as needed.

Demo users (seed) for order checking: `alice`, `bob`, `carol`. When testing order status/delivery, set the `user` field in the payload to match these names.

## 7. Tool Calls Available
- Order Status Lookup
  - Chatbot calls external function to check order status based on intent (regex) and/or `order_id` extracted from message. If `order_id` is not available, system uses the last order belonging to `user` in the payload.
  - Standard status output: `processing`, `shipped`, `delivered`, along with product name.
  - Example payload:
    ```json
    { "user": "alice", "message": "order status" }
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
- RAG focus: catalog data from DB, LLM as complement
- Simple web UI at `/web`, configuration via ENV
- Ready-to-use intents: order status, product info, size/stock, warranty
- Comprehensive error handling and logging
- Input validation and security
- Health check endpoint with database status
- Test suite with pytest

## Folder Structure
```bash
app/                    # Main application code
  ├── main.py          # FastAPI app and routes
  ├── db.py            # Database operations
  ├── models.py        # SQLAlchemy models
  ├── schemas.py       # Pydantic schemas
  ├── utils.py         # Utility functions
  ├── config.py        # Configuration
  └── llm.py           # LLM integration
tests/                 # Test suite
  ├── test_api.py      # API endpoint tests
  └── test_utils.py    # Utility function tests
frontend/              # Web UI
  └── index.html
data/                  # Database files
  └── database.mysql.sql
.env.example           # Environment variables template
docker-compose.yml     # Docker services configuration
Dockerfile             # Container image definition
Makefile              # Common commands
pytest.ini            # Test configuration
requirements.txt      # Python dependencies
CONTRIBUTING.md       # Contribution guidelines
```

## Requirements & ENV Summary
- Python 3.11+, Ollama (model `llama3.2:3b`), SQLite (default) / MySQL (optional)
- Main ENV variables:
  - `DATABASE_URL`: Database connection string
  - `OLLAMA_HOST`: Ollama server URL
  - `OLLAMA_MODEL`: LLM model name
  - `MAX_HISTORY_MESSAGES`: Number of messages to keep in context
  - `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)
- Copy `.env.example` to `.env` and configure as needed

## How to Run

### Local Development
```bash
# Install dependencies
make install

# Run development server with auto-reload
make dev

# Or manually
uvicorn app.main:app --reload
```

### Docker
```bash
# Start all services (API, MySQL, Ollama)
make docker-up

# Or manually
docker compose up --build

# Stop services
make docker-down
```

### Access Points
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Web UI: http://localhost:8000/web
- OpenAPI Spec: http://localhost:8000/openapi.json

## Testing

Run tests with:
```bash
# Run all tests
pytest tests/ -v

# Or use make command
make test

# Run with coverage report
make test-cov
```

Test coverage includes:
- API endpoint validation
- Input validation
- Tool function logic
- Error handling

## Available Make Commands
```bash
make install      # Install dependencies
make dev          # Run development server
make test         # Run tests
make test-cov     # Run tests with coverage
make clean        # Clean cache files
make run          # Run production server
make docker-up    # Start Docker containers
make docker-down  # Stop Docker containers
```

## API Endpoints

### Health Check
```bash
GET /health
```
Returns application health status and database connectivity.

### List Products
```bash
GET /products
```
Returns list of all available products.

### Get User Orders
```bash
GET /orders/{user}
```
Returns latest order for specified user.

### Chat Endpoint
```bash
POST /chat
```

Main chat endpoint for customer support interactions.

Request:
```json
{
  "user": "alice",
  "message": "How much stock for size 42 Ultraboost 22?"
}
```

Response:
```json
{
  "answer": "Ultraboost 22 size 42 stock: 4 pairs."
}
```

Example cURL:
```bash
curl -s http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"user":"alice","message":"What types of shoes are available?"}'
```

## API Documentation (Swagger / OpenAPI)
- Open `http://localhost:8000/docs` to try endpoints interactively (Swagger UI)
- OpenAPI specification available at `http://localhost:8000/openapi.json`
- Useful for:
  - BE/FE integration (generate client with tools like `openapi-generator`)
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
- Main tables: `products`, `product_sizes` (stock per size), `orders`, `conversations`
- Seed automatically creates 16+ products from various categories/brands, stock per size, and sample orders for users like `alice`, `bob`

## Architecture Summary
- Intent and extraction (regex/heuristic) in `app/utils.py`
- Catalog/stock queries in `app/db.py` (SQLAlchemy)
- Tool answers (database) are formatted and prioritized
- If not answered by tool, combined prompt (history + tool context) is sent to Ollama via `app/llm.py`
- Conversation history stored in `conversations` table; number sent to LLM limited by `MAX_HISTORY_MESSAGES`
- Comprehensive logging throughout the application
- Error handling with graceful fallbacks

## Tool Functions (Summary)
- Order Status Lookup: check status based on `order_id` or user's last order
- Catalog Lookup: product details, available sizes, stock per size
- Warranty Info: fixed warranty policy text

Example order status test payload:
```json
{ "user": "alice", "message": "order status" }
```
Demo users: `alice`, `bob`, `carol`

### When Tools Are Used
- Questions requiring precise data: order status, stock per size, size availability, price list, category/brand/size filter → tool is called
- General questions (how to choose size, care tips, casual model suggestions) → answered directly by LLM (concise, empathetic), without fabricating numbers

### Demo Users (Seed) for Order Checking
Available sample users: `alice`, `bob`, `carol`. To check order status/delivery, set the `user` column in payload to match these user names.

Examples:
```bash
curl -s http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"user":"alice","message":"check my order"}'

curl -s http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"user":"bob","message":"order status"}'
```

Helper endpoint:
- `GET /orders/{user}` → get last order for `alice|bob|carol`

### Example Interaction
```json
POST /chat
{
  "user": "alice",
  "message": "How much stock for Ultraboost 22 size 42?"
}

Response:
{
  "answer": "Ultraboost 22 size 42 stock: 4 pairs. Need help checking colors or similar alternatives?"
}
```

## Development
- API version: see `app/main.py` → `FastAPI(..., version="1.5.0")`
- Static UI mounted at `/web` with `StaticFiles`
- Logging configured via `LOG_LEVEL` environment variable
- All database operations include error handling

## Troubleshooting
- Ensure Ollama is running and model is available (`OLLAMA_HOST` is correct). In Docker, `ollama` service automatically exposes `11434`
- For local MySQL, ensure DSN `mysql+pymysql://...` is valid and user has rights to create tables
- If seed doesn't appear, delete SQLite file `data/shoe_support.db` and restart, or ensure DB is empty
- Check logs for detailed error messages (set `LOG_LEVEL=DEBUG` for verbose output)
- Use health check endpoint `/health` to verify database connectivity

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License
See `LICENSE` file.

## Improvements in This Version

### Minor Improvements Implemented:
1. **Environment Configuration**: Added `.env.example` for easy setup
2. **Enhanced Error Handling**: Comprehensive error handling throughout the application
3. **Logging**: Structured logging with configurable log levels
4. **Input Validation**: Improved validation with Pydantic schemas
5. **Health Checks**: Enhanced health endpoint with database status
6. **Testing**: Added pytest test suite with coverage reporting
7. **Docker**: Added docker-compose.yml for easy deployment
8. **Documentation**: Added CONTRIBUTING.md and improved README
9. **Developer Tools**: Added Makefile for common commands
10. **Code Quality**: Better code organization and documentation

### What's New:
- `.env.example` - Environment configuration template
- `docker-compose.yml` - Multi-service Docker setup
- `tests/` - Test suite with pytest
- `Makefile` - Common development commands
- `CONTRIBUTING.md` - Contribution guidelines
- `pytest.ini` - Test configuration
- Enhanced logging throughout the application
- Better error messages and handling
- Improved code documentation
