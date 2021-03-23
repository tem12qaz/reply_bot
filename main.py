import logging.config

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ChatType
from aiogram.utils.executor import start_webhook
from config import API_TOKEN, WEBHOOK_HOST, WEBHOOK_PATH, WEBAPP_PORT, CHAT_ID
from logger_config import logger_config

WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = 'localhost'

logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler(chat_type=[ChatType.SUPERGROUP, ChatType.GROUP])
async def echo(message: types.Message):
    if message.chat.id == CHAT_ID:
        return
    try:
        last_name = message.from_user.last_name
    except AttributeError:
        last_name = message.from_user.username

        text = f'''<i>Из чата: </i> <b>"{message.chat.title}"</b>
    <i>От: </i> <b>"{message.from_user.first_name} {last_name}"</b>
    {message.text}'''

        await bot.send_message(chat_id=CHAT_ID, text=text)

    async def on_startup(dp):
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