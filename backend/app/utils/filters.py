from typing import Any

from sqlalchemy import Select, or_


def apply_search(stmt: Select, columns: list[Any], search: str | None) -> Select:
    if not search or not search.strip():
        return stmt
    term = f"%{search.strip()}%"
    return stmt.where(or_(*[col.ilike(term) for col in columns]))
