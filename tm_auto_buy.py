import codecs
import re
import traceback
import requests
import json
import time
import os
import psutil
import schedule
from json import JSONDecodeError
from datetime import datetime, timedelta
from steampy.client import SteamClient
from steampy.exceptions import InvalidCredentials
from multiprocessing import Process
from key1 import *


def collect_dict_avg():
    try:
        url = "https://market.csgo.com/api/v2/prices/class_instance/RUB.json"
        data = send_req(url)
        items_dict = {}
        for item in data['items']:
            try:
                if (data['items'][item]['price'] and float(data['items'][item]['price']) > min_price
                        and data['items'][item]['popularity_7d'] and float(data['items'][item]['popularity_7d']) > 10
                        and data['items'][item]['buy_order'] and float(data['items'][item]['buy_order']) > 25
                        and data['items'][item]['avg_price'] and float(data['items'][item]['avg_price']) < my_balance
                        and not any(words in data['items'][item]['market_hash_name'] for words in black_list)):
                    class_instance = str(item).split('_')
                    items_dict.update({data['items'][item]['market_hash_name']:
                                               [float(data['items'][item]['avg_price']),
                                                float(data['items'][item]['buy_order']) + 0.01,
                                                class_instance[0], class_instance[1]]})
                    try:
                        avg_price_in_dict = items_dict[data['items'][item]['market_hash_name']][0]
                        if avg_price_in_dict > float(data['items'][item]['avg_price']):
                            items_dict.update({data['items'][item]['market_hash_name']:
                                                   [float(data['items'][item]['avg_price']),
                                                    float(data['items'][item]['buy_order']) + 0.01,
                                                    class_instance[0], class_instance[1]]})
                    except KeyError:
                        items_dict.update({item:[float(data['items'][item]['avg_price']),
                                                float(data['items'][item]['buy_order']) + 0.01,
                                                class_instance[0], class_instance[1]]})
            except:
                traceback.print_exc()
                continue
        return items_dict
    except:
        traceback.print_exc()
        pass


