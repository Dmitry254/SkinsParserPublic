import traceback
import requests
import json
import time
import os
import psutil
from json import JSONDecodeError
from datetime import datetime
from key import *


def price_parser():
    try:
        url = "https://market.csgo.com/api/v2/prices/class_instance/RUB.json"
        api = requests.get(url)
        data = json.loads(api.text)
        for item in data['items']:
            if (data['items'][item]['price'] and float(data['items'][item]['price']) > 50
                    and data['items'][item]['popularity_7d'] and float(data['items'][item]['popularity_7d']) > 14
                    and data['items'][item]['buy_order'] and float(data['items'][item]['buy_order']) > 25
                    and data['items'][item]['avg_price']):
                # print(f"{names_list['items'][item]['market_hash_name']} с ценой {names_list['items'][item]['price']} и средней {names_list['items'][item]['avg_price']}")
                with_order = float(data['items'][item]['price']) / (float((data['items'][item]['buy_order'])))
                with_avg = float(data['items'][item]['avg_price']) / (float(data['items'][item]['price']))
                if (with_order < 1.03 and with_avg > 1.3) or with_avg > 1.4:
                    buy_data = buy_item_for(str(data['items'][item]['market_hash_name']),
                                            float(data['items'][item]['price']))
                    if buy_data['success']:
                        print(f"Купил {str(data['items'][item]['market_hash_name'])} за {float(data['items'][item]['price'])}")
    except JSONDecodeError:
        pass
    except:
        print("В price_parser")
        traceback.print_exc()


def check_time():
    time_now = datetime.today().strftime("%H.%M")
    if time_now == "06.40":
        remove_all_sales()
        sell_item(100)
    if time_now == "06.50":
        sell_item(100)
    if time_now == "07.02":
        update_inventory()
    if time_now == "07.05" or time_now == "07.15" or time_now == "07.25":
        update_inventory()
        time.sleep(1)
        sell_item(100)
    if datetime.today().strftime("%M") == "29":
        update_inventory()
    if datetime.today().strftime("%M") == "31":
        print(f"Покупок {buy_count}, продаж {sell_count}\n")
        sell_item_again(1.0745)
        time.sleep(1)
        sell_item(100)


def ping():
    requests.get(f"https://market.csgo.com/api/v2/ping?key={api_key}")


def update_inventory():
    requests.get(f"https://market.csgo.com/api/v2/update-inventory/?key={api_key}")


def buy_item(item_name, item_price_in):
    item_price = item_price_in * 100
    url = f"https://market.csgo.com/api/v2/buy?key={api_key}&hash_name={item_name}&price={item_price}"
    buy_item_status = requests.get(url)
    buy_data = json.loads(buy_item_status.text)
    return buy_data


def buy_item_for(item_name, item_price_in):
    item_price = item_price_in * 100
    url = f"https://market.csgo.com/api/v2/buy-for?key={api_key}&hash_name={item_name}&price={item_price}&partner=1069768931&token=9Jpb4yxc"
    buy_item_status = requests.get(url)
    buy_data = json.loads(buy_item_status.text)
    return buy_data


def remove_all_sales():
    requests.get(f"https://market.csgo.com/api/v2/remove-all-from-sale?key={api_key}")
    time.sleep(1)
    requests.get(f"https://market.csgo.com/api/v2/remove-all-from-sale?key={api_key}")


def sell_item(percent):
    update_inventory()
    try:
        url = f"https://market.csgo.com/api/v2/my-inventory/?key={api_key}"
        all_items_status = requests.get(url)
        all_sell_items = json.loads(all_items_status.text)
        for item in range(len(all_sell_items['items'])):
            count = 0
            sum_price = 0
            url_item = f"https://market.csgo.com/api/v2/get-list-items-info?key={api_key}&list_hash_name[]=" \
                       f"{all_sell_items['items'][item]['market_hash_name']}"
            item_status = requests.get(url_item)
            current_item = json.loads(item_status.text)
            item_name = all_sell_items['items'][item]['market_hash_name']
            sell_price = float(current_item['names_list'][item_name]['average'])
            for price in current_item['names_list'][item_name]['history']:
                min_border = float(current_item['names_list'][item_name]['average']) / 1.5
                max_border = float(current_item['names_list'][item_name]['average']) * 1.5
                if count < 30 and price != current_item['names_list'][item_name]['history'][-1]:
                    if min_border < price[1] < max_border:
                        sum_price += price[1]
                        count += 1
                else:
                    if count != 0:
                        sell_price = sum_price / (count - 1)
                    else:
                        sell_price = float(current_item['names_list'][item_name]['average'])
                    break
            print(all_sell_items['items'][item]['market_hash_name'], "выставлять за", sell_price,
                  ", а средняя цена",
                  current_item['names_list'][item_name]['average'])
            item_price = float(float("{0:.2f}".format(sell_price)) * percent)
            url_sell = f"https://market.csgo.com/api/v2/add-to-sale?key={api_key}&id=" \
                f"{all_sell_items['items'][item]['id']}&price=" \
                f"{item_price}&cur=RUB"
            sell_status = requests.get(url_sell)
            sell_result = json.loads(sell_status.text)
            if sell_result['success']:
                print(f"{item_name} выставлен на продажу за {item_price / 100} рублей")
            else:
                print(sell_result)
    except JSONDecodeError:
        sell_item(percent)
    except:
        print("В sell_item")
        traceback.print_exc()
        sell_item(percent)


