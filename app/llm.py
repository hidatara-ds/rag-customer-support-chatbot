import requests
import logging
from .config import OLLAMA_HOST, OLLAMA_MODEL

logger = logging.getLogger(__name__)

def generate_answer(prompt: str, temperature: float = 0.2, max_tokens: int = 256) -> str:
    """
    Refines a DB-sourced answer into natural language without altering facts, numbers, or prices.
    Call Ollama local API to generate an answer.
    
    Args:
        prompt: The prompt to send to the LLM
        temperature: Controls randomness (0.0-1.0)
        max_tokens: Maximum tokens to generate
        
    Returns:
        Generated response text
        
    Raises:
        Exception: If Ollama API call fails
    """
    try:
        url = f"{OLLAMA_HOST}/api/generate"
        # Indonesian market — by design
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            },
            "stream": False
        }
        
        logger.debug(f"Calling Ollama API at {url}")
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        
        data = r.json()
        response = data.get("response", "").strip()
        
        if not response:
            logger.warning("Ollama returned empty response")
            return "I apologize, but I'm having trouble generating a response. Please try again."
        
        logger.debug(f"Ollama response length: {len(response)} chars")
        return response
        
    except requests.exceptions.Timeout:
        logger.error("Ollama API request timed out")
        return "I apologize, but the request is taking too long. Please try again."
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to Ollama at {OLLAMA_HOST}")
        return "I apologize, but I'm having trouble connecting to the AI service. Please ensure Ollama is running."
    except Exception as e:
        logger.error(f"Ollama API error: {e}", exc_info=True)
        return "I apologize, but I encountered an error. Please try again later."
