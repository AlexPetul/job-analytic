class Skill:
    def __init__(self, name: str):
        self.name = name


class Position:
    def __init__(self, name: str):
        self.name = name


class PositionSkill:
    def __init__(self, skill_id: int, position_id: int, count: int = 1):
        self.skill_id = skill_id
        self.position_id = position_id
        self.count = count
