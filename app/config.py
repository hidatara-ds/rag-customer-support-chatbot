import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/coffee_support.db")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
MEMORY_TURNS = int(os.getenv("MEMORY_TURNS", "3"))
