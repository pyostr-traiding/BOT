from aiogram.fsm.state import StatesGroup, State


class AddState(StatesGroup):
    input_username = State()
