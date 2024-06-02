# pylint: disable=unsubscriptable-object
"""Описание таблиц, связанных с регистрацией пользователей"""

import datetime
import uuid

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

import lib.models.orm.base as _models_orm_base


class Registration(_models_orm_base.Base, _models_orm_base.IdCreatedUpdatedBaseMixin):
    """Модель для описания полей в таблице Registration"""

    user_id: sa_orm.Mapped[uuid.UUID] = sa_orm.mapped_column(sa.ForeignKey("content.user.id"), nullable=False)
    room_id: sa_orm.Mapped[uuid.UUID] = sa_orm.mapped_column(sa.ForeignKey("content.room.id"), nullable=False)
    dining_table_id: sa_orm.Mapped[uuid.UUID] = sa_orm.mapped_column(
        sa.ForeignKey("content.dining_table.id"), nullable=False
    )
    physician_id: sa_orm.Mapped[uuid.UUID] = sa_orm.mapped_column(sa.ForeignKey("content.physician.id"), nullable=False)
    travel_package_id: sa_orm.Mapped[uuid.UUID] = sa_orm.mapped_column(
        sa.ForeignKey("content.travel_package.id"), nullable=False
    )
    check_in_date: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(sa.DateTime, nullable=False)
    check_out_date: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(sa.DateTime, nullable=False)

    @sa_orm.declared_attr
    @classmethod
    def user(cls) -> sa_orm.Mapped["User"]:  # type: ignore[reportUndefinedVariable]  # noqa: F821
        return sa_orm.relationship(
            "User",
            back_populates="registration",
            cascade="all, delete",
            passive_deletes=True,
            uselist=False,
        )

    @sa_orm.declared_attr
    @classmethod
    def room(cls) -> sa_orm.Mapped["Room"]:  # type: ignore[reportUndefinedVariable]  # noqa: F821
        return sa_orm.relationship(
            "Room",
            passive_deletes=True,
            uselist=False,
        )

    @sa_orm.declared_attr
    @classmethod
    def dining_table(cls) -> sa_orm.Mapped["DiningTable"]:  # type: ignore[reportUndefinedVariable]  # noqa: F821
        return sa_orm.relationship(
            "DiningTable",
            passive_deletes=True,
            uselist=False,
        )

    @sa_orm.declared_attr
    @classmethod
    def physician(cls) -> sa_orm.Mapped["Physician"]:  # type: ignore[reportUndefinedVariable]  # noqa: F821
        return sa_orm.relationship(
            "Physician",
            passive_deletes=True,
            uselist=False,
        )

    @sa_orm.declared_attr
    @classmethod
    def travel_package(cls) -> sa_orm.Mapped["TravelPackage"]:  # type: ignore[reportUndefinedVariable]  # noqa: F821
        return sa_orm.relationship(
            "TravelPackage",
            passive_deletes=True,
            uselist=False,
        )
