import requests
import bs4
from pprint import pprint
import json
import time
import urllib3
import ssl
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context


def get_splits_player(id_player):
    result = {}
    url = 'http://www.espn.com/nba/player/splits/_/id/' + str(id_player) + '/'
    r = requests.get(url, verify=False)
    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    tables = None
    i = 0
    while tables is None or i < 10:
        tables = soup.find_all(class_="Table__TBODY")
        i += 1
    if tables is None or len(tables) < 2:
        return {}
    stats_title = tables[0]
    stats_data = tables[1]
    rows_stats_title = stats_title.find_all("tr", class_="Table__TR")
    # rows_stats_title = iter(rows_stats_title)
    index_stats = {}
    for row in rows_stats_title:
        if row.find('td', class_='fw-medium') is None:
            index_stats[int(row['data-idx'])] = row.find(class_="Table__TD").text\
                .lower().strip().replace('road', 'away').replace('.', '')
            # print(row['data-idx'])
            # print(row.find(class_="Table__TD").text)

    rows_stats_data = stats_data.find_all("tr", class_="Table__TR")
    stats = {}
    for row in rows_stats_data:
        if row.find('td', class_='fw-medium') is None:
            stats[index_stats[int(row['data-idx'])]] = \
                [td.text for td in row.find_all('td') if td.text]
    return stats


# #test
# with open('../../../data/players_nba_espn.json') as p:
#     players = json.load(p)

# len_ = len(players)
# index = 1
# for p, id_p in players.items():
#     print(str(index) + ' of ' + str(len_))
#     print(p, id_p)
#     get_splits_player(id_p)
#     index += 1
