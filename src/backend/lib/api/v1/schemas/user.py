"""Схемы для работы с пользователями."""

import lib.models as _models


class UserCreateSchema(_models.UserInfoModel):
    """Схема для создания пользователя"""


class UserFullSchema(_models.UserFullModel):
    """Полная схема пользователя"""


class UserUpdateSchema(_models.UserOptionalModel):
    """Схема для обновления пользователя"""
