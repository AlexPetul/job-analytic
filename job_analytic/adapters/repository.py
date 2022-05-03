import abc
from typing import List

from sqlalchemy import desc, join, select

from domain import models


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    async def get_position(self, name: str) -> models.Position:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_positions(self) -> List[models.Position]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_or_create_skill(self, name: str):
        raise NotImplementedError

    @abc.abstractmethod
    async def get_position_skills(self, name: str):
        raise NotImplementedError

    @abc.abstractmethod
    async def add_position_skill(self, position_skill: models.PositionSkill):
        raise NotImplementedError

    @abc.abstractmethod
    async def position_skill_exists(self, position: models.Position, skill: models.Skill):
        raise NotImplementedError

    @abc.abstractmethod
    async def update_position_skill(self, position_skill: models.PositionSkill):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    async def get_position(self, name: str) -> models.Position:
        return await self.session.execute(select(models.Position).where(models.Position.name == name)).first()

    async def get_positions(self) -> List[models.Position]:
        result = await self.session.execute(select(models.Position))
        return result.scalars().all()

    async def add_position_skill(self, position_skill: models.PositionSkill):
        self.session.add(position_skill)
        await self.session.commit()
        await self.session.refresh(position_skill)

    async def get_position_skills(self, name: str):
        p_join = join(models.PositionSkill, models.Position, models.PositionSkill.position_id == models.Position.id)
        result = await self.session.execute(
            select(models.PositionSkill)
            .select_from(p_join)
            .filter(models.Position.name == name)
            .order_by(desc(models.PositionSkill.count))
        )
        return result.scalars().all()

    async def get_or_create_skill(self, name: str):
        existing_obj = await self.session.execute(select(models.Skill).where(models.Skill.name == name)).first()
        if existing_obj is not None:
            return existing_obj
        else:
            new_skill = models.Skill(name=name)
            self.session.add(new_skill)
            await self.session.commit()
            await self.session.refresh(new_skill)
            return new_skill

    async def position_skill_exists(self, position: models.Position, skill: models.Skill):
        return await self.session.execute(
            select(models.PositionSkill).where(
                models.PositionSkill.position_id == position.id and models.PositionSkill.skill_id == skill.id
            )
        ).first()

    async def update_position_skill(self, position_skill: models.PositionSkill):
        position_skill.count += 1
        self.session.add(position_skill)
        await self.session.commit()
        await self.session.refresh(position_skill)
