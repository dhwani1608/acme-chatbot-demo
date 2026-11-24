from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, create_engine, func
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)
    password_hash = Column(String)
    consent_given = Column(Boolean, nullable=False)
    consent_notice_version = Column(String, nullable=False)
    consented_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())


class Memory(Base):
    """Chat history embedded for retrieval. Stored redacted."""
    __tablename__ = "memories"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    content = Column(Text)
    embedding = Column(Vector(768))
    created_at = Column(DateTime, server_default=func.now())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
