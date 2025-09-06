from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class EmailCreate(BaseModel):
    provider_id: Optional[str]
    sender: str
    subject: str
    body: str

class EmailOut(BaseModel):
    id: int
    provider_id: Optional[str]
    sender: str
    subject: str
    body: str
    received_date: Optional[datetime]
    sentiment: Optional[str]
    priority: Optional[str]
    ai_response: Optional[str]
    processed: int
    confidence: float
    phone: Optional[str]
    alt_email: Optional[str]
    product_mentions: Optional[str]

    class Config:
        orm_mode = True
