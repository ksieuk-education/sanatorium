import datetime

import aiogram
import aiogram.filters as aiogram_filters
import aiogram.fsm.context as aiogram_fsm_context
import aiogram.utils.formatting as aiogram_utils_formatting
import pydantic

import lib.filters as structures_filters
import lib.routers.utils as routers_utils
import lib.sanatorium.models as media_models
import lib.sanatorium.services as media_services
import lib.structures.fsm as structures_fsm
import lib.structures.keyboards as structures_keyboards


class MediaCreateRouter:
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
            self.create_media,
            aiogram.F.text.lower() == "создать новый медиаанализ",
            aiogram_filters.StateFilter(structures_fsm.MediaStates.get_or_create_media),
        )

        # Back routers
        self.router.message.register(
            self.create_media,
            aiogram.F.text.lower() == "<назад>",
            aiogram_filters.StateFilter(structures_fsm.MediaCreateStates.get_region),
        )
        self.router.message.register(
            self.on_get_region,
            aiogram.F.text.lower() == "<назад>",
            aiogram_filters.StateFilter(structures_fsm.MediaCreateStates.get_start_date),
        )
        self.router.message.register(
            self.on_get_start_date,
            aiogram.F.text.lower() == "<назад>",
            aiogram_filters.StateFilter(structures_fsm.MediaCreateStates.get_end_date),
        )
        self.router.message.register(
            self.on_get_end_date,
            aiogram.F.text.lower() == "<назад>",
            aiogram_filters.StateFilter(structures_fsm.MediaCreateStates.get_query),
        )
        self.router.message.register(
            self.on_get_query,
            aiogram.F.text.lower() == "<назад>",
            aiogram_filters.StateFilter(structures_fsm.MediaCreateStates.get_query_delimiter),
        )
        self.router.message.register(
            self.on_get_query,
            aiogram.F.text.lower() == "<назад>",
            aiogram_filters.StateFilter(structures_fsm.MediaCreateStates.get_is_parsing_comments),
        )
        self.router.message.register(
            self.on_get_is_parsing_comments,
            aiogram.F.text.lower() == "<назад>",
            aiogram_filters.StateFilter(structures_fsm.MediaCreateStates.get_is_marking_posts),
        )
        self.router.message.register(
            self.on_get_is_marking_posts,
            aiogram.F.text.lower() == "<назад>",
            aiogram_filters.StateFilter(structures_fsm.MediaCreateStates.get_is_marking_comments),
        )
        self.router.message.register(
            self.on_get_is_marking_comments,
            aiogram.F.text.lower() == "<назад>",
            aiogram_filters.StateFilter(structures_fsm.MediaCreateStates.get_type),
        )
        self.router.message.register(
            self.on_get_type,
            aiogram.F.text.lower() == "<назад>",
            aiogram_filters.StateFilter(structures_fsm.MediaCreateStates.get_name),
        )
        self.router.message.register(
            self.on_get_name,
            aiogram.F.text.lower() == "<назад>",
            aiogram_filters.StateFilter(structures_fsm.MediaCreateStates.confirmation),
        )

        # Error routers
        self.router.message.register(
            self.__on_error_get_region,
            aiogram.F.text.len() > 255,
            aiogram_filters.StateFilter(structures_fsm.MediaCreateStates.get_region),
        )
        self.router.message.register(
            self.__on_error_get_date,
            ~aiogram_filters.or_f(
                *(
                    structures_filters.CheckDate(date_format)
                    for date_format in media_models.DT_DATETIME_AVAILABLE_FORMATS
                ),
            ),
            aiogram_filters.StateFilter(
                structures_fsm.MediaCreateStates.get_start_date,
                structures_fsm.MediaCreateStates.get_end_date,
            ),
        )
        self.router.message.register(
            self.__on_error_get_query_delimiter,
            aiogram.F.text.len() > 255,
            aiogram_filters.StateFilter(structures_fsm.MediaCreateStates.get_query_delimiter),
        )
        self.router.message.register(
            self.__on_error_get_is_method,
            ~aiogram.F.text.lower().in_({"да", "нет"}),
            aiogram_filters.StateFilter(
                structures_fsm.MediaCreateStates.get_is_parsing_comments,
                structures_fsm.MediaCreateStates.get_is_marking_posts,
                structures_fsm.MediaCreateStates.get_is_marking_comments,
            ),
        )
        self.router.message.register(
            self.__on_error_get_type,
            ~aiogram.F.text.lower().in_([item.value for item in list(media_models.MarkupTypeEnum)]),
            aiogram_filters.StateFilter(structures_fsm.MediaCreateStates.get_type),
        )
        self.router.message.register(
            self.__on_error_get_name,
            aiogram.F.text.len() > 255,
            aiogram_filters.StateFilter(structures_fsm.MediaCreateStates.get_name),
        )

        # General routers
        self.router.message.register(
            self._get_region,
            aiogram.F.text.as_("region"),
            aiogram_filters.StateFilter(structures_fsm.MediaCreateStates.get_region),
        )
        self.router.message.register(
            self._get_start_date,
            aiogram_filters.or_f(
                *(
                    structures_filters.CheckDate(date_format)
                    for date_format in media_models.DT_DATETIME_AVAILABLE_FORMATS
                ),
            ),
            aiogram.F.text.as_("date_str"),
            aiogram_filters.StateFilter(
                structures_fsm.MediaCreateStates.get_start_date,
            ),
        )
        self.router.message.register(
            self._get_end_date,
            aiogram_filters.or_f(
                *(
                    structures_filters.CheckDate(date_format)
                    for date_format in media_models.DT_DATETIME_AVAILABLE_FORMATS
                ),
            ),
            aiogram.F.text.as_("date_str"),
            aiogram_filters.StateFilter(
                structures_fsm.MediaCreateStates.get_end_date,
            ),
        )
        self.router.message.register(
            self._get_query,
            aiogram.F.text.as_("query"),
            aiogram_filters.StateFilter(
                structures_fsm.MediaCreateStates.get_query,
            ),
        )
        self.router.message.register(
            self._get_query_delimiter,
            aiogram.F.text.as_("query_delimiter"),
            aiogram_filters.StateFilter(
                structures_fsm.MediaCreateStates.get_query_delimiter,
            ),
        )
        self.router.message.register(
            self._get_is_parsing_comments,
            aiogram.F.text.as_("parsing_comments"),
            aiogram.F.text.lower().in_({"да", "нет"}),
            aiogram_filters.StateFilter(structures_fsm.MediaCreateStates.get_is_parsing_comments),
        )
        self.router.message.register(
            self._get_is_marking_posts,
            aiogram.F.text.as_("is_marking_posts_text"),
            aiogram.F.text.lower().in_({"да", "нет"}),
            aiogram_filters.StateFilter(structures_fsm.MediaCreateStates.get_is_marking_posts),
        )
        self.router.message.register(
            self._get_is_marking_comments,
            aiogram.F.text.as_("is_marking_comments_text"),
            aiogram.F.text.lower().in_({"да", "нет"}),
            aiogram_filters.StateFilter(structures_fsm.MediaCreateStates.get_is_marking_comments),
        )
        self.router.message.register(
            self._get_type,
            aiogram.F.text.as_("type_"),
            aiogram.F.text.lower().in_([item.value for item in list(media_models.MarkupTypeEnum)]),
            aiogram_filters.StateFilter(
                structures_fsm.MediaCreateStates.get_type,
            ),
        )
        self.router.message.register(
            self._get_name,
            aiogram.F.text.as_("name"),
            aiogram_filters.StateFilter(
                structures_fsm.MediaCreateStates.get_name,
            ),
        )
        self.router.message.register(
            self._create_media_final,
            aiogram.F.text.lower() == "подтвердить",
            aiogram_filters.StateFilter(
                structures_fsm.MediaCreateStates.confirmation,
            ),
        )

    async def create_media(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        response_text = (
            "Приступаем к созданию нового медиаанализа\n\n"
            'Укажите регион (например, "Москва", "Орск", "Орск и Новотроицк"):'
        )
        await message.answer(
            text=response_text,
            reply_markup=structures_keyboards.create_kb_media(include_back_button=False),
        )
        await state.set_state(structures_fsm.MediaCreateStates.get_region)

    async def on_get_region(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        response_text = aiogram_utils_formatting.Text(
            'Укажите регион\n(например, "Москва", "Орск", "Орск и Новотроицк"):\n\n'
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media(),
        )
        await state.set_state(structures_fsm.MediaCreateStates.get_region)

    async def __on_error_get_region(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        response_text = aiogram_utils_formatting.Text(
            "Регион содержит слишком много символов. Максимальное значение: 255\n\n"
            'Укажите регион\n(например, "Москва", "Орск", "Орск и Новотроицк"):\n\n'
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media(),
        )
        await state.set_state(structures_fsm.MediaCreateStates.get_region)

    async def _get_region(
        self,
        message: aiogram.types.Message,
        region: str,
        state: aiogram_fsm_context.FSMContext,
    ):
        await state.update_data(region=region)
        response_text = aiogram_utils_formatting.Text(
            "Отлично, выбран регион: ",
            aiogram_utils_formatting.Code(region),
            "\n\nУкажите ",
            aiogram_utils_formatting.Bold("дату начала"),
            " сбора данных (эта дата должна быть раньше даты окончания).\n\n",
            self.__get_available_date_formats_with_examples_message(),
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media(),
        )
        await state.set_state(structures_fsm.MediaCreateStates.get_start_date)

    async def __on_error_get_date(
        self,
        message: aiogram.types.Message,
    ):
        response_text = aiogram_utils_formatting.Text(
            "Дата введена в неверном формате.\n",
            self.__get_available_date_formats_with_examples_message(),
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media(),
        )

    async def on_get_start_date(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        response_text = aiogram_utils_formatting.Text(
            "Укажите ",
            aiogram_utils_formatting.Bold("дату начала"),
            " сбора данных (эта дата должна быть раньше даты окончания).\n\n",
            self.__get_available_date_formats_with_examples_message(),
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media(),
        )
        await state.set_state(structures_fsm.MediaCreateStates.get_start_date)

    async def _get_start_date(
        self,
        message: aiogram.types.Message,
        date_str: str,
        state: aiogram_fsm_context.FSMContext,
    ):
        start_date = self.__get_date_from_text(date_str)
        await state.update_data(start_date=start_date)

        response_text = aiogram_utils_formatting.Text(
            "Отлично! Дата начала сбора: ",
            aiogram_utils_formatting.Code(start_date.strftime("%d.%m.%Y %H:%M:%S")),
            "\nТеперь введите ",
            aiogram_utils_formatting.Bold("дату окончания"),
            " сбора данных (эта дата должна быть позже даты начала).\n\n",
            self.__get_available_date_formats_with_examples_message(),
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media(),
        )
        await state.set_state(structures_fsm.MediaCreateStates.get_end_date)

    async def on_get_end_date(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        response_text = aiogram_utils_formatting.Text(
            "Введите ",
            aiogram_utils_formatting.Bold("дату окончания"),
            " сбора данных. (эта дата должна быть позже даты начала)\n\n",
            self.__get_available_date_formats_with_examples_message(),
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media(),
        )
        await state.set_state(structures_fsm.MediaCreateStates.get_end_date)

    async def _get_end_date(
        self,
        message: aiogram.types.Message,
        date_str: str,
        state: aiogram_fsm_context.FSMContext,
    ):
        end_date = self.__get_date_from_text(date_str)
        user_data = await state.get_data()
        if end_date <= user_data["start_date"]:
            response_text = aiogram_utils_formatting.Text(
                "Дата окончания сбора данных не может быть раньше или одинакова с датой начала сбора данных.",
                "\nВведите ",
                aiogram_utils_formatting.Bold("дату окончания"),
                " сбора данных.\n\n",
                self.__get_available_date_formats_with_examples_message(),
            )
            await message.answer(
                **response_text.as_kwargs(),
                reply_markup=structures_keyboards.create_kb_media(),
            )
            await state.set_state(structures_fsm.MediaCreateStates.get_end_date)
            return

        await state.update_data(end_date=end_date)

        response_text = aiogram_utils_formatting.Text(
            "Даты сбора данных успешно введены. Дата окончания: ",
            aiogram_utils_formatting.Code(end_date.strftime("%d.%m.%Y %H:%M:%S")),
            "\n\nНапишите ключевое слово, фразу или список слов, "
            "по которым будет идти поиск (регистр не имеет значения). "
            "Позже можно будет добавить разделитель (если хотите передать несколько слов).\n\n"
            "Этот пункт можно пропустить.\n"
            'Примеры: "Петр Земсков", "Яблоко", "яблоко,груша,песня,институт", "<Пропустить>")',
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.get_kb_create_query(),
        )
        await state.set_state(structures_fsm.MediaCreateStates.get_query)

    async def on_get_query(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        response_text = aiogram_utils_formatting.Text(
            "Напишите ключевое слово, фразу или список слов, "
            "по которым будет идти поиск (регистр не имеет значения). "
            "Позже можно будет добавить разделитель (если хотите передать несколько слов).\n\n"
            "Этот пункт можно пропустить.\n"
            'Примеры: "Петр Земсков", "Яблоко", "яблоко,груша,песня,институт", "<Пропустить>")',
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.get_kb_create_query(),
        )
        await state.set_state(structures_fsm.MediaCreateStates.get_query)

    async def _get_query(
        self,
        message: aiogram.types.Message,
        query: str | None,
        state: aiogram_fsm_context.FSMContext,
    ):
        if query == "<Пропустить>":
            await state.update_data(query=None)
            return await self._get_query_delimiter(message, "<Пропустить>", state)

        response_query = f"по ключевому слову (словам): {query}"
        await state.update_data(query=query)

        response_text = (
            f"Поиск будет осуществляться {response_query}\n\n"
            "Если необходимо, укажите разделитель для введенной строки поиска. "
            "Обратите внимание, что есть специальные разделители, "
            "которые могут понадобиться в начале или конце строки\n"
            '(например, ",", ";", "<Пробел>", ",<Пробел>", "<Новая строка>")'
        )

        await message.answer(
            text=response_text,
            reply_markup=structures_keyboards.create_kb_media(
                ",",
                ";",
                "<Пробел>",
                ",<Пробел>",
                "<Новая строка>",
                "<Пропустить>",
            ),
        )
        await state.set_state(structures_fsm.MediaCreateStates.get_query_delimiter)

    async def __on_error_get_query_delimiter(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        response_text = aiogram_utils_formatting.Text(
            "Введенное значение превышает максимальное количество символов (255).\n\n"
            "Необходимо указать разделитель для введенной строки поиска.\n"
            "Обратите внимание, что есть специальные разделители, "
            "которые могут понадобиться в начале или конце строки\n"
            '(например, ",", ";", "<Пробел>", ",<Пробел>", "<Новая строка>")'
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media(
                ",",
                ";",
                "<Пробел>",
                ",<Пробел>",
                "<Новая строка>",
                "<Пропустить>",
            ),
        )
        await state.set_state(structures_fsm.MediaCreateStates.get_query_delimiter)

    async def _get_query_delimiter(
        self,
        message: aiogram.types.Message,
        query_delimiter: str | None,
        state: aiogram_fsm_context.FSMContext,
    ):
        if query_delimiter == "<Пропустить>":
            response_query_delimiter = "Поиск будет осуществляться по всем постам"
            query_delimiter = None
        else:
            user_data = await state.get_data()
            query: str = user_data["query"]
            if query_delimiter is not None:
                query_delimiter = query_delimiter.replace("<Пробел>", " ").replace("<Новая строка>", "\n")

            response_query_delimiter = aiogram_utils_formatting.Text(
                'Указан разделитель: "',
                aiogram_utils_formatting.Code(query_delimiter),
                '"\n\nПоиск будет осуществляться по каждому слову из списка:\n',
                aiogram_utils_formatting.as_numbered_list(*map(lambda word: f'"{word}"', query.split(query_delimiter))),
            )
        await state.update_data(query_delimiter=query_delimiter)

        response_text = aiogram_utils_formatting.Text(
            response_query_delimiter, "\n\nНапишите, нужно ли парсить комментарии к постам"
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media("Да", "Нет"),
        )
        await state.set_state(structures_fsm.MediaCreateStates.get_is_parsing_comments)

    async def on_get_is_parsing_comments(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        response_text = "Напишите, нужно ли парсить комментарии к постам"
        await message.answer(
            text=response_text,
            reply_markup=structures_keyboards.create_kb_media("Да", "Нет"),
        )
        await state.set_state(structures_fsm.MediaCreateStates.get_is_parsing_comments)

    async def _get_is_parsing_comments(
        self,
        message: aiogram.types.Message,
        parsing_comments: str,
        state: aiogram_fsm_context.FSMContext,
    ):
        is_parsing_comments = parsing_comments.lower() == "да"
        await state.update_data(is_parsing_comments=is_parsing_comments)

        await self.on_get_is_marking_posts(message, state)

    async def on_get_is_marking_posts(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        response_text = "Напишите, нужно ли обрабатывать (размечать) посты"
        await message.answer(
            text=response_text,
            reply_markup=structures_keyboards.create_kb_media("Да", "Нет"),
        )
        await state.set_state(structures_fsm.MediaCreateStates.get_is_marking_posts)

    async def _get_is_marking_posts(
        self,
        message: aiogram.types.Message,
        is_marking_posts_text: str,
        state: aiogram_fsm_context.FSMContext,
    ):
        is_marking_posts = is_marking_posts_text.lower() == "да"
        await state.update_data(is_marking_posts=is_marking_posts)

        await self.on_get_is_marking_comments(message, state)

    async def on_get_is_marking_comments(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        response_text = "Напишите, нужно ли обрабатывать (размечать) комментарии к постам"
        await message.answer(
            text=response_text,
            reply_markup=structures_keyboards.create_kb_media("Да", "Нет"),
        )
        await state.set_state(structures_fsm.MediaCreateStates.get_is_marking_comments)

    async def _get_is_marking_comments(
        self,
        message: aiogram.types.Message,
        is_marking_comments_text: str,
        state: aiogram_fsm_context.FSMContext,
    ):
        is_marking_comments = is_marking_comments_text.lower() == "да"
        await state.update_data(is_marking_comments=is_marking_comments)
        await self.on_get_type(message, state)

    async def on_get_type(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        response_text = aiogram_utils_formatting.Text(
            "Укажите, какой тип медиаанализа вы хотите создать из предложенных ниже на клавиатуре",
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media(
                *(item.value for item in list(media_models.MarkupTypeEnum))
            ),
        )
        await state.set_state(structures_fsm.MediaCreateStates.get_type)

    async def _get_type(
        self,
        message: aiogram.types.Message,
        type_: str,
        state: aiogram_fsm_context.FSMContext,
    ):
        await state.update_data(type=type_.lower())

        user_data = await state.get_data()
        region = user_data["region"]

        response_text = aiogram_utils_formatting.Text(
            "И последний пункт! Необходимо указать название для вашего медиаанализа.\n"
            "Оно должно быть уникальным по связке ИМЯ и РЕГИОН. Желательно содержать регион и сегодняшнюю дату "
            '(например, "Орск 31.08.2023", "Новотроицк и Омск 31.08.2023")',
            aiogram_utils_formatting.Bold(
                "\n\nЕсли медиаанализ с таким названием и регионом уже существует, он не будет создан!"
            ),
        )
        timedelta = datetime.timedelta(hours=3)
        date_now = datetime.datetime.utcnow()
        date_now_utc_plus = date_now + timedelta
        date_str = date_now_utc_plus.strftime("%d.%m.%Y")

        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media(f"{region} {date_str}"),
        )
        await state.set_state(structures_fsm.MediaCreateStates.get_name)

    async def on_get_name(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        user_data = await state.get_data()
        region = user_data["region"]

        response_text = (
            "Необходимо указать название для вашего медиаанализа.\n"
            "Оно должно быть уникальным и желательно содержать регион и сегодняшнюю дату "
            '(например, "Орск 31.08.2023", "Новотроицк и Омск 31.08.2023")'
        )
        timezone = datetime.timezone(datetime.timedelta(hours=3))
        date_now = datetime.datetime.now(timezone)
        date_str = date_now.strftime("%d.%m.%Y")

        await message.answer(
            text=response_text,
            reply_markup=structures_keyboards.create_kb_media(f"{region} {date_str}"),
        )
        await state.set_state(structures_fsm.MediaCreateStates.get_name)

    async def _get_name(
        self,
        message: aiogram.types.Message,
        name: str,
        state: aiogram_fsm_context.FSMContext,
    ):
        await state.update_data(name=name)
        user_data = await state.get_data()

        try:
            media_create_request = media_models.MediaCreateRequestModel.model_validate(user_data)
        except pydantic.ValidationError as e:
            await message.answer(
                text=f"Ошибка при валидации данных: {e}\nИсправьте данные и попробуйте ещё раз.",
                reply_markup=structures_keyboards.create_kb_media(),
            )
            await self.on_get_name(message, state)
            return

        await message.answer(
            **media_create_request.get_info_text_formatted().as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media("Подтвердить"),
        )

        await state.set_state(structures_fsm.MediaCreateStates.confirmation)

    async def _create_media_final(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        if message.from_user is None:
            raise ValueError("User is None")
        user_data = await state.get_data()
        request = media_models.MediaCreateRequestModel.model_validate(user_data)

        response_text = "Отлично! Создаю новый медиаанализ..."

        await message.answer(
            text=response_text,
            reply_markup=structures_keyboards.create_kb_media(),
        )
        response = await self.media_service.create_media(request)

        response_text = aiogram_utils_formatting.Text(
            "Параметры медиаанализа успешно сохранены. "
            "Вы можете выбрать этот медиаанализ в главном меню и запустить его!\n\n",
            response.get_info_text_formatted(),
        )

        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media(),
        )

        await routers_utils.send_start_message(message, state)

    async def __on_error_get_type(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        response_text = aiogram_utils_formatting.Text(
            "Необходимо указать тип медиаанализа из предложенных на клавиатуре",
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media(
                *(item.value for item in list(media_models.MarkupTypeEnum))
            ),
        )
        await state.set_state(structures_fsm.MediaCreateStates.get_type)

    async def __on_error_get_name(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        user_data = await state.get_data()
        region = user_data["region"]

        response_text = aiogram_utils_formatting.Text(
            "Название медиаанализа слишком длинное. Максимальное количество символов: 255.\n\n"
            "Необходимо указать название для вашего медиаанализа.\n"
            "Оно должно быть уникальным и желательно содержать регион и сегодняшнюю дату "
            '(например, "Орск 31.08.2023", "Новотроицк и Омск 31.08.2023")'
        )
        timezone = datetime.timezone(datetime.timedelta(hours=3))
        date_now = datetime.datetime.now(timezone)
        date_str = date_now.strftime("%d.%m.%Y")

        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media(f"{region} {date_str}"),
        )
        await state.set_state(structures_fsm.MediaCreateStates.get_name)

    async def __on_error_get_is_method(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        response_text = aiogram_utils_formatting.Text(
            'Необходимо указать "Да" или "Нет".\n\n',
        )
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media("Да", "Нет"),
        )
        await state.set_state(structures_fsm.MediaCreateStates.get_is_parsing_comments)

    @classmethod
    def __get_date_from_text(cls, date_text: str):
        timezone = datetime.timezone(offset=datetime.timedelta(hours=3))
        for date_format in media_models.DT_DATETIME_AVAILABLE_FORMATS:
            try:
                date = datetime.datetime.strptime(date_text, date_format)
            except ValueError:
                pass
            else:
                break
        else:
            raise ValueError("Date is not in available formats")
        date = date.replace(tzinfo=timezone)
        return date

    @classmethod
    def __get_available_date_formats_with_examples_message(cls) -> aiogram_utils_formatting.Text:
        date_formats_line = "\n".join(media_models.DT_DATETIME_AVAILABLE_FORMATS)
        timezone = datetime.timezone(offset=datetime.timedelta(hours=3))
        date_formats_examples = aiogram_utils_formatting.as_list(
            *(
                aiogram_utils_formatting.Code(datetime.datetime.now(tz=timezone).strftime(date_format))
                for date_format in media_models.DT_DATETIME_AVAILABLE_FORMATS
            ),
            sep="\n",
        )
        response_text = aiogram_utils_formatting.Text(
            f"Укажите дату в одном из форматов:\n{date_formats_line}\n\n" f"Примеры:\n", date_formats_examples
        )
        return response_text
