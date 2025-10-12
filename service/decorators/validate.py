import functools
from aiogram import types
from aiogram.fsm.context import FSMContext
from conf.conf import client


def validate_keyboard(value: str):
    """
    Декоратор для проверки, что текст сообщения есть среди допустимых значений из state.
    Если ключ отсутствует или значение 'stop', декоратор пропускает проверку.
    """

    def decorator(function):

        @functools.wraps(function)
        async def wrapper(message: types.Message,
                          state: FSMContext = None,
                          *args, **kwargs):

            data = await state.get_data()
            valid_values = data.get(value)  # безопасно получаем список значений

            if valid_values:
                if message.text not in valid_values:
                    await client.send_message(
                        chat_id=message.from_user.id,
                        text=(
                            'Выберите на клавиатуре!'
                        ),
                    )
                    return  # прерываем выполнение хэндлера

            return await function(message=message, state=state, *args, **kwargs)

        return wrapper
    return decorator
