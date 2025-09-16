import os

# --- Environment ---
# MySQL contoh: mysql+pymysql://user:password@localhost:3306/coffee_support
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/coffee_support")

# Ollama server (lokal)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
# Model sesuai challenge
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

# Memory: jumlah interaksi (Q/A) yang diingat
MEMORY_TURNS = int(os.getenv("MEMORY_TURNS", "3"))
