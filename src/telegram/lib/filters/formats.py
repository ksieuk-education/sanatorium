import datetime
import logging

import aiogram
import aiogram.filters as aiogram_filters

logger = logging.getLogger(__name__)


class CheckDate(aiogram_filters.BaseFilter):
    def __init__(self, date_format: str):
        self.date_format = date_format

        super().__init__()

    async def __call__(self, message: aiogram.types.Message) -> bool:
        message_text = message.text
        if not message_text:
            return False
        try:
            datetime.datetime.strptime(message_text, self.date_format)
        except ValueError:
            return False
        return True


class CheckCommandArgsExists(aiogram_filters.BaseFilter):
    async def __call__(self, message: aiogram.types.Message) -> bool:
        full_message_text = message.text
        if not full_message_text:
            return False
        if not full_message_text.startswith("/"):
            logger.warning("Message is not a command, but checking for command args")
            return False

        return len(full_message_text.split()) > 1


class CheckIsDigit(aiogram_filters.BaseFilter):
    def __init__(self, is_command: bool = False, check_sequence: bool = False):
        self.is_command = is_command
        self.is_sequence = check_sequence

        super().__init__()

    async def __call__(
        self,
        message: aiogram.types.Message,
    ) -> bool:
        full_message_text = message.text
        if not full_message_text:
            return False
        if not self.is_command:
            text = full_message_text
        elif not await CheckCommandArgsExists()(message):
            return False
        else:
            text = full_message_text.split(maxsplit=1)[1]

        if not self.is_sequence:
            return text.isdigit()
        text_sequence = text.split()
        return all(map(lambda item: item.isdigit(), text_sequence))
