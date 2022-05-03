from pydantic import BaseModel


class Position(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class PositionSkill(BaseModel):
    position_id: int
    count: int

    class Config:
        orm_mode = True
