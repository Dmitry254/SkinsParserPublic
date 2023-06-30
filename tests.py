import time
import traceback
from datetime import datetime, date, timedelta
from json import JSONDecodeError
# import psutil
import os
import codecs
# import pyotp
import requests
import json
import random
from key import *

def my_orders():
    url = f"https://bitskins.com/api/v1/get_active_buy_orders/?api_key={api_bit}&code={my_token}"
    api = requests.get(url)
    data = json.loads(api.text)
    print(data)


def cancel_orders():
    url = f"https://bitskins.com/api/v1/get_active_buy_orders/?api_key={api_bit}&code={my_token}"
    api = requests.get(url)
    data = json.loads(api.text)
    print(data)


def item_price2():
    data2 = []
    url1 = f"https://bitskins.com/api/v1/get_price_data_for_items_on_sale/?api_key={api_bit}&code={my_token}"
    api = requests.get(url1)
    data = json.loads(api.text)
    for item in (data['data']['items']):
        if (item['recent_sales_info'] and item['recent_sales_info']['hours']
                and item['recent_sales_info']['average_price'] and float(item['recent_sales_info']['hours']) > 30
                and item['lowest_price'] and 10 > float(item['lowest_price']) > 1):
            data2.append(item)
    return data2


def all_orders():
    data1 = []
    url = f"https://bitskins.com/api/v1/summarize_buy_orders/?api_key={api_bit}&code={my_token}"
    api = requests.get(url)
    data = json.loads(api.text)
    for item in data['data']['items']:
        if item[1]['max_price'] and float(item[1]['max_price']) > 1:
            data1.append(item)
    return data1


def parser():
    current_file = f"items_list_cs.txt"
    file = codecs.open(current_file, mode='a', encoding='utf-8', errors='ignore')
    file_r = codecs.open(current_file, mode='r', encoding='utf-8', errors='ignore')
    data_file = file_r.read()
    try:
        for item2 in data2:
            for item1 in data1:
                if item2['market_hash_name'] == item1[0]:
                    with_order = float(item2['lowest_price']) / float(item1[1]['max_price'])
                    with_avg = float(item2['recent_sales_info']['average_price']) / float(item1[1]['max_price'])
                    if with_order > 1.3 and with_avg < 1.8:
                        item_buy = (f"{item2['market_hash_name']} с ценой {item2['lowest_price']},"
                                    f" средней ценой {item2['recent_sales_info']['average_price']},"
                                    f" и автопокупкой {item1[1]['max_price']}.")
                        print(item_buy)
                        # buy_price = float(data1[1]['max_price']) * 1.1
                        # price = float(float("{0:.2f}".format(sell_price)))
                        # name = data2[count2]['market_hash_name']
                        # check_place(name, price)
                        # if item_buy not in data_file:
                        #     file.write(item_buy + '\n')
                        #     print(item_buy)
    finally:
        file_r.close()
        file.close()


def chtoto():
    filtered_count_items = 0
    start_time = datetime.now()
    end_time = datetime.now()
    work_time = end_time - start_time
    print(work_time)
    white_list = ["(Factory New)", "(Minimal Wear)", "(Field-Tested)", "(Well-Worn)", "(Battle-Scarred)"]
    url = "https://market.csgo.com/api/v2/prices/class_instance/RUB.json"
    api = requests.get(url)
    data = json.loads(api.text)
    source_count_items = len(data['items'])
    for item in data['items']:
        if (any(words in data['items'][item]['market_hash_name'] for words in white_list)
                and data['items'][item]['price'] and data['items'][item]['avg_price']
                and float(data['items'][item]['avg_price']) > 50):
            filtered_count_items += 1
    print(source_count_items)
    print(filtered_count_items)


