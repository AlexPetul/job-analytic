from pydantic import BaseModel


class PositionSkill(BaseModel):
    name: str
    count: int

    class Config:
        orm_mode = True
