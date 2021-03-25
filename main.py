import logging.config

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ChatType
from aiogram.utils.executor import start_webhook
from config import API_TOKEN, WEBHOOK_HOST, WEBHOOK_PATH, WEBAPP_PORT, CHAT_ID, admins
from db import db_init, Chat
from logger_config import logger_config

WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = 'localhost'

logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

waiting_message = []


@dp.message_handler(chat_type=[ChatType.SUPERGROUP, ChatType.GROUP])
async def echo(message: types.Message):
    if message.chat.id == CHAT_ID:
        return
    try:
        last_name = message.from_user.last_name
    except AttributeError:
        last_name = message.from_user.username

    chat = await Chat.get_or_none(telegram_id=message.chat.id)
    if chat is None:
        await Chat.create(telegram_id=message.chat.id)

    text = f'''<i>Из чата: </i> <b>"{message.chat.title}"</b>
<i>От: </i> <b>"{message.from_user.first_name} {last_name}"</b>
{message.text}'''

    await bot.send_message(chat_id=CHAT_ID, text=text)


@dp.message_handler(commands=['send'], chat_type=[ChatType.PRIVATE])
async def send_command(message: types.Message):
    if message.from_user.id not in admins:
        return

    waiting_message.append(message.from_user.id)
    await message.answer('Введите тест сообщения:')


@dp.message_handler(chat_type=[ChatType.PRIVATE])
async def listen_message_text(message: types.Message):
    tg_id = message.from_user.id
    if tg_id not in admins or tg_id not in waiting_message:
        return

    chats = await Chat.all()
    for chat in chats:
        await bot.send_message(str(chat.telegram_id), message.text)

    waiting_message.remove(message.from_user.id)
    await message.answer(f'Отправлено в {len(chats)} чатов')


async def on_startup(dp):
    await db_init()
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(dp):
    logger.warning('Shutting down..')
    await bot.delete_webhook()
    logger.warning('Bye!')


if __name__ == '__main__':
    try:
        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )
    except Exception as e:
        logger.exception('STOP_WEBHOOK')



