"""
Базовая заготовка для таблиц sqlalchemy
"""

import typing

import sqlalchemy.ext.declarative
import sqlalchemy.orm as sa_orm


class Base(sa_orm.DeclarativeBase):
    """Base class for all models."""

    @sqlalchemy.ext.declarative.declared_attr.directive
    def __tablename__(cls) -> str:  # pylint: disable=no-self-argument  # noqa: N805
        """Название таблицы"""

        return cls.__name__.lower()

    __mapper_args__ = {"eager_defaults": True}  # noqa: RUF012
    __table_args__ = {"schema": "app"}  # noqa: RUF012

    def as_dict(self) -> dict[str, typing.Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
