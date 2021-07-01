import requests
import time

from stem import Signal
from stem.control import Controller as Controller


def get_tor_session():
    session = requests.session()
    session.proxies = {'http': 'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session


def new_connection():
    with Controller.from_port(port=9051) as C:
        C.authenticate(password='ttps://landscape.canonic')
        C.signal(Signal.NEWNYM)
