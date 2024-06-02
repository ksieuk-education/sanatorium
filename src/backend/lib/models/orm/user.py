# pylint: disable=unsubscriptable-object
"""Описание таблиц, связанных с пользователями"""

import datetime

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

import lib.models.orm.base as _models_orm_base


class User(_models_orm_base.Base, _models_orm_base.IdCreatedUpdatedBaseMixin):
    """Модель для описания полей в таблице User"""

    first_name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(255), nullable=False)
    last_name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(255), nullable=False)
    passport_series: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.Integer, nullable=False)
    passport_number: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.Integer, nullable=False)
    medical_policy: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.Integer, nullable=False)
    birth_date: sa_orm.Mapped[datetime.date] = sa_orm.mapped_column(sa.Date, nullable=False)

    @sa_orm.declared_attr
    @classmethod
    def registrations(  # type: ignore[reportUnknownParameterType]
        cls,
    ) -> sa_orm.Mapped[list["Registration"]]:  # type: ignore[reportUndefinedVariable]  # noqa: F821
        return sa_orm.relationship(
            "Registration",
            back_populates="user",
            cascade="all, delete",
            passive_deletes=True,
        )


class Admin(_models_orm_base.Base, _models_orm_base.IdCreatedUpdatedBaseMixin):
    """Модель для описания полей в таблице Admin"""

    username: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(255), nullable=False, unique=True)
    password: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(255), nullable=False)
