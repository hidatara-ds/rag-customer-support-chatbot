import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/shoe_support.db")

# Ollama Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

# Application Configuration
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "6"))
MEMORY_TURNS = MAX_HISTORY_MESSAGES // 2  # Number of Q&A pairs
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# API Configuration
API_TITLE = os.getenv("API_TITLE", "Customer Support Chatbot")
API_VERSION = os.getenv("API_VERSION", "1.5.0")
