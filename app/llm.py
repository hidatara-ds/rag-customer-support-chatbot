# app/llm.py
from __future__ import annotations
import os, json, requests

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

def _ollama(payload: dict) -> str:
    url = f"{OLLAMA_HOST}/api/generate"
    r = requests.post(url, json=payload, timeout=120)
    r.raise_for_status()
    # /api/generate streams lines; but when run with "stream": False it returns one json
    data = r.json()
    return data.get("response", "").strip()

def generate_answer(prompt: str, temperature: float = 0.3, top_p: float = 0.9) -> str:
    return _ollama({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": top_p,
            "num_ctx": 4096,
            "repeat_penalty": 1.05,
        },
    })

def refine_answer(user_msg: str, base_answer: str, tool_struct: dict | None = None) -> str:
    """
    Humanize base_answer (yang berasal dari DB) tanpa mengubah fakta.
    Jangan menambah angka/item yang tidak ada di tool_struct/base_answer.
    """
    sys = (
        "Kamu adalah asisten CS toko sepatu yang ramah, singkat, dan natural (Bahasa Indonesia). "
        "TUGAS: Rapikan dan manusiawikan jawaban yang sudah disiapkan (base_answer) "
        "tanpa mengubah fakta, angka, ukuran, atau harga. "
        "Jika ada daftar panjang, tampilkan maksimal 4 poin teratas lalu sebutkan kalau masih ada lagi. "
        "Selalu akhiri dengan SATU pertanyaan tindak lanjut yang relevan. "
        "Jangan mengarang data. Jika informasi kosong/kurang, minta detail singkat."
    )
    tool_json = json.dumps(tool_struct or {}, ensure_ascii=False, indent=2)
    prompt = (
        f"{sys}\n\n"
        f"USER: {user_msg}\n\n"
        f"TOOL_DATA (boleh diringkas, jangan diubah faktanya):\n{tool_json}\n\n"
        f"BASE_ANSWER (harus dipertahankan faktanya):\n{base_answer}\n\n"
        "TULIS JAWABAN AKHIR:"
    )
    return generate_answer(prompt, temperature=0.2, top_p=0.95)