def price_parser():
    """
    Поиск и покупка вещей
    """
    active_orders = {}
    item_names = {}
    items_counter = 0
    link_items = ""
    url = "https://market.csgo.com/api/v2/prices/class_instance/RUB.json"
    all_items = send_req(url)
    for item in all_items['items']:
        try:
            if (all_items['items'][item]['price'] and my_balance > float(all_items['items'][item]['price']) > min_price
                    and (price_border_1 < float(all_items['items'][item]['price']) < price_border_2
                    or price_border_3 < float(all_items['items'][item]['price']) < price_border_4
                    or price_border_5 < float(all_items['items'][item]['price']) < price_border_6)
                    and all_items['items'][item]['popularity_7d'] and float(all_items['items'][item]['popularity_7d']) > popularity
                    and all_items['items'][item]['buy_order'] and float(all_items['items'][item]['buy_order']) > 250
                    and not any(words in all_items['items'][item]['market_hash_name'] for words in black_list)):
                if items_counter < 49:
                    items_counter += 1
                    link_items += "&list_hash_name[]=" + all_items['items'][item]['market_hash_name']
                    item_names.update({item: all_items['items'][item]['market_hash_name']})
                else:
                    url_item = f"https://market.csgo.com/api/v2/get-list-items-info?key={api_key}{link_items}"
                    link_items = ""
                    item_data = send_req(url_item)
                    items_counter = 0
                    for item_id in item_names:
                        try:
                            class_instance = str(item_id).split('_')
                            if item_data['data'][item_names[item_id]]['history']:
                                try:
                                    avg_price = items_dict[item_names[item_id]][0]
                                except KeyError:
                                    if item_data['data'][item_names[item_id]]['average']:
                                        avg_price = item_data['data'][item_names[item_id]]['average']
                                    else:
                                        continue
                                buy_order = float(all_items['items'][item_id]['buy_order'])
                                sales_history = []
                                min_border = float(avg_price) / min_border_cf
                                max_border = float(avg_price) * max_border_cf
                                for sale_info in item_data['data'][item_names[item_id]]['history']:
                                    if sale_info[0] > week_ago and max_border > float(sale_info[1]) > min_border:
                                        sales_history.append(sale_info[1])
                                sales_history.sort()
                                if len(sales_history) > 5:
                                    min_sells = [sales_history[0], sales_history[1], sales_history[2]]
                                    my_buy_order = float("{0:.2f}".format(sum(min_sells) / float(len(min_sells))))
                                    if my_buy_order > buy_order:
                                        buy_order = my_buy_order + 0.01
                                    predict_sell_price = predict_price(100, sales_history, float(avg_price))
                                    with_predict_price = predict_sell_price / buy_order
                                    if with_predict_price > with_predict_price_cf and buy_order > 250:
                                        if (check_buying_item(item_names[item_id], buy_order, avg_price, sales_history)
                                            and (price_border_1 < buy_order < price_border_2
                                                or price_border_3 < buy_order < price_border_4
                                                or price_border_5 < buy_order < price_border_6)):
                                            buy_item = True
                                            for order in my_orders:
                                                try:
                                                    if order['i_classid'] == class_instance[0]\
                                                            and order['i_instanceid'] == class_instance[1]:
                                                        if float(order['o_price']) / 100 == buy_order - 0.01:
                                                            print(f"На {item_names[item_id]} уже есть запрос")
                                                            buy_item = False
                                                            break
                                                        else:
                                                            if start_buy_for == 1:
                                                                update_order_for(class_instance[0],
                                                                                 class_instance[1],
                                                                                buy_order)
                                                            else:
                                                                update_order(class_instance[0],
                                                                             class_instance[1],
                                                                             buy_order)
                                                            print(f"Изменил запрос на {item_names[item_id]} по {buy_order}, "
                                                                  f"средняя {avg_price}, "
                                                                  f"предполагаемой продажи {predict_sell_price}, "
                                                                  f"минимальные продажи {min_sells}, "
                                                                  f"был запрос {all_items['items'][item_id]['buy_order']}")
                                                            buy_item = False
                                                            break
                                                except TypeError:
                                                    pass
                                            if buy_item:
                                                if start_buy_for == 1:
                                                    create_order_for(class_instance[0], class_instance[1],
                                                                     buy_order)
                                                else:
                                                    create_order(class_instance[0], class_instance[1],
                                                                 buy_order)
                                                print(f"Создал запрос на {item_names[item_id]} по {buy_order}, "
                                                      f"средняя {avg_price}, "
                                                      f"предполагаемой продажи {predict_sell_price}, "
                                                      f"минимальные продажи {min_sells}")
                                            active_orders.update({item_names[item_id]: buy_order})
                        except:
                            traceback.print_exc()
                            continue
                    item_names = {}
        except JSONDecodeError:
            time.sleep(1)
            continue
    return all_items, active_orders


def predict_price(percent, sells_list, average_price):
    try:
        sell_price = float(sum(sells_list)) / float(len(sells_list))
        sells_list.sort()
        if average_price * percent / 100 > float(sells_list[-4]) and average_price < sell_price:
            sell_price = average_price
        elif float(sells_list[-4]) < sell_price * percent / 100:
            sell_price = sell_price * 100 / (percent - 2)
        item_price = float("{0:.2f}".format(sell_price / 100 * percent))
        return item_price
    except:
        pass


def check_buying_item(item_name, buy_order, avg_price, sales_history):
    filtered_sells = []
    sells_counter = 0
    for sell in sales_history:
        sells_counter += 1
        if avg_price * 1.4 > sell:
            filtered_sells.append(sell)
    try:
        checked_avg_price = float(sum(filtered_sells) / float(len(filtered_sells)))
        result_percent = checked_avg_price / avg_price
        real_with_avg = float(checked_avg_price) / (float(buy_order))
    except ZeroDivisionError:
        return False
    if (1.15 < result_percent < 0.80 or avg_price - checked_avg_price > 500 or
        len(filtered_sells) * 1.35 < sells_counter) and real_with_avg < 1.25:
        print(f"{item_name} не купил за {buy_order}, средняя цена была {avg_price}, "
              f"а после проверки {checked_avg_price}")
        black_list.append(item_name)
        return False
    return True


