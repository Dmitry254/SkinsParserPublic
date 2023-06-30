import codecs
import time
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
                and item['recent_sales_info']['average_price'] and float(item['recent_sales_info']['hours']) > 1):
            names_list.append(item['market_hash_name'])
            try:
                avg_price_in_dict = avg_dict[item['market_hash_name']]
                if avg_price_in_dict > float(item['recent_sales_info']['average_price']):
                    avg_dict.update(
                        {data['items'][item]['market_hash_name']: float(item['recent_sales_info']['average_price'])})
            except KeyError:
                avg_dict.update(
                    {item['market_hash_name']: float(item['recent_sales_info']['average_price'])})
    return names_list, avg_dict


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
    for item_info in data['data']['items_on_sale']:
        try:
            if item_info['phase'] and not any(words == item_info['phase'] for words in phase_black_list) and \
                    (float(item_info['price']) < (float(item_info['suggested_price']) if item_info['suggested_price'] else 0) * 1.3 or
                    float(item_info['price']) < (float(avg_dict[item_info['market_hash_name']]) if avg_dict[item_info['market_hash_name']] else 0) * 1.3):
                # print(item_info)
                phase_result = (f"{item_info['market_hash_name']}, {item_info['phase']}, "
                                f"цена - {item_info['price']}, рекомендуемая - {item_info['suggested_price']}, "
                                f"{avg_dict[item_info['market_hash_name']]} средняя")
                if phase_result not in data_file:
                    print(phase_result)
                    file.write(str(phase_result) + '\n')
        except:
            continue


if __name__ == "__main__":
    current_file = f"phase_parser.txt"
    file = codecs.open(current_file, mode='a', encoding='utf-8', errors='ignore')
    file_r = codecs.open(current_file, mode='r', encoding='utf-8', errors='ignore')
    data_file = file_r.read()
    run_counter = 1
    while True:
        try:
            run_counter += 1
            start_time = datetime.now()
            avg_dict = {}
            list_id = []
            api_bit = ""
            google_code = ""
            my_secret = google_code
            my_token = pyotp.totp.TOTP(my_secret).now()
            phase_black_list = ["phase1", "phase2", "phase3", "phase4"]
            names_list, avg_dict = items_price()
            parser(names_list)
            if run_counter % 150 == 0:
                file_r.close()
                file.close()
                current_file = f"phase_parser.txt"
                file = codecs.open(current_file, mode='a', encoding='utf-8', errors='ignore')
                file_r = codecs.open(current_file, mode='r', encoding='utf-8', errors='ignore')
                data_file = file_r.read()
                run_counter = 1
            time.sleep(60)
        except:
            pass
        finally:
            file_r.close()
            file.close()
