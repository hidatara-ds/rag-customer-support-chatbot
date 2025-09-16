import os

# DB:
# MySQL:  mysql+pymysql://user:password@127.0.0.1:3306/shoe_support
# SQLite: sqlite:///./data/shoe_support.db
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/shoe_support.db")

# Ollama
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

# History di DB: unlimited
# Batas pesan yang dikirim ke LLM (agar prompt tidak kepanjangan)
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "30"))
