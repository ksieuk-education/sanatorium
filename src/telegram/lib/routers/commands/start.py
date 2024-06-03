import logging

import aiogram
import aiogram.filters as aiogram_filters
import aiogram.fsm.context as aiogram_fsm_context
import aiogram.utils.formatting as aiogram_utils_formatting

import lib.filters as structures_filters
import lib.structures.keyboards as structures_keyboards

logger = logging.getLogger(__name__)


class StartRouter:
    def __init__(self, router: aiogram.Router):
        self.router = router

        self.register()

    def register(self):
        self.router.message.register(
            self.on_start,
            aiogram_filters.Command("start"),
        )

    async def on_start(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        await state.clear()

        response_text = aiogram_utils_formatting.Text("Привет! Первое сообщение")
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.get_kb_user_registration(),
        )
