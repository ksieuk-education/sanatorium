import aiogram
import aiogram.exceptions as aiogram_exceptions
import aiogram.filters as aiogram_filters
import aiogram.fsm.context as aiogram_fsm_context
import aiogram.utils.formatting as aiogram_utils_formatting

import lib.routers.utils as routers_utils
import lib.sanatorium.models as media_models
import lib.sanatorium.services as media_services
import lib.structures.fsm as structures_fsm
import lib.structures.keyboards as structures_keyboards


class MediaGetRouter:
    def __init__(
        self,
        router: aiogram.Router,
        media_service: media_services.MediaService,
    ):
        self.router = router
        self.media_service = media_service

        self.register()

    def register(self):
        self.router.callback_query.register(
            self.callback_get_media,
            structures_keyboards.GetMediaCallbackData.filter(),
            aiogram_filters.StateFilter(structures_fsm.MediaStates.get_or_create_media),
        )
        self.router.callback_query.register(
            self.callback_get_media_status,
            structures_keyboards.GetMediaStatusCallbackData.filter(),
            aiogram_filters.StateFilter(structures_fsm.MediaStates.get_media_actions),
        )
        self.router.message.register(
            self.on_error_get_media,
            ~aiogram.F.text.cast(int).as_("digits"),
            aiogram_filters.StateFilter(structures_fsm.MediaStates.get_or_create_media),
        )
        self.router.message.register(
            self.get_media,
            aiogram.F.text.cast(int).as_("media_number"),
            aiogram_filters.StateFilter(structures_fsm.MediaStates.get_or_create_media),
        )

        self.router.message.register(
            self.on_get_media,
            aiogram.F.text.lower() == "<назад>",
            aiogram_filters.or_f(
                aiogram_filters.StateFilter(structures_fsm.MediaStates.get_media_actions),
                aiogram_filters.StateFilter(structures_fsm.MediaStates.media_analyze_status),
            ),
        )
        self.router.message.register(
            self.get_media_status,
            aiogram.F.text.lower().in_("посмотреть статус"),
            aiogram_filters.StateFilter(structures_fsm.MediaStates.get_media_actions),
        )
        self.router.message.register(
            self.on_get_excel,
            aiogram_filters.or_f(
                aiogram.F.text.lower().in_("получить выгрузку в excel"),
                aiogram.F.text.lower().in_("пересоздать и получить выгрузку в excel"),
            ),
            aiogram_filters.StateFilter(structures_fsm.MediaStates.get_media_actions),
        )
        self.router.message.register(
            self.fix_media,
            aiogram_filters.Command("fix_media"),
            aiogram_filters.StateFilter(structures_fsm.MediaStates.get_media_actions),
        )
        self.router.message.register(
            self.restart_media,
            aiogram_filters.Command("restart_media"),
            aiogram_filters.StateFilter(structures_fsm.MediaStates.get_media_actions),
        )
        self.router.message.register(
            self.fix_markup,
            aiogram_filters.Command("fix_markup"),
            aiogram_filters.StateFilter(structures_fsm.MediaStates.get_media_actions),
        )
        self.router.message.register(
            self.delete_media,
            aiogram_filters.Command("delete_media"),
            aiogram_filters.StateFilter(structures_fsm.MediaStates.get_media_actions),
        )

    async def on_get_media(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        response_text = "Выберите один медиаанализ из списка выше"
        await message.answer(
            text=response_text,
            reply_markup=structures_keyboards.create_kb_media(),
        )
        await state.set_state(structures_fsm.MediaStates.get_or_create_media)

    async def on_error_get_media(
        self,
        message: aiogram.types.Message,
    ):
        response_text = 'Необходимо ввести целое число (например, "1", "2", "15"). Попробуйте еще раз.'
        await message.answer(
            text=response_text,
        )

    async def callback_get_media(
        self,
        query: aiogram.types.CallbackQuery,
        callback_data: structures_keyboards.GetMediaCallbackData,
        state: aiogram_fsm_context.FSMContext,
    ) -> None:
        message = query.message
        if not isinstance(message, aiogram.types.Message):
            return
        await self.get_media(message, int(callback_data.data), state)

    async def get_media(
        self,
        message: aiogram.types.Message,
        media_number: int,
        state: aiogram_fsm_context.FSMContext,
    ):
        user_data = await state.get_data()
        if not (media_list := user_data.get("medias")):
            response_text = (
                "Чтобы получить что-то, нужно сначала создать это :). "
                "Ни одного медиаанализа пока не создано, давайте исправим это?"
            )
            await state.set_state(structures_fsm.MediaStates.get_or_create_media)
            return await message.answer(
                text=response_text,
                reply_markup=structures_keyboards.get_kb_create_media(),
            )
        media_list_line = [item.get_info_line() for item in media_list]
        media_len = len(media_list_line)
        if not 0 < media_number <= media_len:
            response_text = aiogram_utils_formatting.Text(
                "Медиа-анализа под таким номером не существует. Максимальный номер: ",
                aiogram_utils_formatting.Bold(media_len),
                "\n\nПопробуйте еще раз",
            )
            return await message.answer(**response_text.as_kwargs())

        media_text = media_list_line[media_number - 1]
        media_selected = media_list[media_number - 1]
        await state.update_data(
            media_id=media_selected.id,
            media_name=media_selected.name,
            media_status=media_selected.status,
        )
        response_text = aiogram_utils_formatting.Text(
            "Отлично! Медиаанализ выбран:\n",
            aiogram_utils_formatting.Bold(media_text),
            "\n\nЗапустите выгрузку или скачайте файл, если выгрузка уже завершена",
        )

        reply_markup = (
            structures_keyboards.get_kb_media_actions()
            if media_selected.status == media_models.StatusFieldEnum.GROUPS_REQUIRED
            else structures_keyboards.get_kb_media_actions(include_media_start_button=False)
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=reply_markup,
        )
        await state.set_state(structures_fsm.MediaStates.get_media_actions)

        if media_selected.status != media_models.StatusFieldEnum.GROUPS_REQUIRED:
            await self.get_media_status(message, state)

    async def get_media_status(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        user_data = await state.get_data()
        media_status = await self.media_service.get_media_status(user_data["media_id"])
        await state.update_data(media_status=media_status)

        response_message = media_status.get_info_text_formatted()
        await message.answer(
            **response_message.as_kwargs(),
            reply_markup=structures_keyboards.get_kb_inline_refresh(),
        )

    async def callback_get_media_status(
        self,
        query: aiogram.types.CallbackQuery,
        state: aiogram_fsm_context.FSMContext,
    ) -> None:
        user_data = await state.get_data()
        media_id = user_data.get("media_id")
        query_message = query.message
        if not isinstance(query_message, aiogram.types.Message) or not media_id:
            return
        media_status = await self.media_service.get_media_status(user_data["media_id"])
        response_message = media_status.get_info_text_formatted(user_data["media_status"])

        try:
            await query_message.edit_text(
                **response_message.as_kwargs(),
                reply_markup=structures_keyboards.get_kb_inline_refresh(),
            )
        except aiogram_exceptions.TelegramBadRequest:
            pass

    async def on_get_excel(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        if not message.text:
            return
        is_regenerate = "пересоздать" in message.text.lower()

        await message.answer("Создание excel... Это может занять некоторое время")
        user_data = await state.get_data()
        response = await self.media_service.get_media_excel_by_id(user_data["media_id"], is_regenerate=is_regenerate)
        file_bytes = aiogram.types.BufferedInputFile(response, filename=user_data["media_name"] + ".xlsx")
        await message.answer_document(file_bytes)
        await routers_utils.send_start_message(message, state)

    async def fix_media(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        user_data = await state.get_data()
        if not (media_id := user_data.get("media_id")):
            return
        await self.media_service.fix_media_status(media_id)
        await message.answer("Статус медиаанализа обновлен")

    async def restart_media(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        user_data = await state.get_data()
        if not (media_id := user_data.get("media_id")):
            return
        await self.media_service.restart_media(media_id)
        await message.answer("Медиаанализ перезапущен")

    async def fix_markup(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        user_data = await state.get_data()
        if not (media_id := user_data.get("media_id")):
            return
        await self.media_service.fix_markup(media_id)
        await message.answer("Медиаанализ перезапущен")

    async def delete_media(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        user_data = await state.get_data()
        if not (media_id := user_data.get("media_id")):
            return
        await self.media_service.delete_media(media_id)
        await message.answer("Медиаанализ удален")
