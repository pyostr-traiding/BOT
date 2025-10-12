from aiogram.fsm.state import StatesGroup, State


class ReceiptState(StatesGroup):
    from_bank = State()
    bank = State()
    phone = State()
    amount = State()
    name = State()
