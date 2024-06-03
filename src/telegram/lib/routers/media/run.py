import datetime
import uuid

import aiogram
import aiogram.filters as aiogram_filters
import aiogram.fsm.context as aiogram_fsm_context
import aiogram.utils.formatting as aiogram_utils_formatting

import lib.filters as structures_filters
import lib.routers.utils as routers_utils
import lib.sanatorium.models as media_models
import lib.sanatorium.services as media_services
import lib.structures.fsm as structures_fsm
import lib.structures.keyboards as structures_keyboards


class MediaRunRouter:
    def __init__(
        self,
        router: aiogram.Router,
        media_service: media_services.MediaService,
    ):
        self.router = router
        self.media_service = media_service

        self.register()

    def register(self):
        self.router.message.register(
            self.on_get_tg_urls,
            aiogram.F.text.lower() == "<назад>",
            aiogram_filters.StateFilter(structures_fsm.MediaGroupsStates.get_vk_urls),
        )
        self.router.message.register(
            self.on_get_vk_urls,
            aiogram.F.text.lower() == "<назад>",
            aiogram_filters.StateFilter(
                structures_fsm.MediaGroupsStates.get_vk_urls,
                structures_fsm.MediaGroupsStates.get_ok_urls,
            ),
        )
        self.router.message.register(
            self.on_run_media,
            aiogram.F.text.lower().in_("запустить медиаанализ"),
            aiogram_filters.StateFilter(structures_fsm.MediaStates.get_media_actions),
        )
        self.router.message.register(
            self.on_get_tg_urls,
            aiogram.F.text.lower().in_("ввести группы вручную"),
            aiogram_filters.StateFilter(structures_fsm.MediaGroupsStates.on_get_groups),
        )
        self.router.callback_query.register(
            self.callback_get_media,
            structures_keyboards.GetMediaCallbackData.filter(),
            aiogram_filters.StateFilter(structures_fsm.MediaGroupsStates.on_get_groups),
        )
        self.router.message.register(
            self.on_get_vk_urls,
            aiogram.F.text.lower() == "<закончить>",
            aiogram_filters.StateFilter(structures_fsm.MediaGroupsStates.get_tg_urls),
        )
        self.router.message.register(
            self.get_tg_urls,
            aiogram.F.text.as_("tg_urls"),
            aiogram_filters.StateFilter(structures_fsm.MediaGroupsStates.get_tg_urls),
        )
        self.router.message.register(
            self.on_get_ok_urls,
            aiogram.F.text.lower() == "<закончить>",
            aiogram_filters.StateFilter(structures_fsm.MediaGroupsStates.get_vk_urls),
        )
        self.router.message.register(
            self.get_vk_urls,
            aiogram.F.text.as_("vk_urls"),
            aiogram_filters.StateFilter(structures_fsm.MediaGroupsStates.get_vk_urls),
        )
        self.router.message.register(
            self.on_get_dzen_urls,
            aiogram.F.text.lower() == "<закончить>",
            aiogram_filters.StateFilter(structures_fsm.MediaGroupsStates.get_ok_urls),
        )
        self.router.message.register(
            self.get_ok_urls,
            aiogram.F.text.as_("ok_urls"),
            aiogram_filters.StateFilter(structures_fsm.MediaGroupsStates.get_ok_urls),
        )
        self.router.message.register(
            self.on_get_start_date_after_dzen,
            aiogram.F.text.lower() == "<закончить>",
            aiogram_filters.StateFilter(structures_fsm.MediaGroupsStates.get_dzen_urls),
        )
        self.router.message.register(
            self.get_dzen_urls,
            aiogram.F.text.as_("dzen_urls"),
            aiogram_filters.StateFilter(structures_fsm.MediaGroupsStates.get_dzen_urls),
        )
        self.router.message.register(
            self.__on_back_get_start_date,
            aiogram.F.text.lower() == "<назад>",
            aiogram_filters.StateFilter(structures_fsm.MediaGroupsStates.get_start_date),
        )
        self.router.message.register(
            self.__on_skip_get_start_date,
            aiogram.F.text.lower() == "<пропустить>",
            aiogram_filters.StateFilter(structures_fsm.MediaGroupsStates.get_start_date),
        )
        self.router.message.register(
            self.__on_validation_error_get_start_date,
            ~structures_filters.CheckDate("%d.%m.%Y"),
            aiogram_filters.StateFilter(structures_fsm.MediaGroupsStates.get_start_date),
        )
        self.router.message.register(
            self.get_start_date,
            aiogram.F.text.as_("start_date"),
            aiogram_filters.StateFilter(structures_fsm.MediaGroupsStates.get_start_date),
        )
        self.router.message.register(
            self.__on_back_get_start_time,
            aiogram.F.text.lower() == "<назад>",
            aiogram_filters.StateFilter(structures_fsm.MediaGroupsStates.get_start_time),
        )
        self.router.message.register(
            self.__on_validation_error_get_start_time,
            ~structures_filters.CheckDate("%H:%M:%S"),
            aiogram_filters.StateFilter(structures_fsm.MediaGroupsStates.get_start_time),
        )
        self.router.message.register(
            self.get_start_time,
            aiogram.F.text.as_("start_time"),
            aiogram_filters.StateFilter(structures_fsm.MediaGroupsStates.get_start_time),
        )
        self.router.message.register(
            self.__on_back_confirmation,
            aiogram.F.text.lower() == "<назад>",
            aiogram_filters.StateFilter(structures_fsm.MediaGroupsStates.confirmation),
        )
        self.router.message.register(
            self.get_confirmation,
            aiogram.F.text.lower() == "подтвердить",
            aiogram_filters.StateFilter(structures_fsm.MediaGroupsStates.confirmation),
        )

    async def on_run_media(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        response_text = aiogram_utils_formatting.Text(
            "Загрузите группы из другого медиаанализа, выбрав его номер из списка выше\n\n"
            "Или введите группы вручную",
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media("Ввести группы вручную"),
        )
        await state.set_state(structures_fsm.MediaGroupsStates.on_get_groups)

    async def callback_get_media(
        self,
        query: aiogram.types.CallbackQuery,
        callback_data: structures_keyboards.GetMediaCallbackData,
        state: aiogram_fsm_context.FSMContext,
    ) -> None:
        message = query.message
        if not isinstance(message, aiogram.types.Message):
            return
        await self.import_groups_from_media(message, int(callback_data.data), state)

    async def import_groups_from_media(
        self,
        message: aiogram.types.Message,
        media_number: int,
        state: aiogram_fsm_context.FSMContext,
    ):
        user_data = await state.get_data()
        all_medias: list[media_models.MediaTgResponseModel] | None = user_data.get("medias")
        if all_medias is None:
            response_text = aiogram_utils_formatting.Text(
                "Не найдено медиаанализов. Пожалуйста, создайте новый медиаанализ"
            )
            await message.answer(**response_text.as_kwargs())
            await routers_utils.send_start_message(message, state)
            return

        media_list_available = [
            media for media in all_medias if media.status != media_models.StatusFieldEnum.GROUPS_REQUIRED
        ]
        if not media_list_available:
            response_text = aiogram_utils_formatting.Text(
                "Нет доступных медиаанализов для импорта групп. Пожалуйста, введите группы вручную."
            )
            await message.answer(**response_text.as_kwargs())
            await state.set_state(structures_fsm.MediaGroupsStates.on_get_groups)
            return await self.on_get_tg_urls(message, state)

        if not 0 < media_number <= len(all_medias):
            response_text = aiogram_utils_formatting.Text(
                "Медиаанализа под таким номером не существует. Максимальный номер: ",
                aiogram_utils_formatting.Bold(len(all_medias)),
                "\n\nПопробуйте еще раз",
            )
            return await message.answer(**response_text.as_kwargs())

        media_selected = all_medias[media_number - 1]
        media_selected_id: uuid.UUID = media_selected.id
        if media_selected_id == user_data.get("media_id"):
            response_text = aiogram_utils_formatting.Text(
                "Невозможно импортировать группы из текущего медиаанализа. ", "Пожалуйста, выберите другой медиаанализ"
            )
            return await message.answer(**response_text.as_kwargs())

        if media_selected.status == media_models.StatusFieldEnum.GROUPS_REQUIRED:
            response_text = aiogram_utils_formatting.Text(
                "Выбранный медиаанализ ",
                aiogram_utils_formatting.Bold(media_selected.get_info_line()),
                " требует ввода групп. Пожалуйста, выберите другой медиаанализ",
            )
            return await message.answer(**response_text.as_kwargs())

        media_groups = await self.media_service.get_media_groups(media_selected_id)
        await state.update_data(
            tg_urls=media_groups.tg_urls,
            vk_urls=media_groups.vk_urls,
            ok_urls=media_groups.ok_urls,
            dzen_urls=media_groups.dzen_urls,
        )

        response_text = aiogram_utils_formatting.Text(
            "Отлично! Медиаанализ выбран:\n",
            aiogram_utils_formatting.Bold(media_selected.get_info_line()),
            "\n\nГруппы успешно импортированы",
        )
        await message.answer(**response_text.as_kwargs())

        await state.set_state(structures_fsm.MediaGroupsStates.get_start_date)
        return await self.__on_get_start_date(message, state)

    async def on_get_tg_urls(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        user_data = await state.get_data()
        if user_data["media_status"] != media_models.StatusFieldEnum.GROUPS_REQUIRED:
            response_text = aiogram_utils_formatting.Text(
                "Запуск этого медиаанализа ",
                aiogram_utils_formatting.Bold("невозможен"),
                ". Он уже был запущен.\n\n",
                "Создайте новый или выберите другой медиаанализ",
            )
            await message.answer(**response_text.as_kwargs())
            await routers_utils.send_start_message(message, state)
            return
        response_text = aiogram_utils_formatting.Text(
            "Введите группы ",
            aiogram_utils_formatting.Bold("телеграмм"),
            ". Cсылки должны быть разделены пробелом или находится в новой строке) "
            "Пример:\nhttps://t.me/telegram_group [здесь может быть любой текст] https://t.me/telegram_group2\n"
            "https://t.me/telegram_group3\nhttps://t.me/telegram_group4",
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media("<Закончить>"),
        )
        await state.set_state(structures_fsm.MediaGroupsStates.get_tg_urls)

    async def get_tg_urls(
        self,
        message: aiogram.types.Message,
        tg_urls: str,
        state: aiogram_fsm_context.FSMContext,
    ):
        tg_urls_set = {line for line in tg_urls.split() if line.startswith("https://t.me/")}
        user_data = await state.get_data()
        if user_data.get("tg_urls"):
            tg_urls_set = user_data["tg_urls"] | tg_urls_set
        await state.update_data(tg_urls=tg_urls_set)

        response_text = aiogram_utils_formatting.Text(
            f"Всего телеграм групп: {len(tg_urls_set)}\n\n"
            "Если хотите закончить вводить телеграм группы, напишите <Закончить>"
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media("<Закончить>"),
        )

    async def on_get_vk_urls(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        user_data = await state.get_data()
        tg_urls_line = "\n".join(user_data["tg_urls"]) if "tg_urls" in user_data else "Отсутствуют"
        tg_urls_len = len(user_data["tg_urls"]) if "tg_urls" in user_data else 0
        response_groups_text = f"Введенные телеграм группы:\n{tg_urls_line}\n\n" if tg_urls_len <= 50 else ""
        response_text = aiogram_utils_formatting.Text(
            f"{response_groups_text}" f"Всего телеграм групп: {tg_urls_len}\n\n" "Введите группы ",
            aiogram_utils_formatting.Bold("Вконтакте"),
            ". Cсылки должны быть разделены пробелом или находится в новой строке)\n"
            "Пример:\nhttps://vk.com/vk_group https://vk.com/vk_group2\n"
            "https://vk.com/vk_group3\nhttps://vk.com/vk_group4",
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media("<Закончить>"),
        )
        await state.set_state(structures_fsm.MediaGroupsStates.get_vk_urls)

    async def get_vk_urls(
        self,
        message: aiogram.types.Message,
        vk_urls: str,
        state: aiogram_fsm_context.FSMContext,
    ):
        vk_urls_set = {line for line in vk_urls.split() if line.startswith("https://vk.com/")}
        user_data = await state.get_data()
        if user_data.get("vk_urls"):
            vk_urls_set = user_data["vk_urls"] | vk_urls_set
        await state.update_data(vk_urls=vk_urls_set)

        response_text = aiogram_utils_formatting.Text(
            f"Всего групп Вконтакте: {len(vk_urls_set)}\n\n"
            "Если хотите закончить вводить группы Вконтакте, напишите <Закончить>"
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media("<Закончить>"),
        )

    async def on_get_ok_urls(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        user_data = await state.get_data()
        vk_urls_line = "\n".join(user_data["vk_urls"]) if "vk_urls" in user_data else "Отсутствуют"
        vk_urls_len = len(user_data["vk_urls"]) if "vk_urls" in user_data else 0
        response_groups_text = f"Введенные группы Вконтакте:\n{vk_urls_line}\n\n" if vk_urls_len <= 50 else ""
        response_text = aiogram_utils_formatting.Text(
            f"{response_groups_text}" f"Всего групп Вконтакте: {vk_urls_len}\n\n" "Введите группы из ",
            aiogram_utils_formatting.Bold("Одноклассников"),
            ". Cсылки должны быть разделены пробелом или находится в новой строке)\n"
            "Пример:\nhttps://ok.ru/ok_group https://ok.ru/ok_group2\n"
            "https://ok.ru/ok_group3\nhttps://ok.ru/ok_group4",
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media("<Закончить>"),
        )
        await state.set_state(structures_fsm.MediaGroupsStates.get_ok_urls)

    async def get_ok_urls(
        self,
        message: aiogram.types.Message,
        ok_urls: str | None,
        state: aiogram_fsm_context.FSMContext,
    ):
        if not ok_urls:
            raise ValueError("ok_urls is None")
        ok_urls_set = {
            line.replace("https://ok.ru//", "https://ok.ru/")
            for line in ok_urls.split()
            if line.startswith("https://ok.ru/")
        }
        user_data = await state.get_data()
        if user_data.get("ok_urls"):
            ok_urls_set = user_data["ok_urls"] | ok_urls_set
        await state.update_data(ok_urls=ok_urls_set)

        response_text = aiogram_utils_formatting.Text(
            f"Всего групп Одноклассников: {len(ok_urls_set)}\n\n"
            "Если хотите закончить вводить группы из Одноклассников, напишите <Закончить>"
        )

        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media("<Закончить>"),
        )

    async def on_get_dzen_urls(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        user_data = await state.get_data()
        ok_urls_line = "\n".join(user_data["ok_urls"]) if "ok_urls" in user_data else "Отсутствуют"
        ok_urls_len = len(user_data["ok_urls"]) if "ok_urls" in user_data else 0

        response_groups_text = f"Введенные группы Одноклассников:\n{ok_urls_line}\n\n" if ok_urls_len <= 50 else ""
        response_text = aiogram_utils_formatting.Text(
            f"{response_groups_text}" f"Всего групп из Одноклассников: {ok_urls_len}\n\n" "Введите группы из ",
            aiogram_utils_formatting.Bold("Яндекс Дзена"),
            ". Cсылки должны быть разделены пробелом или находится в новой строке)\n"
            "Пример:\nhttps://dzen.ru/ixbt.com?tab=articles, https://dzen.ru/kutovoy\n"
            "https://dzen.ru/dzen_group3\nhttps://dzen.ru/dzen_group4",
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media("<Закончить>"),
        )
        await state.set_state(structures_fsm.MediaGroupsStates.get_dzen_urls)

    async def get_dzen_urls(
        self,
        message: aiogram.types.Message,
        dzen_urls: str | None,
        state: aiogram_fsm_context.FSMContext,
    ):
        if not dzen_urls:
            raise ValueError("dzen_urls is None")
        dzen_urls_set = {line for line in dzen_urls.split() if line.startswith("https://dzen.ru/")}
        user_data = await state.get_data()
        if user_data.get("dzen_urls"):
            dzen_urls_set = user_data["dzen_urls"] | dzen_urls_set
        await state.update_data(dzen_urls=dzen_urls_set)

        response_text = (
            f"Всего групп Дзена: {len(dzen_urls_set)}\n\n"
            "Если хотите закончить вводить группы из Дзена, напишите <Закончить>"
        )

        await message.answer(
            text=response_text,
            reply_markup=structures_keyboards.create_kb_media("<Закончить>"),
        )

    async def on_get_start_date_after_dzen(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        user_data = await state.get_data()
        dzen_urls_line = "\n".join(user_data["dzen_urls"]) if "dzen_urls" in user_data else "Отсутствуют"
        dzen_urls_len = len(user_data["dzen_urls"]) if "dzen_urls" in user_data else 0

        response_groups_text = f"Введенные группы Дзена:\n{dzen_urls_line}\n\n" if dzen_urls_len <= 50 else ""
        response_text = f"{response_groups_text}" f"Всего групп из Дзена: {dzen_urls_len}\n\n"
        await message.answer(text=response_text)
        return await self.__on_get_start_date(message, state)

    async def __on_get_start_date(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        response_text = (
            "Введите дату запуска медиаанализа в формате ДД.ММ.ГГГГ (например, 01.03.2024). "
            "Это функция позволяет сделать отложенный запуск медиаанализа\n"
            "Далее будет предложено ввести точное время старта медиаанализа\n\n"
            "Или напишите <Пропустить>, если хотите запустить медиаанализ прямо сейчас"
        )
        await message.answer(
            text=response_text,
            reply_markup=structures_keyboards.create_kb_media("<Пропустить>"),
        )
        await state.set_state(structures_fsm.MediaGroupsStates.get_start_date)

    async def __on_back_get_start_date(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        await self.on_get_ok_urls(message, state)
        await state.set_state(structures_fsm.MediaGroupsStates.get_vk_urls)

    async def __on_validation_error_get_start_date(
        self,
        message: aiogram.types.Message,
    ):
        response_text = "Необходимо ввести дату в формате ДД.ММ.ГГГГ (например, 01.01.2021). Попробуйте еще раз."
        await message.answer(text=response_text)

    async def __on_skip_get_start_date(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        start_dt = datetime.datetime.now(tz=datetime.timezone(offset=datetime.timedelta(hours=3)))
        await state.update_data(start_date=start_dt.strftime("%d.%m.%Y"))
        await state.update_data(start_time=start_dt)
        response_text = f"Время старта медиаанализа: {start_dt.strftime('%d.%m.%Y %H:%M:%S')}\n\n" "Все верно?"
        await message.answer(
            text=response_text,
            reply_markup=structures_keyboards.create_kb_media("Подтвердить"),
        )
        await state.set_state(structures_fsm.MediaGroupsStates.confirmation)

    async def get_start_date(
        self,
        message: aiogram.types.Message,
        start_date: str | None,
        state: aiogram_fsm_context.FSMContext,
    ):
        await state.update_data(start_date=start_date)

        await message.answer(
            text="Введите точное время старта медиаанализа в формате ЧЧ:ММ:CC (например, 12:00:00)",
            reply_markup=structures_keyboards.create_kb_media("<Пропустить>"),
        )
        await state.set_state(structures_fsm.MediaGroupsStates.get_start_time)

    async def __on_back_get_start_time(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        await self.on_get_start_date_after_dzen(message, state)
        await state.set_state(structures_fsm.MediaGroupsStates.get_start_date)

    async def __on_validation_error_get_start_time(
        self,
        start_time: str,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        if start_time.lower() == "<назад>":
            await self.on_get_start_date_after_dzen(message, state)
            return
        response_text = "Необходимо ввести время в формате ЧЧ:ММ:CC (например, 12:00:00). Попробуйте еще раз."
        await message.answer(
            text=response_text,
        )

    async def get_start_time(
        self,
        message: aiogram.types.Message,
        start_time: str | None,
        state: aiogram_fsm_context.FSMContext,
    ):
        data = await state.get_data()
        start_date = data["start_date"]
        if start_time is None:
            raise ValueError("start_time is None")
        start_time_dt = datetime.datetime.strptime(start_time, "%H:%M:%S")
        start_date_dt = datetime.datetime.strptime(start_date, "%d.%m.%Y")
        start_dt = datetime.datetime.combine(start_date_dt, start_time_dt.time())

        await state.update_data(start_time=start_dt)
        tg_urls_len = len(data["tg_urls"]) if "tg_urls" in data else 0
        vk_urls_len = len(data["vk_urls"]) if "vk_urls" in data else 0
        ok_urls_len = len(data["ok_urls"]) if "ok_urls" in data else 0
        dzen_urls_len = len(data["dzen_urls"]) if "dzen_urls" in data else 0
        response_text = (
            f"Телеграм группы: {tg_urls_len}\n"
            f"Группы Вконтакте: {vk_urls_len}\n"
            f"Группы Одноклассников: {ok_urls_len}\n"
            f"Группы Дзен: {dzen_urls_len}\n\n"
            f"Время старта медиаанализа: {start_dt.strftime('%d.%m.%Y %H:%M:%S')}\n\n"
            "Все верно?"
        )
        await message.answer(
            text=response_text,
            reply_markup=structures_keyboards.create_kb_media("Подтвердить"),
        )
        await state.set_state(structures_fsm.MediaGroupsStates.confirmation)

    async def __on_back_confirmation(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        await self.on_get_start_date_after_dzen(message, state)
        await state.set_state(structures_fsm.MediaGroupsStates.get_start_date)

    async def get_confirmation(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        user_data = await state.get_data()
        if "media_id" not in user_data:
            await message.answer(
                "Выбранный медиаанализ не найден", reply_markup=structures_keyboards.get_kb_user_registration()
            )
            await routers_utils.send_start_message(message, state)
            return
        media_id = user_data["media_id"]
        if message.from_user is None:
            raise ValueError("User is None")

        social_urls: list[list[str]] = []
        for social_name_urls in ("tg_urls", "vk_urls", "ok_urls", "dzen_urls"):
            if social_name_urls in user_data:
                social_urls.append(list(user_data[social_name_urls]))
            else:
                social_urls.append([])

        if not any(social_urls):
            response_text = aiogram_utils_formatting.Text(
                "Необходимо ввести хотя бы одну группу для медиаанализа. Попробуйте еще раз."
            )
            await message.answer(**response_text.as_kwargs())
            await state.set_state(structures_fsm.MediaGroupsStates.on_get_groups)
            await self.on_get_tg_urls(message, state)
            return

        group_request_model = media_models.MediaGroupsRequestModel(
            user_request_id=str(message.from_user.id),
            start_time=user_data["start_time"],
            payload=media_models.MediaGroupsPayloadModel(
                media_id=media_id,
                tg_urls=social_urls[0],
                vk_urls=social_urls[1],
                ok_urls=social_urls[2],
                dzen_urls=social_urls[3],
            ),
        )
        await self.media_service.create_media_groups(group_request_model)
        await message.answer(
            text="Медиа-анализ успешно запущен!",
        )
        await state.set_state(structures_fsm.MediaStates.get_media_number)
        await routers_utils.send_start_message(message, state)
