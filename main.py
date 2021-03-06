import asyncio
import logging.config
import aiohttp
from aiohttp_proxy import ProxyConnector

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook, start_polling
from config import API_TOKEN, WEBHOOK_HOST, WEBHOOK_PATH, WEBAPP_PORT, admins
from db import db_init, Url
from logger_config import logger_config
from parse import get_data
from tor_connection import new_connection

WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = 'localhost'

logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

waiting_add = []
waiting_del = []
waiting_time = []

available_products = {}
sleep_time = 2


def del_actions(tg_id):
    if tg_id in waiting_del:
        waiting_del.remove(tg_id)

    if tg_id in waiting_add:
        waiting_add.remove(tg_id)

    if tg_id in waiting_time:
        waiting_time.remove(tg_id)


async def send_info(data, del_size=None, new_size=None):
    if len(data) == 2:
        text = f'''Товар "{data[0]}"[{data[1]}] исчез из продажи'''
    elif len(data) == 4:
        sizes = 'sizes'
        text = f'''Товар "{data[0]}"[{data[1]}]
Размеры: {data[2]}
{sizes}
{data[3]}
'''
        if not del_size and not new_size:
            text = f'''Товар "{data[0]}"[{data[1]}] появился в наличии.
Размеры: {data[2]}
{data[3]}'''

        else:
            size_str = ''
            if del_size:
                size_str = 'Исчезли из продажи:'
                for size in del_size:
                    size_str += size + ' '

                if new_size:
                    size_str += '''
'''

            if new_size:
                size_str += 'Появились в продаже:'
                for size in new_size:
                    size_str += size + ' '

            text = text.format(sizes=size_str)

    else:
        return

    for admin in admins:
        await bot.send_message(admin, text)


async def parse_url(url: Url, proxy, proxy_auth):
    try:
        data = await get_data(url, proxy, proxy_auth)
    except Exception as ex:
        data = ()
        print(ex)
        logger.exception(ex)

    if len(data) == 2:
        if url.url in available_products:
            available_products.pop(url.url)
            await send_info(data)

    elif len(data) == 3:
        old_size_list = available_products.get(url.url)
        if old_size_list is not None:
            deleted_size_list = set(old_size_list) - set(data[2])
            new_size_list = set(data[2]) - set(old_size_list)
            await send_info(data, deleted_size_list, new_size_list)

        else:
            available_products[url.url] = data[2]
            data.append(url.url)
            await send_info(data)


async def parse_cycle():
    proxies_old = [
        ("213.166.75.128", "9357", "kut1RP", "2p0SDV"),
        ("213.166.73.115", "9528", "kut1RP", "2p0SDV"),
        ("213.166.73.121", "9005", "kut1RP", "2p0SDV"),
        ("213.166.73.21", "9585", "kut1RP", "2p0SDV"),
        ("213.166.74.118", "9188", "kut1RP", "2p0SDV"),
        ("194.67.218.97", "9494", "kut1RP", "2p0SDV"),
        ("194.67.215.27", "9940", "kut1RP", "2p0SDV"),
        ("194.67.213.84", "9821", "kut1RP", "2p0SDV"),
        ("194.67.217.137", "9491", "kut1RP", "2p0SDV"),
        ("194.67.216.82", "9532", "kut1RP", "2p0SDV")
    ]
    
    proxies = (
        ("186.65.115.199", "9918", "3VXHhu", "KjJBaM"),
        ("186.65.114.242", "9140", "3VXHhu", "KjJBaM"),
        ("186.65.117.3", "9107", "3VXHhu", "KjJBaM"),
        ("186.65.114.225", "9715", "3VXHhu", "KjJBaM"),
        ("186.65.117.222", "9780", "3VXHhu", "KjJBaM"),
        ("138.59.206.102", "9492", "3VXHhu", "KjJBaM"),
        ("138.59.205.211", "9675", "3VXHhu", "KjJBaM"),
        ("138.59.207.16", "9907", "3VXHhu", "KjJBaM"),
        ("138.59.204.78", "9187", "3VXHhu", "KjJBaM"),
        ("138.59.206.152", "9248", "3VXHhu", "KjJBaM")
    )

    i = 0
    while True:
        prox = proxies[i % len(proxies)]

        proxy = f'http://{prox[0]}:{prox[1]}'
        proxy_auth = aiohttp.BasicAuth(prox[2], prox[3])
        urls = await Url.all()
        for url in urls:
            loop = asyncio.get_running_loop()
            loop.create_task(parse_url(url, proxy, proxy_auth))

        await asyncio.sleep(sleep_time)
        i += 1


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    if message.from_user.id not in admins:
        return

    text = '''
/add - Добавить url
/del - Удалить url
/cancel - Отменить действие
/list - Список url
/time - Изменить задержку'''

    await message.answer(text)


