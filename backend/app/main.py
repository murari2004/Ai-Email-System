import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.database import init_db
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="AI Email Assistant - Backend (Complete)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(api_router, prefix='/api/v1')

@app.on_event('startup')
async def startup():
    init_db()

@app.get('/')
async def root():
    return {'message': 'AI Email Assistant Backend Running'}
