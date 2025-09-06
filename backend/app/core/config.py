import os
IMAP_HOST = os.getenv('IMAP_HOST','')
IMAP_USER = os.getenv('IMAP_USER','')
IMAP_PASS = os.getenv('IMAP_PASS','')
DATABASE_URL = os.getenv('DATABASE_URL','sqlite:///./emails.db')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY','')
REDIS_URL = os.getenv('REDIS_URL','redis://localhost:6379/0')
