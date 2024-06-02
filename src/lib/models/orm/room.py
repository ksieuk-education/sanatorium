# pylint: disable=unsubscriptable-object
"""Описание таблиц для номеров в санатории"""

import uuid

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

import lib.models.orm.base as _models_orm_base


class Room(_models_orm_base.Base, _models_orm_base.IdCreatedUpdatedBaseMixin):
    """Модель для описания полей в таблице Room"""

    room_number: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.Integer, nullable=False, unique=True)
    capacity: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.Integer, nullable=False)
    type_id: sa_orm.Mapped[uuid.UUID] = sa_orm.mapped_column(sa.ForeignKey("content.room_type.id"), nullable=False)

    @sa_orm.declared_attr
    @classmethod
    def type(cls) -> sa_orm.Mapped["RoomType"]:  # noqa: A003
        return sa_orm.relationship(
            "RoomType",
            passive_deletes=True,
            uselist=False,
        )


class RoomType(_models_orm_base.Base, _models_orm_base.IdCreatedUpdatedBaseMixin):
    """Модель для описания полей в таблице RoomType"""

    @sa_orm.declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:  # pylint: disable=arguments-differ
        """Название таблицы"""

        return "room_type"

    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(255), nullable=False)
    description: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(255), nullable=False)
