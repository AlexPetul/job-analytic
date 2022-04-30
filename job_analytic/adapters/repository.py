import abc
from typing import List

from sqlalchemy import update, desc

from job_analytic.domain import models


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add_skill(self, skill: models.Skill):
        raise NotImplementedError

    @abc.abstractmethod
    def get_skill(self, id: int) -> models.Skill:
        raise NotImplementedError

    @abc.abstractmethod
    def add_position(self, position: models.Position):
        raise NotImplementedError

    @abc.abstractmethod
    def get_position(self, name: str) -> models.Position:
        raise NotImplementedError

    @abc.abstractmethod
    def get_positions(self) -> List[models.Position]:
        raise NotImplementedError

    @abc.abstractmethod
    def list_positions(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_or_create_skill(self, name: str):
        raise NotImplementedError

    @abc.abstractmethod
    def get_position_skills(self, name: str):
        raise NotImplementedError

    @abc.abstractmethod
    def add_position_skill(self, position_skill: models.PositionSkill):
        raise NotImplementedError

    @abc.abstractmethod
    def position_skill_exists(self, position: models.Position, skill: models.Skill):
        raise NotImplementedError

    @abc.abstractmethod
    def update_position_skill(self, position_skill: models.PositionSkill):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):

    def __init__(self, session):
        self.session = session

    def add_skill(self, skill: models.Skill):
        self.session.add(skill)
        self.session.commit()
        self.session.refresh(skill)

    def get_skill(self, id: int) -> models.Skill:
        return self.session.query(models.Skill).get(id)

    def add_position(self, position: models.Position):
        self.session.add(position)

    def get_position(self, name: str) -> models.Position:
        return self.session.query(models.Position).filter(models.Position.name == name).first()

    def get_positions(self) -> List[models.Position]:
        return self.session.query(models.Position).all()

    def list_positions(self) -> List[models.Position]:
        return self.session.query(models.Position).offset(0).all()

    def add_position_skill(self, position_skill: models.PositionSkill):
        self.session.add(position_skill)
        self.session.commit()
        self.session.refresh(position_skill)

    def get_position_skills(self, name: str):
        return self.session.query(models.PositionSkill.count, models.Skill.name)\
            .join(models.Skill)\
            .join(models.Position)\
            .filter(models.Position.name == name)\
            .order_by(desc(models.PositionSkill.count))\
            .all()

    def get_or_create_skill(self, name: str):
        existing_obj = self.session.query(models.Skill).filter_by(name=name).first()
        if existing_obj is not None:
            return existing_obj
        else:
            new_skill = models.Skill(name=name)
            self.add_skill(new_skill)
            return new_skill

    def position_skill_exists(self, position: models.Position, skill: models.Skill):
        return self.session\
            .query(models.PositionSkill)\
            .filter_by(position_id=position.id, skill_id=skill.id)\
            .first()

    def update_position_skill(self, position_skill: models.PositionSkill):
        position_skill.count += 1
        self.session.add(position_skill)
        self.session.commit()
        self.session.refresh(position_skill)
