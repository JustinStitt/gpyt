from pydantic import BaseModel


class Message(BaseModel):
    id: str
    role: str
    content: str


class Conversation(BaseModel):
    id: str
    summary: str
    log: list[Message]