def test_online():
    global bots_info
    for api_key in api_keys:
        url = f"https://market.csgo.com/api/v2/test?key={api_key}"
        api = requests.get(url)
        data = json.loads(api.text)
        if data['success']:
            tests = list(data['status'].values())
            bot_number = api_keys.index(api_key)
            if not tests[0]:
                bots_info[bot_number][0] += 1
            else:
                bots_info[bot_number][0] = 0
            if not tests[1]:
                bots_info[bot_number][1] += 1
            else:
                bots_info[bot_number][1] = 0
            if not tests[2]:
                bots_info[bot_number][2] += 1
            else:
                bots_info[bot_number][2] = 0
            if not tests[3]:
                bots_info[bot_number][3] += 1
            else:
                bots_info[bot_number][3] = 0
    for bot in bots_info:
        if 3 in bot:
            print(f"Есть проблема на {bots_info.index(bot) + 1} боте")


def check_item(item_name):
    url = f"https://market.csgo.com/api/v2/get-list-items-info?key={api_key}&list_hash_name[]={item_name}"
    api = requests.get(url)
    data = json.loads(api.text)
    print(data)


def check_items_history(item_name):
    item_counter = 0
    file_r = codecs.open("history.txt", mode='r', encoding='utf-8', errors='ignore')
    for line in file_r.readlines():
        if item_name in line:
            item_counter += 1
        if item_counter > 2:
            black_list.append(item_name)
            return False
    print(black_list)
    return True


def test_proc():
    process_count = 0
    for process in psutil.process_iter():
        process_count += 1
        print(process)
    print(process_count)


def random_no():
    no_text = random.choice(["Неа"])
    return no_text


def order_buy_for():
    url = f"https://market.csgo.com/api/InsertOrder/310776722/302028390/108/?key={my_api_key}&{url_for}"
    result = requests.get(url)
    trades_info = json.loads(result.text)
    print(trades_info)


