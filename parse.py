import aiohttp
from fake_useragent import UserAgent
from bs4 import BeautifulSoup as bs4

from db import Url

user_agent = UserAgent()


async def get_data(url: Url):
    async with aiohttp.ClientSession() as session:
        response = await session.get(
            url.url,
            headers={'User-Agent': user_agent.random}
        )
        result = await response.text()

    soup = bs4(result, 'html.parser')
    size_div = soup.find('div', class_="product-size-selector__size-list-wrapper")

    size_list = size_div.find_all("li", 'product-size-selector__size-list-item')
    out_of_stock_size_list = size_div.find_all("li", 'product-size-selector__size-list-item--is-disabled')
    size_list = list(set(size_list) - set( out_of_stock_size_list))

    name = soup.find("h1", class_="product-detail-info__name").text
    num = soup.find("p", class_="product-detail-selected-color").text.split('|')[1].replace(' ', '')

    if not size_list:
        data = (name, num)
        return data

    size_text = ''
    for size in size_list:
        size_text += size.find("span", class_="product-size-info__main-label").text
        if size != size_list[-1]:
            size_text += ', '

    data = [name, num, size_text]

    return data




