import traceback
import requests
import json
import time
import os
import psutil
import codecs
import re
import steampy
from steampy.client import SteamClient
from steampy.exceptions import InvalidCredentials
from json import JSONDecodeError
from datetime import datetime, timedelta
from key1 import *


def collect_dict_avg():
    global dict_avg_price
    try:
        url = "https://market.csgo.com/api/v2/prices/class_instance/RUB.json"
        api = requests.get(url)
        data = json.loads(api.text)
        dict_avg_price = {}
        for item in data['items']:
            try:
                if (data['items'][item]['price'] and max_price > float(data['items'][item]['price']) > min_price
                        and data['items'][item]['popularity_7d'] and float(data['items'][item]['popularity_7d']) > item_popularity
                        and data['items'][item]['buy_order'] and float(data['items'][item]['buy_order']) > min_buy_order
                        and data['items'][item]['avg_price']):
                    try:
                        avg_price_in_dict = dict_avg_price[data['items'][item]['market_hash_name']]
                        if avg_price_in_dict > float(data['items'][item]['avg_price']):
                            dict_avg_price.update(
                                {data['items'][item]['market_hash_name']: float(data['items'][item]['avg_price'])})
                    except KeyError:
                        dict_avg_price.update(
                            {data['items'][item]['market_hash_name']: float(data['items'][item]['avg_price'])})
            except:
                continue
    except JSONDecodeError:
        pass


def price_parser():
    """
    Поиск и покупка вещей
    """
    global stop_buy
    try:
        url = "https://market.csgo.com/api/v2/prices/class_instance/RUB.json"
        api = requests.get(url)
        data = json.loads(api.text)
        for item in data['items']:
            try:
                if (data['items'][item]['price'] and max_price > float(data['items'][item]['price']) > min_price
                        and data['items'][item]['buy_order'] and float(data['items'][item]['buy_order']) > min_buy_order):
                    try:
                        avg_price = float(dict_avg_price[data['items'][item]['market_hash_name']])
                    except KeyError:
                        continue
                    with_order = float(data['items'][item]['price']) / (float((data['items'][item]['buy_order'])))
                    with_avg = float(avg_price) / (float(data['items'][item]['price']))
                    if ((with_order < percent_with_order and with_avg > percent_with_avg_and_order)
                        or with_avg > percent_with_avg_only)\
                            and not any(words in data['items'][item]['market_hash_name'] for words in black_list):
                        if check_buying_item(data['items'][item]['market_hash_name'], float(data['items'][item]['price']))\
                                and check_items_history(data['items'][item]['market_hash_name']):
                            item_sell_price = float(predict_price(data['items'][item]['market_hash_name'], second_percent)/100)
                            with_item_sell_price = item_sell_price / (float(data['items'][item]['price']))
                            if with_item_sell_price > percent_with_avg_and_order - 0.07:
                                if start_buy_for == 1:
                                    buy_data = buy_item_for(str(data['items'][item]['market_hash_name']),
                                                            float(data['items'][item]['price']))
                                else:
                                    buy_data = buy_item(str(data['items'][item]['market_hash_name']),
                                                        float(data['items'][item]['price']))
                                if buy_data['success']:
                                    file = codecs.open("history.txt", mode='a', encoding='utf-8', errors='ignore')
                                    file.write(data['items'][item]['market_hash_name'] + "\n")
                                    file.close()
                                    print(f"Купил {str(data['items'][item]['market_hash_name'])} за {float(data['items'][item]['price'])},"
                                          f"а продать собираюсь за {item_sell_price}")
                                    stop_buy = 20
            except:
                continue
    except JSONDecodeError:
        pass
    except:
        print("В price_parser")
        traceback.print_exc()


def predict_price(item_name, percent):
    sells_list = []
    count = 0
    sum_price = 0
    try:
        url_item = f"https://market.csgo.com/api/v2/get-list-items-info?key={api_key}&list_hash_name[]=" \
                   f"{item_name}"
        item_status = requests.get(url_item)
        current_item = json.loads(item_status.text)
        sell_price = float(current_item['data'][item_name]['average'])
        for price in current_item['data'][item_name]['history']:
            min_border = float(current_item['data'][item_name]['average']) / 1.5
            max_border = float(current_item['data'][item_name]['average']) * 1.5
            if len(sells_list) < 25 and price != current_item['data'][item_name]['history'][-1]:
                sells_list.append(price[1])
                if min_border < price[1] < max_border and price[0] > (datetime.now() - timedelta(days=14)).timestamp():
                    count += 1
                    sum_price += price[1]
        if count > 5:
            sells_list.sort()
            sell_price = sum_price / (count - 1)
            if float(current_item['data'][item_name]['average']) * percent / 100 > float(sells_list[-4]) \
                    and float(current_item['data'][item_name]['average']) < sell_price:
                sell_price = float(current_item['data'][item_name]['average'])
            elif float(sells_list[-4]) < sell_price * percent / 100:
                sell_price = sell_price * 100 / (percent - 2)
        else:
            sell_price = float(current_item['data'][item_name]['average'])
        item_price = float("{0:.2f}".format(sell_price * percent))
        return item_price
    except:
        pass


