import pathlib

BASE_PATH = pathlib.Path(__file__).parent.parent.parent.parent.resolve()
ENV_PATH = BASE_PATH / ".env"
