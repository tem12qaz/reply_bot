from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor


def run_bot(dp, app, API_TOKEN, WEBHOOK_HOST, c):
    WEBAPP_HOST = 'localhost'
    WEBHOOK_URL = f"{WEBHOOK_HOST}/{API_TOKEN}"
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot)

    @dp.message_handler()
    async def echo(message: types.Message):
        text = 'Я бот ' + c + ' ! ' + message.text
        await message.answer(text)


    async def on_startup(dp):
        await bot.set_webhook(WEBHOOK_URL)

    async def on_shutdown(dp):
        await bot.delete_webhook()

    custom_executor = executor.set_webhook(
        dispatcher=dp,
        webhook_path='/'+API_TOKEN,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        web_app=app
    )
