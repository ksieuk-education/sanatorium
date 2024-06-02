"""Пользовательские ошибки"""


class ApplicationError(Exception):
    """Ошибка приложения"""

    def __init__(self, message: str, *args: object) -> None:
        """
        Конструктор для объявления сообщения об ошибке

        :param message: Сообщение
        :param args: Дополнительные аргументы
        """

        super().__init__(*args)
        self.message = message

    def __str__(self) -> str:
        """Сообщение об ошибке при попытке преобразования класса к строке"""

        return self.message


class DisposeError(ApplicationError):
    """Ошибка при неуспешной работе деструктора"""


class StartServerError(ApplicationError):
    """Ошибка запуска сервера"""


class ClientError(ApplicationError):
    """Ошибка клиента"""


class RepositoryError(ApplicationError):
    """Ошибка репозитория"""


class RepositoryORMNotFoundError(RepositoryError):
    """Ошибка наличия объекта"""


class RepositoryORMIntegrityError(RepositoryError):
    """Общая ошибка базы данных (по уникальности, индексу)"""


class RepositoryORMForeignKeyViolationError(RepositoryError):
    """Ошибка, связанная с уникальным ключом базы данных"""


class RepositoryORMUniqueViolationError(RepositoryError):
    """Ошибка уникальности"""


class ServiceError(ApplicationError):
    """Ошибка сервиса"""


class ServiceAuthorizationError(ServiceError):
    """Ошибка авторизации"""


__all__ = [
    "ApplicationError",
    "ClientError",
    "DisposeError",
    "RepositoryError",
    "ServiceAuthorizationError",
    "ServiceError",
    "StartServerError",
]
