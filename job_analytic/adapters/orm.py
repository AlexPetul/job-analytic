from sqlalchemy import Column, Integer, String, Table, ForeignKey, MetaData
from sqlalchemy.orm import registry

from job_analytic.domain import models

mapper_registry = registry()
metadata = MetaData()

skill = Table(
    "skill",
    metadata,
    Column("id", Integer, primary_key=True, index=True, autoincrement=True),
    Column("name", String(300), nullable=False)
)

position = Table(
    "position",
    metadata,
    Column("id", Integer, primary_key=True, index=True, autoincrement=True),
    Column("name", String(100), nullable=False)
)

position_skill = Table(
    "position_skill",
    metadata,
    Column("id", Integer, primary_key=True, index=True, autoincrement=True),
    Column("position_id", Integer, ForeignKey("position.id"), index=True),
    Column("skill_id", Integer, ForeignKey("skill.id"), index=True),
    Column("count", Integer),
)


def configure_mappers():
    mapper_registry.map_imperatively(models.Skill, skill)
    mapper_registry.map_imperatively(models.Position, position)
    mapper_registry.map_imperatively(models.PositionSkill, position_skill)
