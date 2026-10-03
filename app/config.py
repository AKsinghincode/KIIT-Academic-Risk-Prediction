import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'edurisk_dev_secret_key_2026'
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'edurisk.db')
