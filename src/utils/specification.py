from sqlalchemy.sql import Select


class Specification[ModelType]:
    def __init__(self, *expressions):
        self._expressions = expressions

    def apply(self, stmt: Select) -> Select:
        stmt = stmt.where(*self._expressions)
        return stmt
