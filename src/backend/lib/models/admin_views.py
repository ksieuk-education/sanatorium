"""Описание таблиц для админки"""

import sqladmin

import lib.models.orm as _models_orm


class UserView(sqladmin.ModelView, model=_models_orm.User):
    """Админка для таблицы User"""

    column_list = [  # noqa: RUF012
        _models_orm.User.id,
        _models_orm.User.first_name,
        _models_orm.User.last_name,
        _models_orm.User.birth_date,
    ]


class AdminView(sqladmin.ModelView, model=_models_orm.Admin):
    """Админка для таблицы Admin"""

    column_list = [_models_orm.Admin.id, _models_orm.Admin.username]  # noqa: RUF012


class RegistrationView(sqladmin.ModelView, model=_models_orm.Registration):
    """Админка для таблицы Registration"""

    column_list = [  # noqa: RUF012
        _models_orm.Registration.id,
        _models_orm.Registration.user_id,
        _models_orm.Registration.room_id,
        _models_orm.Registration.dining_table_id,
        _models_orm.Registration.physician_id,
        _models_orm.Registration.travel_package_id,
        _models_orm.Registration.check_in_date,
        _models_orm.Registration.check_out_date,
    ]


class TravelPackageView(sqladmin.ModelView, model=_models_orm.TravelPackage):
    """Админка для таблицы TravelPackage"""

    column_list = [  # noqa: RUF012
        _models_orm.TravelPackage.id,
        _models_orm.TravelPackage.name,
        _models_orm.TravelPackage.description,
        _models_orm.TravelPackage.room_type_id,
        _models_orm.TravelPackage.dining_type_id,
    ]


class RoomView(sqladmin.ModelView, model=_models_orm.Room):
    """Админка для таблицы Room"""

    column_list = [  # noqa: RUF012
        _models_orm.Room.id,
        _models_orm.Room.room_number,
        _models_orm.Room.capacity,
        _models_orm.Room.type_id,
    ]


class DiningTableView(sqladmin.ModelView, model=_models_orm.DiningTable):
    """Админка для таблицы DiningTable"""

    column_list = [  # noqa: RUF012
        _models_orm.DiningTable.id,
        _models_orm.DiningTable.table_number,
        _models_orm.DiningTable.capacity,
    ]


class PhysicianView(sqladmin.ModelView, model=_models_orm.Physician):
    """Админка для таблицы Physician"""

    column_list = [  # noqa: RUF012
        _models_orm.Physician.id,
        _models_orm.Physician.full_name,
        _models_orm.Physician.specialization,
    ]


class RoomTypeView(sqladmin.ModelView, model=_models_orm.RoomType):
    """Админка для таблицы RoomType"""

    column_list = [_models_orm.RoomType.id, _models_orm.RoomType.name, _models_orm.RoomType.description]  # noqa: RUF012


class DiningTypeView(sqladmin.ModelView, model=_models_orm.DiningType):
    """Админка для таблицы DiningType"""

    column_list = [  # noqa: RUF012
        _models_orm.DiningType.id,
        _models_orm.DiningType.name,
        _models_orm.DiningType.description,
    ]