def check_buying_item(item_name, item_price):
    filtered_sells = []
    sells_counter = 0
    url_item = f"https://market.csgo.com/api/v2/get-list-items-info?key={api_key}&list_hash_name[]={item_name}"
    item_status = requests.get(url_item)
    current_item = json.loads(item_status.text)
    item_history = current_item['data'][item_name]['history']
    avg_price = current_item['data'][item_name]['average']
    for sell in item_history:
        sells_counter += 1
        if avg_price * 1.4 > sell[1] and sell[0] > (datetime.now() - timedelta(days=14)).timestamp():
            filtered_sells.append(sell[1])
    try:
        checked_avg_price = float(sum(filtered_sells) / len(filtered_sells))
        result_percent = checked_avg_price / avg_price
        real_with_avg = float(checked_avg_price) / (float(item_price))
    except ZeroDivisionError:
        return False
    if (1.15 < result_percent < 0.80 or avg_price - checked_avg_price > 500 or
        len(filtered_sells) * 1.35 < sells_counter) and real_with_avg < 1.25:
        print(f"{item_name} не купил за {item_price}, средняя цена была {current_item['data'][item_name]['average']}, "
              f"а после проверки {checked_avg_price}")
        black_list.append(item_name)
        return False
    return True


def check_items_history(item_name):
    item_counter = 0
    file_r = codecs.open("history.txt", mode='r', encoding='utf-8', errors='ignore')
    for line in file_r.readlines():
        if item_name in line:
            item_counter += 1
        if item_counter > 2:
            black_list.append(item_name)
            file_r.close()
            print(f"{item_name} уже был куплен 3 раза")
            return False
    file_r.close()
    return True


def check_time():
    """
    Проверка времени для переодических действий
    """
    try:
        time_now = datetime.today().strftime("%H.%M")
        if time_now == "10.40":
            remove_all_sales()
            update_inventory()
            if int(datetime.now().day) % 5 == 0:
                codecs.open("history.txt", mode='w', encoding='utf-8', errors='ignore').close()
        if time_now == "10.45" or time_now == "10.50" or time_now == "10.55":
            sell_item(second_percent)
        if time_now == "11.02":
            update_inventory()
        if time_now == "11.05" or time_now == "11.15" or time_now == "11.25":
            sell_item(first_percent)
        if datetime.today().strftime("%M") == "29":
            update_inventory()
        if datetime.today().strftime("%M") == "31":
            sell_item_again(1.054)
        if datetime.today().strftime("%M") == "32":
            sell_item(first_percent)
    except:
        traceback.print_exc()
        print("В check_time")


def ping():
    """
    Оставаться онлайн для продаж
    """
    requests.get(f"https://market.csgo.com/api/v2/ping?key={api_key}")


def update_inventory():
    """
    Обновить инвентарь
    """
    requests.get(f"https://market.csgo.com/api/v2/update-inventory/?key={api_key}")


def buy_item(item_name, item_price_in):
    """
    Купить предмет на текущий аккаунт
    """
    item_price = item_price_in * 100
    url = f"https://market.csgo.com/api/v2/buy?key={api_key}&hash_name={item_name}&price={item_price}"
    buy_item_status = requests.get(url)
    buy_data = json.loads(buy_item_status.text)
    return buy_data


def buy_item_for(item_name, item_price_in):
    """
    Купить предмет на другой аккаунт
    """
    item_price = item_price_in * 100
    url = f"https://market.csgo.com/api/v2/buy-for?key={api_key}&hash_name={item_name}&price={item_price}&{url_for}"
    buy_item_status = requests.get(url)
    buy_data = json.loads(buy_item_status.text)
    return buy_data


def remove_all_sales():
    """
    Удалить все предметы с продажи
    """
    requests.get(f"https://market.csgo.com/api/v2/remove-all-from-sale?key={api_key}")
    time.sleep(1)
    requests.get(f"https://market.csgo.com/api/v2/remove-all-from-sale?key={api_key}")


