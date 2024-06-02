# pylint: disable=unsubscriptable-object
"""Описание таблиц, связанных с врачами в санатории"""

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

import lib.models.orm.base as _models_orm_base


class Physician(_models_orm_base.Base, _models_orm_base.IdCreatedUpdatedBaseMixin):
    """Модель для описания полей в таблице Physician"""

    full_name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(255), nullable=False)
    specialization: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(255), nullable=False)
