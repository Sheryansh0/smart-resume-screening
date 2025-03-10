# modules/utils.py
import os

def ensure_upload_folder_exists(upload_folder):
    """Ensure the upload folder exists."""
    os.makedirs(upload_folder, exist_ok=True)