"""Глобальные модели данных пользователя"""

import datetime
import typing
import uuid

import pydantic


class UserInfoModel(pydantic.BaseModel):
    """Модель данных пользователя"""

    first_name: str
    last_name: str
    passport_series: int
    passport_number: int
    medical_policy: int
    birth_date: datetime.date


class UserFullModel(UserInfoModel):
    """Модель данных пользователя с идентификатором"""

    id: uuid.UUID  # noqa: A003
    created_at: datetime.datetime
    updated_at: datetime.datetime | None = None


class UserOptionalModel(pydantic.BaseModel):
    """Модель данных пользователя с возможностью не указывать все поля"""

    id: uuid.UUID  # noqa: A003
    first_name: str | None = None
    last_name: str | None = None
    passport_series: int | None = None
    passport_number: int | None = None
    medical_policy: int | None = None
    birth_date: datetime.date | None = None

    @pydantic.model_validator(mode="before")
    @classmethod
    def required_one(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        """Хотя бы одно поле должно быть передано"""
        expected_values = values.copy()
        expected_values.pop("id")

        if any(expected_values):
            return values
        msg = "At least one of the fields must be provided"
        raise ValueError(msg)
