# pylint: disable=unsubscriptable-object
"""Описание таблиц, связанных со столовой в санатории"""

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

import lib.models.orm.base as _models_orm_base


class DiningTable(_models_orm_base.Base, _models_orm_base.IdCreatedUpdatedBaseMixin):
    """Модель для описания полей в таблице DiningTable"""

    @sa_orm.declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:  # pylint: disable=arguments-differ
        """Название таблицы"""

        return "dining_table"

    table_number: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.Integer, nullable=False, unique=True)
    capacity: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.Integer, nullable=False)


class DiningType(_models_orm_base.Base, _models_orm_base.IdCreatedUpdatedBaseMixin):
    """Модель для описания полей в таблице DiningType"""

    @sa_orm.declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:  # pylint: disable=arguments-differ
        """Название таблицы"""

        return "dining_type"

    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(255), nullable=False)
    description: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(255), nullable=False)
