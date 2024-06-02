"""
Базовая заготовка для таблиц sqlalchemy
"""

import datetime
import typing
import uuid

import sqlalchemy.ext.declarative
import sqlalchemy.orm as sa_orm
import sqlalchemy.sql as sa_sql


class Base(sa_orm.DeclarativeBase):
    """Base class for all models."""

    @sqlalchemy.ext.declarative.declared_attr.directive
    def __tablename__(cls) -> str:  # pylint: disable=no-self-argument  # noqa: N805
        """Название таблицы"""

        return cls.__name__.lower()

    __mapper_args__ = {"eager_defaults": True}  # noqa: RUF012
    __table_args__ = {"schema": "content"}  # noqa: RUF012

    def as_dict(self, exclude_none: bool = False) -> dict[str, typing.Any]:  # noqa: FBT001, FBT002
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if not exclude_none or getattr(self, c.name) is not None
        }


class IdCreatedUpdatedBaseMixin:
    """
    Mixin class that provides common fields for primary key ID and timestamp fields for creation and last update times.
    """

    id: sa_orm.Mapped[uuid.UUID] = sa_orm.mapped_column(primary_key=True, default=uuid.uuid4)  # noqa: A003
    created_at: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        server_default=sa_sql.func.now()  # pylint: disable=not-callable
    )
    updated_at: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        default=None,
        onupdate=sa_sql.func.now(),  # pylint: disable=not-callable
        nullable=True,
    )
