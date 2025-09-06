from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.email import Email
from app.schemas import EmailCreate, EmailOut
from app.services.email_service import EmailService
from app.services.ai_service import AIService
from typing import List
from rq import Queue
from redis import Redis
import os

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post('/fetch')
async def fetch_emails(max_results: int = 20, db: Session = Depends(get_db)):
    svc = EmailService()
    items = svc.fetch_imap(max_results=max_results) or []
    # filter support emails
    items = svc.filter_support(items)
    created = 0
    for it in items:
        # save to DB
        e = Email(provider_id=it.get('provider_id'), sender=it.get('sender'), subject=it.get('subject'), body=it.get('body'))
        info = svc.extract_info(it.get('body',''))
        e.phone = info.get('phone')
        e.alt_email = info.get('alt_email')
        e.product_mentions = info.get('product_mentions')
        db.add(e)
        db.commit()
        db.refresh(e)
        created += 1
    return {'fetched': created}

@router.get('', response_model=List[EmailOut])
async def list_emails(db: Session = Depends(get_db)):
    rows = db.query(Email).order_by(Email.processed.asc(), Email.priority.desc(), Email.received_date.desc()).all()
    return rows

@router.post('/process')
async def process_emails(db: Session = Depends(get_db)):
    # enqueue all unprocessed into RQ with priority handling (urgent first)
    redis_url = os.getenv('REDIS_URL','redis://localhost:6379/0')
    redis_conn = Redis.from_url(redis_url)
    q = Queue('emails', connection=redis_conn)
    unprocessed = db.query(Email).filter(Email.processed == 0).all()
    count = 0
    for e in unprocessed:
        # priority param to worker defined by priority string mapping
        priority_score = 0
        if e.priority == 'urgent': priority_score = 0
        elif e.priority == 'high': priority_score = 5
        else: priority_score = 10
        # enqueue job
        q.enqueue('app.worker.process_email_task', e.id, job_timeout=300, at_front=(priority_score==0))
        count += 1
    return {'enqueued': count}
