"""Settings come from the environment (or a secret manager in production). Nothing is hardcoded."""

import os

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "")
DATABASE_URL = os.environ["DATABASE_URL"]
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
ALLOWED_ORIGINS = [o for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o]

APP_DEBUG = os.getenv("APP_DEBUG") == "1"
CACHE_TTL_SECONDS = 3600
LOG_RETENTION_DAYS = 180         # CERT-In: rolling 180 days
MEMORY_RETENTION_DAYS = 90       # chat memories are purged after 90 days
