from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    get_first_name = State()
    get_last_name = State()
    get_passport_series = State()
    get_passport_number = State()
    get_medical_policy = State()
    get_birth_date = State()
    confirmation = State()
