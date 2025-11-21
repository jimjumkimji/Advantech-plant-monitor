# app/dropbox/client.py
import dropbox
from backend.dropbox import env

def get_client() -> dropbox.Dropbox:
    """
    สร้าง Dropbox client จาก access token ใน .env
    """
    dbx = dropbox.Dropbox(env.DROPBOX_TOKEN)
    return dbx
