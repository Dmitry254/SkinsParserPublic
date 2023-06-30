import requests
import json
from key import api_keys


def get_balances():
    try:
        text = ""
        for key in api_keys:
            item_count = 0
            item_sum = 0
            url = f"https://market.csgo.com/api/v2/get-money?key={key}"
            api = requests.get(url)
            data = json.loads(api.text)
            url1 = f"https://market.csgo.com/api/v2/items?key={key}"
            api1 = requests.get(url1)
            data1 = json.loads(api1.text)
            if data1['items']:
                for item in data1['items']:
                    if item['status'] == "1":
                        item_count += 1
                        item_sum += item['price'] * 0.92
            item_sum = int(item_sum)
            text += f"На {api_keys.index(key) + 1} боте {data['money']} рублей и продаётся {item_count} вещей на сумму {item_sum}рублей\n"
        return text
    except:
        return "Ошибочка вышла"


if __name__ == "__main__":
    print(get_balances())
