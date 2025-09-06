from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Email(Base):
    __tablename__ = 'emails'
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(String, index=True, nullable=True)
    sender = Column(String, index=True)
    subject = Column(String, index=True)
    body = Column(Text)
    received_date = Column(DateTime(timezone=True), server_default=func.now())
    sentiment = Column(String, nullable=True)
    priority = Column(String, nullable=True)
    ai_response = Column(Text, nullable=True)
    processed = Column(Integer, default=0)
    confidence = Column(Float, default=0.0)
    phone = Column(String, nullable=True)
    alt_email = Column(String, nullable=True)
    product_mentions = Column(String, nullable=True)
