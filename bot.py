from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor


def run_bot(app, token, WEBHOOK_HOST, c, route_name):
    WEBAPP_HOST = 'localhost'
    WEBHOOK_URL = f"{WEBHOOK_HOST}/{token}"
    bot = Bot(token=token)
    dp = Dispatcher(bot)

    @dp.message_handler()
    async def echo(message: types.Message):
        print('hello_one')
        text = 'Я бот ' + str(c) + ' ! ' + message.text
        await message.answer(text)


    async def on_startup(dp):
        await bot.set_webhook(WEBHOOK_URL)


    async def on_shutdown(dp):
        await bot.delete_webhook()

    new_executor = executor.set_webhook(
        dispatcher=dp,
        webhook_path='/'+token,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        web_app=app,
        route_name=route_name,
        webhook_run=0
    )