def sell_item(percent):
    """
    Выставить предмет на продажу
    """
    sells_list = []
    try:
        url = f"https://market.csgo.com/api/v2/my-inventory/?key={api_key}"
        all_items_status = requests.get(url)
        all_sell_items = json.loads(all_items_status.text)
        for item in range(len(all_sell_items['items'])):
            sells_list = []
            count = 0
            sum_price = 0
            url_item = f"https://market.csgo.com/api/v2/get-list-items-info?key={api_key}&list_hash_name[]=" \
                       f"{all_sell_items['items'][item]['market_hash_name']}"
            item_status = requests.get(url_item)
            current_item = json.loads(item_status.text)
            item_name = all_sell_items['items'][item]['market_hash_name']
            if not current_item['data']:
                print(item_name, current_item)
                continue
            for price in current_item['data'][item_name]['history']:
                min_border = float(current_item['data'][item_name]['average']) / 1.5
                max_border = float(current_item['data'][item_name]['average']) * 1.5
                if len(sells_list) < 25 and price != current_item['data'][item_name]['history'][-1]:
                    if min_border < price[1] < max_border and price[0] > (datetime.now() - timedelta(days=14)).timestamp():
                        sells_list.append(price[1])
                        count += 1
                        sum_price += price[1]
            if count > 5:
                sells_list.sort()
                sell_price = sum_price / (count - 1)
                if float(current_item['data'][item_name]['average']) * percent / 100 > float(sells_list[-4]) \
                        and float(current_item['data'][item_name]['average']) < sell_price:
                    sell_price = float(current_item['data'][item_name]['average'])
                elif float(sells_list[-4]) < sell_price * percent / 100:
                    sell_price = sell_price * 100 / (percent - 2)
            else:
                sell_price = float(current_item['data'][item_name]['average'])
            item_price = float("{0:.2f}".format(sell_price * percent))
            url_sell = f"https://market.csgo.com/api/v2/add-to-sale?key={api_key}&id=" \
                f"{all_sell_items['items'][item]['id']}&price=" \
                f"{item_price}&cur=RUB"
            sell_status = requests.get(url_sell)
            sell_result = json.loads(sell_status.text)
            if sell_result['success']:
                if len(sells_list) > 5:
                    print(f"{item_name} выставлен на продажу за {item_price / 100} рублей,"
                          f" средняя цена {current_item['data'][item_name]['average']} рублей,"
                          f" а 4 с конца продажа {sells_list[-4]} рублей")
                else:
                    print(f"{item_name} выставлен на продажу за {item_price / 100} рублей,"
                          f" средняя цена {current_item['data'][item_name]['average']} рублей, а истории покупок нет")
    except JSONDecodeError:
        pass
    except:
        print("В sell_item")
        traceback.print_exc()


def sell_item_again(percent):
    """
    Выставить проданный, но не переданный предмет снова на продажу
    """
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
        for item_his in reversed(range(len(data['data']))):
            if data['data'][item_his]['event'] == "sell" and data['data'][item_his]['stage'] == "5":
                for item_sell in range(len(all_sell_items['items'])):
                    if data['data'][item_his]['market_hash_name'] == all_sell_items['items'][item_sell]['market_hash_name']:
                        item_price = float("{0:.2f}".format(float(data['data'][item_his]['received']) * percent))
                        item_name = all_sell_items['items'][item_sell]['market_hash_name']
                        url_sell = f"https://market.csgo.com/api/v2/add-to-sale?key={api_key}&id=" \
                            f"{all_sell_items['items'][item_sell]['id']}&price=" \
                            f"{item_price}&cur=RUB"
                        sell_status = requests.get(url_sell)
                        sell_result = json.loads(sell_status.text)
                        if sell_result['success']:
                            print(f"{item_name} снова выставлен на продажу за {item_price / 100} рублей")
    except JSONDecodeError:
        pass
    except:
        print("В sell_item_again")
        traceback.print_exc()


def count_trades():
    """
    Подсчёт количества трейдов за день
    """
    try:
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
        for item in reversed(range(len(data['data']))):
            if data['data'][item]['event'] == "buy" and data['data'][item]['stage'] == "2":
                buy_count += 1
            if data['data'][item]['event'] == "sell" and data['data'][item]['stage'] == "2":
                sell_count += 1
    except JSONDecodeError:
        pass


def check_trades():
    """
    Проверить есть ли активные трейды для подтверждения
    """
    url = f"https://market.csgo.com/api/v2/trades/?key={api_key}"
    result = requests.get(url)
    trades_info = json.loads(result.text)
    return trades_info


