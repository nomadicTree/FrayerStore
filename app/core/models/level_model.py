class Level:
    def __init__(self, level_id: int, name: str, description: str = None):
        self.level_id = level_id
        self.name = name
        self.description = description

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Level):
            return NotImplemented
        return self.level_id == other.level_id

    def __hash__(self) -> int:
        return hash(self.level_id)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Level):
            return NotImplemented
        return self.name < other.name

    @property
    def pk(self):
        return self.level_id