if __name__ == "__main__":
    url_for = ""
    my_api_key = ""
    order_buy_for()
    # print(random_no())   (&partner=[partner]&token=[token])
    print(len([100, 12, 12, 3]))
    black_list = []
    # check_item("StatTrak™ Sawed-Off | Apocalypto (Well-Worn)")
    # current_day = (datetime.today() - timedelta(days=1)).strftime("%Y %m %d")
    # print(current_day)
    # date.today()
    # my_secret = google_code
    # my_token = pyotp.totp.TOTP(my_secret).now()
    # data1 = all_orders()
    # data2 = item_price2()
    # parser()
    # item_name = "Galil AR | Connexion (Battle-Scarred)"
    # black_list = ["Fracture", "Negev | Ultralight", "P2000 | Gnarled", "SG 553 | Ol' Rusty",
    #               "SSG 08 | Mainframe 001", "P250 | Cassette", "P90 | Freight", "PP-Bizon | Runic",
    #               "MAG-7 | Monster Call", "Tec-9 | Brother", "MAC-10 | Allure", "Galil AR | Connexion",
    #               "MP5-SD | Kitbash", "M4A4 | Tooth Fairy", "Glock-18 | Vogue", "XM1014 | Entombed",
    #               "Desert Eagle | Printstream", "AK-47 | Legion of Anubis", "Five-SeveN | Hyper Beast (Well-Worn)"]
    # print(not any(words in item_name for words in black_list))
    # # print(datetime.today() - timedelta(days=2))
    # test_proc()
    black_list = ["Fracture", "Negev | Ultralight", "P2000 | Gnarled", "SG 553 | Ol' Rusty",
                  "SSG 08 | Mainframe 001", "P250 | Cassette", "P90 | Freight", "PP-Bizon | Runic",
                  "MAG-7 | Monster Call", "Tec-9 | Brother", "MAC-10 | Allure", "Galil AR | Connexion",
                  "MP5-SD | Kitbash", "M4A4 | Tooth Fairy", "Glock-18 | Vogue", "XM1014 | Entombed",
                  "Desert Eagle | Printstream", "AK-47 | Legion of Anubis", "Five-SeveN | Hyper Beast (Well-Worn)",
                  "Sawed-Off | Devourer (Minimal Wear)", "StatTrak™ M4A4 | 龍王 (Dragon King)",
                  "StatTrak™ P90 | Shapewood (Battle-Scarred)",
                  # Fracture case
                  "Little Kev", "Safecracker Voltzmann", "Sir Bloody", "Getaway Sally", "Number K", "Cmdr. Mae",
                  "Dragomir", "'Two Times'", "Rezan the Redshirt", "'Blueberries' Buckshot", "Street Soldier",
                  "John 'Van Healen'", "Bio-Haz Specialist", "1st Lieutenant Farlow", "Sergeant Bombson", "Chem-Haz",
                  # Fang agents
                  "M249 | Predator", "PP-Bizon | Death Rattle", "Tec-9 | Phoenix Chalk", "Sawed-Off | Clay Ambush",
                  "Dual Berettas | Heist", "MP7 | Vault Heist", "UMP-45 | Houndstooth", "R8 Revolver | Phoenix Marker",
                  "Nova | Rust Coat", "P90 | Tiger Pit", "P250 | Bengal Tiger", "Negev | Phoenix Stencil",
                  "Desert Eagle | Night Heist", "Glock-18 | Franklin", "Galil AR | Phoenix Blacklight",
                  "SG 553 | Hypnotic", "MAC-10 | Hot Snakes", "AWP | Silk Tiger", "AK-47 | X-Ray",
                  # The Havoc Collection
                  "AUG | Surveillance", "MP9 | Army Sheen", "CZ75-Auto | Jungle Dashed", "XM1014 | Charter",
                  "P250 | Forest Night", "Dual Berettas | Switch Board", "Desert Eagle | The Bronze", "AWP | Fade",
                  "MAG-7 | Carbon Fiber", "SCAR-20 | Magna Carta", "P2000 | Dispatch", "M4A1-S | Blue Phosphor",
                  "SSG 08 | Threat Detected", "M4A4 | Global Offensive", "FAMAS | Prime Conspiracy", "MP5-SD | Nitro",
                  "Five-SeveN | Berries And Cherries", "UMP-45 | Crime Scene", "USP-S | Target Acquired",
                  # The Control Collection
                  "Galil AR | Vandal", "MP5-SD | Condition Zero", "P250 | Contaminant", "CZ75-Auto | Vendetta",
                  "P90 | Cocoa Rampage", "G3SG1 | Digital Mesh", "M249 | Deep Relief", "UMP-45 | Gold Bismuth",
                  "Dual Berettas | Dezastre", "Nova | Clear Polymer", "SSG 08 | Parallax", "AWP | Exoskeleton",
                  "Five-SeveN | Fairy Tale", "USP-S | Monster Mashup", "M4A4 | Cyber Security", "Glock-18 | Neo-Noir",
                  "M4A1-S | Printstream",
                  # The Operation Broken Fang Collection
                  "G3SG1 | Ancient Ritual", "CZ75-Auto | Silver", "Galil AR | Dusk Ruins", "FAMAS | Dark Water",
                  "Tec-9 | Blast From the Past", "AUG | Carved Jade", "MAC-10 | Gold Brick", "XM1014 | Ancient Lore",
                  "USP-S | Ancient Visions", "P90 | Run and Hide", "AK-47 | Panthera onca",
                  "M4A1-S | Welcome to the Jungle",
                  # The Ancient Collection
                  "2020 RMR"
                  # RMR Stickers
                  ]


# {'success': True, 'trades': [{'dir': 'in', 'trade_id': '4065279759', 'bot_id': '218108937', 'timestamp': 1590468955, 'secret': '9DXW', 'nik': 'PopjaJZ'}]}
# {'success': False, 'error': 'active trades from market not found'}
# {'success': True, 'trades': [{'dir': 'in', 'trade_id': '0', 'bot_id': '342220822', 'timestamp': 1590461792, 'secret': 'FZ32', 'nik': 'radsrei'}]}
# {'success': True, 'trades': [{'dir': 'out', 'trade_id': '4067923943', 'bot_id': '1066570508', 'timestamp': 1590635751, 'secret': 'DUYE', 'nik': 'НАТАХА'}, {'dir': 'out', 'trade_id': '0', 'bot_id': '1086957321', 'timestamp': 1590635786, 'secret': 'U66O', 'nik': '85mie8ntit3wjb8'}]}