def set_orders_for_all():
    for item in all_items['items']:
        for order in active_orders:
            try:
                if all_items['items'][item]['market_hash_name'] == order:
                    buy_item = True
                    class_instance = str(item).split('_')
                    for my_order in my_orders:
                        try:
                            if str(my_order['i_classid']) == class_instance[0] \
                                    and my_order['i_instanceid'] == class_instance[1]:
                                if float(my_order['o_price']) / 100 == float(all_items['items'][item]['buy_order']) \
                                        or float(my_order['o_price']) == active_orders[order]:
                                    buy_item = False
                                    break
                                else:
                                    if start_buy_for == 1:
                                        update_order_for(class_instance[0], class_instance[1], active_orders[order])
                                    else:
                                        update_order(class_instance[0], class_instance[1], active_orders[order])
                                    buy_item = False
                                    break
                        except TypeError:
                            traceback.print_exc()
                            pass
                    if buy_item:
                        if start_buy_for == 1:
                            create_order_for(class_instance[0], class_instance[1], active_orders[order])
                        else:
                            create_order(class_instance[0], class_instance[1], active_orders[order])
            except:
                traceback.print_exc()
                continue


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
                if float(current_item['data'][item_name]['average']) * percent / 100 > float(sells_list[-3]) \
                        and float(current_item['data'][item_name]['average']) < sell_price:
                    sell_price = float(current_item['data'][item_name]['average'])
                elif float(sells_list[-3]) < sell_price * percent / 100:
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
                          f" а 3 с конца продажа {sells_list[-3]} рублей")
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
    update_inventory()
    try:
        now = datetime.now()
        url = f"https://market.csgo.com/api/v2/my-inventory/?key={api_key}"
        all_sell_items = send_req(url)
        if int(now.hour) < 2:
            hour = 0
        else:
            hour = int(now.hour)-2
        date = datetime(year=int(now.year), month=int(now.month), day=int(now.day), hour=hour,
                        minute=int(now.minute), second=int(now.second)).timestamp()
        time_end = datetime.now().timestamp()
        url_his = f"https://market.csgo.com/api/v2/history?key={api_key}&date={date}&date_end={time_end}"
        data = send_req(url_his)
        for item_his in reversed(range(len(data['data']))):
            if data['data'][item_his]['event'] == "sell" and data['data'][item_his]['stage'] == "5":
                for item_sell in range(len(all_sell_items['items'])):
                    if data['data'][item_his]['market_hash_name'] == all_sell_items['items'][item_sell]['market_hash_name']:
                        item_price = float("{0:.2f}".format(float(data['data'][item_his]['received']) * percent))
                        item_name = all_sell_items['items'][item_sell]['market_hash_name']
                        url_sell = f"https://market.csgo.com/api/v2/add-to-sale?key={api_key}&id=" \
                            f"{all_sell_items['items'][item_sell]['id']}&price=" \
                            f"{item_price}&cur=RUB"
                        sell_result = send_req(url_sell)
                        if sell_result['success']:
                            print(f"{item_name} снова выставлен на продажу за {item_price / 100} рублей")
    except JSONDecodeError:
        pass
    except:
        print("В sell_item_again")
        traceback.print_exc()


