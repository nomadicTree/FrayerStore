class Level:
    def __init__(self, level_id: int, name: str, description: str = None):
        self.level_id = level_id
        self.name = name
        self.description = description
