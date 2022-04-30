from pydantic import BaseModel


class Position(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class PositionSkill(BaseModel):
    name: str
    count: int

    class Config:
        orm_mode = True
