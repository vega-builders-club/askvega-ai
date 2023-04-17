# Response Schema

from pydantic import BaseModel, validator


class ChatResponse(BaseModel):
    sender: str
    message: str
    type: str

    @validator("sender")
    def validate_sender(cls, v):
        if v not in ["bot", "you"]:
            raise ValueError("Invalid message sender")
        return v

    @validator("type")
    def validate_message_type(cls, v):
        if v not in ["start", "stream", "end", "error", "info"]:
            raise ValueError("Invalid message type provided")
        return v
