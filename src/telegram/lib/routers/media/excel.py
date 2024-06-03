# import aiogram
# import aiogram.exceptions as aiogram_exceptions
# import aiogram.filters as aiogram_filters
# import aiogram.fsm.context as aiogram_fsm_context
# import aiogram.utils.formatting as aiogram_utils_formatting
#
# import lib.media.models as media_models
# import lib.media.services as media_services
# import lib.routers.utils as routers_utils
# import lib.structures.fsm as structures_fsm
# import lib.structures.keyboards as structures_keyboards
#
#
# class MediaGetRouter:
#     def __init__(
#         self,
#         router: aiogram.Router,
#         media_service: media_services.MediaService,
#     ):
#         self.router = router
#         self.media_service = media_service
#
#         self.register()
#
#     def register(self):
#         self.router.message.register(
#             self.on_get_excel,
#             # aiogram_filters.or_f(
#             aiogram.F.text.lower().in_("получить выгрузку в excel"),
#                 # aiogram.F.text.lower().in_("пересоздать и получить выгрузку в excel"),
#             # ),
#             aiogram_filters.StateFilter(structures_fsm.MediaStates.get_media_actions),
#         )
#
#     async def on_get_excel(
#         self,
#         message: aiogram.types.Message,
#         state: aiogram_fsm_context.FSMContext,
#     ):
#         structures_keyboards.get_kb_inline_medias()
#         if not message.text:
#             return
#         is_regenerate = "пересоздать" in message.text.lower()
#
#         await message.answer("Создание excel... Это может занять некоторое время")
#         user_data = await state.get_data()
#         response = await self.media_service.get_media_excel_by_id(user_data["media_id"], is_regenerate=is_regenerate)
#         file_bytes = aiogram.types.BufferedInputFile(response, filename=user_data["media_name"] + ".xlsx")
#         await message.answer_document(file_bytes)
#         await routers_utils.send_start_message(message, state)