def sell_item_again(percent):
    update_inventory()
    try:
        now = datetime.now()
        url = f"https://market.csgo.com/api/v2/my-inventory/?key={api_key}"
        all_items_status = requests.get(url)
        all_sell_items = json.loads(all_items_status.text)
        if int(now.hour) < 2:
            hour = 0
        else:
            hour = int(now.hour)-2
        date = datetime(year=int(now.year), month=int(now.month), day=int(now.day), hour=hour,
                        minute=int(now.minute), second=int(now.second)).timestamp()
        time_end = datetime.now().timestamp()
        url_his = f"https://market.csgo.com/api/v2/history?key={api_key}&date={date}&date_end={time_end}"
        result = requests.get(url_his)
        data = json.loads(result.text)
        for item_his in reversed(range(len(data['names_list']))):
            if data['names_list'][item_his]['event'] == "sell" and data['names_list'][item_his]['stage'] == "5":
                for item_sell in range(len(all_sell_items['items'])):
                    if data['names_list'][item_his]['market_hash_name'] == all_sell_items['items'][item_sell]['market_hash_name']:
                        item_price = float(float(data['names_list'][item_his]['received']) * percent)
                        item_name = all_sell_items['items'][item_sell]['market_hash_name']
                        url_sell = f"https://market.csgo.com/api/v2/add-to-sale?key={api_key}&id=" \
                            f"{all_sell_items['items'][item_sell]['id']}&price=" \
                            f"{item_price}&cur=RUB"
                        sell_status = requests.get(url_sell)
                        sell_result = json.loads(sell_status.text)
                        if sell_result['success']:
                            print(f"{item_name} снова выставлен на продажу за {item_price / 100} рублей")
                        else:
                            print(sell_result)
    except JSONDecodeError:
        sell_item_again(percent)
    except:
        print("В sell_item_again")
        traceback.print_exc()
        sell_item_again(percent)


def count_trades():
    global buy_count
    global sell_count
    current_year = int(datetime.today().strftime("%Y"))
    current_mount = int(datetime.today().strftime("%m"))
    current_day = int(datetime.today().strftime("%d"))
    date = datetime(current_year, current_mount, current_day).timestamp()
    url = f"https://market.csgo.com/api/v2/history?key={api_key}&date={date}"
    result = requests.get(url)
    data = json.loads(result.text)
    buy_count = 0
    sell_count = 0
    for item in reversed(range(len(data['names_list']))):
        if data['names_list'][item]['event'] == "buy" and data['names_list'][item]['stage'] == "2":
            buy_count += 1
        if data['names_list'][item]['event'] == "sell" and data['names_list'][item]['stage'] == "2":
            sell_count += 1


def check_trades():
    url = f"https://market.csgo.com/api/v2/trades/?key={api_key}"
    result = requests.get(url)
    trades_info = json.loads(result.text)
    return trades_info


def open_sda():
    info = check_trades()
    start = False
    close = False
    if info['success']:
        for item in range(len(info['trades'])):
            if info['trades'][item]['dir'] == 'in':
                start = True
    for process in psutil.process_iter():
        try:
            if process.name() == process_name:
                start = False
                close = True
                break
        except:
            continue
    if info['success'] and start:
        os.startfile(f"E:\SDA\{process_name}")
    if not info['success'] and close:
        os.system(f"TASKKILL /F /IM {process_name}")


def go_offline():
    requests.get(f"https://market.csgo.com/api/v2/go-offline?key={api_key}")


if __name__ == "__main__":
    run_counter = 0
    buy_count = 0
    sell_count = 0
    try:
        count_trades()
    except:
        pass
    while True:
        run_counter += 1
        try:
            if run_counter % 20 == 0:
                try:
                    count_trades()
                except:
                    pass
            if run_counter % 200 == 0:
                print(f"Покупок {buy_count}, продаж {sell_count}")
            if buy_count < 15:
                price_parser()
        except:
            pass
