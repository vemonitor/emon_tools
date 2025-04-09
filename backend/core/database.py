"""Initialise the database connection."""
from sqlmodel import create_engine
from backend.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
