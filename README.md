Customer Support Chatbot Project Setup (FastAPI + Local LLM)

This document outlines the initial setup for a customer support chatbot project, using FastAPI (Python 3.11) and a local LLM model (llama3.2:3B) run via Ollama. The project is structured based on principles from the ai-task-analyst repository and fulfills the requirements (from the PT Synapsis challenge) for answering at least three types of questions: order status, product advantages, and warranty claims. It also implements conversation memory, a simple tool-calling mechanism, and is containerized with Docker for deployment.

Project Structure

The project follows a modular structure, separating concerns for clarity and maintainability. Below is an example folder tree:

customer-support-chatbot/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application initialization and routes
│   ├── db.py            # Database connection and helper functions (SQLite usage)
│   ├── llm.py           # LLM integration (Ollama client or LangChain interface)
│   └── utils.py         # Tool functions (e.g., check order status, fetch product info)
├── data/
│   └── database.sql     # SQL script for database schema and dummy data
├── Dockerfile           # Dockerfile for containerizing the app
└── README.md            # Documentation in English


app/main.py: Creates the FastAPI app and defines REST endpoints (e.g., a /chat endpoint for chatbot interaction).

app/db.py: Manages the SQL database connection. For simplicity, using SQLite with Python's sqlite3 or an ORM (like SQLAlchemy) to execute queries and store conversation history.

app/llm.py: Handles calls to the local LLM. It could use the Ollama REST API or a LangChain wrapper to generate responses from the llama3.2:3B model.

app/utils.py: Contains utility functions, including tool functions such as checking order status by querying the orders table (to demonstrate tool calling capability).

data/database.sql: SQL script to set up the initial database schema (products, orders, conversations tables) with some dummy data for a coffee store scenario.

Dockerfile: Instructions to build a Docker image with the FastAPI app and its dependencies (running on Uvicorn). This enables easy deployment in a container environment (single-container deployment without Compose).

README.md: Documentation covering installation, setup, and usage instructions, as well as explanations of the system design (as required by the challenge).

