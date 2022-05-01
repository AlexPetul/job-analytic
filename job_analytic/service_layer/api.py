from job_analytic.adapters.repository import SQLAlchemyRepository
from job_analytic.db.config import SessionLocal


def get_report(position_name: str):
    db = SessionLocal()
    repository = SQLAlchemyRepository(db)
    return repository.get_position_skills(position_name)


def get_positions():
    db = SessionLocal()
    repository = SQLAlchemyRepository(db)
    return repository.get_positions()
