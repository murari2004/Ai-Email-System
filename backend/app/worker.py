# RQ worker tasks to process emails
from app.core.database import SessionLocal
from app.models.email import Email
from app.services.ai_service import AIService

def process_email_task(email_id: int):
    db = SessionLocal()
    try:
        e = db.query(Email).filter(Email.id==email_id).first()
        if not e:
            return False
        ai = AIService()
        sentiment, conf = ai.analyze_sentiment(e.body or '')
        priority = ai.classify_priority(e.subject or '', e.body or '', sentiment)
        resp = ai.generate_response({'subject': e.subject, 'body': e.body, 'sender': e.sender})
        e.sentiment = sentiment
        e.confidence = conf
        e.priority = priority
        e.ai_response = resp.get('response')
        e.processed = 1
        db.add(e)
        db.commit()
        return True
    finally:
        db.close()
