"""Схемы для проверки работоспособности сервиса"""

import pydantic


class HealthResponse(pydantic.BaseModel):
    """Схема для проверки работоспособности сервиса"""

    status: str = pydantic.Field(default=..., examples=["healthy"], description="Схема доступности сервиса")
