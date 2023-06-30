import requests
import json
from datetime import datetime
import time
import traceback
import codecs
import pyotp
from key import api_bit, google_code


def item_price1():
    data1 = []
    url = f"https://bitskins.com/api/v1/get_all_item_prices/?api_key={api_bit}&code={my_token}"
    api = requests.get(url)
    data = json.loads(api.text)
    for item in data['prices']:
        if item['instant_sale_price'] and float(item['instant_sale_price']) != 0:
            data1.append(item)
    return data1


def item_price2():
    data2 = []
    url1 = f"https://bitskins.com/api/v1/get_price_data_for_items_on_sale/?api_key={api_bit}&code={my_token}"
    api = requests.get(url1)
    data = json.loads(api.text)
    for item in (data['names_list']['items']):
        if (item['recent_sales_info'] and item['recent_sales_info']['hours']
                and item['recent_sales_info']['average_price'] and float(item['recent_sales_info']['hours']) > 50
                and item['lowest_price'] and float(item['lowest_price']) > 0.5):
            data2.append(item)
    return data2


def item_price3():
    data3 = []
    url = "https://market.csgo.com/api/v2/prices/class_instance/USD.json"
    api = requests.get(url)
    data = json.loads(api.text)
    for item in data['items']:
        if (data['items'][item]['price'] and float(data['items'][item]['price']) > 0.5
                and data['items'][item]['popularity_7d'] and float(data['items'][item]['popularity_7d']) > 15
                and data['items'][item]['avg_price']):
            data3.append(data['items'][item])
    return data3


def all_orders():
    data4 = []
    url = f"https://bitskins.com/api/v1/summarize_buy_orders/?api_key={api_bit}&code={my_token}"
    api = requests.get(url)
    data = json.loads(api.text)
    for item in data['names_list']['items']:
        if float(item[1]['max_price']) > 0.5:
            data4.append(item)
    return data4


def parser():
    current_file = f"bit_items_list.txt"
    file = codecs.open(current_file, mode='a', encoding='utf-8', errors='ignore')
    file_r = codecs.open(current_file, mode='r', encoding='utf-8', errors='ignore')
    data_file = file_r.read()
    pars_counter = 0
    count_items = len(data2)
    for item2 in data2:
        pars_counter += 1
        # print(f"{pars_counter}/{count_items}")
        for item1 in data1:
            if item2['market_hash_name'] == item1[0]:
                with_order = float(item2['lowest_price']) / float(item1[1]['max_price'])
                with_avg = float(item2['recent_sales_info']['average_price']) / float(item2['lowest_price'])
                if with_order < 1.01 and with_avg > 1.3:
                    item_buy = (f"{item2['market_hash_name']} с ценой {item2['lowest_price']},"
                                f" средней ценой {item2['recent_sales_info']['average_price']},"
                                f" и автопокупкой {item1[1]['max_price']}.")
                    print(item_buy)
                    get_item_id(item2['market_hash_name'], float(item2['lowest_price']))
                    # buy_price = float(item1[1]['max_price']) * 1.1
                    # price = float(float("{0:.2f}".format(sell_price)))
                    # name = item2['market_hash_name']
                    # check_place(name, price)
                    if item_buy not in data_file:
                        file.write(str(item_buy) + '\n')

    file_r.close()
    file.close()


def check_place(name, price):
    my_secret = google_code
    my_token = pyotp.totp.TOTP(my_secret).now()
    url = f"https://bitskins.com/api/v1/get_expected_place_in_queue_for_new_buy_order/?api_key={api_bit}&code={my_token}&name={name}&price={price}"
    api = requests.get(url)
    data = json.loads(api.text)
    place = int(data['names_list']['expected_place_in_queue'])
    print(f"Место в очереди {place}")
    if place < 1:
        create_order(name, price)


def create_order(name, price):
    my_secret = google_code
    my_token = pyotp.totp.TOTP(my_secret).now()
    url = f"https://bitskins.com/api/v1/create_buy_order/?api_key={api_bit}&code={my_token}&name={name}&price={price}&quantity=1"
    api = requests.get(url)
    data = json.loads(api.text)
    print(data)


def get_item_id(name, price):
    my_secret = google_code
    my_token = pyotp.totp.TOTP(my_secret).now()
    url = f"https://bitskins.com/api/v1/get_inventory_on_sale/?api_key={api_bit}&code={my_token}&market_hash_name={name}"
    api = requests.get(url)
    data = json.loads(api.text)
    for item in data['names_list']['items']:
        if float(item['price']) == price:
            item_id = item['item_id']
            buy_item(item_id, price)
            break


def buy_item(item_id, price):
    my_secret = google_code
    my_token = pyotp.totp.TOTP(my_secret).now()
    url = f"https://bitskins.com/api/v1/buy_item/?api_key={api_bit}&code={my_token}&item_ids={item_id}&prices={price}" \
          f"&app_id=730&auto_trade=false&allow_trade_delayed_purchases=true"
    api = requests.get(url)
    data = json.loads(api.text)
    print(data)


def my_orders():
    url1 = f"https://bitskins.com/api/v1/get_active_buy_orders/?api_key={api_bit}&code={my_token}"
    api = requests.get(url1)
    data = json.loads(api.text)
    print(data)


def buy_orders():
    url1 = f"https://bitskins.com/api/v1/get_market_buy_orders/?api_key={api_bit}&code={my_token}&page=500"
    api = requests.get(url1)
    data = json.loads(api.text)
    print(data)


if __name__ == "__main__":
    run_counter = 0
    while True:
        try:
            run_counter += 1
            print(run_counter)
            my_secret = google_code
            my_token = pyotp.totp.TOTP(my_secret).now()
            data1 = all_orders()
            data2 = item_price2()
            data3 = item_price3()
            parser()
            time.sleep(10)
        except:
            pass
