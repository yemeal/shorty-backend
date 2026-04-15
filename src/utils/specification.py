from __future__ import annotations

"""
TODO (архитектура): ввести порт ``SpecificationPort`` / ``PredicateSpec`` (Protocol) с методом ``apply``,
чтобы ``AbstractAsyncRepository`` и сервисы зависели от абстракции, а текущий класс ``Specification``
стал SQLAlchemy-совместимой реализацией. Сейчас контракт «предикаты + apply(where)» зашит в конкретный тип.
"""

from typing import Any, Protocol, Self


class SupportsWhere(Protocol):
    """SQLAlchemy statements that accept ``.where(...)`` (``Select``, ``Delete``, ``Update``, etc.)."""

    def where(self, *clauses: Any) -> Self: ...


class Specification:
    """
    Boolean predicates for repository queries and deletes.

    **At least one** expression is required so we never build ``SELECT``/``DELETE`` without a
    ``WHERE`` clause (accidental full-table scans or wipes).
    """

    __slots__ = ("_expressions",)

    def __init__(self, *expressions: Any):
        if not expressions:
            raise ValueError(
                "Specification requires at least one predicate; "
                "refuse unbounded SELECT/DELETE (no WHERE)."
            )
        self._expressions = expressions

    def apply[T: SupportsWhere](self, stmt: T) -> T:
        """Narrow ``stmt`` with stored predicates; preserves the concrete statement type."""
        return stmt.where(*self._expressions)
