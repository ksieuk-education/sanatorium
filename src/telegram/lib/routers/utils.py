import aiogram
import aiogram.fsm.context as aiogram_fsm_context

import lib.structures.keyboards as structures_keyboards


async def send_start_message(
    message: aiogram.types.Message,
    state: aiogram_fsm_context.FSMContext,
):
    await state.clear()

    response_text = (
        "И снова здравствуйте!\nЯ помогу собрать данные для твоего медиаанализа и положить их в табличку Excel! "
        "Также ты можешь запустить новый медиаанализ или получить выгрузку Excel, если он уже был запущен :)\n\n"
        "Готов к новому медиаанализу?"
    )
    await message.answer(
        text=response_text,
        reply_markup=structures_keyboards.get_kb_user_registration(),
    )
