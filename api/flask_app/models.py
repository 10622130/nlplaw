# models.py
from sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from core.models.base import User, UserInput
