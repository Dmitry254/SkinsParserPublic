import traceback
import requests
import json
import codecs
import time
from json import JSONDecodeError
from datetime import datetime
from key import *


def collecting_items():
    list_items1 = []
    list_items2 = []
    white_list = ["(Factory New)", "(Minimal Wear)", "(Field-Tested)", "(Well-Worn)", "(Battle-Scarred)"]
    url = "https://market.csgo.com/api/v2/prices/class_instance/RUB.json"
    api = requests.get(url)
    data = json.loads(api.text)
    run_counter = 0
    filtered_count_items = 0
    count_items = len(data['items'])
    for item in data['items']:
        if (any(words in data['items'][item]['market_hash_name'] for words in white_list)
                and data['items'][item]['price'] and data['items'][item]['avg_price']
                and float(data['items'][item]['avg_price']) > 50):
            name_and_price = [data['items'][item]['market_hash_name'], data['items'][item]['avg_price']]
            if len(list_items1) < 4000:
                list_items1.append(name_and_price)
            else:
                list_items2.append(name_and_price)
    print(f"Всего предметов {count_items}, а осталось в первом списке {len(list_items1)}, а во втором {len(list_items2)}")
    return list_items1, list_items2


def float_parser1(list_items):
    run_counter = 0
    for item in list_items:
        run_counter += 1
        try:
            item_name = item[0]
            item_avg = item[1]
            url_item = f"https://market.csgo.com/api/v2/search-list-items-by-hash-name-all?key={api_key}&list_hash_name[]=" \
                       f"{item_name}"
            item_status = requests.get(url_item)
            current_item = json.loads(item_status.text)
            float_value = 0
            if "(Factory New)" in item_name:
                float_value = 0.007
            elif "(Minimal Wear)" in item_name:
                float_value = 0.074
            elif "(Field-Tested)" in item_name:
                float_value = 0.154
            elif "(Well-Worn)" in item_name:
                float_value = 0.3802
            elif "(Battle-Scarred)" in item_name:
                float_value = 0.4502
            for item_info in current_item['data'][item_name]:
                if len(item_info['extra']) > 0 and 'float' in item_info['extra'].keys()\
                        and item_info['price'] and item_info['price'] != 0\
                        and (float(item_info['extra']['float']) < float_value or float(item_info['extra']['float']) > 0.98)\
                        and (float(item_info['price']) / 100) < float(item_avg):
                    item_buy = f"{item_name} с флоатом {item_info['extra']['float']}, ценой {float(item_info['price']) / 100}"
                    item_result = f"{item_buy} и средней ценой {item_avg}"
                    print(item_result)
        except:
            continue


def many_floats(list_items):
    link_items = ""
    items_counter = 0
    dict_name_avg = {}
    for item in list_items:
        try:
            if items_counter < 45:
                items_counter += 1
                item_hash_name = item[0]
                item_avg = item[1]
                dict_name_avg.update({item_hash_name: item_avg})
                link_items += "&list_hash_name[]=" + item_hash_name
            else:
                url_items = f"https://market.csgo.com/api/v2/search-list-items-by-hash-name-all?key={api_key}{link_items}"
                items_counter = 0
                link_items = ""
                items_status = requests.get(url_items)
                current_items = json.loads(items_status.text)
                for item_name in current_items['data'].keys():
                    try:
                        for item_info in current_items['data'][item_name]:
                            try:
                                float_value = 0
                                if "(Factory New)" in item_name:
                                    float_value = 0.007
                                elif "(Minimal Wear)" in item_name:
                                    float_value = 0.074
                                elif "(Field-Tested)" in item_name:
                                    float_value = 0.154
                                elif "(Well-Worn)" in item_name:
                                    float_value = 0.3802
                                elif "(Battle-Scarred)" in item_name:
                                    float_value = 0.4502
                                if len(item_info['extra']) > 0 and 'float' in item_info['extra'].keys() \
                                        and item_info['price'] and item_info['price'] != 0 \
                                        and (float(item_info['extra']['float']) < float_value or float(
                                        item_info['extra']['float']) > 0.98) \
                                        and (float(item_info['price']) / 100) < float(dict_name_avg[item_name]):
                                    item_buy = f"{item_name} с флоатом {item_info['extra']['float']}, ценой {float(item_info['price']) / 100}"
                                    item_result = f"{item_buy} и средней ценой {dict_name_avg[item_name]}"
                                    print(item_result)
                            except:
                                traceback.print_exc()
                                continue
                    except:
                        traceback.print_exc()
                        continue
                dict_name_avg.clear()
        except:
            traceback.print_exc()
            continue


if __name__ == "__main__":
    start_time = datetime.now()
    list_items1, list_items2 = collecting_items()
    # many_floats(list_items1)
    float_parser1(list_items1)
    float_parser1(list_items2)
    end_time = datetime.now()
    work_time = end_time - start_time
    print(work_time)

