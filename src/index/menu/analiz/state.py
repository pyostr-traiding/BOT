from aiogram.fsm.state import StatesGroup, State


class AnalizState(StatesGroup):
    input_choice_action = State()
