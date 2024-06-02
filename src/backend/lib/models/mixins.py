"""Миксины для моделей"""

import typing

import pydantic


class RequiredOneMixin:
    """Миксин для объявления требования к модели"""

    @pydantic.model_validator(mode="before")
    @classmethod
    def required_one(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
        """Хотя бы одно поле должно быть передано"""

        if any(values):
            return values
        msg = "At least one of the fields must be provided"
        raise ValueError(msg)
