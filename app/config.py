import os
from dotenv import load_dotenv

# Laden der .env-Datei
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    REDIRECT_URI = os.getenv('REDIRECT_URI')
