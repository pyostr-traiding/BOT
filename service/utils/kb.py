from typing import Union, List, Optional, Any
from aiogram import types
from pydantic import BaseModel

class KBReturn(BaseModel):
    reply: Union[types.ReplyKeyboardMarkup, types.InlineKeyboardMarkup]
    values: Optional[List[str]] = None

    @classmethod
    def from_keyboard(cls, keyboard: Union[types.ReplyKeyboardMarkup, types.InlineKeyboardMarkup],
                      extra_values: Optional[List[str]] = None):
        values: List[str] = []

        if isinstance(keyboard, types.ReplyKeyboardMarkup):
            for row in keyboard.keyboard:
                for button in row:
                    values.append(button.text)
        elif isinstance(keyboard, types.InlineKeyboardMarkup):
            for row in keyboard.inline_keyboard:
                for button in row:
                    values.append(button.text)

        if extra_values:
            values.extend(extra_values)

        return cls(reply=keyboard, values=values)

def chunk_list(lst: List[Any], n: int) -> List[List[Any]]:
    """
    Разбивает список lst на подсписки длиной n.
    Последний подсписок может содержать меньше элементов.
    """
    return [lst[i:i + n] for i in range(0, len(lst), n)]