import traceback
import requests
import json
import codecs
import time
from json import JSONDecodeError
from datetime import datetime
from key import *


def collecting_items():
    list_items = []
    white_list = ["Doppler", "Case Hardened", "Fade1 "]
    url = "https://market.csgo.com/api/v2/prices/class_instance/RUB.json"
    api = requests.get(url)
    data = json.loads(api.text)
    count_items = len(data['items'])
    for item in data['items']:
        if (any(words in data['items'][item]['market_hash_name'] for words in white_list)
                and data['items'][item]['price'] and data['items'][item]['avg_price']
                and float(data['items'][item]['avg_price']) > 40):
            name_and_price = [data['items'][item]['market_hash_name'], data['items'][item]['avg_price']]
            list_items.append(name_and_price)
    print(f"Всего предметов было {count_items}, а осталось {len(list_items)}")
    return list_items


def phase_parser(names_list):
    dict_name_avg = {}
    link_items = ""
    list_items = []
    items_counter = 0
    for item in names_list:
        if items_counter < 45:
            items_counter += 1
            item_hash_name = item[0]
            item_avg = item[1]
            dict_name_avg.update({item_hash_name: item_avg})
            link_items += "&list_hash_name[]=" + item_hash_name
        else:
            url_item = f"https://market.csgo.com/api/v2/search-list-items-by-hash-name-all?key={api_key}{link_items}"
            link_items = ""
            items_counter = 0
            item_status = requests.get(url_item)
            current_items = json.loads(item_status.text)
            for item_name in current_items['data'].keys():
                for item_info in current_items['data'][item_name]:
                    if item_info['extra'] and 'phase' in item_info['extra'].keys():
                        item_link = ""
                        item_seed = "None"
                        item_float = "None"
                        item_phase = item_info['extra']['phase']
                        if item_info['extra'] and 'float' in item_info['extra'].keys():
                            item_float = item_info['extra']['float']
                        item_price = float(item_info['price']) / 100
                        item_avg_price = float(dict_name_avg[item_name])
                        list_items.append([item_name, item_link, item_float, item_seed, item_phase, item_price, item_avg_price])


if __name__ == "__main__":
    list_items = collecting_items()
    phase_parser(list_items)