def open_sda():
    """
    Открыть/закрыть SDA для подтверждения трейда
    """
    process_count = 0
    info = check_trades()
    start = False
    close = False
    if info['success']:
        for item in range(len(info['trades'])):
            if info['trades'][item]['dir'] == 'in':
                start = True
    for process in psutil.process_iter():
        try:
            process_count += 1
            if process_count > 5000:
                break
            if process.name() == process_name:
                start = False
                close = True
                break
        except:
            continue
    if info['success'] and start:
        os.startfile(f"C:\Bot\sda\{process_name}")
    if not info['success'] and close:
        os.system(f"TASKKILL /F /IM {process_name}")


def accept_gift_trades():
    steam_client = SteamClient(steam_api)
    data = steam_client.get_trade_offers(steam_api)
    for trade in data['response']['trade_offers_received']:
        if not trade['items_to_give']:
            steam_client.login(account_login, account_password, mafile_path)
            steam_client.accept_trade_offer(trade['tradeofferid'])


def search_file_and_names(username):
    file_path = f"C:\Bot"
    file = codecs.open(f"{file_path}\Данные от аккаунта.txt", mode='r', encoding='utf-8', errors='ignore')
    account_data = file.readline()
    account_login, account_password = account_data.split(':')[1:]
    account_login = re.sub(r'[^A-Za-z-0-9-_]', '', account_login)
    account_password = re.sub(r'[^A-Za-z-0-9-@-_]', '', account_password)
    mafile_path = f"{file_path}\{username}.mafile"
    file.close()
    return account_login, account_password, mafile_path


def go_offline():
    """
    Временно остановить продажи
    """
    requests.get(f"https://market.csgo.com/api/v2/go-offline?key={api_key}")


def create_trade():
    """
    Создать трейд для подтверждения
    """
    requests.get(f"https://market.csgo.com/api/v2/trade-request-give-p2p?key={api_key}")
    time.sleep(1)
    requests.get(f"https://market.csgo.com/api/v2/trade-request-give-p2p?key={api_key}")


def get_balance():
    """
    Получить баланс аккаунта
    """
    try:
        global my_balance
        url = f"https://market.csgo.com/api/v2/get-money?key={api_key}"
        result = requests.get(url)
        my_balance = json.loads(result.text)['money']
        return my_balance
    except JSONDecodeError:
        pass


