import requests
import json
from datetime import datetime
import time
import traceback
import pyotp


def find_market_item(item_name):
    market_result = ""
    url = f"https://market.csgo.com/api/v2/search-list-items-by-hash-name-all?key={api_key}&list_hash_name[]={item_name}"
    item_info = requests.get(url)
    data = json.loads(item_info.text)
    item_float = "None"
    item_phase = "None"
    for item in data['data'][item_name]:
        print(item)
        item_link = f"https://market.csgo.com/item/{item['class']}-{item['instance']}"
        item_price = item['price']
        if item['extra']:
            if "float" in item['extra'].keys():
                item_float = item['extra']['float']
            if "phase" in item['extra'].keys():
                item_phase = item['extra']['phase']
            market_result += f"{item_name}: price - {item_price}₽, float - {item_float}, phase - {item_phase}\n"
    return market_result


def find_bit_item(item_name):
    bit_result = ""
    my_secret = google_code
    my_token = pyotp.totp.TOTP(my_secret).now()
    global list_id
    list_id = []
    my_secret = google_code
    my_token = pyotp.totp.TOTP(my_secret).now()
    url = f"https://bitskins.com/api/v1/get_inventory_on_sale/?api_key={api_bit}&code={my_token}&market_hash_name={item_name}"
    api = requests.get(url)
    data = json.loads(api.text)
    for item in data['data']['items']:
        try:
            list_id.append(item['item_id'])
            if len(list_id) > 90:
                bit_result += get_info(list_id)
                list_id = []
        except:
            traceback.print_exc()
            continue
    bit_result += get_info(list_id)
    return bit_result


def get_info(list_id):
    bit_result = ""
    my_secret = google_code
    my_token = pyotp.totp.TOTP(my_secret).now()
    list_id = ",".join(list_id)
    url = f"https://bitskins.com/api/v1/get_specific_items_on_sale/?api_key={api_bit}&code={my_token}&item_ids={list_id}"
    api = requests.get(url)
    data = json.loads(api.text)
    for item_info in data['data']['items_on_sale']:
        print(item_info)
        item_price = item_info['price']
        item_link = f"https://bitskins.com/view_item?app_id=730&item_id={item_info['item_id']}"
        item_float = item_info['float_value']
        item_phase = item_info['phase']
        item_seed = item_info['pattern_info']['paintseed']
        bit_result += f"{item_name}: price - {item_price}$, float - {item_float}, phase - {item_phase}, seed - {item_seed}\n"
    return bit_result


def start_script(item_name):
    global api_bit, google_code, api_key
    api_bit = ""
    google_code = ""
    api_key = ""
    market_result = find_market_item(item_name)
    bit_result = find_bit_item(item_name)
    return market_result, bit_result


if __name__ == "__main__":
    global api_bit, google_code, api_key
    api_bit = ""
    google_code = ""
    api_key = ""
    # AK-47 | Elite Build (Battle-Scarred) Tec-9 | Fuel Injector (Factory New) Butterfly Knife | Case Hardened (Field-Tested)
    item_name = "★ Falchion Knife | Fade (Factory New)"
    market_result = find_market_item(item_name)
    # print(market_result)
    print("---------------------------------")
    bit_result = find_bit_item(item_name)
    # print(bit_result)
