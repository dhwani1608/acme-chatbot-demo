from pydantic import BaseModel


class SignupRequest(BaseModel):
    """PAN removed: a chatbot doesn't need it (data minimisation)."""
    name: str
    email: str
    phone: str
    password: str
    consent_given: bool
    consent_notice_version: str
    consent_purpose: str = "chat-assistant"


class ChatRequest(BaseModel):
    message: str
