from aiogram.fsm.state import StatesGroup, State


class PNLState(StatesGroup):
    input_pnl_period = State()
