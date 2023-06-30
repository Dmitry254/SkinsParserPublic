import requests
import json
from datetime import datetime
import time
import traceback
import codecs
import pyotp
from key import api_bit, google_code


def item_price():
    global avg_dict
    data2 = []
    white_list = ["(Factory New)", "(Minimal Wear)", "(Field-Tested)", "(Well-Worn)", "(Battle-Scarred)"]
    url1 = f"https://bitskins.com/api/v1/get_price_data_for_items_on_sale/?api_key={api_bit}&code={my_token}"
    api = requests.get(url1)
    data = json.loads(api.text)
    for item in (data['data']['items']):
        if (any(words in item['market_hash_name'] for words in white_list)
                and item['recent_sales_info'] and item['recent_sales_info']['hours']
                and item['recent_sales_info']['average_price'] and float(item['recent_sales_info']['hours']) > 10
                and item['lowest_price'] and float(item['lowest_price']) > 0.5):
            data2.append([item['market_hash_name'], float(item['recent_sales_info']['average_price'])])
            avg_dict.update({item['market_hash_name']: float(item['recent_sales_info']['average_price'])})
    print(len(data2))
    return data2


def parser(data):
    pars_counter = 0
    count_items = len(data)
    for item in data:
        try:
            get_item_id(item[0], item[1])
        except:
            traceback.print_exc()
            continue


def get_item_id(name, avg_price):
    global list_id
    my_secret = google_code
    my_token = pyotp.totp.TOTP(my_secret).now()
    url = f"https://bitskins.com/api/v1/get_inventory_on_sale/?api_key={api_bit}&code={my_token}&market_hash_name={name}&max_price={'{0:.2f}'.format(avg_price * 1.2)}"
    api = requests.get(url)
    data = json.loads(api.text)
    for item in data['data']['items']:
        try:
            list_id.append(item['item_id'])
            if len(list_id) > 90:
                get_float(list_id)
                list_id = []
        except:
            traceback.print_exc()
            continue


def get_float(list_id):
    my_secret = google_code
    my_token = pyotp.totp.TOTP(my_secret).now()
    list_id = ",".join(list_id)
    url = f"https://bitskins.com/api/v1/get_specific_items_on_sale/?api_key={api_bit}&code={my_token}&item_ids={list_id}"
    api = requests.get(url)
    data = json.loads(api.text)
    for item_float in data['data']['items_on_sale']:
        try:
            item_name = item_float['market_hash_name']
            max_float_value = 0
            min_float_value = 1
            if "(Factory New)" in item_name:
                max_float_value = 0.006
                min_float_value = 0
            elif "(Minimal Wear)" in item_name:
                max_float_value = 0.074
                min_float_value = 0.07
            elif "(Field-Tested)" in item_name:
                max_float_value = 0.154
                min_float_value = 0.15
            elif "(Well-Worn)" in item_name:
                max_float_value = 0.3802
                min_float_value = 0.38
            elif "(Battle-Scarred)" in item_name:
                max_float_value = 0.4502
                min_float_value = 0.45
            if item_float['float_value'] and min_float_value < float(item_float['float_value']) < max_float_value:
                item_link = f"https://bitskins.com/view_item?app_id=730&item_id={item_float['item_id']}"
                item_float = float(item_float['float_value'])
                item_price = float(item_float['price'])
                item_avg_price = float(avg_dict[item_name])
                print(f"{item_name} с флоатом {item_float['float_value']}, ценой {item_float['price']} и средней ценой {avg_dict[item_name]}")
                print(item_link)
        except:
            traceback.print_exc()
            continue


if __name__ == "__main__":
    start_time = datetime.now()
    avg_dict = {}
    list_id = []
    run_counter = 0
    run_counter += 1
    print(run_counter)
    my_secret = google_code
    my_token = pyotp.totp.TOTP(my_secret).now()
    data = item_price()
    parser(data)
    end_time = datetime.now()
    work_time = end_time - start_time
    print(work_time)
