from aiogram.fsm.state import StatesGroup, State


class GlazState(StatesGroup):
    string_input = State()
