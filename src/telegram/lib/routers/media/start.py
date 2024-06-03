import aiogram
import aiogram.filters as aiogram_filters
import aiogram.fsm.context as aiogram_fsm_context
import aiogram.utils.formatting as aiogram_utils_formatting

import lib.routers.utils as handlers_utils
import lib.sanatorium.models as media_models
import lib.sanatorium.services as media_services
import lib.structures.fsm as structures_fsm
import lib.structures.keyboards as structures_keyboards


class MediaStartRouter:
    def __init__(
        self,
        router: aiogram.Router,
        media_service: media_services.MediaService,
    ):
        self.router = router
        self.media_service = media_service
        self.medias_limit = 10

        self.register()

    def register(self):
        self.router.message.register(
            self.cmd_cancel_media,
            aiogram.F.text.lower().in_({"отменить", "прекратить"}),
            aiogram_filters.StateFilter("*"),
        )
        self.router.message.register(
            self.cmd_cancel_media, aiogram_filters.Command("cancel"), aiogram_filters.StateFilter("*")
        )

        self.router.message.register(
            self.cmd_start_media,
            aiogram.F.text.lower() == "приступить к работе",
            aiogram_filters.StateFilter(None),
        )
        self.router.callback_query.register(
            self.get_medias_next_page,
            structures_keyboards.GetMediaCallbackData.filter(aiogram.F.data == "➡️"),
            aiogram_filters.StateFilter(
                structures_fsm.MediaStates.get_or_create_media,
                structures_fsm.MediaGroupsStates.on_get_groups,
            ),
        )
        self.router.callback_query.register(
            self.get_medias_previous_page,
            structures_keyboards.GetMediaCallbackData.filter(aiogram.F.data == "⬅️"),
            aiogram_filters.StateFilter(
                structures_fsm.MediaStates.get_or_create_media,
                structures_fsm.MediaGroupsStates.on_get_groups,
            ),
        )

    async def cmd_cancel_media(self, message: aiogram.types.Message, state: aiogram_fsm_context.FSMContext):
        await state.clear()
        await message.answer(text="Работа прекращена")
        await handlers_utils.send_start_message(message, state)

    async def __send_media_list(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
        medias: list[media_models.MediaTgResponseModel],
    ):
        media_list: list[aiogram_utils_formatting.Text] = [item.get_info_line_formatted() for item in medias]
        await state.update_data(medias=medias)

        response_text = aiogram_utils_formatting.Text(
            "Список доступных медиаанализов:\n",
            aiogram_utils_formatting.as_numbered_list(*media_list),
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.get_kb_inline_medias(len(media_list)),
        )
        await message.answer(
            "Выберите один из уже существующих медиаанализов или создайте новый",
            reply_markup=structures_keyboards.get_kb_get_or_create_media(),
        )

        await state.set_state(structures_fsm.MediaStates.get_or_create_media)

    async def cmd_start_media(self, message: aiogram.types.Message, state: aiogram_fsm_context.FSMContext):
        medias = await self.media_service.get_all_media_for_tg(
            media_models.MediaGetAllRequestModel(limit=self.medias_limit)
        )

        if not medias:
            response_text = "Пока не создано ни одного медиаанализа. Давайте исправим это?"
            await state.set_state(structures_fsm.MediaStates.get_or_create_media)
            return await message.answer(
                text=response_text,
                reply_markup=structures_keyboards.get_kb_create_media(),
            )
        return await self.__send_media_list(message, state, medias)

    async def get_medias_next_page(
        self,
        query: aiogram.types.CallbackQuery,
        state: aiogram_fsm_context.FSMContext,
    ) -> None:
        message = query.message
        if not isinstance(message, aiogram.types.Message):
            return
        user_data = await state.get_data()
        medias_offset = user_data.get("medias_offset", 0)
        medias_request = media_models.MediaGetAllRequestModel(
            limit=self.medias_limit,
            offset=medias_offset + self.medias_limit,
        )
        medias = await self.media_service.get_all_media_for_tg(medias_request)
        if not medias:
            return

        media_list: list[aiogram_utils_formatting.Text] = [item.get_info_line_formatted() for item in medias]
        await state.update_data(medias=medias)
        await state.update_data(medias_offset=medias_offset + self.medias_limit)

        response_text = aiogram_utils_formatting.Text(
            "Список доступных медиаанализов:\n",
            aiogram_utils_formatting.as_numbered_list(*media_list),
        )

        await message.edit_text(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.get_kb_inline_medias(len(media_list)),
        )

    async def get_medias_previous_page(
        self,
        query: aiogram.types.CallbackQuery,
        state: aiogram_fsm_context.FSMContext,
    ) -> None:
        message = query.message
        if not isinstance(message, aiogram.types.Message):
            return
        user_data = await state.get_data()
        media_offset = user_data.get("medias_offset")
        if not media_offset:
            return
        medias_request = media_models.MediaGetAllRequestModel(
            limit=self.medias_limit,
            offset=media_offset - self.medias_limit,
        )
        medias = await self.media_service.get_all_media_for_tg(medias_request)
        if not medias:
            return

        media_list: list[aiogram_utils_formatting.Text] = [item.get_info_line_formatted() for item in medias]
        await state.update_data(medias=medias)
        await state.update_data(medias_offset=media_offset - self.medias_limit)

        response_text = aiogram_utils_formatting.Text(
            "Список доступных медиаанализов:\n",
            aiogram_utils_formatting.as_numbered_list(*media_list),
        )

        await message.edit_text(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.get_kb_inline_medias(len(media_list)),
        )
