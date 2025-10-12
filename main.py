import ast
import os

from aiogram import types
from aiogram.webhook.aiohttp_server import setup_application, SimpleRequestHandler
from aiohttp.web_app import Application
from aiohttp.web import run_app

from dotenv import load_dotenv

from conf.conf import client, dp, storage

load_dotenv()

PRODUCTION = ast.literal_eval(os.getenv('PRODUCTION'))

BOT_SETTINGS = None


async def delete_webhook():
    print("Delete webhook\n")
    # await start_build()
    await client.delete_webhook()


async def set_webhook():
    print("Set webhook\n")
    await client.set_webhook(
        url=os.getenv('PRODUCTION_URL'),
        # secret_token=os.getenv('TELEGRAM_SECRET_TOKEN'),
    )


async def set_commands():
    commands = [
        types.BotCommand(command='start', description='Главное меню'),
        types.BotCommand(command='receipt', description='Создать чек'),
        types.BotCommand(command='search', description='Глаз бога'),
    ]
    await client.set_my_commands(commands)


def start_development() -> None:
    dp.startup.register(delete_webhook)
    print("Starting DEVELOPMENT BOT")
    dp.run_polling(client)


def start_production() -> None:
    print("Starting PRODUCTION BOT\n")
    dp.startup.register(delete_webhook)
    dp.startup.register(set_webhook)
    app = Application()
    app["bot"] = client
    SimpleRequestHandler(
        dispatcher=dp,
        bot=client,
    ).register(app, path="/telegram/api/")
    setup_application(app, dp, bot=client)
    run_app(app, host="0.0.0.0", port=8000)


if __name__ == '__main__':
    dp.startup.register(set_commands)
    from conf.middlewares import auth_middleware

    import src.callbacks.positions.func as callbacks_positions

    import src.index.func as index
    import src.index.menu.pnl.func as index_pnl

    import src.index.menu.settings.ban.func as index_settings_ban

    import src.index.menu.analiz.func as index_analiz

    import src.glaz.func as glaz
    import src.receipt.func as receipt

    if PRODUCTION:

        start_production()

    else:

        start_development()