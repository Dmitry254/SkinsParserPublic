import traceback
from json import JSONDecodeError
from datetime import datetime
import requests
import json
import time
import codecs


def test_price_parser():
    spaces = " " * 30
    global run_counter
    run_counter += 1
    print(run_counter)
    current_file = f"items_list_cs1.txt"
    file = codecs.open(current_file, mode='a', encoding='utf-8', errors='ignore')
    file_r = codecs.open(current_file, mode='r', encoding='utf-8', errors='ignore')
    data_file = file_r.read()
    try:
        url = "https://market.csgo.com/api/v2/prices/class_instance/RUB.json"
        api = requests.get(url)
        data = json.loads(api.text)
        for item in data['items']:
            if (data['items'][item]['price'] and float(data['items'][item]['price']) > 50
                and data['items'][item]['popularity_7d'] and float(data['items'][item]['popularity_7d']) > 10
                and data['items'][item]['buy_order'] and data['items'][item]['buy_order'] != 0
                    and data['items'][item]['price']):
                if data['items'][item]['avg_price']:
                    avg_price = data['items'][item]['avg_price']
                else:
                    avg_price = "0"
                with_order = float(data['items'][item]['price']) / (float((data['items'][item]['buy_order'])))
                # with_avg = float(data['items'][item]['avg_price']) / (float(data['items'][item]['price']))
                if with_order < 1.05:
                    item_buy = (data['items'][item]['ru_name'] + ", Цена: " + data['items'][item]['price'] +
                                ", Средняя цена: " + avg_price +
                                ", Запрос:" + str(data['items'][item]['buy_order']))
                    print(data['items'][item])
                    print(item_buy)
                    item_link = f"https://market.csgo.com/item/{str(item).replace('_', '-')}"
                    if item_buy not in data_file:
                        file.write(item_buy + spaces + item_link + '\n')
    except:
        traceback.print_exc()
    finally:
        file_r.close()
        file.close()


def collect_dict_avg():
    global dict_avg_price
    items_count = 0
    try:
        url = "https://market.csgo.com/api/v2/prices/class_instance/RUB.json"
        api = requests.get(url)
        data = json.loads(api.text)
        dict_avg_price = {}
        for item in data['items']:
            if (data['items'][item]['price'] and float(data['items'][item]['price']) > 50
                    and data['items'][item]['popularity_7d'] and float(data['items'][item]['popularity_7d']) > 10
                    and data['items'][item]['buy_order'] and float(data['items'][item]['buy_order']) > 25
                    and data['items'][item]['avg_price']):
                items_count += 1
                try:
                    avg_price_in_dict = dict_avg_price[data['items'][item]['market_hash_name']]
                    if avg_price_in_dict > float(data['items'][item]['avg_price']):
                        dict_avg_price.update(
                            {data['items'][item]['market_hash_name']: float(data['items'][item]['avg_price'])})
                except KeyError:
                    dict_avg_price.update({data['items'][item]['market_hash_name']: float(data['items'][item]['avg_price'])})
        print(items_count)
    except JSONDecodeError:
        pass


def test_price_parser_2():
    """
    Поиск и покупка вещей
    """
    global stop_buy
    global dict_avg_price
    item_count = 0
    try:
        url = "https://market.csgo.com/api/v2/prices/class_instance/RUB.json"
        api = requests.get(url)
        data = json.loads(api.text)
        for item in data['items']:
            if (data['items'][item]['price'] and float(data['items'][item]['price']) > 50
                    and data['items'][item]['buy_order'] and float(data['items'][item]['buy_order']) > 25):
                item_count += 1
                try:
                    avg_price = dict_avg_price[data['items'][item]['market_hash_name']]
                    avg_status = "из словаря"
                except KeyError:
                    continue
                with_order = float(data['items'][item]['price']) / (float((data['items'][item]['buy_order'])))
                with_avg = avg_price / (float(data['items'][item]['price']))
                if (with_order < 1.03 and with_avg > 1.25) or with_avg > 1.4:
                    current_file = f"items_list_cs.txt"
                    file = codecs.open(current_file, mode='a', encoding='utf-8', errors='ignore')
                    file_r = codecs.open(current_file, mode='r', encoding='utf-8', errors='ignore')
                    data_file = file_r.read()
                    item_buy = f"Купил {str(data['items'][item]['market_hash_name'])} за {float(data['items'][item]['price'])}"
                    item_link = f"https://market.csgo.com/item/{str(item).replace('_', '-')}"
                    if item_buy not in data_file:
                        item_result = f"{item_buy} со средней ценой {avg_price} {avg_status}"
                        file.write(item_result + " " * 20 + item_link + '\n')
                        print(item_result)
                    file.close()
                    file_r.close()
        # print(item_count)
    except JSONDecodeError:
        pass
    except:
        print("В price_parser")
        traceback.print_exc()


def one_start():
    start_time = datetime.now()
    test_price_parser_2()
    end_time = datetime.now()
    work_time = end_time - start_time
    print(work_time)


def cycle_start():
    collect_dict_avg()
    run_counter = 0
    while True:
        run_counter += 1
        if run_counter % 150:
            collect_dict_avg()
        test_price_parser_2()
        time.sleep(20)


if __name__ == "__main__":
    collect_dict_avg()
    # run_counter = 0
    # while True:
    #     try:
    #         run_counter += 1
    #         if run_counter % 150 == 0:
    #             collect_dict_avg()
    #         test_price_parser_2()
    #         time.sleep(20)
    #     except:
    #         traceback.print_exc()
