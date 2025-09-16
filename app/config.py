import os

# DB:
# - Untuk MySQL:  mysql+pymysql://user:password@127.0.0.1:3306/shoe_support
# - Untuk SQLite: sqlite:///./data/shoe_support.db
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/shoe_support.db")

# Ollama
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

# Memory:
# - Disimpan di DB: unlimited
# - Yang dikirim ke LLM: batasi agar prompt tidak terlalu panjang (bisa diubah via env)
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))  # total pesan (user+assistant)