if __name__ == "__main__":
    """
    Настройки
    """
    username = ""
    first_percent = 106
    second_percent = 102
    url_for = f""
    start_buy_for = 0
    max_buys = -1
    max_sells = 50
    percent_with_order = 1.05
    percent_with_avg_and_order = 1.3
    percent_with_avg_only = 1.4
    max_price = 5000
    min_price = 50
    min_buy_order = 25
    item_popularity = 14
    run_counter = 0
    stop_buy = 0
    buy_count = 0
    sell_count = 0
    stop_login = 0
    black_list = ["Sticker",
                  # Stickers
                  "Patch",
                  # Patches
                  "Pass",
                  # Pass
                  "Souvenir",
                  # Souvenir
                  "Stockholm 2021",
                  # Stockholm 2021
                  "RMR",
                  # RMR
                  "Desert Eagle | Ocean Drive", "AK-47 | Leet Museo", "SSG 08 | Turbo Peek", "Glock-18 | Snack Attack",
                  "MAC-10 | Toybox", "M4A4 | Spider Lily", "MP9 | Mount Fuji", "Five-SeveN | Boost Protocol",
                  "FAMAS | ZX Spectron", "MAG-7 | BI83 Spectrum", "XM1014 | Watchdog", "USP-S | Black Lotus",
                  "PP-Bizon | Lumen", "MP7 | Guerrilla", "G3SG1 | Keeping Tabs", "Dual Berettas | Tread",
                  "AUG | Plague",
                  # Operation Riptide Case
                  "AK-47 | Gold Arabesque", "UMP-45 | Fade", "SSG 08 | Death Strike", "MAC-10 | Case Hardened",
                  "USP-S | Orange Anolis", "M4A4 | Red DDPAT", "Galil AR | Amber Fade", "G3SG1 | New Roots",
                  "P250 | Black & Tan", "Nova | Quick Sand", "M249 | Midnight Palm", "MP9 | Old Roots",
                  "AUG | Spalted Wood", "Five-SeveN | Withered Vine", "SG 553 | Bleached", "MP7 | Prey",
                  "P90 | Desert DDPAT", "R8 Revolver | Desert Brush",
                  # The 2021 Dust 2 Collection
                  "AWP | Desert Hydra", "Desert Eagle | Fennec Fox", "MP5-SD | Oxide Oasis", "Glock-18 | Pink DDPAT",
                  "XM1014 | Elegant Vines", "AUG | Sand Storm", "USP-S | Purple DDPAT", "M249 | Humidor",
                  "SG 553 | Desert Blossom", "MP9 | Music Box", "FAMAS | CaliCamo", "Dual Berettas | Drift Wood",
                  "P90 | Verdant Growth", "CZ75-Auto | Midnight Palm", "P250 | Drought", "MAG-7 | Navy Sheen",
                  "PP-Bizon | Anolis", "SSG 08 | Prey", "MAC-10 | Sienna Damask",
                  # The 2021 Mirage Collection
                  "M4A4 | The Coalition", "Glock-18 | Gamma Doppler", "USP-S | Whiteout", "FAMAS | Meltdown",
                  "MAC-10 | Propaganda", "AWP | POP AWP", "Nova | Red Quartz", "CZ75-Auto | Syndicate",
                  "MP5-SD | Autumn Twilly", "P2000 | Space Race", "R8 Revolver | Blaze", "Desert Eagle | Sputnik",
                  "M4A1-S | Fizzy POP", "AUG | Amber Fade", "Tec-9 | Safety Net", "SSG 08 | Spring Twilly",
                  "UMP-45 | Full Stop",
                  # The 2021 Train Collection
                  "M4A1-S | Imminent Danger", "Five-SeveN | Fall Hazard", "SG 553 | Hazard Pay", "Galil AR | CAUTION!",
                  "MAG-7 | Prism Terrace", "P250 | Digital Architect", "Negev | Infrastructure", "Nova | Interlock",
                  "AK-47 | Green Laminate", "P90 | Schematic", "UMP-45 | Mechanism", "Glock-18 | Red Tire",
                  "SSG 08 | Carbon Fiber", "PP-Bizon | Breaker Box", "FAMAS | Faulty Wiring", "CZ75-Auto | Framework",
                  "Dual Berettas | Oil Change", "MAC-10 | Strats", "XM1014 | Blue Tire",
                  # The 2021 Vertigo Collection
                  "Chef d'Escadron Rouchard | Gendarmerie Nationale", "'Medium Rare' Crasswater | Guerrilla Warfare",
                  "Vypa Sista of the Revolution | Guerrilla Warfare", "Cmdr. Frank 'Wet Sox' Baroud | SEAL Frogman",
                  "Cmdr. Davida 'Goggles' Fernandez | SEAL Frogman", "Crasswater The Forgotten | Guerrilla Warfare",
                  "Elite Trapper Solman | Guerrilla Warfare", "Chem-Haz Capitaine | Gendarmerie Nationale",
                  "Bloody Darryl The Strapped | The Professionals", "Arno The Overgrown | Guerrilla Warfare",
                  "Lieutenant Rex Krikey | SEAL Frogman", "Col. Mangos Dabisi | Guerrilla Warfare",
                  "Officer Jacques Beltram | Gendarmerie Nationale", "Trapper | Guerrilla Warfare",
                  "Lieutenant 'Tree Hugger' Farlow | SWAT", "Sous-Lieutenant Medic | Gendarmerie Nationale",
                  "Primeiro Tenente | Brazilian 1st Battalion", "Trapper Aggressor | Guerrilla Warfare",
                  "D Squadron Officer | NZSAS", "Mr. Muhlik | Elite Crew", "Aspirant | Gendarmerie Nationale",
                  # Operation Riptide Agents
                  ]
    sell_item(first_percent)
    collect_dict_avg()
    try:
        account_login, account_password, mafile_path = search_file_and_names(username)
        count_trades()
        accept_gift_trades()
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
            try:
                check_time()
            except:
                pass
        except:
            pass
        try:
            if run_counter % 25 == 0:
                collect_dict_avg()
            if run_counter % 15 == 0:
                create_trade()
                open_sda()
                try:
                    if stop_login < 1:
                        accept_gift_trades()
                    else:
                        stop_login -= 1
                except InvalidCredentials:
                    stop_login = 500
                except:
                    stop_login = 25
            if buy_count < max_buys and stop_buy < 1:
                price_parser()
            else:
                stop_buy -= 1
                time.sleep(5)
            if sell_count < max_sells:
                if run_counter % 5 == 0:
                    ping()
            else:
                go_offline()
            if buy_count > max_buys and sell_count > max_sells - 1:
                print("Sleep")
                time.sleep(3600)
                count_trades()
            if run_counter > 151:
                run_counter = 0
        except:
            pass
