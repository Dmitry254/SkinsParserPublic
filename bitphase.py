import requests
import json
import traceback
import pyotp
from datetime import datetime


def items_price():
    names_list = []
    avg_dict = {}
    white_list = ["Doppler"]  # ["1Doppler", "Case Hardened", "1Fade "]
    url1 = f"https://bitskins.com/api/v1/get_price_data_for_items_on_sale/?api_key={api_bit}&code={my_token}"
    api = requests.get(url1)
    data = json.loads(api.text)
    for item in (data['data']['items']):
        if (any(words in item['market_hash_name'] for words in white_list)
                and item['recent_sales_info'] and item['recent_sales_info']['hours']
                and item['recent_sales_info']['average_price'] and float(item['recent_sales_info']['hours']) > 10
                and item['lowest_price'] and float(item['lowest_price']) > 0.5):
            names_list.append(item['market_hash_name'])
            avg_dict.update({item['market_hash_name']: float(item['recent_sales_info']['average_price'])})
    print(len(names_list))
    return names_list


def parser(names_list):
    pars_counter = 0
    count_items = len(names_list)
    for item in names_list:
        try:
            get_item_id(item)
        except:
            traceback.print_exc()
            continue


def get_item_id(name):
    global list_id
    my_secret = google_code
    my_token = pyotp.totp.TOTP(my_secret).now()
    url = f"https://bitskins.com/api/v1/get_inventory_on_sale/?api_key={api_bit}&code={my_token}&market_hash_name={name}"
    api = requests.get(url)
    data = json.loads(api.text)
    for item in data['data']['items']:
        try:
            list_id.append(item['item_id'])
            if len(list_id) > 70:
                get_phase(list_id)
                list_id = []
        except:
            traceback.print_exc()
            continue


def get_phase(list_id):
    global items_list
    my_secret = google_code
    my_token = pyotp.totp.TOTP(my_secret).now()
    list_id = ",".join(list_id)
    url = f"https://bitskins.com/api/v1/get_specific_items_on_sale/?api_key={api_bit}&code={my_token}&item_ids={list_id}"
    api = requests.get(url)
    data = json.loads(api.text)
    print(data)
    for item_info in data['data']['items_on_sale']:
        print(item_info)
        print(f"{item_info['market_hash_name']} seed={item_info['pattern_info']['paintseed']}      {item_info['item_id']}")


if __name__ == "__main__":
    global avg_dict
    global list_id
    global items_list
    global google_code
    global api_bit
    global my_token
    global my_secret
    start_time = datetime.now()
    avg_dict = {}
    list_id = []
    items_list = []
    api_bit = ""
    google_code = ""
    my_secret = google_code
    my_token = pyotp.totp.TOTP(my_secret).now()
    names_list = items_price()
    parser(names_list)
    end_time = datetime.now()
    work_time = end_time - start_time
    print(work_time)
