import enum
from typing import Type

from sqlalchemy import Enum


def pg_enum(enum_cls: Type[enum.Enum], name: str) -> Enum:
    """Map Python enums to PostgreSQL enum values (lowercase), not member names."""
    return Enum(
        enum_cls,
        name=name,
        values_callable=lambda x: [e.value for e in x],
    )
