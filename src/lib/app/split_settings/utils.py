"""Утилиты для настроек. Объявление путей"""

import pathlib

BASE_PATH = pathlib.Path(__file__).parent.parent.parent.parent.resolve()
ENV_PATH = BASE_PATH / ".env"
CONFIG_YML_PATH = BASE_PATH / ".config.yml"
