import typing


class ApplicationError(Exception):
    def __init__(self, message: str, *args: typing.Any) -> None:
        super().__init__(*args)
        self.message = message


class DisposeError(ApplicationError):
    pass


class StartServerError(ApplicationError):
    pass


class ClientError(ApplicationError):
    pass
