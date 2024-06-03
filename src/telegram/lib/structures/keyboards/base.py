import aiogram
import aiogram.utils.keyboard as aiogram_utils_keyboard


def create_kb_buttons(*fields: str) -> aiogram_utils_keyboard.ReplyKeyboardBuilder:
    builder = aiogram_utils_keyboard.ReplyKeyboardBuilder()
    for field_text in fields:
        builder.button(text=field_text)
    builder.adjust(3)
    return builder


def create_kb_markup(*fields: str) -> aiogram.types.ReplyKeyboardMarkup:
    builder = create_kb_buttons(*fields)
    return builder.as_markup(resize_keyboard=True)
