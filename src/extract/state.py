from aiogram.fsm.state import StatesGroup, State


class ExtractState(StatesGroup):
    input_file = State()
    input_text = State()
