import os
import sqlite3
from flask import current_app, g

def get_db():
    if 'db' not in g:
        # Default to /tmp for Render cloud write permissions
        db_path = current_app.config.get('DATABASE_PATH') or '/tmp/database.sqlite'
        
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()