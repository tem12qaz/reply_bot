import logging

from aiogram import executor
from aiohttp import web

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher

from bot import run_bot
from config import API_TOKEN, WEBHOOK_HOST, tokens

WEBHOOK_URL = f"{WEBHOOK_HOST}/{API_TOKEN}"
WEBAPP_HOST = 'localhost'
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
c = 0


@dp.message_handler(commands=['newbot'])
async def send_welcome(message: types.Message):
    global c
    token = tokens[c]
    c += 1
    try:
        run_bot(dp, token, token, WEBHOOK_HOST, c)
    except Exception as e:
        text = 'Error ' + str(e)
        await message.answer(text)
        return

    await message.answer('Successful')

app = web.Application()

@dp.message_handler()
async def echo(message: types.Message):
    text = 'Я главный бот! ' + message.text
    await message.answer(text)


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(dp):
    logging.warning('Shutting down..')
    await bot.delete_webhook()
    logging.warning('Bye!')


if __name__ == '__main__':
    custom_executor = executor.set_webhook(
        dispatcher=dp,
        webhook_path='/'+API_TOKEN,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        web_app=app
    )
    custom_executor.run_app()
