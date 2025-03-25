from pydantic import BaseModel

class MessageCreate(BaseModel):
    recipient_id: str
    content: str