"""Обработка ошибок при вызове ручек"""

import logging

import fastapi.responses
import pydantic

import lib.app.errors as _app_errors

logger = logging.getLogger(__name__)


async def value_error_exception_handler(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    """
    Обработка ошибок валидации данных

    :param request: Запрос пользователя
    :param exc: Вызванная ошибка
    """

    if not isinstance(exc, pydantic.ValidationError):
        return await __return_universal_exception(exc, request=request)

    logger.debug("Request Validation error: request values=%s", request.values())
    return fastapi.responses.JSONResponse(
        status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": str(exc)},
    )


async def not_found_exception_handler(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    """
    Обработка ошибок наличия данных

    :param request: Запрос пользователя
    :param exc: Вызванная ошибка
    """

    if not isinstance(exc, _app_errors.RepositoryORMNotFoundError):
        return await __return_universal_exception(exc, request=request)

    logger.error("Request Not Found error: request=%s", request.values())
    return fastapi.responses.JSONResponse(
        status_code=fastapi.status.HTTP_404_NOT_FOUND,
        content={"message": str(exc)},
    )


async def repository_exception_handler(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    """
    Обработка ошибок репозиториев

    :param request: Запрос пользователя
    :param exc: Вызванная ошибка
    """

    if not isinstance(exc, _app_errors.RepositoryError):
        return await __return_universal_exception(exc, request=request)

    logger.error("Request Repository error: request=%s", request)
    return await __return_universal_exception(exc)


async def authorization_exception_handler(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    """
    Обработка ошибок авторизации и аутентификации

    :param request: Запрос пользователя
    :param exc: Вызванная ошибка
    """

    if not isinstance(exc, _app_errors.ServiceAuthorizationError):
        return await __return_universal_exception(exc, request=request)

    logger.error("Request Authorization error: request=%s", request)
    return fastapi.responses.JSONResponse(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        content={"message": str(exc)},
    )


async def service_exception_handler(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    """
    Обработка ошибок авторизации

    :param request: Запрос пользователя
    :param exc: Вызванная ошибка
    """

    if not isinstance(exc, _app_errors.ServiceAuthorizationError):
        return await __return_universal_exception(exc, request=request)

    logger.error("Request Service error: request=%s", request)
    return await __return_universal_exception(exc)


async def __return_universal_exception(exc: Exception, *, request: fastapi.Request | None = None) -> fastapi.Response:
    """
    Возвращение 502 ошибки

    :param request: Запрос пользователя
    :param exc: Вызванная ошибка
    """

    if request is not None:
        logger.error("Request Universal error: request=%s", request)

    return fastapi.responses.JSONResponse(
        status_code=fastapi.status.HTTP_502_BAD_GATEWAY,
        content={"message": str(exc)},
    )
