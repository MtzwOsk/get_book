import requests
from bs4 import BeautifulSoup as bs

BEGIN_COUNTER: int = 11


def has_valign(tag):
    return tag.get('valign', '') == 'baseline'

query_params = {
    'func': 'find-b',
    'request': 'Romeo i Julia',  # TITLE
    'find_code': 'WTI',
    'adjacent': 'Y',
    'local_base': 'SROBK',
}


s = requests.session()
response = s.get('https://aleph.koszykowa.pl/F', params=query_params)


response.encoding = response.apparent_encoding
soup = bs(response.text, "html.parser")
books_number = int(list(filter(None, soup.find(class_='text3').text.split(' ')))[6])  # math.ceil
table = soup.find(id='short_table')

libraries = []
rows = table.find_all(has_valign)
for row in rows:
    library_name_row = row.find_all('td')[-1]
    libraries_a_tags = library_name_row.find_all('a')
    [libraries.append(library_name.text) for library_name in libraries_a_tags]


for library in libraries:
    name, _ = library.split('(')
    print(name)


res = s.get('https://aleph.koszykowa.pl/F?func=short-jump&jump=000021')
table = bs(res.text, "html.parser").find(id='short_table')