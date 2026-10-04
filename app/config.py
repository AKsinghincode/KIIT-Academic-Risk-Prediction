import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DATABASE_PATH = os.environ.get(
        'DATABASE_PATH', 
        os.path.join(os.path.abspath(os.path.dirname(__file__)), '../instance/database.sqlite')
    )