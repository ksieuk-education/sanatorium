"""Стандартный запуск приложения"""


import asyncio
import logging
import os
import sys

import lib.app.app as _app
import lib.app.errors as _errors
import lib.app.settings as _settings

logger = logging.getLogger(__name__)


async def run() -> None:
    """Запуск приложения"""

    settings = _settings.Settings()
    application = _app.Application.from_settings(settings)

    try:
        await application.start()
    finally:
        await application.dispose()


def main() -> None:
    """Запуск приложения и обработка ошибок"""

    try:
        asyncio.run(run())
        sys.exit(os.EX_OK)
    except SystemExit:
        sys.exit(os.EX_OK)
    except _errors.ApplicationError:
        sys.exit(70)
    except KeyboardInterrupt:
        logger.info("Exited with keyboard interruption")
        sys.exit(os.EX_OK)
    except BaseException:
        logger.exception("Unexpected error occurred")
        sys.exit(70)


if __name__ == "__main__":
    main()