@dp.message_handler(commands=['add'])
async def add_command(message: types.Message):
    if message.from_user.id not in admins:
        return

    del_actions(message.from_user.id)
    waiting_add.append(message.from_user.id)

    await message.answer('Введите url для добавления:')


@dp.message_handler(commands=['del'])
async def del_command(message: types.Message):
    if message.from_user.id not in admins:
        return

    del_actions(message.from_user.id)
    waiting_del.append(message.from_user.id)

    await message.answer('Введите url для удаления:')


@dp.message_handler(commands=['cancel'])
async def cancel_command(message: types.Message):
    tg_id = message.from_user.id
    if tg_id not in admins:
        return

    del_actions(tg_id)

    await message.answer('Действие отменено')


@dp.message_handler(commands=['test'])
async def test_ip_command(message: types.Message):
    if message.from_user.id not in admins:
        return
    new_connection()
    connector = ProxyConnector.from_url('socks5://127.0.0.1:9050')
    async with aiohttp.ClientSession(connector=connector) as session:
        response = await session.get(
            'http://httpbin.org/ip'
            )
        result = await response.text()

    await message.answer(result)


@dp.message_handler(commands=['list'])
async def list_command(message: types.Message):
    if message.from_user.id not in admins:
        return

    urls = await Url.all()
    text = ''

    for url in urls:
        row = str(url.id) + '. ' + url.url + '''
-------------------------
'''
        text += row

    if text == '':
        text = 'Нет ни одного url'

    await message.answer(text)


@dp.message_handler(commands=['time'])
async def time_command(message: types.Message):
    if message.from_user.id not in admins:
        return

    del_actions(message.from_user.id)
    waiting_time.append(message.from_user.id)
    text = f'''Сейчас задержка составляет {sleep_time} секунд.
Введите задержку в секундах:'''

    await message.answer(text)


@dp.message_handler()
async def listen_url(message: types.Message):
    global sleep_time
    tg_id = message.from_user.id
    if tg_id not in admins:
        return

    if tg_id in waiting_add:
        try:
            await Url.create(url=message.text)
        except Exception as e:
            print(e)
            await message.answer(f'Такой url уже существует')
        else:
            await message.answer(f'Url добавлен')

    elif tg_id in waiting_del:
        try:
            try:
                url_id = int(message.text)
            except ValueError:
                url = await Url.get(url=message.text)
            else:
                url = await Url.get(id=url_id)
            await url.delete()
        except Exception as e:
            await message.answer('Такого url не существует')
        else:
            await message.answer('Url удален')

    elif tg_id in waiting_time:
        try:
            time = int(message.text)
            sleep_time = time
        except Exception as e:
            await message.delete()
        else:
            await message.answer('Задержка изменена')

    else:
        await message.delete()

    del_actions(message.from_user.id)


async def on_startup(dp):
    await db_init()
    #await bot.set_webhook(WEBHOOK_URL)
    loop = asyncio.get_running_loop()
    loop.create_task(parse_cycle())
    print('start')


async def on_shutdown(dp):
    logger.warning('Shutting down..')
    #await bot.delete_webhook()
    logger.warning('Bye!')


if __name__ == '__main__':
    while True:
        try:
            start_polling(
                dp,
                skip_updates=True,
                on_startup=on_startup,
                on_shutdown=on_shutdown,
            )
        except Exception as e:
            print(e)
            logger.exception('STOP_WEBHOOK')
