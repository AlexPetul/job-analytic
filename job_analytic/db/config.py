from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from job_analytic.core.settings import settings


SQLALCHEMY_DATABASE_URL = URL.create(
    drivername="postgresql",
    host=settings["DATABASE"]["Host"],
    username=settings["DATABASE"]["Username"],
    password=settings["DATABASE"]["Password"],
    database=settings["DATABASE"]["Name"],
)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
