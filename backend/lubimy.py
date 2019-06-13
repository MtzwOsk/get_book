import json

import requests
from requests import Request
from bs4 import BeautifulSoup as bs


def get_book_titles_list():
    USER_ID = 295119
    USER_NAME = 'tomekosk'
    source_url = f'http://lubimyczytac.pl/profil/{USER_ID}/{USER_NAME}/biblioteczka/szczegoly'
    
    
    s = requests.session()
    response = s.get(source_url, headers={'X-Requested-With': 'XMLHttpRequest'})
    
    soup = bs(response.text, "html.parser")
    shelf_want_read = soup.find('a', text='Chcę przeczytać')
    shelf_id = shelf_want_read.attrs.get('data-shelf-id')
    book_to_read_num = shelf_want_read.parent.find(attrs={'data-shelf-id-counter': shelf_id}).text
    
    
    AJAX_URL = 'http://lubimyczytac.pl/profile/getNextBookFromList/json/0/1/1'
    data_args = {
        'page': 1,
        'amountBooks': book_to_read_num,
        'porzadek': 'malejaco',
        'akcja': '',
        'filtr': '',
        'kolejnosc': 'data-przeczytania',
        'czas': '',
        'ilosc': book_to_read_num,
        'viewType': 'miniatury',
        'shelf': shelf_id,
        'isMainShelf': '',
        'emptyText': 'Dupa',
        'ajaxUrl': 'profile/getNextBookFromList/json/0/1/1',
        'accountId': USER_ID,
        'szukaj': '',
    }
    
    req = Request('GET', AJAX_URL, params=data_args, headers={'X-Requested-With': 'XMLHttpRequest'})
    prepped = req.prepare()
    
    resp = s.send(prepped, timeout=15)
    
    # print(resp.status_code)
    # clear_resp = re.sub(r'\\n|\\t|\\', '', resp.text)
    new_soup = bs(json.loads(resp.text).get('html'), "html.parser")
    
    # imgs = new_soup.find_all('img')
    # print(len(imgs))
    
    shelves = new_soup.find_all('div', 'library-shelf')
    
    titles = []
    for shelf in shelves:
        
        # assumption that every book has title in alt on image
        books_in_shelf = shelf.find_all(class_='tipFixed')
        for book in books_in_shelf:
            # book_description = book.find(class_='tipFixed')
            # titles.append({'title': book.find('strong').text,
            #                'author': book.find('br').next})
    
            [titles.append(book.find('strong').text) for book in books_in_shelf]
    return titles
