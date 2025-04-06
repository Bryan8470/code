# File: db/__init__.py
from flask_sqlalchemy import SQLAlchemy

# Export db as a global variable for clarity
db = SQLAlchemy()