def check_all_orders():
    items_counter = 0
    link_items = ""
    item_names = {}
    last_item = False
    for item_data_order in my_orders:
        if item_data_order == my_orders[-1]:
            last_item = True
        try:
            class_instance_str = f"{item_data_order['i_classid']}_{item_data_order['i_instanceid']}"
            for item in all_items['items']:
                try:
                    if class_instance_str == item:
                        if items_counter < 49 and not last_item:
                            items_counter += 1
                            link_items += "&list_hash_name[]=" + all_items['items'][item]['market_hash_name']
                            item_names.update({item: all_items['items'][item]['market_hash_name']})
                        else:
                            url_item = f"https://market.csgo.com/api/v2/get-list-items-info?key={api_key}{link_items}"
                            link_items = ""
                            item_data = send_req(url_item)
                            items_counter = 0
                            for item_id in item_names:
                                try:
                                    class_instance = str(item_id).split('_')
                                    if item_data['data'][item_names[item_id]]['history']:
                                        try:
                                            avg_price = items_dict[item_names[item_id]][0]
                                        except KeyError:
                                            if item_data['data'][item_names[item_id]]['average']:
                                                avg_price = item_data['data'][item_names[item_id]]['average']
                                            else:
                                                continue
                                        buy_order = float(all_items['items'][item_id]['buy_order'])
                                        sales_history = []
                                        min_border = float(avg_price) / min_border_cf
                                        max_border = float(avg_price) * max_border_cf
                                        for sale_info in item_data['data'][item_names[item_id]]['history']:
                                            if sale_info[0] > week_ago and max_border > float(sale_info[1]) > min_border:
                                                sales_history.append(sale_info[1])
                                        sales_history.sort()
                                        if len(sales_history) > 5:
                                            min_sells = [sales_history[0], sales_history[1], sales_history[2]]
                                            buy_order = float(item_data_order['o_price']) / 100
                                            predict_sell_price = predict_price(100, sales_history, float(avg_price))
                                            with_predict_price = predict_sell_price / buy_order
                                            if with_predict_price > with_predict_price_cf and buy_order > 250:
                                                if check_buying_item(item_names[item_id], buy_order, avg_price, sales_history):
                                                    print(f"Подходит запрос на {item_names[item_id]} по {buy_order}, "
                                                          f"средняя {avg_price}, "
                                                          f"предполагаемой продажи {predict_sell_price}, "
                                                          f"минимальные продажи {min_sells}")
                                                    continue
                                        if start_buy_for == 1:
                                            update_order_for(class_instance[0], class_instance[1], 0)
                                        else:
                                            update_order(class_instance[0], class_instance[1], 0)
                                        print(f"Удалён запрос на {item_names[item_id]} по {buy_order}, "
                                              f"средняя {avg_price}")
                                    item_names = {}
                                except:
                                    continue
                except:
                    continue
        except:
            continue


def delete_expensive_orders():
    for item_data_order in my_orders:
        try:
            order_price = float(item_data_order['o_price']) / 100
            if order_price > my_balance:
                if start_buy_for == 1:
                    update_order_for(item_data_order['i_classid'], item_data_order['i_instanceid'], 0)
                else:
                    update_order(item_data_order['i_classid'], item_data_order['i_instanceid'], 0)
                print(f"Удален ордер на {item_data_order['i_market_hash_name']} за {order_price}")
        except:
            traceback.print_exc()
            continue


def check_time():
    """
    Проверка времени для переодических действий
    """
    try:
        time_now = datetime.today().strftime("%H.%M")
        if time_now == "10.40":
            remove_all_sales()
            sell_item(second_percent)
            if int(datetime.now().day) % 5 == 0:
                codecs.open("history.txt", mode='w', encoding='utf-8', errors='ignore').close()
        if time_now == "10.50":
            sell_item(second_percent)
        if time_now == "11.02":
            update_inventory()
        if time_now == "11.05" or time_now == "11.15" or time_now == "11.25":
            update_inventory()
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
    url = f"https://market.csgo.com/api/v2/ping?key={api_key}"
    return send_req(url)


def update_inventory():
    """
    Обновить инвентарь
    """
    url = f"https://market.csgo.com/api/v2/update-inventory/?key={api_key}"
    return send_req(url)


def check_trades():
    """
    Проверить есть ли активные трейды для подтверждения
    """
    url = f"https://market.csgo.com/api/v2/trades/?key={api_key}"
    return send_req(url)


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
    url = f"https://market.csgo.com/api/v2/go-offline?key={api_key}"
    return send_req(url)


def create_trade():
    """
    Создать трейд для подтверждения
    """
    url = f"https://market.csgo.com/api/v2/trade-request-give-p2p?key={api_key}"
    return send_req(url)


def get_my_orders():
    url = f"https://market.csgo.com/api/GetOrders/?key={api_key}"
    return send_req(url)


def create_order(classid, instanceid, item_price_in):
    item_price = item_price_in * 100
    url = f"https://market.csgo.com/api/InsertOrder/{classid}/{instanceid}/{item_price}/?key={api_key}"
    return send_req(url)


def update_order(classid, instanceid, item_price_in):
    item_price = item_price_in * 100
    url = f"https://market.csgo.com/api/UpdateOrder/{classid}/{instanceid}/{item_price}/?key={api_key}"
    return send_req(url)


