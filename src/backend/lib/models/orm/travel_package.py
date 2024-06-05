# pylint: disable=unsubscriptable-object
"""Описание таблиц, связанных с путевками в санаторий"""

import uuid

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

import lib.models.orm.base as _models_orm_base


class TravelPackage(_models_orm_base.Base, _models_orm_base.IdCreatedUpdatedBaseMixin):
    """Модель для описания полей в таблице TravelPackage"""

    @sa_orm.declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:  # pylint: disable=arguments-differ
        """Название таблицы"""

        return "travel_package"

    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(255), nullable=False)
    description: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(255), nullable=False)
    room_type_id: sa_orm.Mapped[uuid.UUID] = sa_orm.mapped_column(sa.ForeignKey("content.room_type.id"), nullable=False)
    dining_type_id: sa_orm.Mapped[uuid.UUID] = sa_orm.mapped_column(
        sa.ForeignKey("content.dining_type.id"), nullable=False
    )

    @sa_orm.declared_attr
    @classmethod
    def room_type(cls) -> sa_orm.Mapped["RoomType"]:  # type: ignore[reportUndefinedVariable]  # noqa: F821
        return sa_orm.relationship(
            "RoomType",
            passive_deletes=True,
            uselist=False,
        )

    @sa_orm.declared_attr
    @classmethod
    def dining_type(cls) -> sa_orm.Mapped["DiningType"]:  # type: ignore[reportUndefinedVariable]  # noqa: F821
        return sa_orm.relationship(
            "DiningType",
            passive_deletes=True,
            uselist=False,
        )

    def __repr__(self):
        return self.name
