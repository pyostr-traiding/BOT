from aiogram import types

from conf.conf import client
from conf.settings import settings


class MessageError(Exception):
    def __init__(self, text):
        self.txt = text


async def send_to_user(
        message: types.Message,
        images: list[str] = None,
        text: str = None,
        inline_keyboard: types.InlineKeyboardMarkup = None,
        reply_keyboard: types.ReplyKeyboardMarkup = None,
):
    """
    :param message:  aiogram.types.Message
    :param images: Список путей до фото
    :param text: Текст сообщения
    :param inline_keyboard:
    :param reply_keyboard:
    :return:
    """
    if not images and not text and not inline_keyboard and not reply_keyboard:
        raise MessageError('Нет данных для отправки')

    if inline_keyboard and reply_keyboard:
        raise MessageError('Можно передать только одну клавиатуру')
    # Медиа группа

    media = []
    if images and len(images) > 1:
        for count, image in enumerate(images):

            image = settings.PATH_MEDIA + image
            if count == 0 and text:
                media.append(types.InputMediaPhoto(media=types.URLInputFile(url=image)))
            else:
                media.append(types.InputMediaPhoto(media=types.URLInputFile(url=image)))
        await client.send_media_group(
            chat_id=message.from_user.id,
            media=media
        )
        if text:
            if inline_keyboard:
                keyboard = inline_keyboard
            else:
                keyboard = reply_keyboard
            if keyboard:
                await client.send_message(
                    chat_id=message.from_user.id,
                    text=text,
                    reply_markup=keyboard
                )
            else:
                await client.send_message(
                    chat_id=message.from_user.id,
                    text=text,
                )
        return

    # Одно фото
    if images and len(images) == 1:
        image = settings.PATH_MEDIA + images[0]
        if inline_keyboard:
            keyboard = inline_keyboard
        else:
            keyboard = reply_keyboard
        if keyboard:
            await client.send_photo(
                chat_id=message.from_user.id,
                photo=types.URLInputFile(url=image),
                caption=text,
                reply_markup=keyboard
            )
        else:
            await client.send_photo(
                chat_id=message.from_user.id,
                photo=types.URLInputFile(url=image),
                caption=text,
            )
        return

    # Текст
    if not images:
        if inline_keyboard:
            keyboard = inline_keyboard
        else:
            keyboard = reply_keyboard
        if keyboard:
            await client.send_message(
                chat_id=message.from_user.id,
                text=text,
                reply_markup=keyboard
            )
        else:
            await client.send_message(
                chat_id=message.from_user.id,
                text=text,
            )
        return