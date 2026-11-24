import hashlib
import os

from google import genai

from .config import GEMINI_API_KEY, GEMINI_MODEL
from .privacy import redact_pii

client = genai.Client(api_key=GEMINI_API_KEY)
OFFLINE = os.getenv("DEMO_OFFLINE") == "1"  # run the demo without calling Gemini


def _fake_embedding(text: str) -> list[float]:
    digest = hashlib.sha256(text.encode()).digest()
    return [digest[i % 32] / 255 for i in range(768)]


def ask(prompt: str) -> str:
    if OFFLINE:
        return "(offline demo answer)"
    response = client.models.generate_content(model=GEMINI_MODEL, contents=redact_pii(prompt))
    return response.text


def embed(text: str) -> list[float]:
    if OFFLINE:
        return _fake_embedding(text)
    result = client.models.embed_content(model="text-embedding-004", contents=redact_pii(text))
    return result.embeddings[0].values