def create_order_for(classid, instanceid, item_price_in):
    item_price = item_price_in * 100
    url = f"https://market.csgo.com/api/InsertOrder/{classid}/{instanceid}/{item_price}/?key={api_key}&{url_for}"
    return send_req(url)


def update_order_for(classid, instanceid, item_price_in):
    item_price = item_price_in * 100
    url = f"https://market.csgo.com/api/UpdateOrder/{classid}/{instanceid}/{item_price}/?key={api_key}&{url_for}"
    return send_req(url)


def delete_all_orders():
    url = f"https://market.csgo.com/api/DeleteOrders/?key={api_key}"
    return send_req(url)


def remove_all_sales():
    """
    Удалить все предметы с продажи
    """
    url = f"https://market.csgo.com/api/v2/remove-all-from-sale?key={api_key}"
    return send_req(url)


def get_balance():
    my_balance = ""
    while my_balance == "":
        try:
            url = f"https://market.csgo.com/api/v2/get-money?key={api_key}"
            my_balance = float(send_req(url)['money'])
        except:
            my_balance = ""
    return my_balance


def send_req(url):
    again = 1
    while again < 20:
        try:
            data = requests.get(url)
            res = json.loads(data.text)
            return res
        except JSONDecodeError:
            again += 1
        except:
            traceback.print_exc()
            again += 1


def start_actions():
    try:
        create_trade()
        open_sda()
        ping()
    except:
        pass


def schedule_run():
    while True:
        schedule.run_pending()
        time.sleep(65)


schedule.every(2).minutes.do(start_actions)
schedule.every(1).minutes.do(check_time)


if __name__ == "__main__":
    """
        Настройки
    """
    first_percent = 106
    second_percent = 102
    url_for = f""
    start_buy_for = 0
    max_buys = 25
    username = ""
    account_number = 1
    if account_number == 1:
        price_border_1 = 500
        price_border_2 = 1000
        price_border_3 = 1500
        price_border_4 = 2000
        price_border_5 = 2500
        price_border_6 = 4000
    elif account_number == 2:
        price_border_1 = 1000
        price_border_2 = 1500
        price_border_3 = 2000
        price_border_4 = 2500
        price_border_5 = 4000
        price_border_6 = 100000
    max_sells = 50
    min_buy_order = 25
    item_popularity = 14
    run_counter = 0
    stop_buy = 0
    buy_count = 0
    sell_count = 0
    stop_login = 0
    start_check_all = 0
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
    min_price = 500
    popularity = 5
    with_predict_price_cf = 1.25
    min_border_cf = 1.6
    max_border_cf = 1.6
    week_ago = (datetime.now() - timedelta(days=21)).timestamp()
    bot_thread = Process(target=schedule_run)
    bot_thread.start()
    try:
        account_login, account_password, mafile_path = search_file_and_names(username)
        accept_gift_trades()
    except:
        pass
    while True:
        try:
            check_time()
        except:
            pass
        try:
            create_trade()
            open_sda()
            sell_item(first_percent)
            sell_item_again(1.054)
            try:
                if stop_login < 1:
                    accept_gift_trades()
                else:
                    stop_login -= 1
            except InvalidCredentials:
                stop_login = 5
            except:
                stop_login = 1
            if buy_count < max_buys:
                my_balance = get_balance()
                items_dict = collect_dict_avg()
                my_orders = get_my_orders()['Orders']
                all_items, active_orders = price_parser()
                set_orders_for_all()
                start_check_all += 1
                if start_check_all % 100 == 0:
                    try:
                        delete_expensive_orders()
                    except:
                        traceback.print_exc()
                        pass
                if start_check_all > 250:
                    try:
                        check_all_orders()
                        start_check_all = 0
                    except:
                        traceback.print_exc()
                        pass
            else:
                stop_buy -= 1
                time.sleep(5)
            if sell_count < max_sells:
                ping()
            else:
                go_offline()
            if buy_count > max_buys and sell_count > max_sells - 1:
                print("Sleep")
                time.sleep(3600)
        except:
            traceback.print_exc()
            pass
