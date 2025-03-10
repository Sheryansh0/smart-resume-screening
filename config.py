# config.py
import os

class Config:
    SECRET_KEY = "your_secret_key"
    UPLOAD_FOLDER = "uploads"
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL_ADDRESS = "naninalli02@gmail.com"
    EMAIL_PASSWORD = "yjmlyaycgytaewdh"

# Ensure 'uploads' folder exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

