"""Demo RAG chatbot — the fixed version of ../demo-app."""

import logging

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from .auth import get_current_user
from .cache import cache_profile, forget_profile
from .config import ALLOWED_ORIGINS, APP_DEBUG
from .db import Base, Memory, User, engine, get_db
from .llm import ask, embed, welcome_sms
from .logging_setup import configure_logging
from .privacy import hash_password, redact_pii
from .schemas import ChatRequest, SignupRequest

configure_logging()
logger = logging.getLogger("demo")

app = FastAPI(debug=APP_DEBUG)
app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_methods=["GET", "POST", "DELETE"])


@app.on_event("startup")
def create_tables():
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(engine)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    logger.info("request %s %s -> %s", request.method, request.url.path, response.status_code)
    return response


@app.post("/signup")
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    if not req.consent_given:
        raise HTTPException(400, "consent is required")
    user = User(name=req.name, email=req.email, phone=req.phone, password_hash=hash_password(req.password),
                consent_given=True, consent_notice_version=req.consent_notice_version)
    db.add(user)
    db.commit()
    cache_profile(user.id, redact_pii(req.name))
    logger.info("new signup user_id=%s", user.id)
    return {"id": user.id, "welcome": welcome_sms(req.name, req.phone)}


@app.post("/chat")
def chat(req: ChatRequest, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    message = redact_pii(req.message)
    vector = embed(message)
    rows = db.execute(
        text("SELECT content FROM memories WHERE user_id = :uid ORDER BY embedding <-> CAST(:v AS vector) LIMIT 3"),
        {"uid": user_id, "v": str(vector)},
    ).fetchall()
    context = "\n".join(r.content for r in rows)
    answer = ask(f"Context:\n{context}\nUser: {message}")
    db.add(Memory(user_id=user_id, content=message, embedding=vector))
    db.commit()
    return {"answer": answer}


@app.get("/users/search")
def search_users(email: str, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT id, name FROM users WHERE email = :email"), {"email": email}).fetchall()
    return [{"id": r.id, "name": r.name} for r in rows]


@app.delete("/users/{user_id}")
def delete_user(user_id: int, caller: int = Depends(get_current_user), db: Session = Depends(get_db)):
    if caller != user_id:
        raise HTTPException(403, "can only delete your own account")
    # Erase from every store that holds this user's data.
    db.execute(text("DELETE FROM memories WHERE user_id = :id"), {"id": user_id})   # pgvector embeddings
    db.execute(text("DELETE FROM users WHERE id = :id"), {"id": user_id})           # account row
    db.commit()
    forget_profile(user_id)                                                          # Redis profile
    logger.info("erased user_id=%s", user_id)
    return {"deleted": user_id}


def purge_old_memories(db: Session):
    """Scheduled daily (Cloud Scheduler -> Cloud Run Job): storage limitation for chat history."""
    db.execute(text("DELETE FROM memories WHERE created_at < now() - interval '90 days'"))
    db.commit()
