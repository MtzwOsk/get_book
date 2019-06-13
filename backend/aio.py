import aiohttp
import asyncio
import math
import lxml

from yarl import URL
from bs4 import BeautifulSoup as bs

BEGIN_COUNTER: int = 11
TABLE_PAGINATION: int = 10


BASE_URL = 'https://aleph.koszykowa.pl/F'


def has_valign(tag):
    return tag.get('valign', '') == 'baseline'


def extend_session(session, soup):
    # cookies from HTML
    meta_tags = soup.find_all('meta')
    for meta in meta_tags:
        if meta.attrs.get('http-equiv') == 'Set-Cookie':
            key, value, *_ = meta.attrs.get('content').replace(' = ', ';').split(';')
            session.cookie_jar.update_cookies(
                {key: value},
                response_url=URL('https://aleph.koszykowa.pl'))

    
def get_library_name(soup):
    table = soup.find(id='short_table')
    if table:
        libraries = []
        rows = table.find_all(has_valign)
        for row in rows:
            library_name_row = row.find_all('td')[-1]
            libraries_a_tags = library_name_row.find_all('a')
            [libraries.append(library_name.text) for library_name in libraries_a_tags]
        
        for library in libraries:
            name, availability = library.split('(')
            number, lend = availability.replace(' ', '').replace(')', '').split('/')
            print(name, f'availability {number==lend}')
    else:
        print('Brak')


async def fetch(session, url, params=None):
    async with session.get(url, params=params) as response:
        response._content_type = 'text/html; charset=UTF-8'
        response_text = await response.text()
        soup = bs(response_text, 'html.parser')
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            if meta.attrs.get('http-equiv') == 'Set-Cookie':
                key, value, *_ = meta.attrs.get('content').replace(' = ', ';').split(';')
                session.cookie_jar.update_cookies(
                    {key: value},
                    response_url=URL('https://aleph.koszykowa.pl'))
        return response_text


async def fetch_table(session, url, params=None):
    async with session.get(url, params=params) as response:
        soup = create_soup(await response.text())
        get_library_name(soup)


def create_soup(html):
    return bs(html, 'lxml')


def get_number_of_tables(soup):
    try:
        books_number = int(list(filter(None, soup.find(class_='text3').text.split(' ')))[6])  # math.ceil
    except IndexError as error:
        print('Bad index')
        return
    return math.ceil(books_number/TABLE_PAGINATION)


# TODO do zmiany nazwa
async def get_books(title: str):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(force_close=True)) as session:
        query_params = {
            'func': 'find-b',
            'find_code': 'WTI',
            'adjacent': 'Y',
            'local_base': 'SROBK',
            # 'find_code': 'WAU',
            # 'request': 'Henryk Sienkiewicz',
        }
        query_params['request'] = title
        html = await fetch(session, BASE_URL, params=query_params)
        soup = create_soup(html)
        # get number from first page
        tables_number = get_number_of_tables(soup)
        if tables_number > 1:
            jumps = [{'func': 'short-jump', 'jump': BEGIN_COUNTER+10*number} for number in range(tables_number)]
            tables_request = [asyncio.ensure_future(fetch_table(session, BASE_URL, jump)) for jump in jumps]
            results = await asyncio.gather(*tables_request)
        return results
    

async def main(titles: list= None):
    title_request = [asyncio.ensure_future(get_books(title)) for title in titles]
    return await asyncio.gather(*title_request)

if __name__ == '__main__':
    import time
    start = time.time()
    results = asyncio.run(main(['Romeo i Julia', 'Ogniem i Mieczem', 'W pustyni i w puszczy']))
    print(time.time() - start)
