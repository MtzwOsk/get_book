import requests
import math

from bs4 import BeautifulSoup as bs


query_params = {
    'request': 'Romeo i Julia',
    'func': 'find-b',
    'find_code': 'WTI',
    'adjacent': 'Y',
    'local_base': 'SROBK',
}

BEGIN_COUNTER: int = 11
TABLE_PAGINATION: int = 10


def get_number_of_tables(soup):
    books_number = int(list(filter(None, soup.find(class_='text3').text.split(' ')))[6])  # math.ceil
    return math.ceil(books_number/TABLE_PAGINATION)


def create_soup(html):
    return bs(html, 'html.parser')


def main():
    session = requests.Session()
    
    response = session.get('https://aleph.koszykowa.pl/F', params=query_params)
    soup = bs(response.text, 'html.parser')
    
    meta_tags = soup.find_all('meta')
    for meta in meta_tags:
        if meta.attrs.get('http-equiv') == 'Set-Cookie':
            key, value, *_ = meta.attrs.get('content').replace(' = ', ';').split(';')
            print(key)
            session.cookies.set(key, value)
    
    tables_number = get_number_of_tables(soup)
    urls = [f'https://aleph.koszykowa.pl/F?func=short-jump&jump={BEGIN_COUNTER+10*number}' for number in range(tables_number)]
    
    for url in urls:
        resp = session.get(url)
        resp.encoding = resp.apparent_encoding
        table_soup = create_soup(resp.text)
        table = table_soup.find(id='short_table')
        if not table:
            title = soup.find('div', class_='text3')
            print(title.text)
    print(table_soup)


if __name__ == '__main__':
    import time
    start = time.time()
    main()
    print(time.time() - start)
