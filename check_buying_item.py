import requests
import json
from datetime import datetime


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
        if avg_price * 1.4 > sell[1]:
            filtered_sells.append(sell[1])
    try:
        checked_avg_price = float(sum(filtered_sells) / len(filtered_sells))
        result_percent = checked_avg_price / avg_price
        real_with_avg = float(checked_avg_price) / (float(item_price))
    except ZeroDivisionError:
        return False
    print(real_with_avg)
    print(len(item_history))
    print(avg_price)
    print(checked_avg_price)
    print(filtered_sells)
    print(len(filtered_sells))
    if (1.15 < result_percent < 0.80 or avg_price - checked_avg_price > 500 or len(filtered_sells) * 1.35 < sells_counter) \
            and real_with_avg < 1.25:
        print(f"{item_name} не купил за {item_price}, средняя цена была {current_item['data'][item_name]['average']}, "
              f"а после проверки {checked_avg_price}")
        black_list.append(item_name)
        return False
    return True


if __name__ == "__main__":
    api_key = ""
    item_name = "StatTrak™ Desert Eagle | Bronze Deco (Minimal Wear)"
    item_price = 100
    black_list = ["Fracture", "Negev | Ultralight", "P2000 | Gnarled", "SG 553 | Ol' Rusty",
                  "SSG 08 | Mainframe 001", "P250 | Cassette", "P90 | Freight", "PP-Bizon | Runic",
                  "MAG-7 | Monster Call", "Tec-9 | Brother", "MAC-10 | Allure", "Galil AR | Connexion",
                  "MP5-SD | Kitbash", "M4A4 | Tooth Fairy", "Glock-18 | Vogue", "XM1014 | Entombed",
                  "Desert Eagle | Printstream", "AK-47 | Legion of Anubis", "Five-SeveN | Hyper Beast (Well-Worn)",
                  "Sawed-Off | Devourer (Minimal Wear)", "StatTrak™ M4A4 | 龍王 (Dragon King) (Minimal Wear)"]
    start_time = datetime.now()
    check_buying_item(item_name, item_price)
    end_time = datetime.now()
    print(end_time - start_time)
