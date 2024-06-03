import aiogram
import aiogram.filters.callback_data as aiogram_filters_callback_data
import aiogram.types as aiogram_types
import aiogram.utils.keyboard as aiogram_utils_keyboard

import lib.structures.keyboards.base as structures_keyboards_base


def create_kb_media(*fields: str, include_back_button: bool = True) -> aiogram.types.ReplyKeyboardMarkup:
    kb = structures_keyboards_base.create_kb_buttons(*fields)
    if include_back_button:
        kb.row(
            aiogram_types.KeyboardButton(text="<Назад>"),
            aiogram_types.KeyboardButton(text="Отменить"),
        )
    else:
        kb.row(
            aiogram_types.KeyboardButton(text="Отменить"),
        )
    return kb.as_markup(resize_keyboard=True)


def get_kb_user_registration() -> aiogram.types.ReplyKeyboardMarkup:
    return structures_keyboards_base.create_kb_markup("Зарегистрироваться")


def get_kb_get_or_create_media() -> aiogram.types.ReplyKeyboardMarkup:
    return create_kb_media(
        "Создать новый медиаанализ",
    )


def get_kb_create_media() -> aiogram.types.ReplyKeyboardMarkup:
    return create_kb_media(
        "Создать новый медиаанализ",
    )


def get_kb_media_actions(include_media_start_button: bool = True) -> aiogram.types.ReplyKeyboardMarkup:
    if include_media_start_button:
        return create_kb_media(
            "Запустить медиаанализ",
            "Получить выгрузку в Excel",
            "Пересоздать и получить выгрузку в Excel",
        )
    return create_kb_media(
        "Получить выгрузку в Excel",
        "Пересоздать и получить выгрузку в Excel",
    )


def get_kb_create_query() -> aiogram.types.ReplyKeyboardMarkup:
    return create_kb_media(
        "университет, вуз",
        "Петр Иванов",
        "<Пропустить>",
    )


class GetMediaCallbackData(aiogram_filters_callback_data.CallbackData, prefix="get_media"):
    data: str


def __create_kb_inline_medias(*fields: str) -> aiogram.types.InlineKeyboardMarkup:
    builder = aiogram_utils_keyboard.InlineKeyboardBuilder()
    for field_text in fields:
        builder.button(
            text=field_text,
            callback_data=GetMediaCallbackData(
                data=field_text,
            ),
        )
    builder.button(
        text="⬅️",
        callback_data=GetMediaCallbackData(
            data="⬅️",
        ),
    )
    builder.button(
        text="➡️",
        callback_data=GetMediaCallbackData(
            data="➡️",
        ),
    )
    first_buttons_adjust = [3] * (len(fields) // 3)
    last_buttons_adjust = len(fields) % 3
    if last_buttons_adjust == 0:
        builder.adjust(*first_buttons_adjust, 2)
    else:
        builder.adjust(*first_buttons_adjust, last_buttons_adjust, 2)
    return builder.as_markup()


def get_kb_inline_medias(medias_number: int = 10) -> aiogram.types.InlineKeyboardMarkup:
    if medias_number <= 0:
        raise ValueError("medias_number must be greater than 0")

    return __create_kb_inline_medias(*map(str, range(1, medias_number + 1)))


class GetMediaStatusCallbackData(aiogram_filters_callback_data.CallbackData, prefix="get_media_status"):
    pass


def get_kb_inline_refresh() -> aiogram.types.InlineKeyboardMarkup:
    builder = aiogram_utils_keyboard.InlineKeyboardBuilder()
    builder.button(
        text="Обновить",
        callback_data=GetMediaStatusCallbackData(),
    )
    return builder.as_markup()
