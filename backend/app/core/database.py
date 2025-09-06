from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from app.models.email import Base

DATABASE_URL = os.getenv('DATABASE_URL','sqlite:///./emails.db')
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
