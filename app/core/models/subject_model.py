class Subject:
    def __init__(self, subject_id: int, name: str):
        self.subject_id = subject_id
        self.name = name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Subject):
            return NotImplemented
        return self.subject_id == other.subject_id

    def __hash__(self) -> int:
        return hash(self.subject_id)

    @property
    def pk(self):
        return self.subject_id
