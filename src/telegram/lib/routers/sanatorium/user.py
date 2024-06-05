import datetime

import aiogram
import aiogram.filters as aiogram_filters
import aiogram.fsm.context as aiogram_fsm_context
import aiogram.utils.formatting as aiogram_utils_formatting
import pydantic

import lib.filters as structures_filters
import lib.routers.utils as routers_utils
import lib.sanatorium.models as _sanatorium_models
import lib.sanatorium.services as _sanatorium_services
import lib.structures.fsm as structures_fsm
import lib.structures.keyboards as structures_keyboards


class UserCreateRouter:
    def __init__(
        self,
        router: aiogram.Router,
        user_service: _sanatorium_services.UserService,
    ):
        self.router = router
        self._user_service = user_service

        self.register()

    def register(self):
        self.router.message.register(
            self.on_get_first_name,
            aiogram.F.text.lower() == "зарегистрироваться",
        )
        self.router.message.register(
            self.on_get_last_name,
            aiogram.F.text.as_("first_name"),
            aiogram_filters.StateFilter(structures_fsm.UserStates.get_first_name),
        )
        self.router.message.register(
            self.on_get_passport_series,
            aiogram.F.text.as_("last_name"),
            aiogram_filters.StateFilter(structures_fsm.UserStates.get_last_name),
        )
        self.router.message.register(
            self.on_get_passport_number,
            aiogram.F.text.as_("passport_series"),
            aiogram_filters.StateFilter(structures_fsm.UserStates.get_passport_series),
        )
        self.router.message.register(
            self.on_get_medical_policy,
            aiogram.F.text.as_("passport_number"),
            aiogram_filters.StateFilter(structures_fsm.UserStates.get_passport_number),
        )
        self.router.message.register(
            self.on_get_birth_date,
            aiogram.F.text.as_("medical_policy"),
            aiogram_filters.StateFilter(structures_fsm.UserStates.get_medical_policy),
        )
        self.router.message.register(
            self.on_confirmation,
            aiogram.F.text.as_("birth_date"),
            aiogram_filters.StateFilter(structures_fsm.UserStates.get_birth_date),
        )
        self.router.message.register(
            self.create_user_final,
            aiogram.F.text.lower() == "подтвердить",
            aiogram_filters.StateFilter(structures_fsm.UserStates.confirmation),
        )

    async def on_get_first_name(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        response_text = aiogram_utils_formatting.Text("Введите своё имя")
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media(),
        )
        await state.set_state(structures_fsm.UserStates.get_first_name)

    async def on_get_last_name(
        self,
        message: aiogram.types.Message,
        first_name: str,
        state: aiogram_fsm_context.FSMContext,
    ):
        await state.update_data(first_name=first_name)

        response_text = aiogram_utils_formatting.Text("Введите свою фамилию")
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media(),
        )
        await state.set_state(structures_fsm.UserStates.get_last_name)

    async def on_get_passport_series(
        self,
        message: aiogram.types.Message,
        last_name: str,
        state: aiogram_fsm_context.FSMContext,
    ):
        await state.update_data(last_name=last_name)

        response_text = aiogram_utils_formatting.Text("Введите серию паспорта")
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media(),
        )
        await state.set_state(structures_fsm.UserStates.get_passport_series)

    async def on_get_passport_number(
        self,
        message: aiogram.types.Message,
        passport_series: str,
        state: aiogram_fsm_context.FSMContext,
    ):
        await state.update_data(passport_series=passport_series)

        response_text = aiogram_utils_formatting.Text("Введите номер паспорта")
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media(),
        )
        await state.set_state(structures_fsm.UserStates.get_passport_number)

    async def on_get_medical_policy(
        self,
        message: aiogram.types.Message,
        passport_number: str,
        state: aiogram_fsm_context.FSMContext,
    ):
        await state.update_data(passport_number=passport_number)

        response_text = aiogram_utils_formatting.Text("Введите номер медицинского полиса")
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media(),
        )
        await state.set_state(structures_fsm.UserStates.get_medical_policy)

    async def on_get_birth_date(
        self,
        message: aiogram.types.Message,
        medical_policy: str,
        state: aiogram_fsm_context.FSMContext,
    ):
        await state.update_data(medical_policy=medical_policy)

        response_text = aiogram_utils_formatting.Text("Введите дату рождения (ГГГГ-ММ-ДД)")
        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media(),
        )
        await state.set_state(structures_fsm.UserStates.get_birth_date)

    async def on_confirmation(
        self,
        message: aiogram.types.Message,
        birth_date: str,
        state: aiogram_fsm_context.FSMContext,
    ):
        await state.update_data(birth_date=birth_date)
        user_data = await state.get_data()
        try:
            user_create_request = _sanatorium_models.UserInfoModel.model_validate(user_data)
        except pydantic.ValidationError as e:
            await message.answer(
                text=f"Ошибка при валидации данных: {e}\nИсправьте данные и попробуйте ещё раз.",
                reply_markup=structures_keyboards.create_kb_media(),
            )
            await self.on_get_first_name(message, state)
            return

        await message.answer(
            **user_create_request.get_info_text_formatted().as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media("Подтвердить"),
        )

        await state.set_state(structures_fsm.UserStates.confirmation)

    async def create_user_final(
        self,
        message: aiogram.types.Message,
        state: aiogram_fsm_context.FSMContext,
    ):
        if message.from_user is None:
            raise ValueError("User is None")

        user_data = await state.get_data()
        request = _sanatorium_models.UserInfoModel.model_validate(user_data)

        response_text = "Отлично! Создаю аккаунт..."

        await message.answer(
            text=response_text,
            reply_markup=structures_keyboards.create_kb_media(),
        )
        response = await self._user_service.create(request)

        response_text = aiogram_utils_formatting.Text(
            "Пользователь успешно создан!\n\n",
            response.get_info_text_formatted(),
        )

        await message.answer(
            **response_text.as_kwargs(),
            reply_markup=structures_keyboards.create_kb_media(),
        )

        await routers_utils.send_start_message(message, state)
