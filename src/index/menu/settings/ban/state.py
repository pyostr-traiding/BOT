from aiogram.fsm.state import StatesGroup, State


class SettingsState(StatesGroup):
    input_choice = State()
    input_choice_ban = State()

    input_choice_ban_new_value = State()
