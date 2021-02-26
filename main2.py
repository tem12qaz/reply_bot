import logging

from aiogram import executor
from aiohttp import web

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher

from bot import run_bot
from config import API_TOKEN, WEBHOOK_HOST, tokens

WEBHOOK_URL = f"{WEBHOOK_HOST}/{API_TOKEN}"
WEBHOOK_URL2 = f"{WEBHOOK_HOST}/{tokens[0]}"
WEBAPP_HOST = 'localhost'
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


bot2 = Bot(token=tokens[0], parse_mode=types.ParseMode.HTML)
dp2 = Dispatcher(bot2)

c = 0
app = web.Application()
z = True


# @dp.message_handler(commands=['newbot'])
# async def send_welcome(message: types.Message):
#     global c
#     token = tokens[c]
#     c += 1
#     route_name = 'webhook_bot' + str(c)
#     app.router._frozen = False
#     run_bot(app, token, WEBHOOK_HOST, c, route_name)
#     for func in app.on_startup_function:
#         await func(1)
#     app.router._frozen = True
#
#     await message.answer('Successful')


@dp.message_handler()
async def echo(message: types.Message):
    a = str(await bot.get_me())
    print('hello_main')
    text = message.text
    await message.answer(a)
    await message.answer(text)


@dp2.message_handler()
async def echo(message: types.Message):
    a = str(await bot.get_me())
    print('hello_main')
    text = message.text
    await message.answer(a)
    await message.answer(text)



async def on_startup(dp):
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(dp):
    logging.warning('Shutting down..')
    await bot.delete_webhook()
    logging.warning('Bye!')


async def on_startup2(dp2):
    await bot2.delete_webhook()
    await bot2.set_webhook(WEBHOOK_URL2)


async def on_shutdown2(dp2):
    logging.warning('Shutting down..')
    await bot2.delete_webhook()
    logging.warning('Bye!')


if __name__ == '__main__':
    custom_executor = executor.set_webhook(
        dispatcher=dp,
        webhook_path='/'+API_TOKEN,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        web_app=app,
        route_name='main_webhook'
    )
    custom_executor2 = executor.set_webhook(
        dispatcher=dp2,
        webhook_path='/' + tokens[0],
        on_startup=on_startup2,
        on_shutdown=on_shutdown2,
        skip_updates=True,
        web_app=app,
        route_name='one_webhook'
    )
    web.run_app(app)
